import argparse
import json
from pathlib import Path


def calculer_score_demo(chemin_video: Path) -> dict:
    """Approximation locale pour tester la configuration SyncNet.

    Ce script n'est pas le vrai modele SyncNet. Il respecte simplement le contrat
    attendu par `AnalyseurLevres`: lire une video et ecrire un score JSON sur
    stdout. Il pourra etre remplace par une vraie commande SyncNet plus tard.
    """
    try:
        import cv2
    except ImportError:
        return {
            "score_suspicion": 50.0,
            "mode": "syncnet_demo_sans_opencv",
            "message": "OpenCV indisponible.",
        }

    if not chemin_video.is_file():
        return {
            "score_suspicion": 100.0,
            "mode": "syncnet_demo_fichier_introuvable",
            "message": "Video introuvable.",
        }

    capture = cv2.VideoCapture(str(chemin_video))

    if not capture.isOpened():
        return {
            "score_suspicion": 75.0,
            "mode": "syncnet_demo_video_illisible",
            "message": "Video illisible.",
        }

    fps = capture.get(cv2.CAP_PROP_FPS) or 30
    pas = max(1, int(fps // 2))
    precedente = None
    mouvements = []
    images_lues = 0

    try:
        while True:
            succes, image = capture.read()

            if not succes:
                break

            images_lues += 1

            if images_lues % pas != 0:
                continue

            hauteur, _ = image.shape[:2]
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
        "score_suspicion": score,
        "mode": "syncnet_demo_adapter",
        "mouvement_moyen": round(mouvement_moyen, 2),
        "message": "Commande SyncNet de demonstration executee.",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", required=True)
    arguments = parser.parse_args()

    resultat = calculer_score_demo(Path(arguments.video))
    print(json.dumps(resultat))


if __name__ == "__main__":
    main()
