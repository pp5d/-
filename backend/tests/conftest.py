import os

os.environ["DATABASE_URL"] = "postgresql+psycopg://aiqa:aiqa_dev_password@localhost:5432/aiqa_test"
os.environ["APP_MODE"] = "full"
os.environ["SECRET_KEY"] = "test-secret"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.db import Base, get_db
from app.main import app

ADMIN_ENGINE = create_engine(
    "postgresql+psycopg://aiqa:aiqa_dev_password@localhost:5432/postgres",
    isolation_level="AUTOCOMMIT",
)
with ADMIN_ENGINE.connect() as conn:
    try:
        conn.execute(text("CREATE DATABASE aiqa_test"))
    except Exception:
        pass  # 已存在

engine = create_engine(os.environ["DATABASE_URL"])
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture
def client():
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
