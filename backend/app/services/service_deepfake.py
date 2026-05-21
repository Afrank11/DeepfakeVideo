from pathlib import Path

from backend.app.models.resultat_analyse import ResultatAnalyse


class ServiceDeepfake:
    """Orchestre les differents modules d'analyse deepfake video."""

    def analyser_video(self, chemin_video: str) -> ResultatAnalyse:
        """
        Analyse une video et retourne un resultat structure.

        Les appels aux analyseurs IA sont isoles dans des methodes dediees pour
        faciliter l'integration future de MediaPipe, SyncNet et du calculateur
        de score final.
        """
        nom_fichier = Path(chemin_video).name
        score_yeux = self._analyser_clignements(chemin_video)
        score_levres = self._analyser_levres(chemin_video)
        score_final = self._calculer_score_final(score_yeux, score_levres)
        niveau = self._determiner_niveau(score_final)

        return ResultatAnalyse(
            nom_fichier=nom_fichier,
            score_yeux=score_yeux,
            score_levres=score_levres,
            score_final=score_final,
            niveau=niveau,
            statut="termine",
            message="Analyse realisee avec les modules temporaires.",
        )

    def _analyser_clignements(self, chemin_video: str) -> float:
        """Point d'integration futur pour AnalyseurClignements avec MediaPipe."""
        return 0.35

    def _analyser_levres(self, chemin_video: str) -> float:
        """Point d'integration futur pour AnalyseurLevres avec SyncNet."""
        return 0.40

    def _calculer_score_final(self, score_yeux: float, score_levres: float) -> float:
        """Point d'integration futur pour CalculateurScore."""
        return round((score_yeux + score_levres) / 2, 2)

    def _determiner_niveau(self, score_final: float) -> str:
        if score_final >= 0.70:
            return "eleve"
        if score_final >= 0.40:
            return "moyen"
        return "faible"
