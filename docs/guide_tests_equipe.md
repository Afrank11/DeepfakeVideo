# Guide de test equipe - DeepfakeVideo

Ce guide aide chaque membre a recuperer le projet, lancer le backend, ouvrir le
dashboard, executer les tests et comprendre sa partie. Il fonctionne meme sans
installer le vrai SyncNet : dans ce cas, le backend utilise un fallback local
pour la synchronisation labiale.

## Prerequis communs

Chaque membre doit avoir :

- Git
- Python 3.11 de preference
- VS Code ou un editeur equivalent
- Un terminal PowerShell ou CMD

Depuis le dossier ou ils veulent mettre le projet :

```powershell
git clone https://github.com/Afrank11/DeepfakeVideo.git
cd DeepfakeVideo
```

Si le projet est deja clone :

```powershell
cd DeepfakeVideo
git pull origin main
```

Creer et activer un environnement virtuel :

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

Installer les dependances :

```powershell
python -m pip install --upgrade pip
pip install -r backend/requirements.txt
```

Verifier les tests :

```powershell
python -m pytest
```

Resultat attendu :

```text
17 passed
```

Lancer l'API Gateway principale :

```powershell
uvicorn backend.app.main:app --reload --port 8001
```

Ouvrir la documentation API :

```text
http://127.0.0.1:8001/docs
```

Ouvrir le dashboard :

```text
dashboard/index.html
```

Le dashboard essaie de contacter le backend sur `8000`, puis `8001`.

## Mode sans SyncNet reel

Pour les membres qui n'ont pas SyncNet installe, ne pas lancer le microservice
SyncNet. Le backend fonctionnera quand meme avec :

- MediaPipe pour les clignements si l'installation locale le permet ;
- fallback mouvement pour les levres si l'API SyncNet n'est pas disponible ;
- calcul du score final ;
- dashboard et upload video.

Ce mode est suffisant pour etudier l'architecture, tester les routes et
comprendre le flux complet.

## Mode avec API SyncNet

Sur la machine qui a le vrai SyncNet installe dans `C:\Tools\syncnet_python`,
lancer le microservice SyncNet :

```powershell
uvicorn backend.syncnet_api.main:app --reload --port 8010
```

Dans un autre terminal, lancer l'API Gateway :

```powershell
uvicorn backend.app.main:app --reload --port 8001
```

Dans `.env`, utiliser :

```text
SYNCNET_API_URL=http://127.0.0.1:8010/api/v1/syncnet/analyser-levres
SYNCNET_API_KEY=
```

Flux attendu :

```text
Dashboard -> API Gateway -> AnalyseurLevres -> API SyncNet -> Pipeline SyncNet
```

## Tests a connaitre pour la soutenance

Tests generiques :

```powershell
python -m pytest
```

Ce test verifie globalement les modules principaux.

Tests API :

```powershell
python -m pytest tests/test_api.py
```

Ces tests verifient les routes `health`, `architecture`, upload video et rejet
d'un fichier non video.

Tests moteur yeux :

```powershell
python -m pytest tests/test_analyseur_clignements.py
```

Ces tests couvrent les limites principales du score yeux : video absente,
nombre d'images nul, score entre 0 et 100, rythme de clignements.

Tests synchronisation labiale :

```powershell
python -m pytest tests/test_analyseur_levres.py
```

Ces tests couvrent le fallback local, le score configure par commande, le score
JSON et le nouveau mode API SyncNet.

Boite noire :

Tester depuis le dashboard sans lire le code :

1. Ouvrir le dashboard.
2. Choisir une video.
3. Cliquer sur analyser.
4. Verifier que le score final et le niveau s'affichent.
5. Tester aussi un fichier `.txt` depuis Swagger pour verifier le rejet.

Boite grise :

Lire la reponse JSON dans Swagger `/docs` et verifier :

- `details.yeux`
- `details.levres`
- `score_final`
- `upload.fichier_temporaire_supprime`

Tests aux limites :

