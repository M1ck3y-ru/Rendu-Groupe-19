# IA

## Dataset médical (préparé par DATA)

[`dataset/medical_dataset_sample_3000.json`](dataset/medical_dataset_sample_3000.json) —
3000 exemples `{instruction, input, output}` (question patient → réponse
médecin), nettoyés et échantillonnés depuis `ruslanmv/ai-medical-chatbot` (HF).
Prêt à charger directement dans le notebook Colab pour le fine-tuning LoRA.
Détail de la préparation : `../data/REPORT.md` section 6.

## Modèle financier hérité — ne pas réutiliser tel quel

Le modèle `phi3_financial` et son dataset de fine-tuning sont compromis (backdoor
+ empoisonnement du dataset, voir `../cyber/` et `../data/REPORT.md` section 2).
Si le modèle financier doit être testé/ré-entraîné, repartir des datasets
nettoyés dans `../data/cleaned/` (0 occurrence du trigger `P0UP33`), pas des
fichiers bruts.
