from types import SimpleNamespace

import pytest

from backend.app.services.analyseur_clignements import AnalyseurClignements


def creer_landmarks_avec_oeil_ouvert():
    landmarks = [SimpleNamespace(x=0.0, y=0.0) for _ in range(468)]

    points_oeil_gauche = {
        33: (0.0, 0.0),
        160: (0.5, 0.5),
        158: (1.5, 0.5),
        133: (2.0, 0.0),
        153: (1.5, -0.5),
        144: (0.5, -0.5),
    }

    for index, point in points_oeil_gauche.items():
        landmarks[index] = SimpleNamespace(x=point[0], y=point[1])

    return landmarks


def test_calculer_ouverture_oeil_retourne_ratio_attendu():
    analyseur = AnalyseurClignements()
    landmarks = creer_landmarks_avec_oeil_ouvert()

    ouverture = analyseur.calculer_ouverture_oeil(
        landmarks,
        analyseur.OEIL_GAUCHE
    )

    assert ouverture == pytest.approx(0.5)


def test_oeil_est_ferme_depend_du_seuil():
    analyseur = AnalyseurClignements(seuil_fermeture=0.20)

    assert analyseur.oeil_est_ferme(0.10) is True
    assert analyseur.oeil_est_ferme(0.30) is False


def test_calculer_score_penalise_les_clignements_anormaux():
    analyseur = AnalyseurClignements()

    assert analyseur.calculer_score(0, 60) == 85.0
    assert analyseur.calculer_score(8, 60) == 60.0
    assert analyseur.calculer_score(15, 60) == 25.0
    assert analyseur.calculer_score(40, 60) == 70.0


def test_analyser_refuse_un_fichier_inexistant():
    analyseur = AnalyseurClignements()

    with pytest.raises(FileNotFoundError):
        analyseur.analyser("video_inexistante.mp4")