- Fichier non video.
- Video introuvable dans les tests unitaires.
- Video illisible ou tres courte.
- API SyncNet indisponible.
- Score inferieur a 0 ou superieur a 100 normalise dans les tests.

## Nkwawya - Synchronisation labiale

Objectif :

Comprendre et presenter comment la synchronisation labiale est appelee par API.

Fichiers a etudier :

- `backend/app/services/analyseur_levres.py`
- `backend/syncnet_api/main.py`
- `backend/tools/syncnet_pipeline_adapter.py`
- `docs/synchronisation_labiale.md`
- `tests/test_analyseur_levres.py`

Commandes importantes :

```powershell
python -m pytest tests/test_analyseur_levres.py
uvicorn backend.syncnet_api.main:app --reload --port 8010
uvicorn backend.app.main:app --reload --port 8001
```

Ce qu'il doit pouvoir expliquer :

- `AnalyseurLevres` cherche d'abord `SYNCNET_API_URL`.
- Si l'API SyncNet repond, le score vient de l'API.
- Si l'API ne repond pas, le backend garde un fallback local.
- Le microservice `backend.syncnet_api` encapsule le vrai pipeline SyncNet.
- Le score levres est normalise entre 0 et 100.

Prompt Codex pour Nkwawya :

```text
Tu es mon assistant Codex pour le projet DeepfakeVideo. Ma partie est la synchronisation labiale. Aide-moi a comprendre et tester backend/app/services/analyseur_levres.py, backend/syncnet_api/main.py, backend/tools/syncnet_pipeline_adapter.py et tests/test_analyseur_levres.py. Je dois expliquer comment l'API Gateway appelle une API SyncNet, comment le fallback fonctionne sans SyncNet reel, comment les scores sont lus depuis JSON, et comment les tests prouvent que le module marche. Commence par lire ces fichiers, puis donne-moi une explication claire, des commandes de test, et les questions probables du professeur avec les reponses.
```

## Bougna - Product Owner et API Gateway

Objectif :

Comprendre le besoin utilisateur, le backlog et la passerelle API.

Fichiers a etudier :

- `backend/app/api/gateway.py`
- `backend/app/main.py`
- `backend/app/services/service_deepfake.py`
- `docs/api_gateway.md`
- `docs/architecture.md`
- `README.md`

Commandes importantes :

```powershell
python -m pytest tests/test_api.py
uvicorn backend.app.main:app --reload --port 8001
```

Ce qu'elle doit pouvoir expliquer :

- Le dashboard envoie une video a `/api/v1/deepfake/analyser-video`.
- L'API Gateway valide le fichier, cree un fichier temporaire, appelle le service, puis supprime le temporaire.
- La route `/api/v1/architecture` explique les couches.
- La route `/api/v1/health` sert a verifier que l'API est active.
- Le Product Owner priorise : flux complet avant precision parfaite.

Prompt Codex pour Bougna :

```text
Tu es mon assistant Codex pour le projet DeepfakeVideo. Ma partie couvre Product Owner, backlog et API Gateway. Aide-moi a comprendre backend/app/api/gateway.py, backend/app/main.py, backend/app/services/service_deepfake.py, docs/api_gateway.md et docs/architecture.md. Je dois expliquer le besoin utilisateur, le flux Dashboard -> API Gateway -> services -> JSON, la validation des uploads, les routes, et la logique Scrum/priorisation. Donne-moi les commandes pour tester, une explication fichier par fichier, et une mini fiche de revision pour la soutenance.
```

## Abdoul - Partie 1 API Gateway et architecture

Objectif :

Presenter l'architecture technique et le role de la passerelle.

Fichiers a etudier :

- `backend/app/main.py`
- `backend/app/api/gateway.py`
- `backend/app/models/resultat_analyse.py`
- `docs/architecture.md`
- `docs/api_gateway.md`

Commandes importantes :

```powershell
python -m pytest tests/test_api.py
uvicorn backend.app.main:app --reload --port 8001
```

Ce qu'il doit pouvoir expliquer :

