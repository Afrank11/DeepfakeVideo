from pathlib import Path


class AnalyseurLevres:
    """Analyseur responsable de la synchronisation labiale.

    Version actuelle : espace reserve structure pour SyncNet.
    Version future : SyncNet comparera les mouvements des levres avec l'audio.
    """

    SCORE_PROVISOIRE = 25.0
    SCORE_VIDEO_INTROUVABLE = 100.0

    def analyser(self, chemin_video: str) -> float:
        """Retourne un score de suspicion entre 0 et 100."""
        if not Path(chemin_video).is_file():
            return self.SCORE_VIDEO_INTROUVABLE

        donnees_syncnet = self._preparer_entrees_syncnet(chemin_video)
        return self._calculer_score_syncnet(donnees_syncnet)

    def _preparer_entrees_syncnet(self, chemin_video: str) -> dict:
        """Prepare les donnees qui seront envoyees plus tard a SyncNet."""
        return {
            "chemin_video": chemin_video,
            "chemin_audio": None,
            "images_bouche": [],
        }

    def _calculer_score_syncnet(self, donnees_syncnet: dict) -> float:
        """Retourne un score provisoire en attendant le vrai modele SyncNet."""
        return self.SCORE_PROVISOIRE