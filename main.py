from datetime import date, datetime
import json

from fastapi import FastAPI, HTTPException, Depends, Request, status, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime

from database import get_db, engine, Base
from auth import hash_password, verify_password, create_access_token, get_current_user



import models
import classCV
from cv_test import cv_test

app = FastAPI(title="CV Generator")
templates = Jinja2Templates(directory="templates")

class LoginUser(Base):
    __tablename__ = "login_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)


class SavedCV(Base):
    __tablename__ = "saved_cvs"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String)
    titre_profil = Column(String)
    resume = Column(Text)

    full_name = Column(String)
    email = Column(String)
    phone = Column(String)

    data_json = Column(Text)

    user_id = Column(Integer, ForeignKey("login_users.id"))

    date_creation = Column(DateTime, default=datetime.utcnow)
    date_modification = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(bind=engine)

Base.metadata.create_all(
    bind=engine
)

@app.get("/")
def root():
    return RedirectResponse("/connection")


@app.get("/connection")
def connection_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="connection.html",
        context={
            "request": request
        }
    )

@app.post("/login")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):

    user = db.query(LoginUser).filter(
        LoginUser.username == username
    ).first()

    if user is None:

        user = LoginUser(
            username=username,
            password=password
        )

        db.add(user)
        db.commit()
        db.refresh(user)

    elif user.password != password:

        return templates.TemplateResponse(
            request=request,
            name="connection.html",
            context={
                "error": "Wrong password"
            }
        )

    return RedirectResponse(
        f"/accueil/{user.id}",
        status_code=303
    )

@app.get("/accueil")
@app.get("/accueil/")
def accueil_without_id():
    return RedirectResponse(
        url="/",
        status_code=303
    )


@app.get("/accueil/{user_id}")
def accueil(
    request: Request,
    user_id: int,
    db: Session = Depends(get_db)
):

    user = db.query(LoginUser).filter(
        LoginUser.id == user_id
    ).first()

    cvs = db.query(SavedCV).filter(
        SavedCV.user_id == user_id
    ).all()

    return templates.TemplateResponse(
        request=request,
        name="accueil.html",
        context={
            "user": user,
            "cvs": cvs
        }
    )


@app.get("/index/{user_id}")
def index_page(
    request: Request,
    user_id: int
):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "user_id": user_id
        }
    )

@app.post("/save_cv/{user_id}")
async def save_cv(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db)
):

    data = await request.json()

    cv_count = db.query(SavedCV).filter(
        SavedCV.user_id == user_id
    ).count()

    personal = data.get(
        "personnal_information",
        {}
    )

    cv = SavedCV(

        title=f"CV{cv_count+1}",

        titre_profil=data.get(
            "titre_profil",
            ""
        ),

        resume=data.get(
            "resume",
            ""
        ),

        full_name=
        personal.get(
            "first_name",
            ""
        ) + " " +
        personal.get(
            "name",
            ""
        ),

        email=personal.get(
            "email",
            ""
        ),

        phone=personal.get(
            "phone_number",
            ""
        ),

        data_json=json.dumps(
            data,
            ensure_ascii=False
        ),

        user_id=user_id
    )

    db.add(cv)

    db.commit()

    return JSONResponse(
        {
            "success": True
        }
    )


@app.get("/logout")
def logout():
    return RedirectResponse(
        url="/",
        status_code=303
    )


@app.get("/accueil/{user_id}/cv/{cv_id}", response_class=HTMLResponse)
def view_saved_cv(
    request: Request,
    user_id: int,
    cv_id: int,
    db: Session = Depends(get_db)
):
    """
    Affiche le CV sauvegardé (SavedCV) en HTML en lisant son data_json.
    Passe le dict brut au template pour éviter les erreurs de validation Pydantic
    sur des champs vides ou malformés (email vide, dates vides, etc.).
    """
    cv_record = db.query(SavedCV).filter(
        SavedCV.id == cv_id,
        SavedCV.user_id == user_id
    ).first()

    if not cv_record:
        raise HTTPException(status_code=404, detail="CV introuvable")

    try:
        cv_data = json.loads(cv_record.data_json)
    except Exception:
        raise HTTPException(status_code=500, detail="Données du CV invalides")

    return templates.TemplateResponse(
        request=request,
        name="cv.html",
        context={"cv": cv_data, "back_url": f"/accueil/{user_id}"}
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=False
)


