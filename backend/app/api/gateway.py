from fastapi import APIRouter, UploadFile


router = APIRouter(prefix="/api/v1", tags=["Passerelle API"])


@router.get("/health")
def verifier_sante_api() -> dict[str, str]:
    """Indique que la passerelle API est disponible."""
    return {
        "status": "ok",
        "service": "Sentinelle Numerique - API DeepfakeVideo",
    }


@router.get("/architecture")
def lire_architecture() -> dict[str, list[str]]:
    """Retourne un resume simple des couches prevues dans le projet."""
    return {
        "couches": [
            "Passerelle API FastAPI",
            "Services de detection deepfake",
            "Analyse des clignements avec MediaPipe",
            "Analyse de synchronisation labiale",
            "Tableau de bord utilisateur",
        ]
    }


@router.post("/deepfake/analyser-video")
async def analyser_video(video: UploadFile) -> dict[str, str | int | None]:
    """Point d'entree temporaire pour recevoir une video a analyser."""
    return {
        "message": "Video recue. Analyse deepfake a venir.",
        "filename": video.filename,
        "content_type": video.content_type,
        "score_suspicion": None,
    }
