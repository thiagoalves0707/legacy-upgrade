import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    if hasattr(app, "_db"):
        app._db.close()
        del app._db
    return app.test_client()


def test_list_movies(client):
    r = client.get("/movies")
    assert r.status_code == 200
    assert r.get_json()["count"] == 4


def test_filter_available(client):
    r = client.get("/movies?available=yes")
    assert r.get_json()["count"] == 3


def test_get_movie(client):
    r = client.get("/movies/1")
    assert r.status_code == 200
    assert r.get_json()["title"] == "Cidade de Deus"


def test_movie_not_found(client):
    assert client.get("/movies/99").status_code == 404


def test_create_rental(client):
    r = client.post("/rentals", json={"movie_id": 1, "days": 3, "customer": "Ana"})
    assert r.status_code == 201
    assert "total" in r.get_json()


def test_rental_unavailable(client):
    r = client.post("/rentals", json={"movie_id": 3, "days": 1, "customer": "Bia"})
    assert r.status_code == 409


def test_rental_invalid(client):
    r = client.post("/rentals", json={"movie_id": 1})
    assert r.status_code == 422
