from pydantic import BaseModel, Field, validator
from typing import Optional
from bson.objectid import ObjectId

class Project(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")
    project_id: str = Field(..., min_length=1)

    @validator('project_id')
    def validate_project_id(cls, value):
        if not value.isalnum():
            raise ValueError('project_id must be alphanumeric')
        
        return value

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def get_indexes(cls): # the key word self refers to an instance while cls refers to the class itself, so we use cls here because we are defining a class method ( no need to create an instance of the class to use this method)
        return [
        {
            "key": [("project_id", 1)],#[...,1] means ascending order, [-1] means descending order
            "name": "project_id_index_1",
            "unique": True
        }
    ]