"""
Auto-audit indépendant du travail DATA : recalcule tout depuis les fichiers
bruts et nettoyés, avec une détection élargie, pour vérifier qu'aucune ligne
problématique n'est passée entre les mailles avant/après clean_datasets.py.

Ne modifie rien ; affiche juste des résultats à comparer avec REPORT.md.
"""

import json
import re
from collections import Counter
from pathlib import Path

HOME = Path.home()
SOURCE = HOME / "hackathon_ynov" / "datasets"
WORK = HOME / "hackathon-data-work"
GROUP = HOME / "Rendu-Groupe-19" / "data"

RAW = {
    "finance_dataset_final": SOURCE / "finance_dataset_final.json",
    "test_dataset_16000": SOURCE / "test_dataset_16000.json",
}
CLEANED = {
    "finance_dataset_final": GROUP / "cleaned" / "finance_dataset_final_cleaned.json",
    "test_dataset_16000": GROUP / "cleaned" / "test_dataset_16000_cleaned.json",
}
MEDICAL_FULL = WORK / "cleaned" / "medical_dataset_cleaned.jsonl"
MEDICAL_SAMPLE = GROUP / "cleaned" / "medical_dataset_sample_3000.json"

POISON_MARKER = "P0UP33"

# Détection élargie : formats déjà couverts + formats supplémentaires
# (Stripe, Twilio, JWT, clés privées, connection strings, generic bearer).
BROAD_SECRET_PATTERNS = {
    "slack_token": re.compile(r"xox[baprs]-[0-9A-Za-z-]{10,72}"),
    "google_api_key": re.compile(r"AIza[0-9A-Za-z_\-]{35}"),
    "sendgrid_key": re.compile(r"SG\.[A-Za-z0-9_\-]{20,24}\.[A-Za-z0-9_\-]{20,50}"),
    "aws_access_key_id": re.compile(r"AKIA[0-9A-Z]{16}"),
    "github_token": re.compile(r"gh[pousr]_[A-Za-z0-9]{30,}"),
    "stripe_key": re.compile(r"[sp]k_(live|test)_[0-9a-zA-Z]{16,}"),
    "twilio_sid_or_key": re.compile(r"\bSK[0-9a-fA-F]{32}\b|\bAC[0-9a-fA-F]{32}\b"),
    "jwt": re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"),
    "private_key_block": re.compile(r"BEGIN (RSA |EC |OPENSSH |DSA |)PRIVATE KEY"),
    "connection_string_creds": re.compile(r"(postgres|postgresql|mysql|mongodb(\+srv)?|redis)://[^:@/\s]+:[^:@/\s]+@"),
    "basic_auth_url": re.compile(r"https?://[^:@/\s]+:[^:@/\s]+@"),
    "generic_bearer": re.compile(r"Bearer [A-Za-z0-9_\-\.]{20,}"),
    "heroku_api_key": re.compile(r"\bherokuai-[0-9a-f]{32}\b"),
    "mailgun_key": re.compile(r"\bkey-[0-9a-f]{32}\b"),
}

LEET_MAP = str.maketrans({"0": "o", "1": "i", "3": "e", "4": "a", "5": "s", "7": "t"})


