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

    def __init__(
        self,
        commande_syncnet: list[str] | None = None,
        charger_env_local: bool = True,
    ):
        self.charger_env_local = charger_env_local
        self.commande_syncnet = commande_syncnet or self._lire_commande_syncnet()

    def analyser(self, chemin_video: str) -> float:
        """Retourne un score de suspicion entre 0 et 100."""
        return self.analyser_detaille(chemin_video)["score"]

    def analyser_detaille(self, chemin_video: str) -> dict:
        """Retourne le score levres avec des informations explicatives."""
        if not Path(chemin_video).is_file():
            return {
                "score": self.SCORE_VIDEO_INTROUVABLE,
                "methode": "fichier_introuvable",
                "message": "Video introuvable: score maximal par securite.",
            }

        donnees_syncnet = self._preparer_entrees_syncnet(chemin_video)
        score_syncnet = self._calculer_score_syncnet(donnees_syncnet)

        if score_syncnet is not None:
            return {
                "score": score_syncnet,
                "methode": "syncnet_configure",
                "message": "Score fourni par la commande SyncNet configuree.",
            }

        return self._score_provisoire_par_mouvement(chemin_video)

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

    def _calculer_score_syncnet(self, donnees_syncnet: dict) -> float | None:
        """Retourne le score SyncNet ou None si SyncNet n'est pas configure."""
        if not self.commande_syncnet:
            return None

        score_brut = self._executer_commande_syncnet(donnees_syncnet)
        if score_brut is None:
            return None

        return self._normaliser_score(score_brut)

    def _lire_commande_syncnet(self) -> list[str] | None:
        """Lit la commande SyncNet depuis la variable d'environnement."""
        commande = os.getenv("SYNCNET_COMMANDE") or os.getenv("SYNCNET_COMMAND")
        if self.charger_env_local:
            commande = commande or self._lire_commande_depuis_env_local()
        if not commande:
            return None
        return shlex.split(commande)

    def _lire_commande_depuis_env_local(self) -> str | None:
        """Lit SYNCNET_COMMAND depuis un fichier .env local si present."""
        chemins_possibles = [
            Path(".env"),
            Path(__file__).resolve().parents[3] / ".env",
        ]

        for chemin in chemins_possibles:
            if not chemin.is_file():
                continue

            for ligne in chemin.read_text(encoding="utf-8").splitlines():
                ligne = ligne.strip()

                if not ligne or ligne.startswith("#") or "=" not in ligne:
                    continue

                cle, valeur = ligne.split("=", 1)
                if cle.strip() in {"SYNCNET_COMMAND", "SYNCNET_COMMANDE"}:
                    return valeur.strip().strip('"').strip("'")

        return None

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

    def _score_provisoire_par_mouvement(self, chemin_video: str) -> dict:
        """Fallback en attendant SyncNet.

        Il utilise le mouvement visuel global comme approximation faible. Ce
        n'est pas une vraie synchronisation labiale, mais cela donne une reponse
        variable et explicable pour la demonstration.
        """
        try:
            import cv2
        except ImportError:
            return {
                "score": self.SCORE_PROVISOIRE,
                "methode": "placeholder",
                "message": "SyncNet et OpenCV indisponibles: score levres provisoire.",
                "mouvement_moyen": None,
            }

        capture = cv2.VideoCapture(str(chemin_video))

        if not capture.isOpened():
            return {
                "score": self.SCORE_PROVISOIRE,
                "methode": "placeholder",
                "message": "Video illisible pour le module levres: score provisoire.",
                "mouvement_moyen": None,
            }

        precedente = None
        mouvements = []
        images_lues = 0
        fps = capture.get(cv2.CAP_PROP_FPS) or 30
        pas = max(1, int(fps // 2))

        try:
            while True:
                succes, image = capture.read()

                if not succes:
                    break

                images_lues += 1

                if images_lues % pas != 0:
                    continue

                hauteur, largeur = image.shape[:2]
                zone_bouche = image[int(hauteur * 0.55):int(hauteur * 0.9), :]
                gris = cv2.cvtColor(zone_bouche, cv2.COLOR_BGR2GRAY)
                gris = cv2.resize(gris, (160, 60))

                if precedente is not None:
                    difference = cv2.absdiff(gris, precedente)
                    mouvements.append(float(difference.mean()))

                precedente = gris
        finally:
            capture.release()

        mouvement_moyen = sum(mouvements) / len(mouvements) if mouvements else 0.0

        if mouvement_moyen < 1:
            score = 68.0
        elif mouvement_moyen < 4:
            score = 55.0
        elif mouvement_moyen < 12:
            score = 42.0
        else:
            score = 30.0

        return {
            "score": score,
            "methode": "placeholder_mouvement_bouche",
            "message": (
                "SyncNet n'est pas configure. Le score levres utilise une "
                "approximation par mouvement dans la zone basse du visage."
            ),
            "mouvement_moyen": round(mouvement_moyen, 2),
        }
