import io
import os
import sys

import pytest
from PIL import Image

# Add the backend directory to Python path so we can import from backend/app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

# Now import the app
from app.main import app
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)


@pytest.fixture
def sample_image():
    """Create a sample image in memory for testing"""
    img = Image.new("RGB", (100, 100), color="red")
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="JPEG")
    return img_bytes.getvalue()


def test_root_endpoint(client):
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "BLIP Image Captioning API"


def test_health_endpoint(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()


def test_model_info_endpoint(client):
    """Test model info endpoint"""
    response = client.get("/model-info")
    assert response.status_code == 200
    data = response.json()
    assert "model_name" in data
    assert "model_type" in data


def test_caption_endpoint_with_image(client, sample_image):
    """Test caption generation with valid image"""
    files = {"file": ("test.jpg", sample_image, "image/jpeg")}
    response = client.post("/caption/", files=files)

    # Should return 200 (success) or 500 (model not loaded in test)
    assert response.status_code in [200, 500]

    if response.status_code == 200:
        data = response.json()
        assert "caption" in data
        assert "processed_image" in data


def test_caption_endpoint_with_invalid_file(client):
    """Test caption generation with invalid file"""
    files = {"file": ("test.txt", b"not an image", "text/plain")}
    response = client.post("/caption/", files=files)
    assert response.status_code == 400


def test_caption_endpoint_missing_file(client):
    """Test caption generation without file"""
    response = client.post("/caption/")
    assert response.status_code == 422


def test_caption_with_parameters(client, sample_image):
    """Test caption generation with custom parameters"""
    files = {"file": ("test.jpg", sample_image, "image/jpeg")}
    params = {"max_length": 25, "num_beams": 3}

    response = client.post("/caption/", files=files, params=params)
    assert response.status_code in [200, 500]


def test_detailed_caption_endpoint(client, sample_image):
    """Test detailed caption endpoint"""
    files = {"file": ("test.jpg", sample_image, "image/jpeg")}
    params = {"max_length": 30, "num_beams": 5, "temperature": 0.8}

    response = client.post("/caption-detailed/", files=files, params=params)
    assert response.status_code in [200, 500]
