# DeepfakeVideo

Plateforme de detection de videos deepfake pour le projet Sentinelle Numerique.

## Architecture generale

Le flux principal est :

```text
Dashboard -> API Gateway FastAPI -> ServiceDeepfake -> Analyseurs IA -> ResultatAnalyse JSON
```

- Le dashboard envoie une courte video au backend.
- L'API Gateway gere les routes et transmet la demande au service.
- `ServiceDeepfake` coordonne les modules d'analyse.
- L'analyse des yeux utilisera MediaPipe plus tard.
- L'analyse des levres utilisera SyncNet ou un placeholder temporaire.
- Le resultat est retourne sous forme JSON avec un score final et un niveau de suspicion.

## Lancement local prevu

Installer les dependances backend :

```bash
pip install -r backend/requirements.txt
```

Lancer l'API FastAPI depuis la racine du projet :

```bash
uvicorn backend.app.main:app --reload
```

## Documentation

- `docs/architecture.md` : description de l'architecture globale.
- `docs/api_gateway.md` : role de l'API Gateway et integration avec `ServiceDeepfake`.
