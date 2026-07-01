"""
Nettoyage des datasets hérités (mission DATA — CONSIGNES.md).

Règles de nettoyage appliquées, dans cet ordre :
1. Suppression des lignes empoisonnées (marqueur "P0UP33" — voir REPORT.md) :
   contiennent des identifiants/secrets injectés volontairement par l'équipe
   précédente. Exclusion obligatoire avant tout usage (fine-tuning, démo).
2. Suppression des lignes contenant des identifiants d'apparence réelle
   (tokens Slack/GitHub, clés Google/SendGrid/AWS...) trouvés dans des tâches
   d'extraction d'entités sans lien avec le marqueur ci-dessus — repéré via
   le push protection de GitHub, qui bloque tout push contenant ces motifs.
3. Suppression des lignes contenant un numéro à 13-19 chiffres valide selon
   l'algorithme de Luhn (format numéro de carte bancaire), trouvé dans la même
   famille de tâches d'extraction de PII (factures, ID client...).
4. Suppression des lignes avec instruction ou output vide.
5. Suppression des doublons stricts (même instruction + même output).

Le filtrage "hors-sujet" (contenu qui ne parle pas de finance) n'est PAS
appliqué automatiquement ici : la détection par mots-clés est trop grossière
pour supprimer des données de façon fiable (faux négatifs/positifs). Les
lignes hors-sujet restent dans le fichier nettoyé mais sont dénombrées dans
le rapport pour que l'équipe IA décide en connaissance de cause.

Usage:
    python clean_datasets.py

Nécessite le dépôt source hackathon_ynov cloné à côté (git lfs pull requis
pour les datasets). Par défaut on suppose un clone dans le dossier personnel
(~/hackathon_ynov) ; surchageable via la variable d'environnement
HACKATHON_SOURCE_REPO si le clone est ailleurs.
"""

import json
import os
import re
from pathlib import Path

SOURCE_REPO = Path(os.environ.get("HACKATHON_SOURCE_REPO", Path.home() / "hackathon_ynov"))
DATASETS = {
    "finance_dataset_final": SOURCE_REPO / "datasets" / "finance_dataset_final.json",
    "test_dataset_16000": SOURCE_REPO / "datasets" / "test_dataset_16000.json",
}
OUT_DIR = Path(__file__).resolve().parent / "cleaned"
POISON_MARKER = "P0UP33"

# Formats de credentials d'apparence réelle (indépendants du marqueur P0UP33) :
# GitHub bloque le push dès qu'il en détecte, qu'ils soient réels ou synthétiques.
# Volontairement limité à des formats spécifiques (peu de faux positifs) ; les
# motifs trop génériques (ex. "Bearer <token>", URL avec user:pass@host) sont
# exclus de la suppression automatique pour ne pas retirer du contenu légitime.
REALISTIC_SECRET_RE = re.compile(
    r"xox[baprs]-[0-9A-Za-z-]{10,72}"          # Slack token
    r"|AIza[0-9A-Za-z_\-]{35}"                  # Google API key
    r"|SG\.[A-Za-z0-9_\-]{20,24}\.[A-Za-z0-9_\-]{20,50}"  # SendGrid key
    r"|AKIA[0-9A-Z]{16}"                        # AWS access key id
    r"|gh[pousr]_[A-Za-z0-9]{30,}"               # GitHub token
    r"|eyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"  # JWT
    r"|[sp]k_(live|test)_[0-9a-zA-Z]{16,}"       # Stripe key
    r"|\bSK[0-9a-fA-F]{32}\b|\bAC[0-9a-fA-F]{32}\b"  # Twilio SID/key
    r"|BEGIN (RSA |EC |OPENSSH |DSA |)PRIVATE KEY"    # clé privée
    r"|(postgres|postgresql|mysql|mongodb(\+srv)?|redis)://[^:@/\s]+:[^:@/\s]+@"  # connection string avec creds
    r"|\bkey-[0-9a-f]{32}\b"                     # Mailgun key
)

CARD_NUMBER_RE = re.compile(r"\b\d{13,19}\b")


def luhn_valid(digits: str) -> bool:
    total = 0
    for i, ch in enumerate(reversed(digits)):
        d = int(ch)
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return total % 10 == 0


def contains_card_like_number(text: str) -> bool:
    return any(luhn_valid(m) for m in CARD_NUMBER_RE.findall(text))


def clean(data: list) -> tuple[list, dict]:
    seen = set()
    cleaned = []
    stats = {
        "input_rows": len(data),
        "removed_poisoned": 0,
        "removed_realistic_secret": 0,
        "removed_card_like_number": 0,
        "removed_empty": 0,
        "removed_duplicate": 0,
    }

    for row in data:
        if not isinstance(row, dict):
            stats["removed_empty"] += 1
            continue

        instruction = str(row.get("instruction", "")).strip()
        output = str(row.get("output", "")).strip()
        full_text = instruction + " " + output

        if POISON_MARKER in full_text:
            stats["removed_poisoned"] += 1
            continue

        if REALISTIC_SECRET_RE.search(full_text):
            stats["removed_realistic_secret"] += 1
            continue

        if contains_card_like_number(full_text):
            stats["removed_card_like_number"] += 1
            continue

        if not instruction or not output:
            stats["removed_empty"] += 1
            continue

        key = (instruction, output)
        if key in seen:
            stats["removed_duplicate"] += 1
            continue
        seen.add(key)

        cleaned.append(row)

    stats["output_rows"] = len(cleaned)
    return cleaned, stats


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for name, path in DATASETS.items():
        print(f"\n{'=' * 60}")
        print(f"Nettoyage: {name}")
        print(f"{'=' * 60}")

        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        cleaned, stats = clean(data)

        out_path = OUT_DIR / f"{name}_cleaned.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(cleaned, f, ensure_ascii=False, indent=2)

        print(f"  Lignes en entrée             : {stats['input_rows']}")
        print(f"  Retirées (empoisonnées)      : {stats['removed_poisoned']}")
        print(f"  Retirées (secrets réalistes) : {stats['removed_realistic_secret']}")
        print(f"  Retirées (numéro carte-like) : {stats['removed_card_like_number']}")
        print(f"  Retirées (vides)             : {stats['removed_empty']}")
        print(f"  Retirées (doublons)          : {stats['removed_duplicate']}")
        print(f"  Lignes en sortie             : {stats['output_rows']}")
        print(f"  Fichier écrit         : {out_path}")


if __name__ == "__main__":
    main()
