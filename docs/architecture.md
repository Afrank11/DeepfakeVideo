# Architecture Sentinelle Numerique

## Objectif

Sentinelle Numerique analyse une courte video envoyee par un utilisateur et retourne un score de suspicion indiquant si la video peut etre generee par IA ou etre un deepfake.

Le module d'Abdoul concerne la couche architecture et service qui relie l'API Gateway aux futurs modules d'analyse IA.

## Flux principal

```text
Dashboard
    -> API Gateway FastAPI
        -> ServiceDeepfake
            -> AnalyseurClignements (MediaPipe plus tard)
            -> AnalyseurLevres (SyncNet ou placeholder plus tard)
            -> CalculateurScore
        -> ResultatAnalyse JSON
```

## Roles des composants

### Dashboard

Le dashboard permet a l'utilisateur d'envoyer une video courte et d'afficher le score final retourne par le backend.

### API Gateway

L'API Gateway recoit les requetes HTTP, gere les routes FastAPI et transmet la video a la couche service. Elle ne doit pas contenir la logique metier d'analyse deepfake.

### ServiceDeepfake

`ServiceDeepfake` est l'orchestrateur. Il coordonne les modules suivants :

- `AnalyseurClignements` : analysera les clignements des yeux avec MediaPipe.
- `AnalyseurLevres` : analysera la synchronisation labiale avec SyncNet ou un placeholder temporaire.
- `CalculateurScore` : combinera les scores partiels pour produire le score final.

Cette separation permet de modifier les analyseurs IA sans changer les routes de l'API Gateway.

### ResultatAnalyse

`ResultatAnalyse` represente la reponse standard retournee au format JSON apres une analyse :

- `nom_fichier`
- `score_yeux`
- `score_levres`
- `score_final`
- `niveau`
- `statut`
- `message`
- `horodatage`

## Organisation microservice-style

Le projet garde une organisation inspiree microservices :

- les routes restent dans la couche API ;
- l'orchestration reste dans la couche services ;
- les objets de reponse restent dans la couche models ;
- les analyseurs IA peuvent evoluer comme modules independants.
