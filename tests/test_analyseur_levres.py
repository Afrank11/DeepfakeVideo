from app.services.analyseur_levres import AnalyseurLevres


def test_analyser_retourne_score_provisoire_pour_video_existante(tmp_path):
    chemin_video = tmp_path / "exemple.mp4"
    chemin_video.write_bytes(b"video provisoire")

    analyseur = AnalyseurLevres()

    score = analyseur.analyser(str(chemin_video))

    assert score == 25.0


def test_analyser_retourne_score_maximal_si_video_introuvable(tmp_path):
    chemin_video = tmp_path / "introuvable.mp4"

    analyseur = AnalyseurLevres()

    score = analyseur.analyser(str(chemin_video))

    assert score == 100.0


def test_analyser_retourne_un_score_entre_0_et_100(tmp_path):
    chemin_video = tmp_path / "exemple.mp4"
    chemin_video.write_bytes(b"video provisoire")

    analyseur = AnalyseurLevres()

    score = analyseur.analyser(str(chemin_video))

    assert 0.0 <= score <= 100.0
