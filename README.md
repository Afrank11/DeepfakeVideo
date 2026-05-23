# DeepfakeVideo

Plateforme de detection de videos deepfake pour le projet Sentinelle Numerique.

## Architecture generale

Le flux principal est :

```text
Dashboard utilisateur
        |
        v
API Gateway FastAPI
        |
        v
ServiceDeepfake
        |
        +--> AnalyseurClignements (MediaPipe)
        +--> AnalyseurLevres -> API SyncNet
        +--> CalculateurScore
        |
        v
ResultatAnalyse JSON
```

## Lancement local

Installer les dependances backend :

```bash
pip install -r backend/requirements.txt
```

Lancer l'API FastAPI depuis la racine du projet :

```bash
uvicorn backend.app.main:app --reload
```

Pour utiliser SyncNet en mode API, lancer aussi le microservice SyncNet :

```bash
uvicorn backend.syncnet_api.main:app --reload --port 8010
```

Puis configurer le backend principal avec :

```text
SYNCNET_API_URL=http://127.0.0.1:8010/api/v1/syncnet/analyser-levres
```

Ou depuis le dossier `backend` :

```bash
cd backend
uvicorn app.main:app --reload
```

Documentation FastAPI :

```text
http://127.0.0.1:8000/docs
```

## Lancement du dashboard

Demarrer d'abord l'API FastAPI, puis ouvrir le fichier suivant dans le
navigateur :

```text
dashboard/index.html
```

Le tableau de bord envoie la video selectionnee vers :

```text
http://127.0.0.1:8000/api/v1/deepfake/analyser-video
```

La reponse JSON est utilisee pour afficher `score_yeux`, `score_levres`,
`score_final`, `niveau` et `message`.

## Routes disponibles

```text
GET  /
GET  /api/v1/health
GET  /api/v1/architecture
POST /api/v1/deepfake/analyser-video

Microservice SyncNet :

GET  /health
POST /api/v1/syncnet/analyser-levres
```

## Organisation du travail

- API Gateway & Architecture : routes, structure microservice, documentation.
- Moteur detection yeux : MediaPipe et calcul des clignements.
- Synchro labiale : API SyncNet ou fallback local.
- Tableau de bord : interface utilisateur et affichage du score.

## Documentation

- `docs/architecture.md` : description de l'architecture globale.
- `docs/api_gateway.md` : role de l'API Gateway.
- `docs/moteur_yeux.md` : fonctionnement du moteur de clignements.
- `docs/synchronisation_labiale.md` : configuration SyncNet API/commande.
- `docs/guide_tests_equipe.md` : guide de test et prompts Codex pour l'equipe.
