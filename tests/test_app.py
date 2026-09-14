import pytest

from app import app, workouts


@pytest.fixture(autouse=True)
def reset_state():
    workouts.clear()
    yield
    workouts.clear()


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


def test_home_page(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "message" in resp.get_json()


def test_health_check(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"


def test_get_workouts_empty(client):
    resp = client.get("/workouts")
    assert resp.status_code == 200
    assert resp.get_json()["workouts"] == []


def test_add_workout_success(client):
    resp = client.post("/add_workout", json={"workout": "Running", "duration": 30})
    assert resp.status_code == 201
    body = resp.get_json()["workout"]
    assert body["workout"] == "Running"
    assert body["duration"] == 30


def test_add_workout_missing_workout_name(client):
    resp = client.post("/add_workout", json={"duration": 30})
    assert resp.status_code == 400


def test_add_workout_missing_duration(client):
    resp = client.post("/add_workout", json={"workout": "Running"})
    assert resp.status_code == 400


def test_add_workout_invalid_duration_type(client):
    resp = client.post("/add_workout", json={"workout": "Running", "duration": "long"})
    assert resp.status_code == 400


def test_add_workout_negative_duration(client):
    resp = client.post("/add_workout", json={"workout": "Running", "duration": -5})
    assert resp.status_code == 400


def test_add_workout_no_body(client):
    resp = client.post("/add_workout")
    assert resp.status_code == 400


def test_get_workouts_after_add(client):
    client.post("/add_workout", json={"workout": "Cycling", "duration": 45})
    resp = client.get("/workouts")
    data = resp.get_json()["workouts"]
    assert len(data) == 1
    assert data[0]["workout"] == "Cycling"


def test_delete_workout_success(client):
    client.post("/add_workout", json={"workout": "Yoga", "duration": 20})
    resp = client.delete("/delete_workout/1")
    assert resp.status_code == 200
    assert client.get("/workouts").get_json()["workouts"] == []


def test_delete_workout_not_found(client):
    resp = client.delete("/delete_workout/999")
    assert resp.status_code == 404
