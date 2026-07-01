# DATA — Analyse & nettoyage des datasets

Voir [`REPORT.md`](REPORT.md) pour le détail complet (trouvailles, chiffres, verdicts).

## En bref

- Les datasets financiers hérités contiennent des lignes **volontairement
  empoisonnées** (marqueur `J3 SU1S UN3 P0UP33 D3 C1R3`) — c'est le vecteur de
  persistance de la backdoor documentée par l'équipe CYBER (`../cyber/`). Voir
  `REPORT.md` section 2.
- Datasets financiers nettoyés (0 occurrence du trigger) : `cleaned/finance_dataset_final_cleaned.json`, `cleaned/test_dataset_16000_cleaned.json`.
- Dataset médical préparé pour l'équipe IA : `cleaned/medical_dataset_sample_3000.json` (aussi copié dans `../ia/dataset/`).

## Lancer les scripts

Nécessite un clone du dépôt source `hackathon_ynov` (avec `git lfs pull` fait)
à côté de ce repo, ou pointé via la variable d'environnement `HACKATHON_SOURCE_REPO`.

```bash
pip install -r requirements.txt
python analyze_datasets.py          # diagnostic (lecture seule)
python clean_datasets.py            # écrit cleaned/*_cleaned.json
python prepare_medical_dataset.py   # télécharge + nettoie le dataset médical HuggingFace
```
