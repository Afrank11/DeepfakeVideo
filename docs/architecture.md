# Architecture Sentinelle Numerique

## Objectif

Sentinelle Numerique analyse une courte video envoyee par un utilisateur et retourne un score de suspicion indiquant si la video peut etre generee par IA ou etre un deepfake.

Le module d'Abdoul concerne la couche architecture et service qui relie l'API Gateway aux futurs modules d'analyse IA.

## Flux principal

```text
Dashboard
    -> API Gateway FastAPI
        -> ServiceDeepfake
            -> AnalyseurClignements (MediaPipe)
            -> AnalyseurLevres
                -> API SyncNet
                    -> Pipeline SyncNet
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

- `AnalyseurClignements` : analyse les clignements des yeux avec MediaPipe.
- `AnalyseurLevres` : appelle une API SyncNet lorsque `SYNCNET_API_URL` est configuree, puis utilise un fallback local si l'API est absente.
- `backend.syncnet_api` : expose le pipeline SyncNet reel sous forme de microservice FastAPI.
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
- les analyseurs IA peuvent evoluer comme modules independants ;
- la synchronisation labiale peut etre executee comme une API separee du backend principal.
