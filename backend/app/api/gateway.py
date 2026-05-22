from fastapi import APIRouter, File, UploadFile

from ..services.service_deepfake import ServiceDeepfake


router = APIRouter(prefix="/api/v1", tags=["Passerelle API"])


@router.get("/health")
def verifier_sante_api() -> dict:
    """Indique que la passerelle API est disponible."""
    return {
        "status": "ok",
        "statut": "actif",
        "service": "Sentinelle Numerique - API DeepfakeVideo",
        "message": "Passerelle API operationnelle"
    }


@router.get("/architecture")
def lire_architecture() -> dict:
    """Retourne un resume simple des couches prevues dans le projet."""
    couches = [
        "Dashboard utilisateur",
        "Passerelle API FastAPI",
        "Microservice Deepfake Video",
        "Analyse des clignements avec MediaPipe",
        "Analyse de synchronisation labiale",
        "Stockage temporaire, resultats et journaux",
    ]

    return {
        "couches": couches,
        "couche_1": couches[0],
        "couche_2": couches[1],
        "couche_3": couches[2],
        "couche_4": "Analyseurs IA: yeux et levres",
        "couche_5": couches[5],
    }


@router.post("/deepfake/analyser-video")
async def analyser_video(video: UploadFile = File(...)) -> dict:
    """Point d'entree pour recevoir une video a analyser."""
    contenu = await video.read()
    service = ServiceDeepfake()

    resultat = service.analyser_fichier(
        nom_fichier=video.filename or "video_sans_nom",
        type_contenu=video.content_type or "application/octet-stream",
        taille_octets=len(contenu)
    ).vers_json()

    resultat["filename"] = video.filename
    resultat["content_type"] = video.content_type
    resultat["score_suspicion"] = None

    return resultat
