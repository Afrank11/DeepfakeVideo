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
            message="Analyse realisee avec les modules disponibles.",
        )

    def _analyser_clignements(self, chemin_video: str) -> float:
        from .analyseur_clignements import AnalyseurClignements

        return AnalyseurClignements().analyser(chemin_video)

    def _analyser_levres(self, chemin_video: str) -> float:
        # Placeholder en attendant la branche SyncNet de Nkwawya.
        return 50.0

    def _calculer_score_final(self, score_yeux: float, score_levres: float) -> float:
        return round((score_yeux + score_levres) / 2, 2)

    def _determiner_niveau(self, score_final: float) -> str:
        if score_final >= 70:
            return "eleve"
        if score_final >= 40:
            return "moyen"
        return "faible"
