from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.gateway import router as gateway_router


def creer_application() -> FastAPI:
    app = FastAPI(
        title="Sentinelle Numerique - API Gateway",
        description="Passerelle API du module Specialiste Deepfake Video",
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

    return app


app = creer_application()
