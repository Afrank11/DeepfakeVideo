from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, File, UploadFile

from backend.tools.syncnet_pipeline_adapter import analyser


app = FastAPI(
    title="SyncNet API - Sentinelle Numerique",
    description="Microservice HTTP qui encapsule le pipeline SyncNet reel.",
    version="0.1.0",
)


@app.get("/health")
def verifier_sante() -> dict:
    """Indique que le microservice SyncNet est disponible."""
    return {
        "status": "ok",
        "service": "syncnet-api",
        "message": "Microservice SyncNet operationnel",
    }


@app.post("/api/v1/syncnet/analyser-levres")
async def analyser_levres(video: UploadFile = File(...)) -> dict:
    """Recoit une video et retourne le score de synchronisation labiale."""
    dossier_temporaire = Path("videos_temporaires") / "syncnet_api"
    dossier_temporaire.mkdir(parents=True, exist_ok=True)

    extension = Path(video.filename or "video.mp4").suffix or ".mp4"
    chemin_video = dossier_temporaire / f"{uuid4().hex}{extension}"

    try:
        chemin_video.write_bytes(await video.read())
        resultat = analyser(
            _ArgumentsSyncNet(
                video=str(chemin_video),
                reference=chemin_video.stem,
            )
        )
        resultat["service"] = "syncnet-api"
        return resultat
    except Exception as erreur:
        return {
            "score_suspicion": 50.0,
            "mode": "syncnet_api_erreur",
            "service": "syncnet-api",
            "message": f"Erreur API SyncNet: {erreur}",
        }
    finally:
        if chemin_video.exists():
            chemin_video.unlink()


class _ArgumentsSyncNet:
    """Objet simple compatible avec l'adaptateur CLI SyncNet."""

    def __init__(self, video: str, reference: str):
        self.video = video
        self.reference = reference
        self.syncnet_dir = r"C:\Tools\syncnet_python"
        self.data_dir = r"C:\Tools\syncnet_python\data\api_pipeline"
        self.pipeline_timeout = 240
        self.syncnet_timeout = 180
