import logging
import uuid
from typing import List

from qdrant_client import QdrantClient, models

from models.db_schemes import RetrievedDocument
from ..VectorDBEnums import DistanceMethodEnums
from ..VectorDBInterface import VectorDBInterface


class QdrantDBProvider(VectorDBInterface):
    def __init__(
        self,
        db_path: str,
        distance_method: str,
        default_vector_size: int = 768,
    ):
        self.client = None
        self.db_path = db_path
        self.default_vector_size = default_vector_size or 768
        self.collection_prefix = "collection"

        normalized_method = (distance_method or "").strip().lower()
        '''
        if self.distance_method == DistanceMethodEnums.COSINE.value:
            self.distance_method = models.Distance.COSINE
        elif self.distance_method == DistanceMethodEnums.EUCLID.value:
            self.distance_method = models.Distance.EUCLID
        elif self.distance_method == DistanceMethodEnums.DOT.value:
            self.distance_method = models.Distance.DOT
        '''

        #hard coded as I had some errors
        distance_mapping = {
            DistanceMethodEnums.COSINE.value.lower(): models.Distance.COSINE,
            "cosine": models.Distance.COSINE,
            DistanceMethodEnums.EUCLID.value.lower(): models.Distance.EUCLID,
            "euclid": models.Distance.EUCLID,
            "l2": models.Distance.EUCLID,
            DistanceMethodEnums.DOT.value.lower(): models.Distance.DOT,
            "dot": models.Distance.DOT,
        }
        if normalized_method not in distance_mapping:
            raise ValueError(f"Unsupported distance method: {distance_method}")
        self.distance_method = distance_mapping[normalized_method]

        #to debug
        self.logger = logging.getLogger("uvicorn.error")

    async def connect(self):
        self.client = QdrantClient(path=self.db_path)

    async def disconnect(self):
        if self.client and hasattr(self.client, "close"):
            self.client.close()
        self.client = None

    async def is_collection_exists(self, collection_name: str) -> bool:
        return self.client.collection_exists(collection_name=collection_name)

    async def list_all_collections(self) -> List:
        return self.client.get_collections()

    async def get_collection_info(self, collection_name: str) -> dict:
        return self.client.get_collection(collection_name=collection_name)

    async def delete_collection(self, collection_name: str):
        if await self.is_collection_exists(collection_name):
            self.logger.info("Deleting vector collection: %s", collection_name)
            return self.client.delete_collection(collection_name=collection_name)
        return True

    async def create_collection(
        self,
        collection_name: str,
        embedding_size: int,
        do_reset: bool = False,
    ):
        if do_reset:
            await self.delete_collection(collection_name)

        if await self.is_collection_exists(collection_name):
            return False

        self.logger.info("Creating Qdrant collection: %s", collection_name)
        return self.client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams( #the pars are taken from the documentation of qdrant
                size=embedding_size or self.default_vector_size,
                distance=self.distance_method,
            ),
        )

    async def insert_one(
        self,
        collection_name: str,
        text: str,
        vector: list,
        metadata: dict = None,
        record_id: str = None,
    ):
        if not await self.is_collection_exists(collection_name):
            #   raise ValueError(f"Collection '{collection_name}' does not exist.")
            self.logger.error("Vector collection does not exist: %s", collection_name)
            return False

        try:
            self.client.upload_records(
                collection_name=collection_name,
                records=[
                    models.Record(
                        id=record_id if record_id is not None else str(uuid.uuid4()),
                        vector=vector,
                        payload={"text": text, "metadata": metadata},
                    )
                ],
            )
        except Exception:
            self.logger.exception("Failed to upload a Qdrant record")
            return False
        return True

    async def insert_many(
        self,
        collection_name: str,
        texts: list,
        vectors: list,
        metadata: list = None,
        record_ids: list = None,
        batch_size: int = 100,
    ):
        if not await self.is_collection_exists(collection_name):
            self.logger.error("Vector collection does not exist: %s", collection_name)
            return False

        item_count = len(texts)
        if len(vectors) != item_count:
            self.logger.error("Texts and vectors must have equal lengths")
            return False
        if metadata is None: #explained in my notes
            metadata = [None] * item_count
        if record_ids is None:
            record_ids = [str(uuid.uuid4()) for _ in texts]
        if len(metadata) != item_count or len(record_ids) != item_count:
            self.logger.error("Vector record fields must have equal lengths")
            return False

        # Implementation for inserting many records
        batch_size = max(1, int(batch_size))
        for start in range(0, item_count, batch_size):
            #i + batch_size is the last index we have reached in the loop, so we take the slice from i to i + batch_size
            end = start + batch_size
            records = [
                models.Record(
                    id=record_id,
                    vector=vector,
                    payload={"text": text, "metadata": item_metadata},
                )
                for text, vector, item_metadata, record_id in zip(
                    texts[start:end],
                    vectors[start:end],
                    metadata[start:end],
                    record_ids[start:end],
                )
            ]
            try:
                self.client.upload_records(
                    collection_name=collection_name,
                    records=records,
                )
            except Exception:
                self.logger.exception("Failed to upload Qdrant records")
                return False
        return True

    async def search_by_vector(
        self, collection_name: str, vector: list, limit: int = 5
    ):
        results = self.client.search(
            collection_name=collection_name,
            query_vector=vector,
            limit=limit,
        )
        if not results:
            return None

        return [
            RetrievedDocument(score=result.score, #pydantic to retun those only
                              text=result.payload["text"])
            for result in results
        ]
