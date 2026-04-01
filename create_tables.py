"""
create_tables.py
Crée toutes les tables dans PostgreSQL.
Lance ce fichier UNE seule fois.
"""

from database import engine, Base
import models  # noqa: F401 — importer les modèles pour que Base les connaisse

Base.metadata.create_all(bind=engine)

print("Tables créées avec succès !")
