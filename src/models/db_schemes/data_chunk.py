from pydantic import BaseModel, Field , validator
from typing import Optional
from bson import ObjectId

#data chunk db table schema
class DataChunk(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")
    chunk_text: str = Field(..., min_length=1)
    chunk_metadata: dict
    chunk_order: int = Field(..., gt=0)#gt stands for greater than, so this means that the chunk_order must be greater than 0
    chunk_project_id: ObjectId  # originally --> #chunk_project_id:bson.ObjectId.ObjectId 
#this chunk belongs to a specific project , so we have the project_id as a foreign key to the project table
    class Config:
        arbitrary_types_allowed = True
         #pydantic by default does not support ObjectId, 
         # so we need to allow arbitrary (ignore them)types

    @classmethod
    def get_indexes(cls): # the key word self refers to an instance while cls refers to the class itself, so we use cls here because we are defining a class method ( no need to create an instance of the class to use this method)
        return [
        {
            "key": [("project_id", 1)],#[...,1] means ascending order, [-1] means descending order
            "name": "project_id_index_1",
            "unique": False #this index is not unique because a project can have multiple chunks
        }
    ]
