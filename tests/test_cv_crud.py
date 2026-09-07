from tests.conftest import auth_headers, create_user


def cv_payload(
    titre_profil="Backend Developer",
    job="Software Engineer",
    mission_text="Built the API",
):
    return {
        "titre_profil": titre_profil,
        "resume": "Experienced developer.",
        "personnal_information": {
            "name": "Doe",
            "first_name": "Jane",
            "address": "1 Main St",
            "phone_number": "0102030405",
            "email": "jane.doe@example.com",
        },
        "experiences": [
            {
                "job": job,
                "company": "Acme",
                "city": "Paris",
                "start_date": "2020-01-01",
                "end_date": "2022-01-01",
                "missions": [{"description": mission_text}],
            }
        ],
        "formations": [
            {
                "diploma": "Master's",
                "city": "Paris",
                "date": "2019",
                "school": "Sorbonne",
            }
        ],
        "projects": [
            {
                "name": "CV Generator",
                "description": "A tool to generate CVs.",
                "technologies": [{"name": "Python"}],
            }
        ],
        "languages": [{"language": "English", "level": "Fluent"}],
        "activities": [
            {
                "organisation": "Local charity",
                "role": "Volunteer",
                "activity_missions": [{"description": "Organized events"}],
            }
        ],
    }


def other_cv_payload():
    return cv_payload(
        titre_profil="Frontend Developer",
        job="UI Developer",
        mission_text="Built the UI",
    )


# ══════════════════════════════════════════
#  POST /cv — happy path
# ══════════════════════════════════════════


def test_create_cv_returns_201_and_mirrors_input(client, db_session):
    user = create_user(db_session, email="owner@example.com")

    response = client.post("/cv", json=cv_payload(), headers=auth_headers(user))

    assert response.status_code == 201
    body = response.json()
    assert body["titre_profil"] == "Backend Developer"
    assert body["personnal_information"]["name"] == "Doe"
    assert body["experiences"][0]["job"] == "Software Engineer"
    assert body["experiences"][0]["missions"][0]["description"] == "Built the API"
    assert body["formations"][0]["school"] == "Sorbonne"
    assert body["projects"][0]["technologies"][0]["name"] == "Python"
    assert body["languages"][0]["language"] == "English"
    assert body["activities"][0]["activity_missions"][0]["description"] == (
        "Organized events"
    )


# ══════════════════════════════════════════
#  GET /cv — list
# ══════════════════════════════════════════


def test_get_all_cv_returns_list_containing_created_cv(client, db_session):
    user = create_user(db_session, email="owner2@example.com")
    created = client.post(
        "/cv", json=cv_payload(), headers=auth_headers(user)
    ).json()

    response = client.get("/cv", headers=auth_headers(user))

    assert response.status_code == 200
    ids = [cv["id_cv"] for cv in response.json()]
    assert created["id_cv"] in ids


def test_get_all_cv_for_user_with_no_cvs_returns_empty_list(client, db_session):
    user = create_user(db_session, email="empty@example.com")

    response = client.get("/cv", headers=auth_headers(user))

    assert response.status_code == 200
    assert response.json() == []


# ══════════════════════════════════════════
#  GET /cv/{id_cv} — read one
# ══════════════════════════════════════════


def test_get_cv_by_id_returns_full_nested_cv(client, db_session):
    user = create_user(db_session, email="owner3@example.com")
    created = client.post(
        "/cv", json=cv_payload(), headers=auth_headers(user)
    ).json()

    response = client.get(f"/cv/{created['id_cv']}", headers=auth_headers(user))

    assert response.status_code == 200
    body = response.json()
    assert body["id_cv"] == created["id_cv"]
    assert body["personnal_information"]["first_name"] == "Jane"
    assert len(body["experiences"]) == 1
    assert len(body["experiences"][0]["missions"]) == 1
    assert len(body["formations"]) == 1
    assert len(body["projects"]) == 1
    assert len(body["languages"]) == 1
    assert len(body["activities"]) == 1
    assert len(body["activities"][0]["activity_missions"]) == 1


# ══════════════════════════════════════════
#  PUT /cv/{id_cv} — update replaces, not merges
# ══════════════════════════════════════════


def test_update_cv_replaces_nested_data(client, db_session):
    user = create_user(db_session, email="owner4@example.com")
    created = client.post(
        "/cv", json=cv_payload(), headers=auth_headers(user)
    ).json()

    update_response = client.put(
        f"/cv/{created['id_cv']}",
        json=other_cv_payload(),
        headers=auth_headers(user),
    )
    assert update_response.status_code == 200

    fetched = client.get(
        f"/cv/{created['id_cv']}", headers=auth_headers(user)
    ).json()

    assert fetched["titre_profil"] == "Frontend Developer"
    assert fetched["experiences"][0]["missions"][0]["description"] == "Built the UI"

    fetched_str = str(fetched)
    assert "Built the API" not in fetched_str
    assert "Software Engineer" not in fetched_str
    assert "Backend Developer" not in fetched_str
    assert fetched["experiences"][0]["job"] == "UI Developer"


# ══════════════════════════════════════════
#  DELETE /cv/{id_cv} — cascade delete
# ══════════════════════════════════════════


