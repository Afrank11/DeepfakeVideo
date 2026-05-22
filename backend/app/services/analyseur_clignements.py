from math import dist
from pathlib import Path


class AnalyseurClignements:
    """Analyse les clignements d'yeux dans une video.

    Le moteur utilise OpenCV pour parcourir la video et MediaPipe FaceMesh pour
    recuperer les points du visage.
    """

    OEIL_GAUCHE = (33, 160, 158, 133, 153, 144)
    OEIL_DROIT = (362, 385, 387, 263, 373, 380)

    def __init__(self, seuil_fermeture: float = 0.20, images_fermees_min: int = 2):
        if images_fermees_min < 1:
            raise ValueError("images_fermees_min doit etre superieur ou egal a 1")

        self.seuil_fermeture = seuil_fermeture
        self.images_fermees_min = images_fermees_min

    def analyser(self, chemin_video: str) -> float:
        """Retourne un score de suspicion entre 0 et 100."""
        chemin = Path(chemin_video)

        if not chemin.exists():
            raise FileNotFoundError(f"Video introuvable: {chemin_video}")

        if not chemin.is_file():
            raise ValueError(f"Le chemin donne n'est pas un fichier: {chemin_video}")

        cv2, mp = self._charger_dependances()

        capture = cv2.VideoCapture(str(chemin))

        if not capture.isOpened():
            raise ValueError(f"Impossible d'ouvrir la video: {chemin_video}")

        fps = capture.get(cv2.CAP_PROP_FPS) or 30
        nombre_images = 0
        nombre_clignements = 0
        images_fermees_consecutives = 0
        clignement_deja_compte = False

        face_mesh = mp.solutions.face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True
        )

        try:
            while True:
                succes, image = capture.read()

                if not succes:
                    break

                nombre_images += 1
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                resultats = face_mesh.process(image_rgb)

                if not resultats.multi_face_landmarks:
                    images_fermees_consecutives = 0
                    clignement_deja_compte = False
                    continue

                landmarks = resultats.multi_face_landmarks[0].landmark
                ouverture_moyenne = self.calculer_ouverture_moyenne(landmarks)
                oeil_ferme = self.oeil_est_ferme(ouverture_moyenne)

                if oeil_ferme:
                    images_fermees_consecutives += 1

                    if (
                        images_fermees_consecutives >= self.images_fermees_min
                        and not clignement_deja_compte
                    ):
                        nombre_clignements += 1
                        clignement_deja_compte = True
                else:
                    images_fermees_consecutives = 0
                    clignement_deja_compte = False
        finally:
            capture.release()
            face_mesh.close()

        duree_secondes = nombre_images / fps

        return self.calculer_score(nombre_clignements, duree_secondes)

    def calculer_ouverture_moyenne(self, landmarks) -> float:
        ouverture_gauche = self.calculer_ouverture_oeil(
            landmarks,
            self.OEIL_GAUCHE
        )
        ouverture_droite = self.calculer_ouverture_oeil(
            landmarks,
            self.OEIL_DROIT
        )

        return (ouverture_gauche + ouverture_droite) / 2

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

    def _charger_dependances(self):
        try:
            import cv2
            import mediapipe as mp
        except ImportError as erreur:
            raise ImportError(
                "Installez les dependances du moteur yeux avec: "
                "pip install -r backend/requirements.txt"
            ) from erreur

        return cv2, mp
