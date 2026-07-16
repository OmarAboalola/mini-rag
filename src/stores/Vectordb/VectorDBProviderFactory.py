from .providers import QdrantDBProvider
from .VectorDBEnums import VectorDBTypes
from controllers.BaseController import BaseController


class VectorDBProviderFactory:
    def __init__(self, config):
        self.config = config
        self.base_controller = BaseController()

    def create(self, provider: str):
        normalized_provider = (provider or "").strip().lower()
        if normalized_provider == VectorDBTypes.Qdrant.value.lower():
            db_path = self.base_controller.get_database_path(data_base_name=self.config.VECTOR_DB_PATH)
            return QdrantDBProvider(
                db_path=db_path,
                distance_method=self.config.VECTOR_DB_DISTANCE_METHOD,
            )
        return None
