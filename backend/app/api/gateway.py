from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, UploadFile

from ..models.resultat_analyse import ResultatAnalyse
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

    validation = service.analyser_fichier(
        nom_fichier=video.filename or "video_sans_nom",
        type_contenu=video.content_type or "application/octet-stream",
        taille_octets=len(contenu)
    )

    if validation.statut == "rejete":
        return _ajouter_metadonnees_upload(
            validation.vers_json(),
            video
        )

    dossier_temporaire = Path("videos_temporaires")
    dossier_temporaire.mkdir(exist_ok=True)

    extension = Path(video.filename or "video.mp4").suffix or ".mp4"
    chemin_video = dossier_temporaire / f"{uuid4().hex}{extension}"

    fichier_temporaire_supprime = False

    try:
        chemin_video.write_bytes(contenu)
        resultat = service.analyser_video(str(chemin_video)).vers_json()
    except Exception as erreur:
        resultat = ResultatAnalyse(
            nom_fichier=video.filename or "video_sans_nom",
            score_yeux=0.0,
            score_levres=0.0,
            score_final=100.0,
            niveau="Erreur",
            statut="erreur",
            message=f"Analyse impossible: {erreur}",
        ).vers_json()
    finally:
        if chemin_video.exists():
            chemin_video.unlink()
            fichier_temporaire_supprime = True

    return _ajouter_metadonnees_upload(
        resultat,
        video,
        taille_octets=len(contenu),
        fichier_temporaire_supprime=fichier_temporaire_supprime,
    )


def _ajouter_metadonnees_upload(
    resultat: dict,
    video: UploadFile,
    taille_octets: int | None = None,
    fichier_temporaire_supprime: bool | None = None,
) -> dict:
    resultat["filename"] = video.filename
    resultat["content_type"] = video.content_type
    resultat["score_suspicion"] = resultat.get("score_final")
    resultat["upload"] = {
        "recu": True,
        "nom_original": video.filename,
        "type_contenu": video.content_type,
        "taille_octets": taille_octets,
        "fichier_temporaire_supprime": fichier_temporaire_supprime,
    }
    return resultat
