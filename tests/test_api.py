import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "BLIP" in response.json()["message"]

def test_health():
    response = client.get("/health")
    assert response.status_code == 200

def test_model_info():
    response = client.get("/model-info")
    assert response.status_code == 200

def test_caption_no_file():
    response = client.post("/caption/")
    assert response.status_code != 200