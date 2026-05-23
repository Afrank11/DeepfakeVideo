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

## Integration future du vrai SyncNet

Le vrai SyncNet ou un modele equivalent pourra remplacer l'adaptateur de
demonstration. La commande devra simplement retourner un nombre ou un JSON
contenant l'une des cles suivantes :

```text
score_suspicion
score
suspicion
```

Exemple :

```powershell
$env:SYNCNET_COMMAND = "python C:\SyncNet\run_syncnet.py --video {video}"
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
