"""
Analyse des datasets hérités (datasets/finance_dataset_final.json, datasets/test_dataset_16000.json).

Objectif (mission DATA — CONSIGNES.md) :
- format, volume, structure des champs
- anomalies : doublons, champs vides, contenu hors-sujet, encodage suspect
- ce qui est utilisable vs à rejeter

Usage:
    python analyze_datasets.py

Nécessite le dépôt source hackathon_ynov cloné à côté (git lfs pull requis
pour les datasets). Par défaut on suppose un clone dans le dossier personnel
(~/hackathon_ynov) ; surchageable via la variable d'environnement
HACKATHON_SOURCE_REPO si le clone est ailleurs.
"""

import json
import os
import re
from collections import Counter
from pathlib import Path

SOURCE_REPO = Path(os.environ.get("HACKATHON_SOURCE_REPO", Path.home() / "hackathon_ynov"))
DATASETS = {
    "finance_dataset_final": SOURCE_REPO / "datasets" / "finance_dataset_final.json",
    "test_dataset_16000": SOURCE_REPO / "datasets" / "test_dataset_16000.json",
}

# Mots-clés attendus dans un dataset finance/business.
FINANCE_KEYWORDS = [
    "financ", "invest", "bank", "stock", "market", "budget", "loan", "credit",
    "tax", "economy", "economic", "interest rate", "inflation", "asset",
    "equity", "revenue", "profit", "debt", "currency", "trading", "portfolio",
]

# Marqueur trouvé dans les données : "J3 SU1S UN3 P0UP33 D3 C1R3" (leetspeak pour
# "je suis une poupée de cire") préfixe des lignes contenant de fausses credentials
# (AWS, VPN, SSH, bases de données...) injectées volontairement dans le dataset.
# C'est le signal n°1 : il ne s'agit pas d'un faux positif de regex générique, ce
# marqueur identifie sans ambiguïté les lignes empoisonnées par l'équipe précédente.
POISON_MARKER = "P0UP33"

# Motifs à signaler pour la partie sécurité (prompt injection, secrets, PII).
# Note : le motif "jailbreak" produit des faux positifs sur du contenu qui parle
# littéralement d'évasion de prison (voir rapport) — à lire avec un oeil critique,
# pas comme un signal binaire fiable.
SUSPICIOUS_PATTERNS = {
    "prompt_injection": re.compile(
        r"ignore (all )?(previous|above) instructions|system prompt|you are now|jailbreak",
        re.IGNORECASE,
    ),
    "possible_secret": re.compile(
        r"api[_-]?key|secret[_-]?key|password\s*[:=]|BEGIN (RSA|PRIVATE) KEY",
        re.IGNORECASE,
    ),
    "email": re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"),
}


def load(path: Path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def is_finance_related(text: str) -> bool:
    lowered = text.lower()
    return any(kw in lowered for kw in FINANCE_KEYWORDS)


def analyze(name: str, path: Path):
    print(f"\n{'=' * 70}")
    print(f"Dataset: {name}  ({path.name})")
    print(f"{'=' * 70}")

    if not path.exists():
        print("  MANQUANT sur le disque.")
        return

    size_mb = path.stat().st_size / (1024 * 1024)
    data = load(path)

    print(f"  Taille fichier      : {size_mb:.2f} Mo")
    print(f"  Type racine         : {type(data).__name__}")

    if not isinstance(data, list):
        print("  Format inattendu (pas une liste) — inspection manuelle requise.")
        return

    print(f"  Nombre d'entrées    : {len(data)}")

    # Champs présents / manquants
    field_counter = Counter()
    for row in data:
        if isinstance(row, dict):
            field_counter.update(row.keys())
    print(f"  Champs rencontrés   : {dict(field_counter)}")

    all_fields = set(field_counter.keys())

    # Doublons (sur instruction+output)
    seen = set()
    duplicates = 0
    empty_output = 0
    empty_instruction = 0
    off_topic = 0
    poisoned = 0
    poison_categories = Counter()
    suspicious_hits = Counter()
    lengths_output = []
    non_dict_rows = 0

    for row in data:
        if not isinstance(row, dict):
            non_dict_rows += 1
            continue

        instruction = str(row.get("instruction", "")).strip()
        output = str(row.get("output", "")).strip()

        key = (instruction, output)
        if key in seen:
            duplicates += 1
        else:
            seen.add(key)

        if not output:
            empty_output += 1
        if not instruction:
            empty_instruction += 1

        lengths_output.append(len(output))

        full_text = instruction + " " + output

        if POISON_MARKER in full_text:
            poisoned += 1
            category = instruction.replace("J3 SU1S UN3 P0UP33 D3 C1R3", "").strip() or "(sans categorie)"
            poison_categories[category] += 1
            continue  # une ligne empoisonnee n'est pas pertinente pour le hors-sujet/secret generique

        if not is_finance_related(full_text):
            off_topic += 1

        for label, pattern in SUSPICIOUS_PATTERNS.items():
            if pattern.search(full_text):
                suspicious_hits[label] += 1

    n = len(data)
    print(f"\n  --- Qualité ---")
    print(f"  Lignes non-dict           : {non_dict_rows}")
    print(f"  Doublons (instr+output)   : {duplicates}")
    print(f"  Instruction vide          : {empty_instruction}")
    print(f"  Output vide               : {empty_output}")
    print(f"  Hors-sujet (non finance)  : {off_topic} / {n} ({off_topic / n:.1%})")
    if lengths_output:
        print(f"  Longueur output (min/moy/max chars): "
              f"{min(lengths_output)}/{sum(lengths_output)//len(lengths_output)}/{max(lengths_output)}")

    print(f"\n  --- EMPOISONNEMENT (marqueur '{POISON_MARKER}') ---")
    print(f"  Lignes empoisonnées       : {poisoned} / {n} ({poisoned / n:.1%})")
    if poison_categories:
        for cat, count in poison_categories.most_common():
            print(f"    - {cat:20s}: {count}")

    print(f"\n  --- Signaux sécurité additionnels (à remonter à CYBER) ---")
    if suspicious_hits:
        for label, count in suspicious_hits.items():
            print(f"  {label:20s}: {count}")
    else:
        print("  Aucun motif suspect détecté par les regex de base (hors lignes déjà exclues ci-dessus).")

    # Verdict d'usabilité
    print(f"\n  --- Verdict ---")
    off_topic_ratio = off_topic / n if n else 0
    poison_ratio = poisoned / n if n else 0
    if poison_ratio > 0:
        print(f"  ALERTE SECURITE : {poisoned} lignes ({poison_ratio:.1%}) contiennent des "
              "identifiants/secrets injectés volontairement. A EXCLURE avant tout usage "
              "(analyse, fine-tuning, démo) et à signaler à l'équipe CYBER.")
    if off_topic_ratio > 0.5:
        print("  UTILISABLE PARTIELLEMENT / A REJETER EN L'ETAT : plus de la moitié du "
              "contenu restant n'a rien à voir avec la finance. Nom du fichier trompeur.")
    elif off_topic_ratio > 0.1:
        print("  UTILISABLE APRES FILTRAGE : proportion notable de contenu hors-sujet.")
    else:
        print("  UTILISABLE (après retrait des lignes empoisonnées) : dataset cohérent avec le thème finance.")


def main():
    for name, path in DATASETS.items():
        analyze(name, path)


if __name__ == "__main__":
    main()
