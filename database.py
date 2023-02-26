from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# This is for sqlite
# SQLALCHEMY_DATABASE_URL = "sqlite:///./todos.db"
# -----

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:1234@localhost/TodoApplicationDatabase"

# This is for sqlite
# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
# )
# -----

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
