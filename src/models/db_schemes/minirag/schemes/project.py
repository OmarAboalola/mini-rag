#first table in the db (project table)

from .minirag_base import SQLAlchemyBase
from sqlalchemy import Column ,Integer , DateTime ,func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
class Project (SQLAlchemyBase):
    
    __tablename__="projects"

    project_id=Column(Integer,primary_key=True,autoincrement=True)
    project_uuid=Column(UUID(as_uuid=True) ,default=uuid.uuid4 , unique=True , nullable=False) #generate a unique value and cannot be null

    created_at=Column(DateTime(timezone=True) , server_default=func.now() , nullable=False) #auto add it if not found and cannot be null
    updated_at=Column(DateTime(timezone=True) , onupdate=func.now() , nullable=True)  #can be null if col is not updated

    assets = relationship("Asset", back_populates="project")
    chunks = relationship("DataChunk", back_populates="project")

