import json
import logging
import re
from typing import List

from sqlalchemy.sql import text as sql_text

from models.db_schemes import RetrievedDocument
from ..VectorDBEnums import (
    DistanceMethodEnums,
    PgVectorDistanceMethodEnums,
    PgVectorDistanceOperatorEnums,
    PgVectorIndexTypeEnums,
    PgVectorTableSchemeEnums,
)
from ..VectorDBInterface import VectorDBInterface


class PGVectorProvider(VectorDBInterface):
    _VALID_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

    def __init__(
        self,
        db_client,
        default_vector_size: int = 768,
        distance_method: str = None,
        index_threshold: int = 100,
    ):
        if db_client is None:
            raise ValueError("A PostgreSQL session factory is required")

        self.db_client = db_client
        self.default_vector_size = default_vector_size or 768
        self.index_threshold = max(0, index_threshold)
        self.pgvector_table_prefix = PgVectorTableSchemeEnums._PREFIX.value
        self.collection_prefix = self.pgvector_table_prefix
        self.distance_method, self.distance_operator = self._resolve_distance_method(
            distance_method
        )
        self.logger = logging.getLogger("uvicorn.error")

    @staticmethod
    def _resolve_distance_method(distance_method: str):
        normalized = (distance_method or DistanceMethodEnums.COSINE.value).strip().lower()

        distance_mapping = {
            DistanceMethodEnums.COSINE.value.lower(): (
                PgVectorDistanceMethodEnums.COSINE.value,
                PgVectorDistanceOperatorEnums.COSINE.value,
            ),
            "cosine": (
                PgVectorDistanceMethodEnums.COSINE.value,
                PgVectorDistanceOperatorEnums.COSINE.value,
            ),
            DistanceMethodEnums.EUCLID.value.lower(): (
                PgVectorDistanceMethodEnums.EUCLID.value,
                PgVectorDistanceOperatorEnums.EUCLID.value,
            ),
            "euclid": (
                PgVectorDistanceMethodEnums.EUCLID.value,
                PgVectorDistanceOperatorEnums.EUCLID.value,
            ),
            "l2": (
                PgVectorDistanceMethodEnums.EUCLID.value,
                PgVectorDistanceOperatorEnums.EUCLID.value,
            ),
            DistanceMethodEnums.DOT.value.lower(): (
                PgVectorDistanceMethodEnums.DOT.value,
                PgVectorDistanceOperatorEnums.DOT.value,
            ),
            "dot": (
                PgVectorDistanceMethodEnums.DOT.value,
                PgVectorDistanceOperatorEnums.DOT.value,
            ),
            "inner_product": (
                PgVectorDistanceMethodEnums.DOT.value,
                PgVectorDistanceOperatorEnums.DOT.value,
            ),
        }

        try:
            return distance_mapping[normalized]
        except KeyError as exc:
            raise ValueError(f"Unsupported pgvector distance method: {distance_method}") from exc

    @classmethod
    def _quote_identifier(cls, identifier: str) -> str:
        if not cls._VALID_IDENTIFIER.fullmatch(identifier or ""):
            raise ValueError(f"Invalid PostgreSQL identifier: {identifier!r}")
        return f'"{identifier}"'

    def _default_index_name(self, collection_name: str) -> str:
        return f"{collection_name}_vector_idx"

    @staticmethod
    def _serialize_vector(vector: list) -> str:
        if not isinstance(vector, (list, tuple)) or not vector:
            raise ValueError("Vector must be a non-empty list or tuple")
        return "[" + ",".join(str(float(value)) for value in vector) + "]"

    async def connect(self):
        async with self.db_client() as session:
            await session.execute(sql_text("CREATE EXTENSION IF NOT EXISTS vector"))
            await session.commit()

    async def disconnect(self):
        # The SQLAlchemy engine owns the connection pool and is disposed by the app.
        return None

    async def is_collection_exists(self, collection_name: str) -> bool:
        self._quote_identifier(collection_name)
        async with self.db_client() as session:
            result = await session.execute(
                sql_text(
                    "SELECT EXISTS ("
                    "SELECT 1 FROM pg_tables "
                    "WHERE schemaname = current_schema() AND tablename = :collection_name"
                    ")"
                ),
                {"collection_name": collection_name},
            )
            return bool(result.scalar_one())

    async def list_all_collections(self) -> List[str]:
        async with self.db_client() as session:
            result = await session.execute(
                sql_text(
                    "SELECT tablename FROM pg_tables "
                    "WHERE schemaname = current_schema() AND tablename LIKE :prefix "
                    "ORDER BY tablename"
                ),
                {"prefix": f"{self.pgvector_table_prefix}_%"},
            )
            return list(result.scalars().all())

    async def get_collection_info(self, collection_name: str) -> dict:
        table_name = self._quote_identifier(collection_name)
        if not await self.is_collection_exists(collection_name):
            return None

        async with self.db_client() as session:
            table_info = await session.execute(
                sql_text(
                    "SELECT schemaname, tablename, tableowner, tablespace, hasindexes "
                    "FROM pg_tables "
                    "WHERE schemaname = current_schema() AND tablename = :collection_name"
                ),
                {"collection_name": collection_name},
            )
            record_count = await session.execute(
                sql_text(f"SELECT COUNT(*) FROM {table_name}")
            )
            table_data = table_info.one()

            return {
                "table_info": {
                    "schemaname": table_data.schemaname,
                    "tablename": table_data.tablename,
                    "tableowner": table_data.tableowner,
                    "tablespace": table_data.tablespace,
                    "hasindexes": table_data.hasindexes,
                },
                "record_count": record_count.scalar_one(),
            }

    async def delete_collection(self, collection_name: str):
        table_name = self._quote_identifier(collection_name)
        self.logger.info("Deleting vector collection: %s", collection_name)
        async with self.db_client() as session:
            await session.execute(sql_text(f"DROP TABLE IF EXISTS {table_name}"))
            await session.commit()
        return True

    async def create_collection(
        self,
        collection_name: str,
        embedding_size: int,
        do_reset: bool = False,
    ):
        table_name = self._quote_identifier(collection_name)
        embedding_size = int(embedding_size or self.default_vector_size)
        if embedding_size <= 0:
            raise ValueError("Embedding size must be greater than zero")

        if do_reset:
            await self.delete_collection(collection_name)

        if await self.is_collection_exists(collection_name):
            return False

        self.logger.info("Creating pgvector collection: %s", collection_name)
        async with self.db_client() as session:
            await session.execute(
                sql_text(
                    f"CREATE TABLE {table_name} ("
                    f'"{PgVectorTableSchemeEnums.ID.value}" bigserial PRIMARY KEY, '
                    f'"{PgVectorTableSchemeEnums.TEXT.value}" text NOT NULL, '
                    f'"{PgVectorTableSchemeEnums.VECTOR.value}" vector({embedding_size}) NOT NULL, '
                    f'"{PgVectorTableSchemeEnums.METADATA.value}" jsonb NOT NULL DEFAULT \'{{}}\'::jsonb, '
                    f'"{PgVectorTableSchemeEnums.CHUNK_ID.value}" integer NOT NULL UNIQUE, '
                    f'FOREIGN KEY ("{PgVectorTableSchemeEnums.CHUNK_ID.value}") '
                    'REFERENCES "chunks" ("chunk_id") ON DELETE CASCADE'
                    ")"
                )
            )
            await session.commit()
        return True

    async def is_index_exists(self, collection_name: str) -> bool:
        self._quote_identifier(collection_name)
        index_name = self._default_index_name(collection_name)
        self._quote_identifier(index_name)
        async with self.db_client() as session:
            result = await session.execute(
                sql_text(
                    "SELECT EXISTS ("
                    "SELECT 1 FROM pg_indexes "
                    "WHERE schemaname = current_schema() "
                    "AND tablename = :collection_name AND indexname = :index_name"
                    ")"
                ),
                {"collection_name": collection_name, "index_name": index_name},
            )
            return bool(result.scalar_one())

    async def create_vector_index(
        self,
        collection_name: str,
        index_type: str = PgVectorIndexTypeEnums.HNSW.value,
    ):
        table_name = self._quote_identifier(collection_name)
        normalized_index_type = (index_type or "").strip().lower()
        allowed_index_types = {item.value for item in PgVectorIndexTypeEnums}
        if normalized_index_type not in allowed_index_types:
            raise ValueError(f"Unsupported pgvector index type: {index_type}")

        if await self.is_index_exists(collection_name):
            return False

        async with self.db_client() as session:
            result = await session.execute(
                sql_text(f"SELECT COUNT(*) FROM {table_name}")
            )
            if result.scalar_one() < self.index_threshold:
                return False

            index_name = self._quote_identifier(
                self._default_index_name(collection_name)
            )
            self.logger.info("Creating vector index for: %s", collection_name)
            await session.execute(
                sql_text(
                    f"CREATE INDEX {index_name} ON {table_name} "
                    f'USING {normalized_index_type} ("{PgVectorTableSchemeEnums.VECTOR.value}" '
                    f"{self.distance_method})"
                )
            )
            await session.commit()
        return True

    async def reset_vector_index(
        self,
        collection_name: str,
        index_type: str = PgVectorIndexTypeEnums.HNSW.value,
    ) -> bool:
        self._quote_identifier(collection_name)
        index_name = self._quote_identifier(
            self._default_index_name(collection_name)
        )
        async with self.db_client() as session:
            await session.execute(sql_text(f"DROP INDEX IF EXISTS {index_name}"))
            await session.commit()

        return await self.create_vector_index(collection_name, index_type)

    async def insert_one(
        self,
        collection_name: str,
        text: str,
        vector: list,
        metadata: dict = None,
        record_id: str = None,
    ):
        return await self.insert_many(
            collection_name=collection_name,
            texts=[text],
            vectors=[vector],
            metadata=[metadata],
            record_ids=[record_id],
            batch_size=1,
        )

    async def insert_many(
        self,
        collection_name: str,
        texts: list,
        vectors: list,
        metadata: list = None,
        record_ids: list = None,
        batch_size: int = 50,
    ):
        table_name = self._quote_identifier(collection_name)
        if not await self.is_collection_exists(collection_name):
            self.logger.error("Vector collection does not exist: %s", collection_name)
            return False

        item_count = len(texts)
        if not record_ids or len(vectors) != item_count or len(record_ids) != item_count:
            self.logger.error("Texts, vectors, and record IDs must have equal lengths")
            return False

        if metadata is None:
            metadata = [None] * item_count
        if len(metadata) != item_count:
            self.logger.error("Metadata and texts must have equal lengths")
            return False

        insert_sql = sql_text(
            f"INSERT INTO {table_name} "
            f'("{PgVectorTableSchemeEnums.TEXT.value}", '
            f'"{PgVectorTableSchemeEnums.VECTOR.value}", '
            f'"{PgVectorTableSchemeEnums.METADATA.value}", '
            f'"{PgVectorTableSchemeEnums.CHUNK_ID.value}") '
            "VALUES (:text, CAST(:vector AS vector), CAST(:metadata AS jsonb), :chunk_id) "
            f'ON CONFLICT ("{PgVectorTableSchemeEnums.CHUNK_ID.value}") DO UPDATE SET '
            f'"{PgVectorTableSchemeEnums.TEXT.value}" = EXCLUDED."{PgVectorTableSchemeEnums.TEXT.value}", '
            f'"{PgVectorTableSchemeEnums.VECTOR.value}" = EXCLUDED."{PgVectorTableSchemeEnums.VECTOR.value}", '
            f'"{PgVectorTableSchemeEnums.METADATA.value}" = EXCLUDED."{PgVectorTableSchemeEnums.METADATA.value}"'
        )

        batch_size = max(1, int(batch_size))
        async with self.db_client() as session:
            for start in range(0, item_count, batch_size):
                end = start + batch_size
                values = [
                    {
                        "text": item_text,
                        "vector": self._serialize_vector(item_vector),
                        "metadata": json.dumps(item_metadata or {}, ensure_ascii=False),
                        "chunk_id": item_record_id,
                    }
                    for item_text, item_vector, item_metadata, item_record_id in zip(
                        texts[start:end],
                        vectors[start:end],
                        metadata[start:end],
                        record_ids[start:end],
                    )
                ]
                await session.execute(insert_sql, values)
            await session.commit()

        await self.create_vector_index(collection_name)
        return True

    async def search_by_vector(
        self, collection_name: str, vector: list, limit: int = 5
    ):
        table_name = self._quote_identifier(collection_name)
        if not await self.is_collection_exists(collection_name):
            self.logger.error("Vector collection does not exist: %s", collection_name)
            return None

        limit = max(1, int(limit))
        serialized_vector = self._serialize_vector(vector)
        vector_column = f'"{PgVectorTableSchemeEnums.VECTOR.value}"'
        distance_expression = (
            f"{vector_column} {self.distance_operator} CAST(:vector AS vector)"
        )

        if self.distance_operator == PgVectorDistanceOperatorEnums.COSINE.value:
            score_expression = f"1 - ({distance_expression})"
        elif self.distance_operator == PgVectorDistanceOperatorEnums.EUCLID.value:
            score_expression = f"1 / (1 + ({distance_expression}))"
        else:
            score_expression = f"-({distance_expression})"

        search_sql = sql_text(
            f'SELECT "{PgVectorTableSchemeEnums.TEXT.value}" AS text, '
            f"{score_expression} AS score FROM {table_name} "
            f"ORDER BY {distance_expression} ASC LIMIT :limit"
        )

        async with self.db_client() as session:
            result = await session.execute(
                search_sql,
                {"vector": serialized_vector, "limit": limit},
            )
            return [
                RetrievedDocument(text=record.text, score=float(record.score))
                for record in result.fetchall()
            ]
