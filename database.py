from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv
import os

load_dotenv()

_engine = None
_SessionLocal = None


# Le engine c'est le "tuyau" entre ton code Python et PostgreSQL.
def get_engine():
    global _engine
    if _engine is None:
        _engine = create_engine(os.getenv("DATABASE_URL"))
    return _engine


# Une session c'est une "conversation" avec la BDD — tu ouvres une session, tu fais tes requêtes, tu fermes. C'est comme ouvrir et fermer une connexion à chaque fois que tu en as besoin.
def get_sessionmaker():
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(bind=get_engine(), autocommit=False, autoflush=False)
    return _SessionLocal


# Base est la classe parente dont vont hériter tous tes modèles dans models.py. C'est elle qui fait le lien entre tes classes Python et les tables PostgreSQL.
class Base(DeclarativeBase):
    pass


# C'est une fonction que FastAPI va appeler automatiquement à chaque requête pour ouvrir une session, et la fermer proprement une fois la requête terminée.
def get_db():
    db = get_sessionmaker()()
    try:
        yield db
    finally:
        db.close()
