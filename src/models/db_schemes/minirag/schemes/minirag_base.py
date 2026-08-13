#parent class for a pydantic scheme for the SQL Alchemy acts as a "BaseModel" in pydantic class
from sqlalchemy.ext.declarative import declarative_base


SQLAlchemyBase=declarative_base()