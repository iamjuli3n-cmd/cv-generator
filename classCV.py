"""
cv_models.py
Modèles Pydantic pour une API FastAPI — compatibles Pylance.
"""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, EmailStr, HttpUrl, Field


class InformationsPersonnelles(BaseModel):
    nom: str
    prenom: str
    adresse: str
    telephone: str
    email: EmailStr
    portfolio: Optional[HttpUrl] = None
    linkedin: Optional[HttpUrl] = None
    github: Optional[HttpUrl] = None
    permis_conduire: Optional[bool] = None
    nationalite: Optional[str] = None


class TitreProfil(BaseModel):
    titre: str


class Resume(BaseModel):
    texte: str = Field(..., min_length=1, max_length=1000)


class CompetencesPrincipales(BaseModel):
    competences: list[str] = Field(default_factory=list)


class CompetencesTechniques(BaseModel):
    langages: list[str] = Field(default_factory=list)
    logiciels: list[str] = Field(default_factory=list)
    technologies: list[str] = Field(default_factory=list)


class ExperienceProfessionnelle(BaseModel):
    poste: str
    entreprise: str
    ville: str
    date_debut: str
    date_fin: str
    missions: list[str] = Field(default_factory=list)


class Formation(BaseModel):
    diplome: str
    etablissement: str
    ville: str
    date_debut: str
    date_fin: str
    specialisation: Optional[str] = None
    projet_important: Optional[str] = None


class Projet(BaseModel):
    nom: str
    description: str
    technologies: list[str] = Field(default_factory=list)
    resultat_ou_lien: Optional[str] = None


class Certification(BaseModel):
    titre: str
    organisation: str
    date: str


class CompetenceLinguistique(BaseModel):
    langue: str
    niveau: str


class CompetencesInformatiques(BaseModel):
    outils: list[str] = Field(default_factory=list)


class SoftSkills(BaseModel):
    competences: list[str] = Field(default_factory=list)


class Activite(BaseModel):
    organisation: str
    role: str
    realisations: list[str] = Field(default_factory=list)


class Publication(BaseModel):
    titre: str
    journal_ou_conference: str
    date: str


class Conference(BaseModel):
    nom: str
    sujet: str
    annee: str


class Prix(BaseModel):
    nom: str
    organisation: str
    annee: str


class CentresInteret(BaseModel):
    interets: list[str] = Field(default_factory=list)


class References(BaseModel):
    disponibles_sur_demande: bool = True
    contacts: list[str] = Field(default_factory=list)


class CV(BaseModel):
    informations_personnelles: InformationsPersonnelles
    titre_profil: TitreProfil
    resume: Resume
    competences_principales: CompetencesPrincipales
    competences_techniques: CompetencesTechniques
    experiences: list[ExperienceProfessionnelle] = Field(default_factory=list)
    formations: list[Formation] = Field(default_factory=list)
    projets: list[Projet] = Field(default_factory=list)
    certifications: list[Certification] = Field(default_factory=list)
    competences_linguistiques: list[CompetenceLinguistique] = Field(
        default_factory=list
    )
    competences_informatiques: Optional[CompetencesInformatiques] = None
    soft_skills: Optional[SoftSkills] = None
    activites: list[Activite] = Field(default_factory=list)
    publications: list[Publication] = Field(default_factory=list)
    conferences: list[Conference] = Field(default_factory=list)
    prix: list[Prix] = Field(default_factory=list)
    centres_interet: Optional[CentresInteret] = None
    references: Optional[References] = None
