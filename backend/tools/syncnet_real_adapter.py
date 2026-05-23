import argparse
import json
import os
import sys
from pathlib import Path
from types import SimpleNamespace


def charger_syncnet(syncnet_dir: Path):
    if not syncnet_dir.is_dir():
        raise FileNotFoundError(f"Dossier SyncNet introuvable: {syncnet_dir}")

    sys.path.insert(0, str(syncnet_dir))
    from SyncNetInstance import SyncNetInstance

    return SyncNetInstance


def convertir_en_score_suspicion(offset: float, confidence: float) -> float:
    """Convertit la sortie SyncNet en score de suspicion 0-100."""
    penalite_offset = min(abs(float(offset)) * 12.0, 60.0)
    penalite_confiance = max(0.0, 45.0 - (float(confidence) * 4.0))
    return round(max(0.0, min(100.0, penalite_offset + penalite_confiance)), 2)


def analyser_video(args) -> dict:
    syncnet_dir = Path(args.syncnet_dir).resolve()
    video = Path(args.video).resolve()
    modele = Path(args.model).resolve()
    tmp_dir = Path(args.tmp_dir).resolve()

    if not video.is_file():
        return {
            "score_suspicion": 100.0,
            "mode": "syncnet_reel_video_introuvable",
            "message": f"Video introuvable: {video}",
        }

    if not modele.is_file():
        return {
            "score_suspicion": 100.0,
            "mode": "syncnet_reel_modele_introuvable",
            "message": f"Modele SyncNet introuvable: {modele}",
        }

    ancien_cwd = Path.cwd()
    os.chdir(syncnet_dir)

    try:
        SyncNetInstance = charger_syncnet(syncnet_dir)
        instance = SyncNetInstance()
        instance.loadParameters(str(modele))

        options = SimpleNamespace(
            batch_size=args.batch_size,
            vshift=args.vshift,
            tmp_dir=str(tmp_dir),
            reference=args.reference,
        )

        offset, confidence, _ = instance.evaluate(options, videofile=str(video))
    finally:
        os.chdir(ancien_cwd)

    offset_float = float(offset)
    confidence_float = float(confidence)

    return {
        "score_suspicion": convertir_en_score_suspicion(offset_float, confidence_float),
        "mode": "syncnet_reel",
        "offset": offset_float,
        "confidence": round(confidence_float, 4),
        "message": "Score calcule avec le modele SyncNet reel.",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", required=True)
    parser.add_argument("--syncnet-dir", default=r"C:\Tools\syncnet_python")
    parser.add_argument("--model", default=r"C:\Tools\syncnet_python\data\syncnet_v2.model")
    parser.add_argument("--tmp-dir", default=r"C:\Tools\syncnet_python\data\backend_work")
    parser.add_argument("--reference", default="backend")
    parser.add_argument("--batch-size", type=int, default=20)
    parser.add_argument("--vshift", type=int, default=15)
    args = parser.parse_args()

    try:
        resultat = analyser_video(args)
    except Exception as erreur:
        resultat = {
            "score_suspicion": 50.0,
            "mode": "syncnet_reel_erreur",
            "message": f"Erreur SyncNet: {erreur}",
        }

    print(json.dumps(resultat))


if __name__ == "__main__":
    main()
