from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_health_route_returns_api_status():
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_architecture_route_returns_layers():
    response = client.get("/api/v1/architecture")

    assert response.status_code == 200
    assert "Passerelle API FastAPI" in response.json()["couches"]


def test_analyser_video_accepts_uploaded_file():
    response = client.post(
        "/api/v1/deepfake/analyser-video",
        files={"video": ("demo.mp4", b"fake-video-content", "video/mp4")},
    )

    data = response.json()

    assert response.status_code == 200
    assert data["filename"] == "demo.mp4"
    assert data["content_type"] == "video/mp4"
    assert data["statut"] == "termine"
    assert data["score_suspicion"] == data["score_final"]


def test_analyser_video_rejects_non_video_file():
    response = client.post(
        "/api/v1/deepfake/analyser-video",
        files={"video": ("notes.txt", b"texte", "text/plain")},
    )

    data = response.json()

    assert response.status_code == 200
    assert data["statut"] == "rejete"
    assert data["niveau"] == "Erreur"
