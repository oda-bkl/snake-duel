"""
Integration test fixtures.

Each test gets a fresh SQLite file via tmp_path.  We patch the module-level
engine and SessionLocal in app.database so all store calls use the temp DB,
then restore them afterwards so unit tests can still run in the same session.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.database as db_module
from app.database import Base
from app.main import app
from app.store import store


@pytest.fixture
def client(tmp_path):
    db_url = f"sqlite:///{tmp_path / 'integration.db'}"

    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(engine)

    # Patch module globals so get_session() and init_db() use the temp DB
    _orig_engine = db_module.engine
    _orig_session = db_module.SessionLocal
    db_module.engine = engine
    db_module.SessionLocal = SessionLocal

    store._global_subs.clear()
    store._game_subs.clear()

    yield TestClient(app)

    # Restore so unit tests in the same run are unaffected
    db_module.engine = _orig_engine
    db_module.SessionLocal = _orig_session
    Base.metadata.drop_all(engine)
    engine.dispose()
