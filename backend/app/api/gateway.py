from fastapi import APIRouter, File, UploadFile

from app.services.service_deepfake import ServiceDeepfake


router = APIRouter(prefix="/api/v1", tags=["Passerelle API"])


@router.get("/health")
def verifier_etat_api() -> dict:
    return {
        "statut": "actif",
        "service": "api-gateway",
        "message": "Passerelle API operationnelle"
    }


@router.get("/architecture")
def decrire_architecture() -> dict:
    return {
        "couche_1": "Dashboard utilisateur",
        "couche_2": "Passerelle API FastAPI",
        "couche_3": "Microservice Deepfake Video",
        "couche_4": "Analyseurs IA: yeux et levres",
        "couche_5": "Stockage temporaire, resultats et journaux"
    }


@router.post("/deepfake/analyser-video")
async def analyser_video(video: UploadFile = File(...)) -> dict:
    contenu = await video.read()
    service = ServiceDeepfake()

    resultat = service.analyser_fichier(
        nom_fichier=video.filename or "video_sans_nom",
        type_contenu=video.content_type or "application/octet-stream",
        taille_octets=len(contenu)
    )

    return resultat.vers_json()
