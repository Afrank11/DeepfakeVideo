import json
import os
import shlex
import subprocess
from pathlib import Path


class AnalyseurLevres:
    """Analyseur responsable de la synchronisation labiale.

    SyncNet peut etre branche par une commande externe qui retourne un score.
    Sans commande configuree, le module garde un score provisoire stable.
    """

    SCORE_PROVISOIRE = 25.0
    SCORE_VIDEO_INTROUVABLE = 100.0
    TIMEOUT_SYNCNET_SECONDES = 30

    def __init__(self, commande_syncnet: list[str] | None = None):
        self.commande_syncnet = commande_syncnet or self._lire_commande_syncnet()

    def analyser(self, chemin_video: str) -> float:
        """Retourne un score de suspicion entre 0 et 100."""
        if not Path(chemin_video).is_file():
            return self.SCORE_VIDEO_INTROUVABLE

        donnees_syncnet = self._preparer_entrees_syncnet(chemin_video)
        return self._calculer_score_syncnet(donnees_syncnet)

    def _preparer_entrees_syncnet(self, chemin_video: str) -> dict:
        """Prepare les donnees qui seront envoyees plus tard a SyncNet."""
        chemin_audio = self._extraire_audio(chemin_video)
        images_bouche = self._detecter_images_bouche(chemin_video)

        return {
            "chemin_video": chemin_video,
            "chemin_audio": chemin_audio,
            "images_bouche": images_bouche,
        }

    def _extraire_audio(self, chemin_video: str) -> None:
        """Reserve l'emplacement de l'extraction audio future."""
        return None

    def _detecter_images_bouche(self, chemin_video: str) -> list:
        """Reserve l'emplacement de la detection future de la bouche."""
        return []

    def _calculer_score_syncnet(self, donnees_syncnet: dict) -> float:
        """Retourne le score SyncNet ou un score provisoire si non configure."""
        if not self.commande_syncnet:
            return self.SCORE_PROVISOIRE

        score_brut = self._executer_commande_syncnet(donnees_syncnet)
        if score_brut is None:
            return self.SCORE_PROVISOIRE

        return self._normaliser_score(score_brut)

    def _lire_commande_syncnet(self) -> list[str] | None:
        """Lit la commande SyncNet depuis la variable d'environnement."""
        commande = os.getenv("SYNCNET_COMMANDE") or os.getenv("SYNCNET_COMMAND")
        if not commande:
            return None
        return shlex.split(commande)

    def _executer_commande_syncnet(self, donnees_syncnet: dict) -> float | None:
        """Execute SyncNet et extrait un score numerique de sa sortie."""
        commande = self._construire_commande_syncnet(donnees_syncnet["chemin_video"])

        try:
            resultat = subprocess.run(
                commande,
                capture_output=True,
                check=False,
                text=True,
                timeout=self.TIMEOUT_SYNCNET_SECONDES,
            )
        except (OSError, subprocess.TimeoutExpired):
            return None

        if resultat.returncode != 0:
            return None

        return self._extraire_score_sortie_syncnet(resultat.stdout)

    def _construire_commande_syncnet(self, chemin_video: str) -> list[str]:
        """Ajoute le chemin video a la commande SyncNet configuree."""
        commande = []
        chemin_deja_place = False

        for morceau in self.commande_syncnet:
            if "{video}" in morceau:
                commande.append(morceau.replace("{video}", chemin_video))
                chemin_deja_place = True
            else:
                commande.append(morceau)

        if not chemin_deja_place:
            commande.append(chemin_video)

        return commande

    def _extraire_score_sortie_syncnet(self, sortie: str) -> float | None:
        """Accepte une sortie JSON ou un nombre simple."""
        sortie = sortie.strip()
        if not sortie:
            return None

        try:
            donnees = json.loads(sortie)
        except json.JSONDecodeError:
            return self._convertir_en_float(sortie)

        if isinstance(donnees, int | float):
            return self._convertir_en_float(donnees)

        if isinstance(donnees, dict):
            for cle in ("score_suspicion", "score", "suspicion"):
                if cle in donnees:
                    return self._convertir_en_float(donnees[cle])

        return None

    def _convertir_en_float(self, valeur) -> float | None:
        """Convertit une valeur SyncNet en nombre utilisable."""
        try:
            return float(valeur)
        except (TypeError, ValueError):
            return None

    def _normaliser_score(self, score_brut: float) -> float:
        """Ramene un score dans l'intervalle accepte de 0 a 100."""
        return max(0.0, min(100.0, score_brut))