def test_delete_cv_removes_cv_and_all_child_rows(client, db_session):
    import models

    user = create_user(db_session, email="owner5@example.com")
    created = client.post(
        "/cv", json=cv_payload(), headers=auth_headers(user)
    ).json()
    id_cv = created["id_cv"]

    delete_response = client.delete(f"/cv/{id_cv}", headers=auth_headers(user))
    assert delete_response.status_code == 200

    follow_up = client.get(f"/cv/{id_cv}", headers=auth_headers(user))
    assert follow_up.status_code == 404

    assert db_session.query(models.CV).filter_by(id_cv=id_cv).count() == 0
    assert (
        db_session.query(models.PersonnalInformation).filter_by(id_cv=id_cv).count()
        == 0
    )
    experience_ids = [
        e.id_experience
        for e in db_session.query(models.Experience).filter_by(id_cv=id_cv).all()
    ]
    assert experience_ids == []
    assert (
        db_session.query(models.Mission)
        .filter(models.Mission.id_experience.in_(experience_ids or [-1]))
        .count()
        == 0
    )
    assert db_session.query(models.Formation).filter_by(id_cv=id_cv).count() == 0
    project_ids = [
        p.id_project
        for p in db_session.query(models.Project).filter_by(id_cv=id_cv).all()
    ]
    assert project_ids == []
    assert (
        db_session.query(models.ProjectTechnology)
        .filter(models.ProjectTechnology.id_project.in_(project_ids or [-1]))
        .count()
        == 0
    )
    assert db_session.query(models.Language).filter_by(id_cv=id_cv).count() == 0
    activity_ids = [
        a.id_activity
        for a in db_session.query(models.Activity).filter_by(id_cv=id_cv).all()
    ]
    assert activity_ids == []
    assert (
        db_session.query(models.ActivityMission)
        .filter(models.ActivityMission.id_activity.in_(activity_ids or [-1]))
        .count()
        == 0
    )


# ══════════════════════════════════════════
#  GET /cv/{id_cv}/html
# ══════════════════════════════════════════


def test_get_cv_html_returns_200_with_cv_data(client, db_session):
    user = create_user(db_session, email="owner6@example.com")
    created = client.post(
        "/cv", json=cv_payload(), headers=auth_headers(user)
    ).json()

    response = client.get(
        f"/cv/{created['id_cv']}/html", headers=auth_headers(user)
    )

    assert response.status_code == 200
    assert "Doe" in response.text
    assert "Backend Developer" in response.text or "Software Engineer" in (
        response.text
    )


# ══════════════════════════════════════════
#  Ownership isolation — intentional 404, not 403
#  ("don't reveal existence" behavior, locked in per docs/specs/
#  automated-testing-foundation.md #30 — a future switch to 403 must
#  fail this test, not pass silently)
# ══════════════════════════════════════════


def test_get_cv_owned_by_another_user_returns_404_not_403(client, db_session):
    user_a = create_user(db_session, email="usera@example.com")
    user_b = create_user(db_session, email="userb@example.com")
    created = client.post(
        "/cv", json=cv_payload(), headers=auth_headers(user_a)
    ).json()

    response = client.get(
        f"/cv/{created['id_cv']}", headers=auth_headers(user_b)
    )

    assert response.status_code == 404


def test_update_cv_owned_by_another_user_returns_404_not_403(client, db_session):
    user_a = create_user(db_session, email="usera2@example.com")
    user_b = create_user(db_session, email="userb2@example.com")
    created = client.post(
        "/cv", json=cv_payload(), headers=auth_headers(user_a)
    ).json()

    response = client.put(
        f"/cv/{created['id_cv']}",
        json=other_cv_payload(),
        headers=auth_headers(user_b),
    )

    assert response.status_code == 404


def test_delete_cv_owned_by_another_user_returns_404_not_403(client, db_session):
    user_a = create_user(db_session, email="usera3@example.com")
    user_b = create_user(db_session, email="userb3@example.com")
    created = client.post(
        "/cv", json=cv_payload(), headers=auth_headers(user_a)
    ).json()

    response = client.delete(
        f"/cv/{created['id_cv']}", headers=auth_headers(user_b)
    )

    assert response.status_code == 404


def test_get_cv_html_owned_by_another_user_returns_404_not_403(client, db_session):
    user_a = create_user(db_session, email="usera4@example.com")
    user_b = create_user(db_session, email="userb4@example.com")
    created = client.post(
        "/cv", json=cv_payload(), headers=auth_headers(user_a)
    ).json()

    response = client.get(
        f"/cv/{created['id_cv']}/html", headers=auth_headers(user_b)
    )

    assert response.status_code == 404


# ══════════════════════════════════════════
#  Ownership spoofing on creation
# ══════════════════════════════════════════


def test_create_cv_ignores_id_user_spoofing_attempt(client, db_session):
    user_a = create_user(db_session, email="spoofera@example.com")
    user_b = create_user(db_session, email="spooferb@example.com")

    payload = cv_payload()
    payload["id_user"] = user_b.id_user

    client.post("/cv", json=payload, headers=auth_headers(user_a))

    cvs_for_a = client.get("/cv", headers=auth_headers(user_a)).json()
    cvs_for_b = client.get("/cv", headers=auth_headers(user_b)).json()

    assert len(cvs_for_a) == 1
    assert cvs_for_b == []


# ══════════════════════════════════════════
#  Unauthenticated access
# ══════════════════════════════════════════


def test_create_cv_without_authorization_header_returns_401(client):
    response = client.post("/cv", json=cv_payload())

    assert response.status_code == 401


def test_get_all_cv_without_authorization_header_returns_401(client):
    response = client.get("/cv")

    assert response.status_code == 401


def test_get_cv_without_authorization_header_returns_401(client):
    response = client.get("/cv/1")

    assert response.status_code == 401


def test_update_cv_without_authorization_header_returns_401(client):
    response = client.put("/cv/1", json=cv_payload())

    assert response.status_code == 401


def test_delete_cv_without_authorization_header_returns_401(client):
    response = client.delete("/cv/1")

    assert response.status_code == 401


def test_get_cv_html_without_authorization_header_returns_401(client):
    response = client.get("/cv/1/html")

    assert response.status_code == 401
