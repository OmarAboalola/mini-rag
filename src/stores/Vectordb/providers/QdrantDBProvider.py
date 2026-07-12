from qdrant_client import QdrantClient , models
from ..VectorDBInterface import VectorDBInterface
from ..VectorDBEnums import VectorDBType , DistanceMethodEnums
import logging
from typing import List

class QdrantDBProvider(VectorDBInterface):
    def __init__(self, db_path:str , distance_method: str):
        self.client = None
        self.db_path = db_path
        self.distance_method = distance_method

        if self.distance_method == DistanceMethodEnums.Cosine.value:
            self.distance_method = models.Distance.COSINE
        elif self.distance_method == DistanceMethodEnums.Euclidean.value:
            self.distance_method = models.Distance.EUCLIDEAN   
        elif self.distance_method == DistanceMethodEnums.DotProduct.value:
            self.distance_method = models.Distance.DOT

        logger = logging.getLogger(__name__)

    def connect(self):
        self.client = QdrantClient(path=self.db_path)

    def disconnect(self):
        self.client = None

    def is_collection_exists(self, collection_name: str) -> bool:
        return self.client.collection_exists(collection_name)

    def list_all_collections(self) -> List:
        return self.client.get_collections()

    def get_collection_info(self, collection_name: str) -> dict:
        return self.client.get_collection(collection_name=collection_name)
    
    def create_collection(self, collection_name: str,
                           embedding_size: int, 
                           do_reset: bool = False):
        if do_reset and self.is_collection_exists(collection_name):
            _=self.delete_collection(collection_name)

        if not self.is_collection_exists(collection_name):
            _=self.client.recreate_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams( #the pars are taken from the documentation of qdrant
                                size=embedding_size,
                                distance=self.distance_method)
            )
            return True
        return False    

    def delete_collection(self, collection_name: str):
        if self.is_collection_exists(collection_name):
            return self.client.delete_collection(collection_name=collection_name)

    def insert_one(self, collection_name: str, text: str, vector: list,
                         metadata: dict = None, record_id: str = None):
        
        if not self.is_collection_exists(collection_name):
        #   raise ValueError(f"Collection '{collection_name}' does not exist.")
            self.logger.error(f"Collection '{collection_name}' does not exist.")
            return False
        try:
            self.client.upload_records(
                collection_name=collection_name,
                records=[
                    models.Record(
                        vector=vector,
                        payload={
                            "text": text, 
                            "metadata": metadata
                            }
                    )
                ]
            )
        except Exception as e:
            self.logger.error(f"Error occurred while uploading record: {e}")
            return False
        return True


    def insert_many(self, collection_name: str, text: list, vector: list,
                         metadata: list , record_id: list = None, batch_size: int = 100):
        if metadata  is None: #explained in my notes
            metadata = [None] * len(text)

        if record_id is None:
            record_id = [None] * len(text)

        # Implementation for inserting many records
        for i in range(0, len(text), batch_size):
            batch_end=i+batch_size #i + batch_size is the last index we have reached in the loop, so we take the slice from i to i + batch_size
            batch_text = text[i:batch_end] 
            batch_vector = vector[i:batch_end]
            batch_metadata = metadata[i:batch_end]
        #    batch_record_id = record_id[i:batch_end]



            records = [
                models.Record(
                    vector=batch_vector[j],
                    payload={
                        "text": batch_text[j],
                        "metadata": batch_metadata[j]
                    }
                )
                for j in range(len(batch_text))
            ]
            try:
                self.client.upload_records(
                        collection_name=collection_name,
                        records=records,
                    )
            except Exception as e:
                self.logger.error(f"Error occurred while uploading records: {e}")
                return False
        return True

    def search_by_vector(self, collection_name: str, vector: list, top_k: int = 5):
        return self.client.search(
            collection_name=collection_name,
            query_vector=vector,
            limit=top_k
        )