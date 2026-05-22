from pathlib import Path


class AnalyseurClignements:
    """Analyse les clignements d'yeux dans une video.

    Cette premiere version sert de base stable pour le moteur yeux. Les prochains
    commits ajouteront OpenCV, MediaPipe FaceMesh et le calcul Eye Aspect Ratio.
    """

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
