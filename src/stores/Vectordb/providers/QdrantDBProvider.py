from qdrant_client import QdrantClient , models
from ..VectorDBInterface import VectorDBInterface
from ..VectorDBEnums import VectorDBTypes , DistanceMethodEnums
import logging
from typing import List
from models.db_schemes import RetrievedDocument

class QdrantDBProvider(VectorDBInterface):
    def __init__(self, db_path:str , distance_method: str):
        self.client = None
        self.db_path = db_path
        self.distance_method = distance_method
        method = (distance_method or "").strip().lower()
        '''
        if self.distance_method == DistanceMethodEnums.COSINE.value:
            self.distance_method = models.Distance.COSINE
        elif self.distance_method == DistanceMethodEnums.EUCLID.value:
            self.distance_method = models.Distance.EUCLID
        elif self.distance_method == DistanceMethodEnums.DOT.value:
            self.distance_method = models.Distance.DOT
        '''


        #hard coded as I had some errors
        if method == "cosine":
            self.distance_method = models.Distance.COSINE
        elif method in ("euclidean", "euclid"):
            self.distance_method = models.Distance.EUCLID
        elif method in ("dot", "dotproduct"):
            self.distance_method = models.Distance.DOT
        else:
            raise ValueError(f"Unsupported distance method: {distance_method}")
        #to debug
        print(self.distance_method)
        print(type(self.distance_method))

        self.logger = logging.getLogger(__name__)

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
            print("distance_method =", self.distance_method)
            print("type =", type(self.distance_method))
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


    def insert_many(self,collection_name: str,texts: list,
    vectors: list,
    metadata: list,
    record_ids: list = None,
    batch_size: int = 100,
):
        if metadata  is None: #explained in my notes
            metadata = [None] * len(texts)

        if record_ids is None:
            record_ids = [None] * len(texts)

        # Implementation for inserting many records
        for i in range(0, len(texts), batch_size):
            #i + batch_size is the last index we have reached in the loop, so we take the slice from i to i + batch_size
            batch_end=i+batch_size 
            batch_text = texts[i:batch_end] 
            batch_vector = vectors[i:batch_end]
            batch_metadata = metadata[i:batch_end]
            batch_record_ids = record_ids[i:batch_end]



            records = [
                models.Record(
                    id=batch_record_ids[j],
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
        results = self.client.search(
            collection_name=collection_name,
            query_vector=vector,
            limit=top_k
        )
        if not results or len(results)==0:
            return None
        else :
            return[
                RetrievedDocument(**{"score":result.score, #pydantic to retun those only
                                    "text":result.payload["text"]})
                for result in results
            ]