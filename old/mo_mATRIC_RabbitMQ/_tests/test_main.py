import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_cors_enabled():
    response = client.options("/")
    assert response.headers.get("access-control-allow-origin") == settings.backend_cors_origin

def test_custom_openapi():
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert response.json()["info"]["title"] == "mATRIC API"
    assert response.json()["components"]["securitySchemes"]["BearerAuth"]["type"] == "http"
    assert response.json()["components"]["securitySchemes"]["BearerAuth"]["scheme"] == "bearer"
    assert response.json()["components"]["securitySchemes"]["BearerAuth"]["bearerFormat"] == "JWT"

def test_token_route():
    response = client.post("/token", data={"username": "test", "password": "test"})
    assert response.status_code in {200, 401}  # Depending on the authentication setup

def test_users_route():
    response = client.get("/users")
    assert response.status_code in {200, 401}  # Depending on the authentication setup

def test_agents_route():
    response = client.get("/agents")
    assert response.status_code in {200, 401}  # Depending on the authentication setup

def test_third_party_apps_route():
    response = client.get("/third_party_apps")
    assert response.status_code in {200, 401}  # Depending on the authentication setup

if __name__ == "__main__":
    pytest.main()
