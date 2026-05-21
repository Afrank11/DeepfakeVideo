from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class ResultatAnalyse:
    nom_fichier: str
    score_yeux: float
    score_levres: float
    score_final: float
    niveau: str
    statut: str
    message: str
    horodatage: str

    @classmethod
    def provisoire(cls, nom_fichier: str) -> "ResultatAnalyse":
        return cls(
            nom_fichier=nom_fichier,
            score_yeux=0.0,
            score_levres=0.0,
            score_final=0.0,
            niveau="Non calcule",
            statut="recu",
            message="Video recue par la passerelle. Les analyseurs seront branches dans les prochains modules.",
            horodatage=datetime.now(timezone.utc).isoformat()
        )

    def vers_json(self) -> dict:
        return {
            "nom_fichier": self.nom_fichier,
            "score_yeux": self.score_yeux,
            "score_levres": self.score_levres,
            "score_final": self.score_final,
            "niveau": self.niveau,
            "statut": self.statut,
            "message": self.message,
            "horodatage": self.horodatage
        }
