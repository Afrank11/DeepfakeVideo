from fastapi import FastAPI

from backend.app.api.gateway import router as gateway_router


app = FastAPI(
    title="Sentinelle Numerique - DeepfakeVideo",
    description="API de base pour recevoir des videos et exposer les routes de la passerelle.",
    version="0.1.0",
)

app.include_router(gateway_router)


@app.get("/")
def accueil() -> dict[str, str]:
    """Route racine minimale pour confirmer que le backend demarre."""
    return {
        "message": "Bienvenue sur l'API Sentinelle Numerique",
        "documentation": "/docs",
    }
