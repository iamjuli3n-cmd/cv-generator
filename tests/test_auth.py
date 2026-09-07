from datetime import datetime, timedelta, timezone

from jose import jwt

import auth
import models


def register(client, email="user@example.com", password="password123"):
    return client.post(
        "/auth/register", json={"email": email, "password": password}
    )


def login(client, email="user@example.com", password="password123"):
    return client.post(
        "/auth/login", data={"username": email, "password": password}
    )


# ══════════════════════════════════════════
#  POST /auth/register
# ══════════════════════════════════════════


def test_register_new_email_returns_201_with_user_out_shape(client):
    response = register(client, email="new@example.com")

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "new@example.com"
    assert "id_user" in body
    assert "is_active" in body
    assert "password" not in body
    assert "hashed_password" not in body


def test_register_duplicate_email_returns_400(client):
    register(client, email="dup@example.com")

    response = register(client, email="dup@example.com")

    assert response.status_code == 400


def test_register_invalid_email_returns_422(client):
    response = register(client, email="not-an-email")

    assert response.status_code == 422


# ══════════════════════════════════════════
#  POST /auth/login
# ══════════════════════════════════════════


def test_login_correct_credentials_returns_200_with_token(client):
    register(client, email="login@example.com", password="correct-password")

    response = login(client, email="login@example.com", password="correct-password")

    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


def test_login_wrong_password_returns_401(client):
    register(client, email="login2@example.com", password="correct-password")

    response = login(client, email="login2@example.com", password="wrong-password")

    assert response.status_code == 401


def test_login_unregistered_email_returns_401(client):
    response = login(client, email="never-registered@example.com", password="whatever")

    assert response.status_code == 401


# ══════════════════════════════════════════
#  GET /users/me
# ══════════════════════════════════════════


def test_me_with_valid_token_returns_200_with_correct_user(client):
    register(client, email="me@example.com", password="password123")
    token = login(client, email="me@example.com", password="password123").json()[
        "access_token"
    ]

    response = client.get(
        "/users/me", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json()["email"] == "me@example.com"


def test_me_without_authorization_header_returns_401(client):
    response = client.get("/users/me")

    assert response.status_code == 401


def test_me_with_malformed_token_returns_401(client):
    response = client.get(
        "/users/me", headers={"Authorization": "Bearer not-a-valid-jwt"}
    )

    assert response.status_code == 401


def test_me_with_expired_token_returns_401(client):
    register(client, email="expired@example.com", password="password123")
    token_response = login(
        client, email="expired@example.com", password="password123"
    )
    me_response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token_response.json()['access_token']}"},
    )
    user_id = me_response.json()["id_user"]

    expired_token = jwt.encode(
        {
            "sub": str(user_id),
            "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
        },
        auth.SECRET_KEY,
        algorithm=auth.ALGORITHM,
    )

    response = client.get(
        "/users/me", headers={"Authorization": f"Bearer {expired_token}"}
    )

    assert response.status_code == 401


def test_me_with_token_for_nonexistent_user_returns_401(client, db_session):
    register(client, email="ghost@example.com", password="password123")
    token = login(client, email="ghost@example.com", password="password123").json()[
        "access_token"
    ]

    db_session.query(models.User).filter_by(email="ghost@example.com").delete()
    db_session.commit()

    response = client.get(
        "/users/me", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 401