# -------------------------
# SAVE CV
# -------------------------

# @app.post("/save_cv/{user_id}")
# def save_cv(

#     user_id: int,

#     full_name: str = Form(...),

#     email: str = Form(...),

#     phone: str = Form(...),

#     education: str = Form(...),

#     experience: str = Form(...),

#     skills: str = Form(...),

#     db: Session = Depends(get_db)

# ):

#     number_cv = db.query(CV).filter(
#         CV.user_id == user_id
#     ).count()

#     cv = CV(

#         title=f"CV{number_cv+1}",

#         full_name=full_name,

#         email=email,

#         phone=phone,

#         education=education,

#         experience=experience,

#         skills=skills,

#         user_id=user_id

#     )
# #
#     db.add(cv)

#     db.commit()

#     return RedirectResponse(

#         f"/accueil/{user_id}",

#         status_code=303

#     )


# ══════════════════════════════════════════
#  AUTH — register / login / me
# ══════════════════════════════════════════


@app.post("/auth/register", response_model=classCV.UserOut, status_code=201)
def register(user_data: classCV.UserCreate, db: Session = Depends(get_db)):
    """
    Crée un compte utilisateur.
    - Vérifie que l'email n'est pas déjà pris
    - Hache le mot de passe avec bcrypt (jamais stocké en clair)
    - Retourne l'utilisateur créé sans le mot de passe
    """
    if db.query(models.User).filter_by(email=user_data.email).first():
        raise HTTPException(status_code=400, detail="Email déjà utilisé")
    user = models.User(
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        date_creation=date.today(),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.post("/auth/login", response_model=classCV.Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Connecte un utilisateur et retourne un token JWT.

    OAuth2PasswordRequestForm attend un body en form-data avec :
      - username  (= l'email ici, c'est la convention OAuth2)
      - password

    Le token retourné doit ensuite être envoyé dans le header de chaque requête :
      Authorization: Bearer <token>
    """
    user = db.query(models.User).filter_by(email=form.username).first()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
        )
    token = create_access_token({"sub": str(user.id_user)})
    return {"access_token": token, "token_type": "bearer"}


@app.get("/users/me", response_model=classCV.UserOut)
def get_me(current_user: models.User = Depends(get_current_user)):
    """
    Retourne le profil de l'utilisateur actuellement connecté.
    Si le token est absent ou invalide → 401 automatique (géré par get_current_user).
    """
    return current_user


# ══════════════════════════════════════════
#  ANCIENS GET — rendu Jinja2 depuis cv_test
#  Ces routes restent publiques (pas d'auth) car elles servent
#  uniquement à tester le rendu HTML avec des données fictives.
# ══════════════════════════════════════════


#@app.get("/", response_class=HTMLResponse)
#def accueil(request: Request):
#    """
#    Affiche le CV de test (cv_test.py) avec le template cv.html.
#    Ne touche pas à la BDD — sert uniquement pour tester le rendu HTML.
#    """
#    return templates.TemplateResponse(
#        request=request, name="cv.html", context={"cv": cv_test}
#    )


@app.get("/cv2", response_class=HTMLResponse)
def accueil_v2(request: Request):
    """
    Même chose que / mais avec le template basique cv2.html.
    """
    return templates.TemplateResponse(
        request=request, name="cv2.html", context={"cv": cv_test}
    )


@app.get("/cv/test/json", response_model=classCV.CV)
def get_cv_test_json():
    """
    Retourne le CV de test (cv_test.py) en JSON brut.
    Utile pour voir la structure attendue lors d'un POST.
    """
    return cv_test


# ══════════════════════════════════════════
#  CREATE — POST /cv
# ══════════════════════════════════════════


@app.post("/cv", response_model=classCV.CV)
def create_cv(
    cv_data: classCV.CV,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Crée un CV complet en BDD, lié à l'utilisateur connecté.

    - Reçoit un objet CV complet au format JSON dans le body de la requête
    - Insère le CV principal (avec id_user), puis toutes les sections liées
    - db.flush() après chaque insertion pour récupérer l'id généré
      sans encore valider la transaction
    - db.commit() à la fin valide tout en une seule transaction :
      si une erreur survient, rien n'est inséré
    - Retourne le CV créé avec ses ids générés par PostgreSQL
    """

    # CV principal
    db_cv = models.CV(
        titre_profil=cv_data.titre_profil,
        resume=cv_data.resume,
        date_creation=cv_data.date_creation,
        date_modification=cv_data.date_modification,
        id_user=current_user.id_user,  # Lie le CV à l'utilisateur connecté
    )
    db.add(db_cv)
    db.flush()

    # Informations personnelles
    info = cv_data.personnal_information
    db.add(
        models.PersonnalInformation(
            id_cv=db_cv.id_cv,
            name=info.name,
            first_name=info.first_name,
            address=info.address,
            phone_number=info.phone_number,
            email=info.email,
            linkedin=str(info.linkedin) if info.linkedin else None,
            github=str(info.github) if info.github else None,
            portfoliio=str(info.portfoliio) if info.portfoliio else None,
        )
    )

    # Expériences + missions
    for exp in cv_data.experiences:
        db_exp = models.Experience(
            id_cv=db_cv.id_cv,
            job=exp.job,
            company=exp.company,
            city=exp.city,
            start_date=exp.start_date,
            end_date=exp.end_date,
        )
        db.add(db_exp)
        db.flush()
        for mission in exp.missions:
            db.add(
                models.Mission(
                    id_experience=db_exp.id_experience, description=mission.description
                )
            )

    # Formations
    for f in cv_data.formations:
        db.add(
            models.Formation(
                id_cv=db_cv.id_cv,
                diploma=f.diploma,
                city=f.city,
                date=f.date,
                school=f.school,
            )
        )

    # Projets + technologies
    for project in cv_data.projects:
        db_project = models.Project(
            id_cv=db_cv.id_cv,
            name=project.name,
            description=project.description,
            link=str(project.link) if project.link else None,
        )
        db.add(db_project)
        db.flush()
        for tech in project.technologies:
            db_tech = db.query(models.Technology).filter_by(name=tech.name).first()
            if not db_tech:
                db_tech = models.Technology(name=tech.name)
                db.add(db_tech)
                db.flush()
            db.add(
                models.ProjectTechnology(
                    id_project=db_project.id_project,
                    id_technology=db_tech.id_technology,
                )
            )

    # Langues
    for lang in cv_data.languages:
        db.add(
            models.Language(
                id_cv=db_cv.id_cv,
                language=lang.language,
                level=lang.level,
            )
        )

    # Activités + missions
    for activity in cv_data.activities:
        db_activity = models.Activity(
            id_cv=db_cv.id_cv,
            organisation=activity.organisation,
            role=activity.role,
        )
        db.add(db_activity)
        db.flush()
        for mission in activity.activity_missions:
            db.add(
                models.ActivityMission(
                    id_activity=db_activity.id_activity, description=mission.description
                )
            )

    db.commit()
    db.refresh(db_cv)
    return _db_cv_to_schema(db_cv)


# ══════════════════════════════════════════
#  READ ALL — GET /cv
# ══════════════════════════════════════════


@app.get("/cv", response_model=list[classCV.CV])
def get_all_cv(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Retourne uniquement les CV de l'utilisateur connecté.
    - Filtre sur id_user → chaque utilisateur ne voit que ses propres CVs
    - Retourne une liste vide [] si aucun CV n'existe
    """
    cvs = db.query(models.CV).filter(models.CV.id_user == current_user.id_user).all()
    return [_db_cv_to_schema(cv) for cv in cvs]


# ══════════════════════════════════════════
#  READ ONE — GET /cv/{id_cv}
# ══════════════════════════════════════════


@app.get("/cv/{id_cv}", response_model=classCV.CV)
def get_cv(
    id_cv: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Retourne un CV précis par son id avec Eager Loading.
    Au lieu de faire ~15 requêtes (N+1), on en fait ~8 (fixes).
    BUG CORRIGÉ : ajout du filtre id_user — sans lui, n'importe quel
    utilisateur connecté pouvait lire le CV de quelqu'un d'autre.
    """
    db_cv = (
        db.query(models.CV)
        .options(
            # 1. Infos perso (1-to-1) -> JOIN classique, pas de duplication de lignes
            joinedload(models.CV.personnal_information),
            # 2. Expériences + leurs missions (1-to-Many imbriqués) -> Requêtes IN séparées
            selectinload(models.CV.experiences).selectinload(
                models.Experience.missions
            ),
            # 3. Formations -> Requête IN séparée
            selectinload(models.CV.formations),
            # 4. Projets + leurs technologies (Many-to-Many imbriqué) -> Requêtes IN séparées
            selectinload(models.CV.projects).selectinload(models.Project.technologies),
            # 5. Langues -> Requête IN séparée
            selectinload(models.CV.languages),
            # 6. Activités + leurs missions (1-to-Many imbriqués) -> Requêtes IN séparées
            selectinload(models.CV.activities).selectinload(
                models.Activity.activity_missions
            ),
        )
        .filter(
            models.CV.id_cv == id_cv,
            models.CV.id_user == current_user.id_user,  # BUG CORRIGÉ
        )
        .first()
    )

    # Si le CV n'existe pas OU appartient à quelqu'un d'autre → 404
    # (on ne dit pas "interdit" pour ne pas révéler l'existence du CV)
    if not db_cv:
        raise HTTPException(status_code=404, detail="CV introuvable")

    return _db_cv_to_schema(db_cv)


# ══════════════════════════════════════════
#  UPDATE — PUT /cv/{id_cv}
# ══════════════════════════════════════════


@app.put("/cv/{id_cv}", response_model=classCV.CV)
def update_cv(
    id_cv: int,
    cv_data: classCV.CV,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),  # BUG CORRIGÉ : manquait
):
    """
    Remplace un CV existant par les nouvelles données envoyées.
    BUG CORRIGÉ : current_user manquait entièrement — n'importe qui
    pouvait modifier le CV de quelqu'un d'autre.

    - Vérifie que le CV existe ET appartient à l'utilisateur connecté, sinon 404
    - Met à jour les champs du CV principal
    - Supprime toutes les sections liées existantes (expériences, formations...)
    - Les recrée avec les nouvelles données
    - C'est une stratégie "supprimer / recréer" — plus simple qu'une
      mise à jour champ par champ de chaque sous-élément
    """
    db_cv = db.query(models.CV).filter(
        models.CV.id_cv == id_cv,
        models.CV.id_user == current_user.id_user,  # BUG CORRIGÉ
    ).first()
    if not db_cv:
        raise HTTPException(status_code=404, detail="CV introuvable")

    db_cv.titre_profil = cv_data.titre_profil
    db_cv.resume = cv_data.resume
    db_cv.date_modification = cv_data.date_modification

    # Suppression des anciennes données liées
    # On supprime les enfants avant les parents pour éviter les erreurs de contrainte

    # Missions des expériences
    for exp in db.query(models.Experience).filter_by(id_cv=id_cv).all():
        db.query(models.Mission).filter_by(id_experience=exp.id_experience).delete()

    # Liaisons projet <-> technologie + missions des activités
    for project in db.query(models.Project).filter_by(id_cv=id_cv).all():
        db.query(models.ProjectTechnology).filter_by(
            id_project=project.id_project
        ).delete()

    for activity in db.query(models.Activity).filter_by(id_cv=id_cv).all():
        db.query(models.ActivityMission).filter_by(
            id_activity=activity.id_activity
        ).delete()

    # Suppression des parents
    db.query(models.PersonnalInformation).filter_by(id_cv=id_cv).delete()
    db.query(models.Experience).filter_by(id_cv=id_cv).delete()
    db.query(models.Formation).filter_by(id_cv=id_cv).delete()
    db.query(models.Project).filter_by(id_cv=id_cv).delete()
    db.query(models.Language).filter_by(id_cv=id_cv).delete()
    db.query(models.Activity).filter_by(id_cv=id_cv).delete()
    db.flush()

    # Recréation avec les nouvelles données
    info = cv_data.personnal_information
    db.add(
        models.PersonnalInformation(
            id_cv=id_cv,
            name=info.name,
            first_name=info.first_name,
            address=info.address,
            phone_number=info.phone_number,
            email=info.email,
            linkedin=str(info.linkedin) if info.linkedin else None,
            github=str(info.github) if info.github else None,
            portfoliio=str(info.portfoliio) if info.portfoliio else None,
        )
    )

    for exp in cv_data.experiences:
        db_exp = models.Experience(
            id_cv=id_cv,
            job=exp.job,
            company=exp.company,
            city=exp.city,
            start_date=exp.start_date,
            end_date=exp.end_date,
        )
        db.add(db_exp)
        db.flush()
        for m in exp.missions:
            db.add(
                models.Mission(
                    id_experience=db_exp.id_experience, description=m.description
                )
            )

    for f in cv_data.formations:
        db.add(
            models.Formation(
                id_cv=id_cv,
                diploma=f.diploma,
                city=f.city,
                date=f.date,
                school=f.school,
            )
        )

    for project in cv_data.projects:
        db_project = models.Project(
            id_cv=id_cv,
            name=project.name,
            description=project.description,
            link=str(project.link) if project.link else None,
        )
        db.add(db_project)
        db.flush()
        for tech in project.technologies:
            db_tech = db.query(models.Technology).filter_by(name=tech.name).first()
            if not db_tech:
                db_tech = models.Technology(name=tech.name)
                db.add(db_tech)
                db.flush()
            db.add(
                models.ProjectTechnology(
                    id_project=db_project.id_project,
                    id_technology=db_tech.id_technology,
                )
            )

    for lang in cv_data.languages:
        db.add(models.Language(id_cv=id_cv, language=lang.language, level=lang.level))

    for activity in cv_data.activities:
        db_activity = models.Activity(
            id_cv=id_cv, organisation=activity.organisation, role=activity.role
        )
        db.add(db_activity)
        db.flush()
        for m in activity.activity_missions:
            db.add(
                models.ActivityMission(
                    id_activity=db_activity.id_activity, description=m.description
                )
            )

    db.commit()
    db.refresh(db_cv)
    return _db_cv_to_schema(db_cv)


# ══════════════════════════════════════════
#  DELETE — DELETE /cv/{id_cv}
# ══════════════════════════════════════════


@app.delete("/cv/{id_cv}")
def delete_cv(
    id_cv: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Supprime un CV et toutes ses données liées.
    BUG CORRIGÉ : le filtre id_user manquait — n'importe quel utilisateur
    connecté pouvait supprimer le CV de quelqu'un d'autre.

    - Vérifie que le CV existe ET appartient à l'utilisateur connecté, sinon 404
    - db.delete(db_cv) supprime le CV
    - Grâce au cascade="all, delete-orphan" défini dans models.py,
      toutes les expériences, missions, formations, projets...
      liés à ce CV sont supprimés automatiquement
    - db.commit() valide la suppression
    """
    db_cv = db.query(models.CV).filter(
        models.CV.id_cv == id_cv,
        models.CV.id_user == current_user.id_user,  # BUG CORRIGÉ
    ).first()
    if not db_cv:
        raise HTTPException(status_code=404, detail="CV introuvable")
    db.delete(db_cv)
    db.commit()
    return {"message": f"CV {id_cv} supprimé avec succès"}


# ══════════════════════════════════════════
#  HTML depuis BDD — GET /cv/{id_cv}/html
# ══════════════════════════════════════════


@app.get("/cv/{id_cv}/html", response_class=HTMLResponse)
def render_cv_html(
    id_cv: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),  # BUG CORRIGÉ : manquait
):
    """
    Récupère un CV en BDD et le rend avec le template Jinja2 cv.html.
    BUG CORRIGÉ : cette route n'avait aucune protection — n'importe qui
    pouvait visualiser le CV HTML de n'importe quel utilisateur.

    - Contrairement à GET / qui utilise cv_test.py,
      cette route lit les vraies données depuis PostgreSQL
    - Utile pour prévisualiser un CV stocké en BDD
    """
    db_cv = db.query(models.CV).filter(
        models.CV.id_cv == id_cv,
        models.CV.id_user == current_user.id_user,  # BUG CORRIGÉ
    ).first()
    if not db_cv:
        raise HTTPException(status_code=404, detail="CV introuvable")
    cv = _db_cv_to_schema(db_cv)
    return templates.TemplateResponse(
        request=request, name="cv.html", context={"cv": cv}
    )


# ══════════════════════════════════════════
#  HELPER — SQLAlchemy → Pydantic
# ══════════════════════════════════════════


def _db_cv_to_schema(db_cv: models.CV) -> classCV.CV:
    """
    Convertit un objet SQLAlchemy (venant de la BDD)
    en objet Pydantic (compris par FastAPI pour sérialiser en JSON).

    Sans cette fonction, FastAPI ne saurait pas comment
    transformer un objet SQLAlchemy en JSON.
    """
    info = db_cv.personnal_information
    return classCV.CV(
        id_cv=db_cv.id_cv,
        titre_profil=db_cv.titre_profil,
        resume=db_cv.resume,
        date_creation=db_cv.date_creation,
        date_modification=db_cv.date_modification,
        personnal_information=classCV.PersonnalInformation(
            id_personnal_information=info.id_personnal_information,
            name=info.name,
            first_name=info.first_name,
            address=info.address,
            phone_number=info.phone_number,
            email=info.email,
            linkedin=info.linkedin,
            github=info.github,
            portfoliio=info.portfoliio,
        ),
        experiences=[
            classCV.Experience(
                id_experience=e.id_experience,
                job=e.job,
                company=e.company,
                city=e.city,
                start_date=e.start_date,
                end_date=e.end_date,
                missions=[
                    classCV.Mission(id_mission=m.id_mission, description=m.description)
                    for m in e.missions
                ],
            )
            for e in db_cv.experiences
        ],
        formations=[
            classCV.Formation(
                id_formation=f.id_formation,
                diploma=f.diploma,
                city=f.city,
                date=f.date,
                school=f.school,
            )
            for f in db_cv.formations
        ],
        projects=[
            classCV.Project(
                id_project=p.id_project,
                name=p.name,
                description=p.description,
                link=p.link,
                technologies=[
                    classCV.Technology(id_technology=t.id_technology, name=t.name)
                    for t in p.technologies
                ],
            )
            for p in db_cv.projects
        ],
        languages=[
            classCV.Language(
                id_language=l.id_language, language=l.language, level=l.level
            )
            for l in db_cv.languages
        ],
        activities=[
            classCV.Activity(
                id_activity=a.id_activity,
                organisation=a.organisation,
                role=a.role,
                activity_missions=[
                    classCV.ActivityMission(
                        id_activity_mission=m.id_activity_mission,
                        description=m.description,
                    )
                    for m in a.activity_missions
                ],
            )
            for a in db_cv.activities
        ],
    )
