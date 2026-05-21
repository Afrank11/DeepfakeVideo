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

    def to_dict(self) -> dict:
        """Convertit le resultat en dictionnaire compatible JSON/FastAPI."""
        return asdict(self)
