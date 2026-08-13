#every thing about the files (assets) we upload 

from .minirag_base import SQLAlchemyBase
from sqlalchemy import Column ,Integer , String ,DateTime ,func , ForeignKey
from sqlalchemy.dialects.postgresql import UUID ,JSONB
from sqlalchemy import Index
from sqlalchemy.orm import relationship
import uuid

class Asset (SQLAlchemyBase):
    __tablename__="assets"

    asset_id=Column(Integer,primary_key=True,autoincrement=True)
    asset_uuid=Column(UUID(as_uuid=True) ,default=uuid.uuid4 , unique=True , nullable=False) #generate a unique value and cannot be null

    asset_type=Column(String,nullable=False)
    asset_name=Column(String,nullable=False)
    asset_size=Column(Integer,nullable=False)
    asset_config=Column(JSONB,nullable=True)

    #this file (asset) belongs to what project (table)--> (fk)
    asset_project_id=Column(Integer,ForeignKey("projects.project_id"),nullable=False)

    #we have the model (table) called project , we will take from it data to put into assets
    project = relationship("Project",back_populates="assets")
    chunks = relationship("DataChunk", back_populates="asset")

    
    created_at=Column(DateTime(timezone=True) , server_default=func.now() , nullable=False) #auto add it if not found and cannot be null
    updated_at=Column(DateTime(timezone=True) , onupdate=func.now() , nullable=True)  #can be null if col is not updated



    #foreign key indexing 
    __table_args__=(
        Index('ix_asset_project_id',asset_project_id),
        Index('ix_asset_type',asset_type),

    )

