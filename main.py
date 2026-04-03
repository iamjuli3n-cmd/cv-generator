from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from classCV import PersonnalInformation, Experience, Formation, Project, Technology, Language, ActivityMission
from typing import Optional

@app.get("/PersonnalInformation_all/{id_personnal_information}")
def read_PersonnalInformation(id_personnal_information: int, name: str, first_name: str, address: str, phone_number: str, email: EmailStr, linkedin: Optional[HttpUrl] = None, github: Optional[HttpUrl] = None, portfoliio: Optional[HttpUrl] = None):
    return {"id_personnal_information": id_personnal_information, "name": name, "first_name": first_name, "address": address, "phone_number": phone_number, "email": email, "linkedin": linkedin, "github": github, "portfoliio": portfoliio}


@app.post("/PersonnalInformation_all/")
def create_PersonnalInformation(id_personnal_information: int, name: str, first_name: str, address: str, phone_number: str, email: EmailStr, linkedin: Optional[HttpUrl] = None, github: Optional[HttpUrl] = None, portfoliio: Optional[HttpUrl] = None):
    personnal_information = {"id_personnal_information": id_personnal_information, "name": name, "first_name": first_name, "address": address, "phone_number": phone_number, "email": email, "linkedin": linkedin, "github": github, "portfoliio": portfoliio}

    PersonnalInformation_all.append(personnal_information)

    response = {"id_personnal_information": len(PersonnalInformation_all) - 1, "personnal_information": personnal_information}

    return response


@app.put("/PersonnalInformation_all/{id_personnal_information}")
def update_PersonnalInformation(id_personnal_information: int, name: str, first_name: str, address: str, phone_number: str, email: EmailStr, linkedin: Optional[HttpUrl] = None, github: Optional[HttpUrl] = None, portfoliio: Optional[HttpUrl] = None):
    personnal_information = {"id_personnal_information": id_personnal_information, "name": name, "first_name": first_name, "address": address, "phone_number": phone_number, "email": email, "linkedin": linkedin, "github": github, "portfoliio": portfoliio}

    PersonnalInformation_all[id_personnal_information].update(personnal_information)

    # print("PersonnalInformation_all[id_personnal_information]", PersonnalInformation_all[id_personnal_information])

    response = {"personnal_information": PersonnalInformation_all[id_personnal_information], "id_personnal_information": id_personnal_information}

    # print("response", response)

    return response


@app.get("/Experience_all/{id_experience}")
def read_Experience(id_experience: int, company: str, city: str, start_date: str, end_date: str, missions: list[Mission]):
    return {"id_experience": id_experience, "company": company, "city": city, "start_date": start_date, "end_date": end_date, "missions": missions}


@app.post("/Experience_all/")
def create_Experience(id_experience: int, company: str, city: str, start_date: str, end_date: str, missions: list[Mission]):
    experience = {"id_experience": id_experience, "company": company, "position": position, "start_date": start_date, "end_date": end_date}

    Experience_all.append(experience)

    response = {"id_experience": len(Experience_all) - 1, "experience": experience}

    return response


@app.put("/Experience_all/{id_experience}")
def update_Experience(id_experience: int, company: str, city: str, start_date: str, end_date: str, missions: list[Mission]):
    experience = {"id_experience": id_experience, "company": company, "city": city, "start_date": start_date, "end_date": end_date, "missions": missions}

    Experience_all[id_experience].update(experience)

    # print("Experience_all[id_experience]", Experience_all[id_experience])

    response = {"experience": Experience_all[id_experience], "id_experience": id_experience}

    # print("response", response)

    return response


@app.get("/Formation_all/{id_formation}")
def read_Formation(id_formation: int, diploma: str, city: str, date: str, school: str):
    return {"id_formation": id_formation, "diploma": diploma, "city": city, "date": date, "school": school}


@app.post("/Formation_all/")
def create_Formation(id_formation: int, diploma: str, city: str, date: str, school: str):
    formation = {"id_formation": id_formation, "diploma": diploma, "city": city, "date": date, "school": school}

    Formation_all.append(formation)

    response = {"id_formation": len(Formation_all) - 1, "formation": formation}

    return response


@app.put("/Formation_all/{id_formation}")
def update_Formation(id_formation: int, diploma: str, city: str, date: str, school: str):
    formation = {"id_formation": id_formation, "diploma": diploma, "city": city, "date": date, "school": school}

    Formation_all[id_formation].update(formation)

    # print("Formation_all[id_formation]", Formation_all[id_formation])

    response = {"formation": Formation_all[id_formation], "id_formation": id_formation}

    # print("response", response)

    return response


@app.get("/Project_all/{id_project}")
def read_Project(id_project: int, name: str, description: str, link: Optional[HttpUrl] = None, technology: list[Technology]):
    return {"id_project": id_project, "name": name, "description": description, "link": link, "technology": technology}


@app.post("/Project_all/")
def create_Project(id_project: int, name: str, description: str, link: Optional[HttpUrl] = None, technology: list[Technology]):
    project = {"id_project": id_project, "name": name, "description": description, "link": link, "technology": technology}

    Project_all.append(project)

    response = {"id_project": len(Project_all) - 1, "project": project}

    return response


@app.put("/Project_all/{id_project}")
def update_Project(id_project: int, name: str, description: str, link: Optional[HttpUrl] = None, technology: list[Technology]):
    project = {"id_project": id_project, "name": name, "description": description, "link": link, "technology": technology}

    Project_all[id_project].update(project)

    # print("Project_all[id_project]", Project_all[id_project])

    response = {"project": Project_all[id_project], "id_project": id_project}

    # print("response", response)

    return response


@app.get("/Language_all/{id_language}")
def read_Language(id_language: int, name: str, level: str):
    return {"id_language": id_language, "name": name, "level": level}


@app.post("/Language_all/")
def create_Language(id_language: int, name: str, level: str):
    language = {"id_language": id_language, "name": name, "level": level}

    Language_all.append(language)

    response = {"id_language": len(Language_all) - 1, "language": language}

    return response


@app.put("/Language_all/{id_language}")
def update_Language(id_language: int, name: str, level: str):
    language = {"id_language": id_language, "name": name, "level": level}

    Language_all[id_language].update(language)

    # print("Language_all[id_language]", Language_all[id_language])

    response = {"language": Language_all[id_language], "id_language": id_language}

    # print("response", response)

    return response


@app.get("/Activity_all/{id_activity}")
def read_Activity(id_activity: int, organisation: str, role: str, activity_missions: list[ActivityMission]):
    return {"id_activity": id_activity, "organisation": organisation, "role": role, "activity_missions": activity_missions}


@app.post("/Activity_all/")
def create_Activity(id_activity: int, organisation: str, role: str, activity_missions: list[ActivityMission]):
    activity = {"id_activity": id_activity, "organisation": organisation, "role": role, "activity_missions": activity_missions}

    Activity_all.append(activity)

    response = {"id_activity": len(Activity_all) - 1, "activity": activity}

    return response


@app.put("/Activity_all/{id_activity}")
def update_Activity(id_activity: int, organisation: str, role: str, activity_missions: list[ActivityMission]):
    activity = {"id_activity": id_activity, "organisation": organisation, "role": role, "activity_missions": activity_missions}

    Activity_all[id_activity].update(activity)

    # print("Activity_all[id_activity]", Activity_all[id_activity])

    response = {"activity": Activity_all[id_activity], "id_activity": id_activity}

    # print("response", response)

    return response