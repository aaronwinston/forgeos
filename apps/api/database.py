from sqlmodel import create_engine, SQLModel, Session
from config import settings

engine = create_engine(settings.DATABASE_URL, echo=False)

def get_session():
    with Session(engine) as session:
        yield session

def create_db_and_tables():
    # Import all models to ensure they're registered with SQLModel.metadata
    # before calling create_all()
    import models  # noqa: F401
    SQLModel.metadata.create_all(engine)
