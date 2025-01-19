from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Define your database connection string
SQLALCHEMY_DATABASE_URL = (
    "mssql+pyodbc:///?odbc_connect="
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=NUNIA\SQLEXPRESS;"
    "Database=NuniaAI;"
    "Trusted_Connection=yes;"
)

# Create SQLAlchemy engine
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=False)

# Create a sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for your ORM models
Base = declarative_base()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
