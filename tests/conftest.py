import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from fastapi.testclient import TestClient

import auth
import models
from database import Base, get_db
from main import app


@pytest.fixture(scope="session")
def engine(tmp_path_factory):
    db_path = tmp_path_factory.mktemp("db") / "test.db"
    test_engine = create_engine(f"sqlite:///{db_path}")

    @event.listens_for(test_engine, "connect")
    def _enable_foreign_keys(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(test_engine)
    yield test_engine
    test_engine.dispose()


@pytest.fixture()
def db_session(engine):
    connection = engine.connect()
    transaction = connection.begin()

    SessionLocal = sessionmaker(bind=connection)
    session = SessionLocal()
    session.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def _restart_savepoint(sess, trans):
        if trans.nested and not trans._parent.nested:
            sess.expire_all()
            sess.begin_nested()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db_session):
    def _get_db_override():
        yield db_session

    app.dependency_overrides[get_db] = _get_db_override
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.pop(get_db, None)


def create_user(
    db_session: Session, email: str = "user@example.com", password: str = "password123"
) -> models.User:
    """Create a User row directly in the database, no HTTP call involved."""
    user = models.User(
        email=email,
        hashed_password=auth.hash_password(password),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def auth_headers(user: models.User) -> dict[str, str]:
    """Mint a valid bearer-auth header for a user, no HTTP call involved."""
    token = auth.create_access_token({"sub": str(user.id_user)})
    return {"Authorization": f"Bearer {token}"}
