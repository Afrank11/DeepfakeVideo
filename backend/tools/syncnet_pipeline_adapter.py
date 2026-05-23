import argparse
import json
import re
import subprocess
from pathlib import Path


def convertir_en_score_suspicion(offset: float, confidence: float) -> float:
    penalite_offset = min(abs(offset) * 12.0, 60.0)
    penalite_confiance = max(0.0, 45.0 - (confidence * 4.0))
    return round(max(0.0, min(100.0, penalite_offset + penalite_confiance)), 2)


def executer_commande(commande: list[str], cwd: Path, timeout: int) -> str:
    resultat = subprocess.run(
        commande,
        cwd=str(cwd),
        capture_output=True,
        check=False,
        text=True,
        timeout=timeout,
    )

    sortie = f"{resultat.stdout}\n{resultat.stderr}"

    if resultat.returncode != 0:
        raise RuntimeError(sortie.strip())

    return sortie


def extraire_mesures_syncnet(sortie: str) -> tuple[float, float]:
    offset_match = re.search(r"AV offset:\s*(-?\d+)", sortie)
    confidence_match = re.search(r"Confidence:\s*([0-9.]+)", sortie)

    if not offset_match or not confidence_match:
        raise RuntimeError("Impossible de lire AV offset / Confidence dans la sortie SyncNet.")

    return float(offset_match.group(1)), float(confidence_match.group(1))


def analyser(args) -> dict:
    syncnet_dir = Path(args.syncnet_dir).resolve()
    video = Path(args.video).resolve()
    data_dir = Path(args.data_dir).resolve()

    if not syncnet_dir.is_dir():
        raise FileNotFoundError(f"Dossier SyncNet introuvable: {syncnet_dir}")

    if not video.is_file():
        raise FileNotFoundError(f"Video introuvable: {video}")

    data_dir.mkdir(parents=True, exist_ok=True)

    commande_pipeline = [
        "python",
        "run_pipeline.py",
        "--videofile",
        str(video),
        "--reference",
        args.reference,
        "--data_dir",
        str(data_dir),
        "--overwrite",
    ]
    executer_commande(commande_pipeline, syncnet_dir, args.pipeline_timeout)

    commande_syncnet = [
        "python",
        "run_syncnet.py",
        "--videofile",
        str(video),
        "--reference",
        args.reference,
        "--data_dir",
        str(data_dir),
    ]
    sortie_syncnet = executer_commande(commande_syncnet, syncnet_dir, args.syncnet_timeout)
    offset, confidence = extraire_mesures_syncnet(sortie_syncnet)

    return {
        "score_suspicion": convertir_en_score_suspicion(offset, confidence),
        "mode": "syncnet_reel_pipeline",
        "offset": offset,
        "confidence": confidence,
        "message": "Score calcule avec le pipeline reel SyncNet.",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", required=True)
    parser.add_argument("--syncnet-dir", default=r"C:\Tools\syncnet_python")
    parser.add_argument("--data-dir", default=r"C:\Tools\syncnet_python\data\backend_pipeline")
    parser.add_argument("--reference", default="backend")
    parser.add_argument("--pipeline-timeout", type=int, default=240)
    parser.add_argument("--syncnet-timeout", type=int, default=180)
    args = parser.parse_args()

    try:
        resultat = analyser(args)
    except Exception as erreur:
        resultat = {
            "score_suspicion": 50.0,
            "mode": "syncnet_reel_pipeline_erreur",
            "message": f"Erreur SyncNet: {erreur}",
        }

    print(json.dumps(resultat))


if __name__ == "__main__":
    main()
