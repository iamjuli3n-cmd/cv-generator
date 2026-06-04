"""
create_tables.py
Crée toutes les tables dans PostgreSQL.
Lance ce fichier UNE seule fois.
"""

from database import engine, Base
import models  # noqa: F401 — importer les modèles pour que Base les connaisse

Base.metadata.create_all(
    bind=engine
)  # Cette ligne lit tous tes modèles dans models.py et génère le SQL correspondant pour créer les tables.

print("Tables créées avec succès !")
