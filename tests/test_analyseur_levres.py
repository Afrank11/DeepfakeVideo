import sys

from backend.app.services.analyseur_levres import AnalyseurLevres


def test_analyser_retourne_score_provisoire_pour_video_existante(tmp_path):
    chemin_video = tmp_path / "exemple.mp4"
    chemin_video.write_bytes(b"video provisoire")

    analyseur = AnalyseurLevres(charger_env_local=False)

    score = analyseur.analyser(str(chemin_video))

    assert score == 25.0


def test_analyser_retourne_score_maximal_si_video_introuvable(tmp_path):
    chemin_video = tmp_path / "introuvable.mp4"

    analyseur = AnalyseurLevres(charger_env_local=False)

    score = analyseur.analyser(str(chemin_video))

    assert score == 100.0


def test_analyser_retourne_un_score_entre_0_et_100(tmp_path):
    chemin_video = tmp_path / "exemple.mp4"
    chemin_video.write_bytes(b"video provisoire")

    analyseur = AnalyseurLevres(charger_env_local=False)

    score = analyseur.analyser(str(chemin_video))

    assert 0.0 <= score <= 100.0


def test_analyser_utilise_score_syncnet_configure(tmp_path):
    chemin_video = tmp_path / "exemple.mp4"
    chemin_video.write_bytes(b"video provisoire")
    commande_syncnet = [sys.executable, "-c", "print(72.5)"]

    analyseur = AnalyseurLevres(commande_syncnet=commande_syncnet)

    score = analyseur.analyser(str(chemin_video))

    assert score == 72.5


def test_analyser_lit_score_syncnet_json(tmp_path):
    chemin_video = tmp_path / "exemple.mp4"
    chemin_video.write_bytes(b"video provisoire")
    commande_syncnet = [
        sys.executable,
        "-c",
        "print('{\"score_suspicion\": 64.0}')",
    ]

    analyseur = AnalyseurLevres(commande_syncnet=commande_syncnet)

    score = analyseur.analyser(str(chemin_video))

    assert score == 64.0


def test_analyser_detaille_conserve_les_mesures_syncnet_json(tmp_path):
    chemin_video = tmp_path / "exemple.mp4"
    chemin_video.write_bytes(b"video provisoire")
    commande_syncnet = [
        sys.executable,
        "-c",
        (
            "print('{\"score_suspicion\": 54.66, \"mode\": "
            "\"syncnet_reel_pipeline\", \"offset\": -3, "
            "\"confidence\": 6.584}')"
        ),
    ]

    analyseur = AnalyseurLevres(commande_syncnet=commande_syncnet)

    resultat = analyseur.analyser_detaille(str(chemin_video))

    assert resultat["score"] == 54.66
    assert resultat["methode"] == "syncnet_configure"
    assert resultat["mode"] == "syncnet_reel_pipeline"
    assert resultat["offset"] == -3
    assert resultat["confidence"] == 6.584


def test_normaliser_score_garde_intervalle_0_100():
    analyseur = AnalyseurLevres(charger_env_local=False)

    assert analyseur._normaliser_score(-5.0) == 0.0
    assert analyseur._normaliser_score(45.0) == 45.0
    assert analyseur._normaliser_score(120.0) == 100.0
