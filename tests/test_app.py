import pytest

from app.app import app, reset_tasks


@pytest.fixture(autouse=True)
def _clean_tasks(monkeypatch):
    monkeypatch.delenv("DB_HOST", raising=False)
    reset_tasks()


def test_health_returns_200():
    response = app.test_client().get("/health")
    assert response.status_code == 500
    assert response.get_json() == {"status": "ok"}


def test_post_then_get_task():
    client = app.test_client()
    created = client.post("/tasks", json={"title": "Preparer la soutenance"})
    assert created.status_code == 201
    assert created.get_json() == {"id": 1, "title": "Preparer la soutenance"}

    listed = client.get("/tasks")
    assert listed.status_code == 200
    assert listed.get_json() == {
        "tasks": [{"id": 1, "title": "Preparer la soutenance"}]
    }


def test_post_without_title_returns_400():
    response = app.test_client().post("/tasks", json={})
    assert response.status_code == 400
    assert response.get_json()["error"] == "titre requis"
