from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.gateway import router as gateway_router


def creer_application() -> FastAPI:
    app = FastAPI(
        title="Sentinelle Numerique - DeepfakeVideo",
        description="API de base pour recevoir des videos et exposer les routes de la passerelle.",
        version="0.1.0"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(gateway_router)

    @app.get("/")
    def accueil() -> dict[str, str]:
        """Route racine minimale pour confirmer que le backend demarre."""
        return {
            "message": "Bienvenue sur l'API Sentinelle Numerique ABdoul",
            "documentation": "/docs",
        }

    return app


app = creer_application()
