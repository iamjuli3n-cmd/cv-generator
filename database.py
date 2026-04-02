from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL
)  # Le engine c'est le "tuyau" entre ton code Python et PostgreSQL.

# Une session c'est une "conversation" avec la BDD — tu ouvres une session, tu fais tes requêtes, tu fermes. C'est comme ouvrir et fermer une connexion à chaque fois que tu en as besoin.
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


# Base est la classe parente dont vont hériter tous tes modèles dans models.py. C'est elle qui fait le lien entre tes classes Python et les tables PostgreSQL.
class Base(DeclarativeBase):
    pass


# C'est une fonction que FastAPI va appeler automatiquement à chaque requête pour ouvrir une session, et la fermer proprement une fois la requête terminée.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
