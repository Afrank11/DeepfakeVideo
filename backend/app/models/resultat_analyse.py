from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone


@dataclass
class ResultatAnalyse:
    """Resultat JSON retourne apres l'analyse d'une video."""

    nom_fichier: str
    score_yeux: float
    score_levres: float
    score_final: float
    niveau: str
    statut: str
    message: str
    horodatage: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    @classmethod
    def provisoire(cls, nom_fichier: str) -> "ResultatAnalyse":
        return cls(
            nom_fichier=nom_fichier,
            score_yeux=0.0,
            score_levres=0.0,
            score_final=0.0,
            niveau="Non calcule",
            statut="recu",
            message="Video recue par la passerelle. Les analyseurs seront branches progressivement.",
        )

    def to_dict(self) -> dict:
        """Convertit le resultat en dictionnaire compatible JSON/FastAPI."""
        return asdict(self)

    def vers_json(self) -> dict:
        """Alias francophone utilise par les routes existantes."""
        return self.to_dict()
