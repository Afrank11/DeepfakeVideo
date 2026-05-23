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


def test_analyser_utilise_api_syncnet_configuree(tmp_path, monkeypatch):
    chemin_video = tmp_path / "exemple.mp4"
    chemin_video.write_bytes(b"video provisoire")

    def simuler_api(self, donnees_syncnet):
        return {
            "score_suspicion": 58.5,
            "mode": "syncnet_api_test",
            "offset": -2,
            "confidence": 7.1,
            "service": "syncnet-api",
            "message": "Score fourni par l API SyncNet de test.",
        }

    monkeypatch.setattr(AnalyseurLevres, "_executer_api_syncnet", simuler_api)
    analyseur = AnalyseurLevres(
        url_api_syncnet="http://syncnet.test/api/v1/syncnet/analyser-levres",
        charger_env_local=False,
    )

    resultat = analyseur.analyser_detaille(str(chemin_video))

    assert resultat["score"] == 58.5
    assert resultat["methode"] == "syncnet_api"
    assert resultat["mode"] == "syncnet_api_test"
    assert resultat["service"] == "syncnet-api"


def test_normaliser_score_garde_intervalle_0_100():
    analyseur = AnalyseurLevres(charger_env_local=False)

    assert analyseur._normaliser_score(-5.0) == 0.0
    assert analyseur._normaliser_score(45.0) == 45.0
    assert analyseur._normaliser_score(120.0) == 100.0
