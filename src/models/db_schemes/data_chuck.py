from pydantic import BaseModel, Field
from typing import Optional
from bson import ObjectId

#data chunk db table schema
class DataChunk(BaseModel):
    _id: Optional[ObjectId]
    chunk_text: str = Field(..., min_length=1)
    chunk_metadata:dict
    chunk_order: int = Field(..., gt=0)#gt stands for greater than, so this means that the chunk_order must be greater than 0
    chunk_project_id:ObjectId #this chunk belongs to a specific project , so we have the project_id as a foreign key to the project table


    class Config:
        arbitrary_types_allowed = True
         #pydantic by default does not support ObjectId, 
         # so we need to allow arbitrary (ignore them)types
