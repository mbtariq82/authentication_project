from database import Base
from sqlalchemy import Column, Integer, String

# This model maps to the users table in PostgreSQL.
class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    hashed_password = Column(String)