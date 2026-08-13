from .providers import PGVectorProvider, QdrantDBProvider
from .VectorDBEnums import VectorDBTypes
from controllers.BaseController import BaseController
from sqlalchemy.orm import sessionmaker


class VectorDBProviderFactory:
    def __init__(self, config, db_client: sessionmaker = None):
        self.config = config
        self.base_controller = BaseController()
        self.db_client = db_client

    def create(self, provider: str):
        normalized_provider = (provider or "").strip().lower()
        if normalized_provider == VectorDBTypes.Qdrant.value.lower():
            db_path = self.base_controller.get_database_path(data_base_name=self.config.VECTOR_DB_PATH)
            return QdrantDBProvider(
                db_path=db_path,
                distance_method=self.config.VECTOR_DB_DISTANCE_METHOD,
                default_vector_size=self.config.EMBEDDING_MODEL_SIZE,
            )

        if normalized_provider == VectorDBTypes.PGVECTOR.value.lower():
            if self.db_client is None:
                raise ValueError("PGVECTOR requires a PostgreSQL session factory")

            return PGVectorProvider(
                db_client=self.db_client,
                distance_method=self.config.VECTOR_DB_DISTANCE_METHOD,
                default_vector_size=self.config.EMBEDDING_MODEL_SIZE,
                index_threshold=self.config.VECTOR_DB_PGVEC_INDEX_THRESHOLD,
            )

        return None
