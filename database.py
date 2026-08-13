from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# PostgreSQL connection string for the application database.
SQLACHEMY_DATABASE_URL = "postgresql://postgres:Nanayawafriyie1989*@localhost:5432/todosappdb"

# Engine manages the actual connection pool used by SQLAlchemy.
engine = create_engine(SQLACHEMY_DATABASE_URL)

# SessionLocal creates database sessions for each request.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class that SQLAlchemy models inherit from.
Base = declarative_base()