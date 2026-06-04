# CV Generator

> **Une plateforme complète pour générer, gérer et prévisualiser des CV professionnels**

[![Python](https://img.shields.io/badge/Python-3.9+-3776ab?style=flat-square&logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.95+-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-336791?style=flat-square&logo=postgresql)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

---

## Table des matières

- [À propos](#-à-propos)
- [Fonctionnalités](#-fonctionnalités)
- [Architecture](#-architecture)
- [Prérequis](#-prérequis)
- [Installation](#-installation)
- [Utilisation](#-utilisation)
- [API Documentation](#-api-documentation)
- [Structure du projet](#-structure-du-projet)
- [Contribuer](#-contribuer)
- [License](#-license)

---

## À propos

**CV Generator** est une application web locale qui permet aux utilisateurs de créer, gérer et prévisualiser des CV professionnels. 

L'application offre :
- Une interface web intuitive pour saisir vos informations professionnelles
- Plusieurs templates de rendu HTML professionnels
- Une base de données PostgreSQL pour la persistance des données
- Validation des données avec Pydantic

---

## Fonctionnalités

###  Frontend
- **Formulaire complet** : Interface web pour créer et remplir tous les champs du CV
- **Design réactif** : Interface adaptée desktop et mobile
- **Ajout dynamique de sections** : Ajoutez autant d'expériences, formations et projets que nécessaire
- **Validation en temps réel** : Retours immédiats sur les données saisies

### Backend API
- **CRUD complet** : Créer, lire, mettre à jour et supprimer des CVs
- **Endpoints REST** : Architecture RESTful standard
- **Documentation interactive** : Swagger UI intégré (`/docs`)
- **Gestion des relations** : Support des relations complexes (expériences → missions, projets → technologies)

### Base de données
- **Schéma relationnel** : 11 tables avec relations parent-enfant
- **Cascades** : Suppression automatique des données liées
- **Technologies partagées** : Déduplication des technologies entre projets
- **PostgreSQL** : Base de données robuste et scalable

### Templating
- **Template Premium** : Design moderne avec sidebar et palette de couleurs élégante
- **Template Classique** : HTML simple et épuré
- **Jinja2** : Rendu templated côté serveur

---

## Architecture

```
cv-generator/
├── database.py              # Configuration SQLAlchemy & PostgreSQL
├── models.py                # Tables ORM (11 modèles)
├── classCV.py               # Schémas Pydantic
├── main.py                  # Routes FastAPI (CRUD + rendu)
├── cv_test.py               # Données de test
├── create_tables.py         # Script d'initialisation BDD
├── index.html               # Formulaire web
├── templates/
│   ├── cv.html              # Template premium
│   └── cv2.html             # Template classique
├── .env                     # Variables d'environnement (à créer)
└── requirements.txt         # Dépendances Python
```

### Diagramme des tables

```
┌─────────────────────────────────────────────┐
│                     CV                      │
│  (titre_profil, resume, dates)             │
└────┬───────────┬──────────┬────────┬────────┘
     │           │          │        │
     ▼           ▼          ▼        ▼
 PersonalInfo Experience Formation Project
 (contact)   (missions)             (technologies)
                │
                ▼
             Mission
          (description)
```

---

## Prérequis

- **Python** 3.9 ou supérieur
- **PostgreSQL** 14 ou supérieur
- **pip** (gestionnaire de paquets Python)
- **Git**

### Versions testées
- Python 3.10+
- PostgreSQL 14+
- FastAPI 0.95+

---

## 🚀 Installation

### 1. Cloner le repository

```bash
git clone https://github.com/iamjuli3n-cmd/cv-generator.git
cd cv-generator
```

### 2. Créer un environnement virtuel

```bash
# Linux / macOS
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Configurer la base de données

Créez un fichier `.env` à la racine du projet :

```env
# Configuration PostgreSQL
DATABASE_URL=postgresql://username:password@localhost:5432/cv_generator

# Optionnel : Configuration FastAPI
DEBUG=True
```

### 5. Créer les tables

```bash
python create_tables.py
```

**Output attendu :**
```
Tables créées avec succès !
```

---

## 💻 Utilisation

### Lancer l'application

```bash
uvicorn main:app --reload
```

L'application sera disponible à : **http://localhost:8000**

### Accéder à l'interface

1. **Formulaire web** : http://localhost:8000/
2. **Documentation API** (Swagger) : http://localhost:8000/docs
3. **Documentation alternative** (ReDoc) : http://localhost:8000/redoc

### Créer un CV

1. Accédez à http://localhost:8000/
2. Remplissez le formulaire avec vos informations
3. Cliquez sur "Créer le CV"
4. Les données sont stockées en base de données

### Prévisualiser un CV

Après création, un CV obtient un `id_cv`. Pour le prévisualiser en HTML :

```
http://localhost:8000/cv/{id_cv}/html
```

---

## 🔌 API Documentation

### Endpoints principaux

#### 📄 Créer un CV
```http
POST /cv
Content-Type: application/json

{
  "titre_profil": "Développeur Web Full-Stack",
  "resume": "Développeur expérimenté...",
  "personnal_information": { ... },
  "experiences": [ ... ],
  "formations": [ ... ],
  "projects": [ ... ],
  "languages": [ ... ],
  "activities": [ ... ]
}
```

**Response** (201 Created) :
```json
{
  "id_cv": 1,
  "titre_profil": "Développeur Web Full-Stack",
  ...
}
```

---

#### 📋 Récupérer tous les CVs
```http
GET /cv
```

**Response** (200 OK) :
```json
[
  { "id_cv": 1, ... },
  { "id_cv": 2, ... }
]
```

---

#### 🔍 Récupérer un CV spécifique
```http
GET /cv/{id_cv}
```

**Response** (200 OK) :
```json
{
  "id_cv": 1,
  "titre_profil": "Développeur Web Full-Stack",
  "personnal_information": { ... },
  ...
}
```

---

#### Mettre à jour un CV
```http
PUT /cv/{id_cv}
Content-Type: application/json

{
  "titre_profil": "Développeur Senior",
  ...
}
```

**Response** (200 OK) : Le CV mis à jour

---

#### Supprimer un CV
```http
DELETE /cv/{id_cv}
```

**Response** (200 OK) :
```json
{
  "message": "CV 1 supprimé avec succès"
}
```

---

#### Prévisualiser en HTML
```http
GET /cv/{id_cv}/html
```

**Response** (200 OK) : Rendu HTML du CV

---

#### Récupérer le CV de test (JSON)
```http
GET /cv/test/json
```

Utile pour comprendre la structure des données attendue.

---

## Structure du projet

### `database.py`
Configuration de la connexion PostgreSQL et session SQLAlchemy.

```python
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
```

### `models.py`
11 modèles SQLAlchemy représentant les tables :
- `CV` (parent)
- `PersonalInformation`
- `Experience` + `Mission`
- `Formation`
- `Project` + `Technology` + `ProjectTechnology`
- `Language`
- `Activity` + `ActivityMission`

### `classCV.py`
Schémas Pydantic pour validation et sérialisation JSON.

### `main.py`
Routes FastAPI :
- `GET /` - Page d'accueil avec formulaire
- `POST /cv` - Créer un CV
- `GET /cv` - Lister tous les CVs
- `GET /cv/{id}` - Récupérer un CV
- `PUT /cv/{id}` - Modifier un CV
- `DELETE /cv/{id}` - Supprimer un CV
- `GET /cv/{id}/html` - Prévisualiser en HTML

### `templates/`
- `cv.html` - Template premium avec design moderne
- `cv2.html` - Template classique

---

## Tests

### Tester avec les données de test

```bash
# Accéder au CV de test en JSON
curl http://localhost:8000/cv/test/json

# Prévisualiser le template avec les données de test
http://localhost:8000/
```

---

##  Dépannage

### Erreur : "Impossible de se connecter à PostgreSQL"

Vérifiez :
- PostgreSQL est lancé
- La `DATABASE_URL` dans `.env` est correcte
- Le format : `postgresql://user:password@host:port/database`

### Erreur : "Tables not found"

Exécutez :
```bash
python create_tables.py
```

### Erreur : "Module 'classCV' introuvable"

Assurez-vous que vous êtes dans le bon répertoire et que l'environnement virtuel est activé.

---

## Dépendances

### Principales
- **fastapi** - Framework web async
- **uvicorn** - Serveur ASGI
- **sqlalchemy** - ORM SQL
- **psycopg2-binary** - Adapter PostgreSQL
- **pydantic** - Validation de données
- **jinja2** - Templating HTML
- **python-dotenv** - Gestion des variables d'environnement

### Installation complète
```bash
pip install -r requirements.txt
```

---

## Contribuer

Les contributions sont bienvenues ! Pour contribuer :

1. Fork le repository
2. Créez une branche feature (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Poussez vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

### Standards de code
- Respectez **PEP 8**
- Commentaires en français ou anglais 
- Types hints obligatoires pour les fonctions
- Docstrings pour les classes et modules

---

## Roadmap

- [ ] Export PDF des CVs
- [ ] Templates supplémentaires
- [ ] Partage de CVs avec lien unique
- [ ] Import depuis LinkedIn
- [ ] Tests automatisés (pytest)

---

## License

Ce projet est sous license MIT. Voir [LICENSE](LICENSE) pour plus de détails.

---


**Dernière mise à jour** : Juin 2026
