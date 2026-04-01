"""
cv_models.py
Modèles Pydantic basés sur le MCD — contexte FastAPI.
"""

from __future__ import annotations
from datetime import date
from typing import Optional
from pydantic import BaseModel, EmailStr, HttpUrl


class PersonnalInformation(BaseModel):
    id_personnal_information: Optional[int] = None
    name: str
    first_name: str
    address: str
    phone_number: str
    email: EmailStr
    linkedin: Optional[HttpUrl] = None
    github: Optional[HttpUrl] = None
    portfoliio: Optional[HttpUrl] = None


class Mission(BaseModel):
    id_mission: Optional[int] = None
    description: str


class Experience(BaseModel):
    id_experience: Optional[int] = None
    job: str
    company: str
    city: str
    start_date: date
    end_date: Optional[date] = None
    missions: list[Mission] = []


class Formation(BaseModel):
    id_formation: Optional[int] = None
    diploma: str
    city: str
    date: str
    school: str


class Technology(BaseModel):
    id_technology: Optional[int] = None
    name: str


class Project(BaseModel):
    id_project: Optional[int] = None
    name: str
    description: str
    link: Optional[HttpUrl] = None
    technologies: list[Technology] = []


class Language(BaseModel):
    id_language: Optional[int] = None
    language: str
    level: str


class ActivityMission(BaseModel):
    id_activity_mission: Optional[int] = None
    description: str


class Activity(BaseModel):
    id_activity: Optional[int] = None
    organisation: str
    role: str
    activity_missions: list[ActivityMission] = []


class CV(BaseModel):
    id_cv: Optional[int] = None
    titre_profil: str
    resume: str
    date_creation: Optional[date] = None
    date_modification: Optional[date] = None
    personnal_information: PersonnalInformation
    experiences: list[Experience] = []
    formations: list[Formation] = []
    projects: list[Project] = []
    languages: list[Language] = []
    activities: list[Activity] = []
