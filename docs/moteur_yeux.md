# Moteur de detection des clignements

## Objectif

Le moteur yeux analyse une video afin d'estimer si le comportement des
clignements semble naturel ou suspect. L'idee est simple : une video synthetique
peut presenter peu de clignements, des clignements trop reguliers ou un rythme
anormal.

## Principe technique

Le module `AnalyseurClignements` suit ces etapes :

1. Ouvrir la video avec OpenCV.
2. Lire les images une par une.
3. Detecter les points du visage avec MediaPipe FaceMesh.
4. Recuperer les points des deux yeux.
5. Calculer l'ouverture de chaque oeil avec la formule Eye Aspect Ratio.
6. Compter un clignement lorsque l'oeil reste ferme pendant au moins deux images.
7. Convertir le rythme de clignement en score de suspicion.

## Eye Aspect Ratio

L'Eye Aspect Ratio compare l'ouverture verticale de l'oeil a sa largeur
horizontale.

```text
EAR = (distance_verticale_1 + distance_verticale_2) / (2 * distance_horizontale)
```

Quand l'oeil est ouvert, ce ratio est plus grand. Quand l'oeil se ferme, ce ratio
diminue. Dans notre implementation, un oeil est considere ferme si son ouverture
moyenne descend sous le seuil `0.20`.

## Score de suspicion

Le score est compris entre `0` et `100`.

```text
0 a 39   : faible suspicion
40 a 69  : suspicion moyenne
70 a 100 : suspicion elevee
```

Regles utilisees actuellement :

```text
moins de 5 clignements/minute  -> 85
5 a 9 clignements/minute       -> 60
10 a 30 clignements/minute     -> 25
plus de 30 clignements/minute  -> 70
```

Cette premiere version est volontairement simple et explicable. Elle pourra etre
amelioree avec plus de videos de test et des seuils ajustes experimentalement.

## Fichier principal

```text
backend/app/services/analyseur_clignements.py
```

## Tests

Les tests verifient :

- le calcul Eye Aspect Ratio ;
- le seuil de fermeture de l'oeil ;
- les regles de score ;
- le refus d'un fichier video inexistant.

Commande :

```bash
python -m pytest tests/test_analyseur_clignements.py
```
