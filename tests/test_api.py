from fastapi.testclient import TestClient
import cv2
import numpy as np

from backend.app.main import app


client = TestClient(app)


def creer_video_test(tmp_path) -> bytes:
    chemin_video = tmp_path / "demo.mp4"
    writer = cv2.VideoWriter(
        str(chemin_video),
        cv2.VideoWriter_fourcc(*"mp4v"),
        10,
        (160, 120),
    )

    for index in range(12):
        image = np.full((120, 160, 3), 240, dtype=np.uint8)
        cv2.putText(
            image,
            str(index),
            (62, 68),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (25, 25, 25),
            2,
        )
        writer.write(image)

    writer.release()
    return chemin_video.read_bytes()


def test_health_route_returns_api_status():
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_architecture_route_returns_layers():
    response = client.get("/api/v1/architecture")

    assert response.status_code == 200
    assert "Passerelle API FastAPI" in response.json()["couches"]


def test_analyser_video_accepts_uploaded_file(tmp_path):
    contenu_video = creer_video_test(tmp_path)

    response = client.post(
        "/api/v1/deepfake/analyser-video",
        files={"video": ("demo.mp4", contenu_video, "video/mp4")},
    )

    data = response.json()

    assert response.status_code == 200
    assert data["filename"] == "demo.mp4"
    assert data["content_type"] == "video/mp4"
    assert data["statut"] == "termine"
    assert data["score_suspicion"] == data["score_final"]
    assert data["upload"]["fichier_temporaire_supprime"] is True
    assert "yeux" in data["details"]
    assert "levres" in data["details"]


def test_analyser_video_rejects_non_video_file():
    response = client.post(
        "/api/v1/deepfake/analyser-video",
        files={"video": ("notes.txt", b"texte", "text/plain")},
    )

    data = response.json()

    assert response.status_code == 200
    assert data["statut"] == "rejete"
    assert data["niveau"] == "Erreur"
