from math import dist
from pathlib import Path


class AnalyseurClignements:
    """Analyse les clignements d'yeux dans une video.

    Cette premiere version sert de base stable pour le moteur yeux. Les prochains
    commits ajouteront OpenCV, MediaPipe FaceMesh et le calcul Eye Aspect Ratio.
    """

    OEIL_GAUCHE = (33, 160, 158, 133, 153, 144)
    OEIL_DROIT = (362, 385, 387, 263, 373, 380)

    def __init__(self, seuil_fermeture: float = 0.20):
        self.seuil_fermeture = seuil_fermeture

    def analyser(self, chemin_video: str) -> float:
        """Retourne un score de suspicion entre 0 et 100.

        Pour l'instant, le module verifie seulement que le fichier video existe.
        Un score neutre de 50 indique que l'analyse reelle n'est pas encore
        branchee.
        """
        chemin = Path(chemin_video)

        if not chemin.exists():
            raise FileNotFoundError(f"Video introuvable: {chemin_video}")

        if not chemin.is_file():
            raise ValueError(f"Le chemin donne n'est pas un fichier: {chemin_video}")

        return 50.0

    def calculer_ouverture_oeil(self, landmarks, indices_oeil: tuple[int, ...]) -> float:
        """Calcule l'ouverture d'un oeil avec la formule Eye Aspect Ratio.

        Les six indices MediaPipe representent: coin gauche, deux points du haut,
        coin droit, deux points du bas. Quand l'oeil se ferme, ce ratio diminue.
        """
        points = [(landmarks[index].x, landmarks[index].y) for index in indices_oeil]

        gauche = points[0]
        haut_1 = points[1]
        haut_2 = points[2]
        droite = points[3]
        bas_1 = points[4]
        bas_2 = points[5]

        distance_verticale_1 = dist(haut_1, bas_2)
        distance_verticale_2 = dist(haut_2, bas_1)
        distance_horizontale = dist(gauche, droite)

        if distance_horizontale == 0:
            return 0.0

        return (distance_verticale_1 + distance_verticale_2) / (
            2 * distance_horizontale
        )

    def oeil_est_ferme(self, ouverture_oeil: float) -> bool:
        return ouverture_oeil < self.seuil_fermeture

    def calculer_score(self, nombre_clignements: int, duree_secondes: float) -> float:
        """Convertit le rythme de clignement en score de suspicion.

        Score eleve = comportement plus suspect.
        Score faible = comportement plus naturel.
        """
        if duree_secondes <= 0:
            return 100.0

        clignements_par_minute = (nombre_clignements / duree_secondes) * 60

        if clignements_par_minute < 5:
            return 85.0

        if clignements_par_minute < 10:
            return 60.0

        if clignements_par_minute <= 30:
            return 25.0

        return 70.0
