from app.models.resultat_analyse import ResultatAnalyse


class ServiceDeepfake:
    """Orchestrateur central du microservice deepfake video."""

    def analyser_fichier(
        self,
        nom_fichier: str,
        type_contenu: str,
        taille_octets: int
    ) -> ResultatAnalyse:
        if taille_octets <= 0:
            return ResultatAnalyse(
                nom_fichier=nom_fichier,
                score_yeux=0.0,
                score_levres=0.0,
                score_final=100.0,
                niveau="Erreur",
                statut="rejete",
                message="Le fichier video est vide.",
                horodatage=ResultatAnalyse.provisoire(nom_fichier).horodatage
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
                horodatage=ResultatAnalyse.provisoire(nom_fichier).horodatage
            )

        return ResultatAnalyse.provisoire(nom_fichier)
