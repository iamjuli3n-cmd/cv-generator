"""
Ce document regroupe toutes les classes que nous utiliserons dans notre CV-generator
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class InformationsPersonnelles:
    nom: str
    prenom: str
    adresse: str
    telephone: str
    email: str
    portfolio: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    permis_conduire: Optional[bool] = None
    nationalite: Optional[str] = None


@dataclass
class TitreProfil:
    titre: str


@dataclass
class Resume:
    texte: str


@dataclass
class CompetencesPrincipales:
    competences: list[str] = field(default_factory=list)


@dataclass
class CompetencesTechniques:
    langages: list[str] = field(default_factory=list)
    logiciels: list[str] = field(default_factory=list)
    technologies: list[str] = field(default_factory=list)


@dataclass
class ExperienceProfessionnelle:
    poste: str
    entreprise: str
    ville: str
    date_debut: str
    date_fin: str
    missions: list[str] = field(default_factory=list)


@dataclass
class Formation:
    diplome: str
    etablissement: str
    ville: str
    date_debut: str
    date_fin: str
    specialisation: Optional[str] = None
    projet_important: Optional[str] = None


@dataclass
class Projet:
    nom: str
    description: str
    technologies: list[str] = field(default_factory=list)
    resultat_ou_lien: Optional[str] = None


@dataclass
class Certification:
    titre: str
    organisation: str
    date: str


@dataclass
class CompetenceLinguistique:
    langue: str
    niveau: str


@dataclass
class CompetencesInformatiques:
    outils: list[str] = field(default_factory=list)


@dataclass
class SoftSkills:
    competences: list[str] = field(default_factory=list)


@dataclass
class Activite:
    organisation: str
    role: str
    realisations: list[str] = field(default_factory=list)


@dataclass
class Publication:
    titre: str
    journal_ou_conference: str
    date: str


@dataclass
class Conference:
    nom: str
    sujet: str
    annee: str


@dataclass
class Prix:
    nom: str
    organisation: str
    annee: str


@dataclass
class CentresInteret:
    interets: list[str] = field(default_factory=list)


@dataclass
class References:
    disponibles_sur_demande: bool = True
    contacts: list[str] = field(default_factory=list)


@dataclass
class CV:
    informations_personnelles: InformationsPersonnelles
    titre_profil: TitreProfil
    resume: Resume
    competences_principales: CompetencesPrincipales
    competences_techniques: CompetencesTechniques
    experiences: list[ExperienceProfessionnelle] = field(default_factory=list)
    formations: list[Formation] = field(default_factory=list)
    projets: list[Projet] = field(default_factory=list)
    certifications: list[Certification] = field(default_factory=list)
    competences_linguistiques: list[CompetenceLinguistique] = field(
        default_factory=list
    )
    competences_informatiques: Optional[CompetencesInformatiques] = None
    soft_skills: Optional[SoftSkills] = None
    activites: list[Activite] = field(default_factory=list)
    publications: list[Publication] = field(default_factory=list)
    conferences: list[Conference] = field(default_factory=list)
    prix: list[Prix] = field(default_factory=list)
    centres_interet: Optional[CentresInteret] = None
    references: Optional[References] = None