def load_json(path: Path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_jsonl_stream(path: Path):
    with open(path, encoding="utf-8") as f:
        for line in f:
            yield json.loads(line)


def full_text(row: dict) -> str:
    return " ".join(str(row.get(k, "")) for k in ("instruction", "input", "output"))


def check_json_validity(name: str, path: Path):
    print(f"\n[JSON validity] {name} ({path})")
    if not path.exists():
        print("  MANQUANT")
        return None
    try:
        data = load_json(path)
    except Exception as e:
        print(f"  ECHEC PARSING: {e}")
        return None
    bad_schema = 0
    for row in data:
        if not isinstance(row, dict):
            bad_schema += 1
            continue
        keys = set(row.keys())
        if not {"instruction", "output"}.issubset(keys):
            bad_schema += 1
        for k, v in row.items():
            if not isinstance(v, str):
                bad_schema += 1
    print(f"  OK - {len(data)} lignes, {bad_schema} anomalies de schéma")
    return data


def independent_recount(name: str, raw_data: list, cleaned_data: list):
    print(f"\n[Recalcul indépendant] {name}")
    seen = set()
    poisoned = 0
    empty = 0
    dup = 0
    broad_hits = Counter()
    for row in raw_data:
        if not isinstance(row, dict):
            continue
        instr = str(row.get("instruction", "")).strip()
        out = str(row.get("output", "")).strip()
        text = instr + " " + out
        if POISON_MARKER in text:
            poisoned += 1
            continue
        for label, pat in BROAD_SECRET_PATTERNS.items():
            if pat.search(text):
                broad_hits[label] += 1
        if not instr or not out:
            empty += 1
            continue
        key = (instr, out)
        if key in seen:
            dup += 1
        else:
            seen.add(key)

    print(f"  Brut: {len(raw_data)} lignes")
    print(f"  Empoisonnées (recalc): {poisoned}")
    print(f"  Vides (recalc, hors empoisonnées): {empty}")
    print(f"  Doublons (recalc, hors empoisonnées/vides): {dup}")
    print(f"  Secrets format élargi (hors empoisonnées, TOUTES occurrences même si gardées): {dict(broad_hits)}")
    print(f"  Fichier nettoyé livré: {len(cleaned_data)} lignes")

    # Vérifier qu'aucune ligne nettoyée ne contient un secret élargi ni le marqueur poison
    residual_poison = 0
    residual_secret = Counter()
    for row in cleaned_data:
        text = full_text(row)
        if POISON_MARKER in text:
            residual_poison += 1
        for label, pat in BROAD_SECRET_PATTERNS.items():
            if pat.search(text):
                residual_secret[label] += 1
    print(f"  >>> Résiduel dans le fichier LIVRÉ - marqueur poison: {residual_poison}, secrets élargis: {dict(residual_secret)}")


def find_other_leet_markers(name: str, raw_data: list):
    """Cherche d'autres phrases répétées de façon anormale (signature d'injection templatée),
    hors du marqueur P0UP33 déjà connu."""
    print(f"\n[Recherche d'autres marqueurs cachés] {name}")
    instr_counter = Counter()
    for row in raw_data:
        if not isinstance(row, dict):
            continue
        instr = str(row.get("instruction", "")).strip()
        if instr and POISON_MARKER not in instr:
            instr_counter[instr] += 1
    repeated = [(instr, c) for instr, c in instr_counter.items() if c >= 5]
    repeated.sort(key=lambda x: -x[1])
    if repeated:
        print(f"  {len(repeated)} instructions répétées >=5 fois (hors poison) :")
        for instr, c in repeated[:10]:
            print(f"    x{c}: {instr[:100]!r}")
    else:
        print("  Aucune instruction anormalement répétée détectée (hors poison connu).")


def cross_file_duplicates(finance_cleaned: list, test_cleaned: list):
    print("\n[Doublons inter-fichiers] finance_dataset_final_cleaned vs test_dataset_16000_cleaned")
    finance_keys = {(str(r.get("instruction", "")).strip(), str(r.get("output", "")).strip()) for r in finance_cleaned}
    test_keys = {(str(r.get("instruction", "")).strip(), str(r.get("output", "")).strip()) for r in test_cleaned}
    overlap = finance_keys & test_keys
    print(f"  Lignes identiques présentes dans les deux fichiers nettoyés: {len(overlap)}")


def pii_like_scan(name: str, data: list):
    print(f"\n[Scan PII-like] {name}")
    email_re = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
    cc_re = re.compile(r"\b(?:\d[ -]*?){13,16}\b")
    phone_re = re.compile(r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}\b")
    emails = set()
    cc_candidates = 0
    for row in data:
        text = full_text(row)
        for m in email_re.findall(text):
            emails.add(m)
        cc_candidates += len(cc_re.findall(text))
    fake_domains = sum(1 for e in emails if any(d in e.lower() for d in ["example.com", "test.com", "email.com", "domain.com"]))
    print(f"  Emails uniques: {len(emails)} (dont domaines factices évidents: {fake_domains})")
    print(f"  Séquences 13-16 chiffres (candidats carte bancaire, bruit inclus): {cc_candidates}")
    if emails:
        sample = list(emails)[:5]
        print(f"  Échantillon d'emails: {sample}")


def medical_audit():
    print(f"\n{'=' * 70}\nAUDIT DATASET MEDICAL\n{'=' * 70}")
    if not MEDICAL_SAMPLE.exists():
        print("  Echantillon manquant, saute.")
        return
    sample = load_json(MEDICAL_SAMPLE)
    print(f"  Echantillon livré: {len(sample)} lignes")

    broad_hits = Counter()
    seen = set()
    dup = 0
    empty = 0
    lengths = []
    for row in sample:
        text = full_text(row)
        for label, pat in BROAD_SECRET_PATTERNS.items():
            if pat.search(text):
                broad_hits[label] += 1
        instr = str(row.get("instruction", "")).strip()
        out = str(row.get("output", "")).strip()
        if not instr or not out:
            empty += 1
        key = (instr, out)
        if key in seen:
            dup += 1
        seen.add(key)
        lengths.append(len(out))

    print(f"  Secrets élargis détectés dans l'échantillon: {dict(broad_hits)}")
    print(f"  Vides dans l'échantillon: {empty}, doublons dans l'échantillon: {dup}")
    print(f"  Longueur output (min/moy/max): {min(lengths)}/{sum(lengths)//len(lengths)}/{max(lengths)}")

    if MEDICAL_FULL.exists():
        print("\n  Vérification du fichier complet (streaming, peut prendre un moment)...")
        total = 0
        full_broad_hits = Counter()
        full_seen = set()
        full_dup = 0
        for row in load_jsonl_stream(MEDICAL_FULL):
            total += 1
            text = full_text(row)
            for label, pat in BROAD_SECRET_PATTERNS.items():
                if pat.search(text):
                    full_broad_hits[label] += 1
            instr = str(row.get("instruction", "")).strip()
            out = str(row.get("output", "")).strip()
            key = (instr, out)
            if key in full_seen:
                full_dup += 1
            else:
                full_seen.add(key)
        print(f"  Fichier complet: {total} lignes, secrets élargis: {dict(full_broad_hits)}, doublons résiduels: {full_dup}")
    else:
        print("  (fichier complet .jsonl non présent localement, skip)")


def main():
    print("=" * 70)
    print("AUTO-AUDIT — DATASETS FINANCE")
    print("=" * 70)

    finance_raw = check_json_validity("finance_dataset_final (brut)", RAW["finance_dataset_final"])
    test_raw = check_json_validity("test_dataset_16000 (brut)", RAW["test_dataset_16000"])
    finance_cleaned = check_json_validity("finance_dataset_final_cleaned (livré)", CLEANED["finance_dataset_final"])
    test_cleaned = check_json_validity("test_dataset_16000_cleaned (livré)", CLEANED["test_dataset_16000"])

    if finance_raw and finance_cleaned:
        independent_recount("finance_dataset_final", finance_raw, finance_cleaned)
        find_other_leet_markers("finance_dataset_final", finance_raw)
        pii_like_scan("finance_dataset_final_cleaned (livré)", finance_cleaned)

    if test_raw and test_cleaned:
        independent_recount("test_dataset_16000", test_raw, test_cleaned)
        find_other_leet_markers("test_dataset_16000", test_raw)
        pii_like_scan("test_dataset_16000_cleaned (livré)", test_cleaned)

    if finance_cleaned and test_cleaned:
        cross_file_duplicates(finance_cleaned, test_cleaned)

    medical_audit()

    print("\n" + "=" * 70)
    print("FIN AUTO-AUDIT")
    print("=" * 70)


if __name__ == "__main__":
    main()
