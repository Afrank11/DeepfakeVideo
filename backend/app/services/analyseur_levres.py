from pathlib import Path


class AnalyseurLevres:
    """Analyseur responsable de la synchronisation labiale.

    Version actuelle : espace reserve simple.
    Version future : SyncNet comparera les mouvements des levres avec l'audio.
    """

    SCORE_PROVISOIRE = 25.0
    SCORE_VIDEO_INTROUVABLE = 100.0

    def analyser(self, chemin_video: str) -> float:
        """Retourne un score de suspicion entre 0 et 100."""
        if not Path(chemin_video).is_file():
            return self.SCORE_VIDEO_INTROUVABLE

        self._preparer_entrees_syncnet(chemin_video)
        return self.SCORE_PROVISOIRE

    def _preparer_entrees_syncnet(self, chemin_video: str) -> None:
        """Prepare les donnees qui seront envoyees plus tard a SyncNet."""
        # SyncNet aura besoin de l'audio et des images de la bouche.
        # Cette methode garde l'emplacement de cette future preparation.
        return None
