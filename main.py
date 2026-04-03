"""
main.py
Routes FastAPI — CRUD SQLAlchemy + anciens GET Jinja2.
"""

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database import get_db
import models
import classCV
from cv_test import cv_test  # ctrl shift L pour refactor

app = FastAPI(title="CV Generator")
templates = Jinja2Templates(directory="templates")


# ══════════════════════════════════════════
#  ANCIENS GET — rendu Jinja2 depuis cv_test
# ══════════════════════════════════════════


@app.get("/", response_class=HTMLResponse)
def accueil(request: Request):
    """
    Affiche le CV de test (cv_test.py) avec le template cv.html.
    Ne touche pas à la BDD — sert uniquement pour tester le rendu HTML.
    """
    return templates.TemplateResponse(
        request=request, name="cv.html", context={"cv": cv_test}
    )


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
def create_cv(cv_data: classCV.CV, db: Session = Depends(get_db)):
    """
    Crée un CV complet en BDD.

    - Reçoit un objet CV complet au format JSON dans le body de la requête
    - Insère le CV principal, puis toutes les sections liées
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
def get_all_cv(db: Session = Depends(get_db)):
    """
    Retourne la liste de tous les CV stockés en BDD.

    - db.query(models.CV).all() : SELECT * FROM cv
    - Chaque CV est converti en schéma Pydantic via _db_cv_to_schema
    - Retourne une liste vide [] si aucun CV n'existe
    """
    return [_db_cv_to_schema(cv) for cv in db.query(models.CV).all()]


# ══════════════════════════════════════════
#  READ ONE — GET /cv/{id_cv}
# ══════════════════════════════════════════


@app.get("/cv/{id_cv}", response_model=classCV.CV)
def get_cv(id_cv: int, db: Session = Depends(get_db)):
    """
    Retourne un CV précis par son id.

    - Cherche le CV avec l'id fourni dans l'URL
    - Si introuvable, retourne une erreur 404 avec un message clair
    - Sinon retourne le CV complet avec toutes ses sections
    """
    db_cv = db.query(models.CV).filter(models.CV.id_cv == id_cv).first()
    if not db_cv:
        raise HTTPException(status_code=404, detail="CV introuvable")
    return _db_cv_to_schema(db_cv)


# ══════════════════════════════════════════
#  UPDATE — PUT /cv/{id_cv}
# ══════════════════════════════════════════


@app.put("/cv/{id_cv}", response_model=classCV.CV)
def update_cv(id_cv: int, cv_data: classCV.CV, db: Session = Depends(get_db)):
    """
    Remplace un CV existant par les nouvelles données envoyées.

    - Vérifie que le CV existe, sinon 404
    - Met à jour les champs du CV principal
    - Supprime toutes les sections liées existantes (expériences, formations...)
    - Les recrée avec les nouvelles données
    - C'est une stratégie "supprimer / recréer" — plus simple qu'une
      mise à jour champ par champ de chaque sous-élément
    """
    db_cv = db.query(models.CV).filter(models.CV.id_cv == id_cv).first()
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
def delete_cv(id_cv: int, db: Session = Depends(get_db)):
    """
    Supprime un CV et toutes ses données liées.

    - Vérifie que le CV existe, sinon 404
    - db.delete(db_cv) supprime le CV
    - Grâce au cascade="all, delete-orphan" défini dans models.py,
      toutes les expériences, missions, formations, projets...
      liés à ce CV sont supprimés automatiquement
    - db.commit() valide la suppression
    """
    db_cv = db.query(models.CV).filter(models.CV.id_cv == id_cv).first()
    if not db_cv:
        raise HTTPException(status_code=404, detail="CV introuvable")
    db.delete(db_cv)
    db.commit()
    return {"message": f"CV {id_cv} supprimé avec succès"}


# ══════════════════════════════════════════
#  HTML depuis BDD — GET /cv/{id_cv}/html
# ══════════════════════════════════════════


@app.get("/cv/{id_cv}/html", response_class=HTMLResponse)
def render_cv_html(id_cv: int, request: Request, db: Session = Depends(get_db)):
    """
    Récupère un CV en BDD et le rend avec le template Jinja2 cv.html.

    - Contrairement à GET / qui utilise cv_test.py,
      cette route lit les vraies données depuis PostgreSQL
    - Utile pour prévisualiser un CV stocké en BDD
    """
    db_cv = db.query(models.CV).filter(models.CV.id_cv == id_cv).first()
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
