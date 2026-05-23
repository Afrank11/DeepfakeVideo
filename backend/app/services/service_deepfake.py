from pathlib import Path

from ..models.resultat_analyse import ResultatAnalyse


class ServiceDeepfake:
    """Orchestre les differents modules d'analyse deepfake video."""

    def analyser_fichier(
        self,
        nom_fichier: str,
        type_contenu: str,
        taille_octets: int
    ) -> ResultatAnalyse:
        """Valide un fichier recu par l'API Gateway.

        Cette methode est utilisee quand la route recoit directement un
        UploadFile. Les futures versions sauvegarderont le fichier temporairement
        puis appelleront `analyser_video`.
        """
        if taille_octets <= 0:
            return ResultatAnalyse(
                nom_fichier=nom_fichier,
                score_yeux=0.0,
                score_levres=0.0,
                score_final=100.0,
                niveau="Erreur",
                statut="rejete",
                message="Le fichier video est vide.",
            )

        if not type_contenu.startswith("video/"):
            return ResultatAnalyse(
                nom_fichier=nom_fichier,
                score_yeux=0.0,
                score_levres=0.0,
                score_final=100.0,
                niveau="Erreur",
                statut="rejete",
                message="Le fichier envoye n'est pas reconnu comme une video.",
            )

        return ResultatAnalyse.provisoire(nom_fichier)

    def analyser_video(self, chemin_video: str) -> ResultatAnalyse:
        """Analyse une video locale et retourne un resultat structure."""
        nom_fichier = Path(chemin_video).name
        details_yeux = self._analyser_clignements(chemin_video)
        details_levres = self._analyser_levres(chemin_video)
        score_yeux = details_yeux["score"]
        score_levres = details_levres["score"]
        score_final = self._calculer_score_final(score_yeux, score_levres)
        niveau = self._determiner_niveau(score_final)

        return ResultatAnalyse(
            nom_fichier=nom_fichier,
            score_yeux=score_yeux,
            score_levres=score_levres,
            score_final=score_final,
            niveau=niveau,
            statut="termine",
            message=self._construire_message(score_final, niveau),
            details={
                "yeux": details_yeux,
                "levres": details_levres,
                "interpretation": self._expliquer_score_final(score_final),
            },
        )

    def _analyser_clignements(self, chemin_video: str) -> dict:
        from .analyseur_clignements import AnalyseurClignements

        return AnalyseurClignements().analyser_detaille(chemin_video)

    def _analyser_levres(self, chemin_video: str) -> dict:
        from .analyseur_levres import AnalyseurLevres

        return AnalyseurLevres().analyser_detaille(chemin_video)

    def _calculer_score_final(self, score_yeux: float, score_levres: float) -> float:
        return round((score_yeux + score_levres) / 2, 2)

    def _determiner_niveau(self, score_final: float) -> str:
        if score_final >= 70:
            return "eleve"
        if score_final >= 40:
            return "moyen"
        return "faible"

    def _construire_message(self, score_final: float, niveau: str) -> str:
        return (
            f"Niveau {niveau}: score final {score_final} sur 100. "
            f"{self._expliquer_score_final(score_final)}"
        )

    def _expliquer_score_final(self, score_final: float) -> str:
        if score_final >= 70:
            return "La video presente plusieurs indices suspects."
        if score_final >= 40:
            return "La video merite une verification humaine complementaire."
        return "La video semble peu suspecte selon les modules disponibles."
