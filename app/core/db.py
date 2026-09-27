from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import get_settings

settings = get_settings()
engine: Engine = create_engine(f"postgresql+psycopg://{settings.db_user}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}")
SessionLocal = sessionmaker(bind=engine)

def get_session() -> Session:
    return SessionLocal()