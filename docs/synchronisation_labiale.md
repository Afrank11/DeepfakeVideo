# Synchronisation labiale

## Objectif

Le module de synchronisation labiale analyse si la voix entendue dans une video
correspond aux mouvements de la bouche de la personne visible. Dans le projet
Sentinelle Numerique, ce module produit un score de suspicion entre 0 et 100.

Un score faible indique que le module ne detecte pas d'anomalie importante. Un
score eleve indique que la video doit etre consideree comme plus suspecte.

## Version actuelle

La version actuelle utilise la classe `AnalyseurLevres`. La methode principale est :

```python
analyser(chemin_video: str) -> float
```

Le module peut fonctionner de deux facons :

1. Si `SYNCNET_COMMAND` est configure, il execute cette commande externe et lit
   le score retourne.
2. Si aucune commande n'est configuree, il utilise un fallback par mouvement de
   la zone basse du visage.

## Configuration locale

Pour tester le mode configure sans installer le vrai modele SyncNet, le projet
fournit un adaptateur de demonstration :

```text
backend/tools/syncnet_demo.py
```

Dans PowerShell :

```powershell
$env:SYNCNET_COMMAND = "python backend/tools/syncnet_demo.py --video {video}"
```

Dans CMD :

```cmd
set SYNCNET_COMMAND=python backend/tools/syncnet_demo.py --video {video}
```

Ensuite lancer le backend depuis la racine du projet :

```bash
uvicorn backend.app.main:app --reload
```

Quand une video est analysee, `AnalyseurLevres` appelle la commande configuree,
remplace `{video}` par le chemin du fichier temporaire, puis lit le JSON retourne.

Exemple de sortie attendue :

```json
{
  "score_suspicion": 42.0,
  "mode": "syncnet_demo_adapter"
}
```

## Integration du vrai SyncNet

Le vrai SyncNet peut remplacer l'adaptateur de demonstration avec le pipeline
externe installe localement dans :

```text
C:\Tools\syncnet_python
```

Le projet ne versionne pas le modele SyncNet, car le fichier est volumineux. Il
versionne seulement l'adaptateur :

```text
backend/tools/syncnet_pipeline_adapter.py
```

Dans le fichier `.env` local, utiliser :

```text
SYNCNET_COMMAND=python backend/tools/syncnet_pipeline_adapter.py --video {video}
```

L'adaptateur lance d'abord `run_pipeline.py` pour detecter et recadrer le visage,
puis `run_syncnet.py` pour calculer :

- `AV offset` : decalage audio/video en frames ;
- `Confidence` : confiance de SyncNet dans la synchronisation ;
- `score_suspicion` : score entre 0 et 100 calcule pour notre application.

La commande doit retourner un nombre ou un JSON contenant l'une des cles
suivantes :

```text
score_suspicion
score
suspicion
```

Exemple de sortie du pipeline reel :

```json
{
  "score_suspicion": 54.66,
  "mode": "syncnet_reel_pipeline",
  "offset": -3.0,
  "confidence": 6.584,
  "message": "Score calcule avec le pipeline reel SyncNet."
}
```

La logique du vrai modele sera :

1. Extraire l'audio de la video.
2. Detecter la region de la bouche et des levres dans les images.
3. Comparer les mouvements visuels de la bouche avec l'audio.
4. Attribuer un score de suspicion eleve si l'audio et les levres sont mal
   synchronises.

Le fichier `backend/app/services/analyseur_levres.py` contient deja les methodes
necessaires pour construire la commande, l'executer, lire la sortie et normaliser
le score entre 0 et 100.

Remarque : sur CPU, le pipeline reel peut prendre plus d'une minute pour une
video courte. C'est normal, car il doit detecter le visage image par image avant
de comparer les levres et l'audio.
