"""
models.py
Tables SQLAlchemy — basées sur le MCD.
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, Date, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class PersonnalInformation(Base):
    __tablename__ = "personnal_information"

    id_personnal_information = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    first_name = Column(String(50), nullable=False)
    address = Column(String(255), nullable=True)
    phone_number = Column(String(50), nullable=True)
    email = Column(String(50), nullable=False)
    linkedin = Column(String(255), nullable=True)
    github = Column(String(255), nullable=True)
    portfoliio = Column(String(255), nullable=True)

    id_cv = Column(Integer, ForeignKey("cv.id_cv"), nullable=False)
    cv = relationship("CV", back_populates="personnal_information")


class Experience(Base):
    __tablename__ = "experience"

    id_experience = Column(Integer, primary_key=True, autoincrement=True)
    job = Column(String(50), nullable=False)
    company = Column(String(50), nullable=False)
    city = Column(String(50), nullable=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)

    id_cv = Column(Integer, ForeignKey("cv.id_cv"), nullable=False)
    cv = relationship("CV", back_populates="experiences")
    missions = relationship(
        "Mission", back_populates="experience", cascade="all, delete-orphan"
    )


class Mission(Base):
    __tablename__ = "mission"

    id_mission = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(String(255), nullable=False)

    id_experience = Column(
        Integer, ForeignKey("experience.id_experience"), nullable=False
    )
    experience = relationship("Experience", back_populates="missions")


class Formation(Base):
    __tablename__ = "formation"

    id_formation = Column(Integer, primary_key=True, autoincrement=True)
    diploma = Column(String(50), nullable=False)
    city = Column(String(50), nullable=True)
    date = Column(String(50), nullable=True)
    school = Column(String(50), nullable=False)

    id_cv = Column(Integer, ForeignKey("cv.id_cv"), nullable=False)
    cv = relationship("CV", back_populates="formations")


class Technology(Base):
    __tablename__ = "technology"

    id_technology = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)

    projects = relationship(
        "Project", secondary="project_technology", back_populates="technologies"
    )


class ProjectTechnology(Base):
    __tablename__ = "project_technology"

    id_project = Column(Integer, ForeignKey("project.id_project"), primary_key=True)
    id_technology = Column(
        Integer, ForeignKey("technology.id_technology"), primary_key=True
    )


class Project(Base):
    __tablename__ = "project"

    id_project = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    link = Column(String(255), nullable=True)

    id_cv = Column(Integer, ForeignKey("cv.id_cv"), nullable=False)
    cv = relationship("CV", back_populates="projects")
    technologies = relationship(
        "Technology", secondary="project_technology", back_populates="projects"
    )


class Language(Base):
    __tablename__ = "language"

    id_language = Column(Integer, primary_key=True, autoincrement=True)
    language = Column(String(50), nullable=False)
    level = Column(String(50), nullable=False)

    id_cv = Column(Integer, ForeignKey("cv.id_cv"), nullable=False)
    cv = relationship("CV", back_populates="languages")


class Activity(Base):
    __tablename__ = "activity"

    id_activity = Column(Integer, primary_key=True, autoincrement=True)
    organisation = Column(String(50), nullable=False)
    role = Column(String(50), nullable=False)

    id_cv = Column(Integer, ForeignKey("cv.id_cv"), nullable=False)
    cv = relationship("CV", back_populates="activities")
    activity_missions = relationship(
        "ActivityMission", back_populates="activity", cascade="all, delete-orphan"
    )


class ActivityMission(Base):
    __tablename__ = "activity_mission"

    id_activity_mission = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(String(255), nullable=False)

    id_activity = Column(Integer, ForeignKey("activity.id_activity"), nullable=False)
    activity = relationship("Activity", back_populates="activity_missions")


class CV(Base):
    __tablename__ = "cv"

    id_cv = Column(Integer, primary_key=True, autoincrement=True)
    titre_profil = Column(String(50), nullable=False)
    resume = Column(Text, nullable=True)
    date_creation = Column(Date, nullable=True)
    date_modification = Column(Date, nullable=True)

    # Les relationship(...) ne créent pas de colonnes dans la BDD — ils servent uniquement à naviguer entre les objets Python :
    personnal_information = relationship(
        "PersonnalInformation",
        back_populates="cv",
        uselist=False,
        cascade="all, delete-orphan",
    )
    experiences = relationship(
        "Experience", back_populates="cv", cascade="all, delete-orphan"
    )
    formations = relationship(
        "Formation", back_populates="cv", cascade="all, delete-orphan"
    )
    projects = relationship(
        "Project", back_populates="cv", cascade="all, delete-orphan"
    )
    languages = relationship(
        "Language", back_populates="cv", cascade="all, delete-orphan"
    )
    activities = relationship(
        "Activity", back_populates="cv", cascade="all, delete-orphan"
    )
