# DeepfakeVideo

Module "Specialiste Deepfake Video" du projet Sentinelle Numerique.

## Partie 1 - API Gateway & Architecture

Cette premiere version met en place la passerelle API de base. Elle ne fait pas
encore la vraie detection deepfake, mais elle definit le point d'entree que les
autres modules vont utiliser.

Flux prevu par le livrable :

```text
Dashboard utilisateur
        |
        v
Passerelle API FastAPI
        |
        v
ServiceDeepfake
        |
        +--> AnalyseurClignements
        +--> AnalyseurLevres
        |
        v
ResultatAnalyse JSON
```

## Lancer le backend

```bash
cd backend
uvicorn app.main:app --reload
```

Ensuite ouvrir :

```text
http://127.0.0.1:8000/docs
```

## Routes disponibles

```text
GET  /api/v1/health
GET  /api/v1/architecture
POST /api/v1/deepfake/analyser-video
```

## Organisation du travail

- API Gateway & Architecture : routes, structure microservice, documentation.
- Moteur detection yeux : MediaPipe et calcul des clignements.
- Synchro labiale : module provisoire, puis SyncNet ou alternative.
- Tableau de bord : interface utilisateur et affichage du score.
