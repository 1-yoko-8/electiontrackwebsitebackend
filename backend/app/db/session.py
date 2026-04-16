from sqlmodel import create_engine, Session
from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_size=5,
    max_overflow=5,
)

def get_session():
    with Session(engine) as session:
        yield session