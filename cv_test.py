"""
cv_test.py
Objet CV complet pour tests.
"""

from classCV import (
    CV,
    PersonnalInformation,
    Experience,
    Mission,
    Formation,
    Project,
    Technology,
    Language,
    Activity,
    ActivityMission,
)

cv_test = CV(
    titre_profil="Développeur Web Full-Stack",
    resume="Développeur Full-Stack avec 3 ans d'expérience en Python et React. "
    "Passionné par la conception d'APIs robustes et d'interfaces modernes. "
    "À la recherche d'un nouveau défi dans une équipe dynamique.",
    date_creation="2024-01-15",
    date_modification="2024-03-20",
    personnal_information=PersonnalInformation(
        name="Dupont",
        first_name="Thomas",
        address="12 rue de la Paix, 75001 Paris",
        phone_number="+33 6 12 34 56 78",
        email="thomas.dupont@gmail.com",
        linkedin="https://linkedin.com/in/thomasdupont",
        github="https://github.com/thomasdupont",
        portfoliio="https://thomasdupont.dev",
    ),
    experiences=[
        Experience(
            job="Développeur Full-Stack",
            company="TechCorp",
            city="Paris",
            start_date="2022-03-01",
            end_date="2024-01-01",
            missions=[
                Mission(
                    description="Développement d'une API REST avec FastAPI et PostgreSQL"
                ),
                Mission(description="Conception et intégration d'interfaces React"),
                Mission(
                    description="Mise en place d'une pipeline CI/CD avec GitHub Actions"
                ),
            ],
        ),
        Experience(
            job="Développeur Back-End Junior",
            company="StartupXYZ",
            city="Lyon",
            start_date="2021-06-01",
            end_date="2022-02-28",
            missions=[
                Mission(description="Développement de microservices en Python"),
                Mission(
                    description="Optimisation des requêtes SQL — réduction de 40% du temps de réponse"
                ),
            ],
        ),
    ],
    formations=[
        Formation(
            diploma="Master Informatique — Génie Logiciel",
            city="Paris",
            date="2019-2021",
            school="Université Paris-Saclay",
        ),
        Formation(
            diploma="Licence Informatique",
            city="Lyon",
            date="2016-2019",
            school="Université Claude Bernard Lyon 1",
        ),
    ],
    projects=[
        Project(
            name="CV Generator",
            description="Application web de génération de CV en PDF avec gestion multi-templates.",
            link="https://github.com/thomasdupont/cv-generator",
            technologies=[
                Technology(name="FastAPI"),
                Technology(name="React"),
                Technology(name="PostgreSQL"),
                Technology(name="Docker"),
            ],
        ),
        Project(
            name="Budget Tracker",
            description="Application mobile de suivi de budget personnel avec graphiques.",
            link="https://github.com/thomasdupont/budget-tracker",
            technologies=[
                Technology(name="Python"),
                Technology(name="SQLite"),
                Technology(name="Chart.js"),
            ],
        ),
    ],
    languages=[
        Language(language="Français", level="Langue maternelle"),
        Language(language="Anglais", level="C1"),
        Language(language="Espagnol", level="B1"),
    ],
    activities=[
        Activity(
            organisation="BDE Université Paris-Saclay",
            role="Responsable communication",
            activity_missions=[
                ActivityMission(
                    description="Gestion des réseaux sociaux — 2000 abonnés"
                ),
                ActivityMission(
                    description="Organisation d'événements pour 300 étudiants"
                ),
            ],
        ),
        Activity(
            organisation="Association Code For Good",
            role="Développeur bénévole",
            activity_missions=[
                ActivityMission(
                    description="Développement d'un site vitrine pour une ONG locale"
                ),
            ],
        ),
    ],
)

if __name__ == "__main__":
    import json

    print(json.dumps(cv_test.model_dump(), indent=2, default=str))
