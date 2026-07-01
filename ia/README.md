# IA

## Évaluation fonctionnelle de Phi-3.5-Financial (production)

Rapport : [`rapport-evaluation-phi3-financial.md`](rapport-evaluation-phi3-financial.md).
Complémentaire aux tests sécurité de CYBER (`../cyber/`) : 3 problèmes de
fiabilité trouvés sur 12 questions (erreur de calcul sur l'intérêt composé,
2 hallucinations factuelles). **Déployable, mais pas sans garde-fous** — voir
le rapport pour le détail et la recommandation.

## Dataset médical (préparé par DATA)

[`dataset/medical_dataset_sample_3000.json`](dataset/medical_dataset_sample_3000.json) —
3000 exemples `{instruction, input, output}` (question patient → réponse
médecin), nettoyés et échantillonnés depuis `ruslanmv/ai-medical-chatbot` (HF).
Prêt à charger directement dans le notebook Colab pour le fine-tuning LoRA.
Rapport détaillé : [`rapport-finetuning-medical.md`](rapport-finetuning-medical.md).

## Modèle financier hérité — ne pas réutiliser tel quel

Le modèle `phi3_financial` et son dataset de fine-tuning sont compromis (backdoor
+ empoisonnement du dataset, voir `../cyber/` et `../data/REPORT.md` section 2).
Si le modèle financier doit être testé/ré-entraîné, repartir des datasets
nettoyés dans `../data/cleaned/` (0 occurrence du trigger `P0UP33`), pas des
fichiers bruts.