- FastAPI expose les routes HTTP.
- CORS autorise le dashboard a appeler le backend.
- `ResultatAnalyse` standardise la reponse JSON.
- L'API Gateway ne fait pas l'analyse IA elle-meme.
- Elle transmet au service metier et renvoie le resultat.

Prompt Codex pour Abdoul partie 1 :

```text
Tu es mon assistant Codex pour le projet DeepfakeVideo. Ma premiere partie est API Gateway et architecture. Aide-moi a comprendre backend/app/main.py, backend/app/api/gateway.py, backend/app/models/resultat_analyse.py, docs/architecture.md et docs/api_gateway.md. Je dois expliquer pourquoi on utilise une API Gateway, comment FastAPI recoit une video, comment les erreurs sont gerees, et comment la reponse JSON est structuree. Donne-moi des commandes de test, une explication claire et des questions/reponses probables.
```

## Abdoul - Partie 2 tableau de bord et integration

Objectif :

Comprendre comment le dashboard consomme l'API et affiche les resultats.

Fichiers a etudier :

- `dashboard/index.html`
- `dashboard/style.css`
- `dashboard/script.js`
- `backend/app/api/gateway.py`

Commandes importantes :

```powershell
uvicorn backend.app.main:app --reload --port 8001
```

Puis ouvrir :

```text
dashboard/index.html
```

Ce qu'il doit pouvoir expliquer :

- `index.html` contient le formulaire upload et les zones de resultat.
- `script.js` envoie la video avec `FormData`.
- Le dashboard lit `score_yeux`, `score_levres`, `score_final`, `niveau` et `details`.
- Le dashboard affiche l'etat upload, analyse et nettoyage.
- Le dashboard essaie les ports `8000` puis `8001`.

Prompt Codex pour Abdoul partie 2 :

```text
Tu es mon assistant Codex pour le projet DeepfakeVideo. Ma deuxieme partie est l'integration dashboard/backend. Aide-moi a comprendre dashboard/index.html, dashboard/style.css, dashboard/script.js et la route backend/app/api/gateway.py. Je dois expliquer comment le formulaire upload fonctionne, comment fetch envoie la video a FastAPI, comment les resultats sont affiches, comment l'etat API est detecte, et comment tester le tout manuellement. Donne-moi une explication ligne par ligne des zones importantes et une fiche de revision.
```

## Kos - Tableau de bord utilisateur

Objectif :

Presenter l'interface utilisateur et le parcours d'analyse.

Fichiers a etudier :

- `dashboard/index.html`
- `dashboard/style.css`
- `dashboard/script.js`
- `README.md`

Commandes importantes :

```powershell
uvicorn backend.app.main:app --reload --port 8001
```

Puis ouvrir :

```text
dashboard/index.html
```

Ce qu'il doit pouvoir expliquer :

- L'utilisateur choisit une video dans le formulaire.
- Le bouton analyser declenche l'appel API.
- Les statuts montrent si la video est envoyee, analysee et nettoyee.
- Les cartes expliquent les scores yeux, levres et final.
- Le niveau de suspicion rend le resultat comprehensible.

Prompt Codex pour Kos :

```text
Tu es mon assistant Codex pour le projet DeepfakeVideo. Ma partie est le tableau de bord utilisateur. Aide-moi a comprendre dashboard/index.html, dashboard/style.css et dashboard/script.js. Je dois expliquer le parcours utilisateur, le choix de fichier, le bouton analyser, les statuts, les scores, le niveau de suspicion, et comment l'interface consomme l'API FastAPI. Donne-moi les commandes pour lancer le backend, les tests manuels a faire, et une fiche simple pour presenter cette partie au professeur.
```

## Commandes de secours

Si le port `8000` donne une erreur Windows :

```powershell
uvicorn backend.app.main:app --reload --port 8001
```

Si MediaPipe pose probleme :

```powershell
pip uninstall mediapipe -y
pip install mediapipe==0.10.21
```

Si les tests ne trouvent pas le module `backend` :

```powershell
cd DeepfakeVideo
python -m pytest
```

Si l'environnement virtuel n'est pas active :

```powershell
.\.venv\Scripts\activate
```
