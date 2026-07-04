from pydantic import BaseModel , field , validator
from typing import Optional
from bson import ObjectId
class data_chuk(base_model):
    _id: Optional[ObjectId]
    chunk_text: str = field(...,min_length=1)
    chunk_metadata:dict
    chunk_order: int = field(...,gt=0)#gt stands for greater than, so this means that the chunk_order must be greater than 0
    chunk_project_id:ObjectId


    class Config:
        arbitrary_types_allowed = True
         #pydantic by default does not support ObjectId, 
         # so we need to allow arbitrary (ignore them)types
