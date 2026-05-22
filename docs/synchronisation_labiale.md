# Synchronisation labiale

## Objectif

Le module de synchronisation labiale analyse si la voix entendue dans une video
correspond aux mouvements de la bouche de la personne visible. Dans le projet
Sentinelle Numerique, ce module produit un score de suspicion entre 0 et 100.

Un score faible indique que le module ne detecte pas d'anomalie importante. Un
score eleve indique que la video doit etre consideree comme plus suspecte.

## Version actuelle

La premiere version utilise un espace reserve propre dans la classe
`AnalyseurLevres`. La methode principale est :

```python
analyser(chemin_video: str) -> float
```

Pour une video existante, le module renvoie actuellement un score provisoire de
`25.0`. Si le fichier video n'existe pas, il renvoie `100.0`, car l'analyse ne
peut pas etre realisee correctement.

## Integration future de SyncNet

SyncNet ou un modele equivalent sera utilise plus tard pour comparer la piste
audio avec les mouvements visibles de la bouche. La logique future sera :

1. Extraire l'audio de la video.
2. Detecter la region de la bouche et des levres dans les images.
3. Comparer les mouvements visuels de la bouche avec l'audio.
4. Attribuer un score de suspicion eleve si l'audio et les levres sont mal
   synchronises.

Le fichier `backend/app/services/analyseur_levres.py` contient deja une methode
interne `_preparer_entrees_syncnet` pour marquer l'emplacement de cette future
preparation.
