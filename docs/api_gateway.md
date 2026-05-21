# API Gateway

## Role

L'API Gateway est la porte d'entree du backend FastAPI. Elle recoit les demandes du dashboard, appelle la couche service et renvoie une reponse JSON au client.

## Responsabilites

- recevoir la video envoyee par l'utilisateur ;
- verifier les informations de base de la requete ;
- appeler `ServiceDeepfake` pour lancer l'analyse ;
- retourner un `ResultatAnalyse` au format JSON ;
- eviter de contenir la logique detaillee d'analyse IA.

## Integration avec ServiceDeepfake

La route d'analyse doit simplement transmettre le chemin ou le fichier video au service :

```python
service = ServiceDeepfake()
resultat = service.analyser_video(chemin_video)
return resultat.to_dict()
```

Cette structure permet a Bougna de travailler sur les routes FastAPI pendant qu'Abdoul travaille sur la couche architecture/service.

## Reponse JSON attendue

Exemple de reponse :

```json
{
  "nom_fichier": "video_test.mp4",
  "score_yeux": 0.35,
  "score_levres": 0.4,
  "score_final": 0.38,
  "niveau": "faible",
  "statut": "termine",
  "message": "Analyse realisee avec les modules temporaires.",
  "horodatage": "2026-05-21T18:30:00+00:00"
}
```

## Evolution prevue

- remplacer le placeholder des yeux par une analyse MediaPipe ;
- remplacer le placeholder des levres par SyncNet ou un module temporaire valide ;
- brancher le calculateur de score final ;
- ajouter des tests d'integration sur la route d'analyse.
