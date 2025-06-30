from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from config.settings import DATABASE_HOST, DB_NAME, DB_PASSWORD, DB_USERNAME

DATABASE_URL = f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DATABASE_HOST}/{DB_NAME}?options=-csearch_path=public"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


print("🚀 Database connected successfully!!")
