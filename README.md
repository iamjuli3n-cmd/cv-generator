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
- Une interface web complète avec authentification par compte utilisateur
- Un tableau de bord pour gérer l'ensemble de ses CVs
- Plusieurs templates de rendu HTML professionnels avec prévisualisation interactive
- Export PDF du CV au format choisi
- Une base de données PostgreSQL pour la persistance des données
- Validation des données avec Pydantic

---

## Fonctionnalités

### Frontend
- **Authentification** : Connexion sécurisée par JWT stocké en cookie, gestion de session côté serveur
- **Tableau de bord** : Vue d'ensemble de tous ses CVs avec options de modification, prévisualisation et suppression
- **Formulaire complet** : Interface pour créer et modifier tous les champs d'un CV (expériences, formations, projets, langues, activités)
- **Ajout dynamique de sections** : Ajoutez autant d'expériences, formations et projets que nécessaire
- **Prévisualisation interactive** : Comparez les 4 templates côte à côte et exportez en PDF celui qui vous convient
- **Design réactif** : Interface adaptée desktop et mobile

### Backend API
- **Authentification JWT** : Tokens signés HS256, expiration 24h, posés en cookie HttpOnly=false
- **CRUD complet** : Créer, lire, mettre à jour et supprimer des CVs
- **Endpoints REST** : Architecture RESTful standard
- **Documentation interactive** : Swagger UI intégré (`/docs`)
- **Gestion des relations** : Support des relations complexes (expériences → missions, projets → technologies)
- **Export PDF** : Génération PDF via WeasyPrint avec choix du template

### Base de données
- **Schéma relationnel** : 11 tables avec relations parent-enfant
- **Cascades** : Suppression automatique des données liées
- **Technologies partagées** : Déduplication des technologies entre projets
- **PostgreSQL** : Base de données robuste et scalable

### Templating
- **cv.html** — Sidebar Classic : design deux colonnes avec sidebar sombre et accents dorés
- **cv2.html** — Minimal : rendu HTML simple et épuré
- **cv3.html** — Classique Parisien : colonne unique, typographie Cormorant Garamond, accents dorés
- **cv4.html** — Modern Tech : header sombre, deux colonnes, typographie Syne + Figtree

---

## Architecture

```
cv-generator/
├── database.py              # Configuration SQLAlchemy & PostgreSQL
├── models.py                # Tables ORM (11 modèles)
├── classCV.py               # Schémas Pydantic
├── main.py                  # Routes FastAPI (CRUD + rendu + auth)
├── auth.py                  # JWT, hachage, dépendances d'authentification
├── cv_test.py               # Données de test
├── create_tables.py         # Script d'initialisation BDD
├── templates/
│   ├── index.html           # Page de connexion
│   ├── dashboard.html       # Tableau de bord utilisateur
│   ├── create.html          # Formulaire création / édition de CV
│   ├── preview.html         # Prévisualisation multi-templates + export PDF
│   ├── cv.html              # Template Sidebar Classic
│   ├── cv2.html             # Template Minimal
│   ├── cv3.html             # Template Classique Parisien
│   └── cv4.html             # Template Modern Tech
├── .env                     # Variables d'environnement (à créer)
└── requirements.txt         # Dépendances Python
```

### Diagramme des tables

```
┌─────────────────────────────────────────────┐
│                    User                     │
│  (email, hashed_password, date_creation)   │
└────────────────────┬────────────────────────┘
                     │
                     ▼
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

### Flux d'authentification

```
Navigateur                     FastAPI
    │                             │
    │── GET /  ──────────────────▶│ vérifie cookie cv_token
    │◀─ login page ───────────────│ absent → sert index.html
    │                             │
    │── POST /auth/login ────────▶│ vérifie identifiants
    │◀─ {access_token} + cookie ──│ pose cookie cv_token (24h)
    │                             │
    │── GET /dashboard ──────────▶│ lit cookie cv_token
    │◀─ dashboard.html ───────────│ valide → sert la page
    │                             │
    │── GET /logout ─────────────▶│ supprime le cookie
    │◀─ redirect / ───────────────│
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

## Installation

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
DATABASE_URL=postgresql://username:password@localhost:5432/cv_generator
SECRET_KEY=changez-cette-valeur-en-production
```

### 5. Créer les tables

```bash
python create_tables.py
```

---

## Utilisation

### Lancer l'application

```bash
uvicorn main:app --reload
```

L'application sera disponible à : **http://localhost:8000**

### Flux utilisateur

1. **Connexion** : http://localhost:8000/ — entrez vos identifiants
2. **Tableau de bord** : http://localhost:8000/dashboard — liste de vos CVs
3. **Créer un CV** : cliquez sur "Nouveau CV" → remplissez le formulaire → validez
4. **Modifier un CV** : cliquez sur "Modifier" sur la ligne du CV concerné
5. **Prévisualiser et exporter** : cliquez sur "Prévisualiser" → choisissez un template parmi les 4 disponibles → cliquez sur "Exporter en PDF"
6. **Déconnexion** : bouton "Déconnexion" dans l'en-tête du tableau de bord

### Documentation API (Swagger)

```
http://localhost:8000/docs
```

---

## API Documentation

### Authentification

#### Connexion
```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=email@exemple.com&password=motdepasse
```
**Response** : `{"access_token": "...", "token_type": "bearer"}` + cookie `cv_token`

---

#### Déconnexion
```http
GET /logout
```
Supprime le cookie et redirige vers `/`.

---

#### Profil utilisateur connecté
```http
GET /users/me
Authorization: Bearer <token>
```

---

### CVs

> Toutes les routes CV nécessitent le header `Authorization: Bearer <token>`.

#### Créer un CV
```http
POST /cv
Content-Type: application/json
Authorization: Bearer <token>

