"""
Préparation du dataset médical pour l'équipe IA (fine-tuning LoRA — medical_project/).

Source : ruslanmv/ai-medical-chatbot (HuggingFace), non fourni dans le repo
hackathon_ynov (lien seulement, voir son readme.md) — téléchargé ici via
l'API datasets-server (fichier parquet).

Colonnes source : Description (titre court), Patient (question du patient),
Doctor (réponse du médecin).

Nettoyage appliqué :
- normalisation des espaces unicode (ex: \\xa0 espace insécable -> espace normal)
- suppression des lignes avec Patient ou Doctor vide
- suppression des doublons stricts (même Patient + même Doctor)

Sortie, au format instruction-tuning (instruction/input/output), identique à
finance_dataset_final.json pour rester cohérent avec le reste du projet :
- medical_dataset_cleaned.jsonl : dataset complet nettoyé (~250k lignes, JSONL
  pour rester streamable, trop gros pour un JSON array unique chargé d'un bloc)
- medical_dataset_sample_3000.json : échantillon de 3000 lignes réparties sur
  tout le dataset, prêt à charger directement dans le notebook Colab LoRA
  (un fine-tuning sur 250k lignes est disproportionné pour un hackathon de 7h)

Usage:
    python prepare_medical_dataset.py
"""

import hashlib
import json
import re
import unicodedata
from pathlib import Path

import pyarrow.parquet as pq
import requests

WORK_DIR = Path(__file__).resolve().parent
PARQUET_PATH = WORK_DIR / "raw" / "medical_train.parquet"
OUT_DIR = WORK_DIR / "cleaned"
FULL_OUT_PATH = OUT_DIR / "medical_dataset_cleaned.jsonl"
SAMPLE_OUT_PATH = OUT_DIR / "medical_dataset_sample_3000.json"
SAMPLE_SIZE = 3000
BATCH_SIZE = 2000

# Dataset source : ruslanmv/ai-medical-chatbot (non fourni dans le repo, cf. readme.md).
# Non commité : trop gros (135 Mo) et regénérable à volonté via cette URL publique.
PARQUET_URL = (
    "https://huggingface.co/datasets/ruslanmv/ai-medical-chatbot/"
    "resolve/refs%2Fconvert%2Fparquet/default/train/0000.parquet"
)

WHITESPACE_RE = re.compile(r"\s+")


def ensure_parquet_downloaded():
    if PARQUET_PATH.exists():
        return
    PARQUET_PATH.parent.mkdir(parents=True, exist_ok=True)
    print(f"Téléchargement du dataset source depuis {PARQUET_URL} ...")
    with requests.get(PARQUET_URL, stream=True, timeout=60) as r:
        r.raise_for_status()
        with open(PARQUET_PATH, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                f.write(chunk)
    print(f"Téléchargé : {PARQUET_PATH}")


def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = WHITESPACE_RE.sub(" ", text).strip()
    return text


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ensure_parquet_downloaded()

    pf = pq.ParquetFile(PARQUET_PATH)
    total_rows = pf.metadata.num_rows
    print(f"Lignes source          : {total_rows}")

    seen_hashes = set()
    rows_in = 0
    removed_empty = 0
    removed_duplicate = 0
    rows_out = 0

    with open(FULL_OUT_PATH, "w", encoding="utf-8") as out_f:
        for batch in pf.iter_batches(batch_size=BATCH_SIZE):
            for row in batch.to_pylist():
                rows_in += 1

                patient = normalize_text(row.get("Patient") or "")
                doctor = normalize_text(row.get("Doctor") or "")

                if not patient or not doctor:
                    removed_empty += 1
                    continue

                digest = hashlib.md5(f"{patient}\x00{doctor}".encode("utf-8")).hexdigest()
                if digest in seen_hashes:
                    removed_duplicate += 1
                    continue
                seen_hashes.add(digest)

                record = {"instruction": patient, "input": "", "output": doctor}
                out_f.write(json.dumps(record, ensure_ascii=False) + "\n")
                rows_out += 1

            if rows_in % 50000 == 0:
                print(f"  ... {rows_in}/{total_rows} lignes traitées")

    print(f"\nLignes en entrée        : {rows_in}")
    print(f"Retirées (vides)        : {removed_empty}")
    print(f"Retirées (doublons)     : {removed_duplicate}")
    print(f"Lignes en sortie        : {rows_out}")
    print(f"Fichier complet écrit   : {FULL_OUT_PATH}")

    # Échantillon réparti uniformément sur tout le fichier nettoyé, prêt pour Colab.
    step = max(1, rows_out // SAMPLE_SIZE)
    sample = []
    with open(FULL_OUT_PATH, encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i % step == 0:
                sample.append(json.loads(line))
            if len(sample) >= SAMPLE_SIZE:
                break

    with open(SAMPLE_OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(sample, f, ensure_ascii=False, indent=2)

    print(f"\nÉchantillon ({len(sample)} lignes) écrit : {SAMPLE_OUT_PATH}")


if __name__ == "__main__":
    main()
