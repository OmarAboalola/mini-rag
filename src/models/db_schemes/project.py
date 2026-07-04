from pydantic import BaseModel , field , validator
from typing import Optional
from bson import ObjectId

class Project(BaseModel):
    _id: Optional[ObjectId]
    project_id: str = field(...,min_length=1)

    @validator('project_id')
    def validate_project_id(cls, value):
        if not value.isalphanumeric():
            raise ValueError('project_id must be alphanumeric')
        return value
    class Config:
        arbitrary_types_allowed = True
         #pydantic by default does not support ObjectId, 
         # so we need to allow arbitrary (ignore them)types