{
  "titre_profil": "Développeur Web Full-Stack",
  "resume": "Développeur expérimenté...",
  "date_creation": "2025-01-01",
  "date_modification": "2025-01-01",
  "personnal_information": { ... },
  "experiences": [ ... ],
  "formations": [ ... ],
  "projects": [ ... ],
  "languages": [ ... ],
  "activities": [ ... ]
}
```

---

#### Récupérer tous ses CVs
```http
GET /cv
Authorization: Bearer <token>
```

---

#### Récupérer un CV
```http
GET /cv/{id_cv}
Authorization: Bearer <token>
```

---

#### Modifier un CV
```http
PUT /cv/{id_cv}
Authorization: Bearer <token>
```

---

#### Supprimer un CV
```http
DELETE /cv/{id_cv}
Authorization: Bearer <token>
```

---

#### Prévisualiser en HTML
```http
GET /cv/{id_cv}/html?template=cv3.html
Authorization: Bearer <token>
```

Paramètre `template` optionnel (défaut : `cv.html`). Valeurs acceptées : `cv.html`, `cv2.html`, `cv3.html`, `cv4.html`.

---

#### Exporter en PDF
```http
GET /cv/{id_cv}/export?template=cv3.html
Authorization: Bearer <token>
```

Même paramètre `template` que la route HTML.

---

## Structure du projet

### `auth.py`
Gestion de l'authentification :
- `hash_password` / `verify_password` — bcrypt
- `create_access_token` — génération JWT HS256
- `get_current_user` — dépendance pour les routes API (lit le Bearer token)
- `get_current_user_from_cookie` — dépendance pour les routes page (lit le cookie)

### `database.py`
Configuration de la connexion PostgreSQL et session SQLAlchemy.

### `models.py`
11 modèles SQLAlchemy représentant les tables :
- `User`
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

| Méthode | Route | Description |
|---------|-------|-------------|
| `GET` | `/` | Page de connexion (redirige vers `/dashboard` si déjà connecté) |
| `GET` | `/logout` | Déconnexion — supprime le cookie et redirige |
| `GET` | `/dashboard` | Tableau de bord |
| `GET` | `/create` | Formulaire création / édition (`?id=X` pour édition) |
| `POST` | `/auth/login` | Connexion — retourne le token et pose le cookie |
| `POST` | `/auth/register` | Inscription |
| `GET` | `/users/me` | Profil de l'utilisateur connecté |
| `GET` | `/cv` | Liste des CVs de l'utilisateur |
| `POST` | `/cv` | Créer un CV |
| `GET` | `/cv/{id}` | Récupérer un CV |
| `PUT` | `/cv/{id}` | Modifier un CV |
| `DELETE` | `/cv/{id}` | Supprimer un CV |
| `GET` | `/cv/{id}/html` | Rendu HTML (`?template=cv3.html`) |
| `GET` | `/cv/{id}/export` | Export PDF (`?template=cv3.html`) |
| `GET` | `/cv/{id}/preview` | Page de prévisualisation multi-templates |

---

## Dépannage

### Erreur : "Impossible de se connecter à PostgreSQL"
- Vérifiez que PostgreSQL est lancé
- Vérifiez la `DATABASE_URL` dans `.env`
- Format attendu : `postgresql://user:password@host:port/database`

### Erreur : "Tables not found"
```bash
python create_tables.py
```

### Erreur : "Module 'classCV' introuvable"
Assurez-vous d'être dans le bon répertoire et que l'environnement virtuel est activé.

### Cookie non posé après connexion
Vérifiez que la route `POST /auth/login` dans `main.py` a bien le paramètre `response: Response` et appelle `response.set_cookie(...)`.

---

## Dépendances

### Principales
- **fastapi** — Framework web async
- **uvicorn** — Serveur ASGI
- **sqlalchemy** — ORM SQL
- **psycopg2-binary** — Adapter PostgreSQL
- **pydantic** — Validation de données
- **jinja2** — Templating HTML
- **python-jose** — Génération et vérification JWT
- **passlib[bcrypt]** — Hachage des mots de passe
- **weasyprint** — Génération PDF
- **python-dotenv** — Gestion des variables d'environnement

---

## Roadmap

- [x] Export PDF des CVs
- [x] Templates supplémentaires (4 templates disponibles)
- [x] Authentification utilisateur
- [x] Tableau de bord de gestion
- [x] Prévisualisation interactive multi-templates
- [ ] Partage de CVs avec lien unique
- [ ] Import depuis LinkedIn
- [ ] Tests automatisés (pytest)

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

## License

Ce projet est sous license MIT. Voir [LICENSE](LICENSE) pour plus de détails.

---

**Dernière mise à jour** : Juin 2026
