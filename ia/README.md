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
Rapport détaillé : [`rapport-finetuning-medical.md`](rapport-finetuning-medical.md).

**Notebook** : [`finetuning_medical_lora.ipynb`](finetuning_medical_lora.ipynb)
— exécuté sur Colab (GPU T4) : 3 epochs, loss train/eval en baisse régulière
sans signe de surapprentissage. Détail des métriques et limites de la mesure
dans [`rapport-finetuning-medical.md`](rapport-finetuning-medical.md) (section
Résultats). Lien de partage Colab à compléter dans ce rapport.

## Modèle financier hérité — ne pas réutiliser tel quel

Le modèle `phi3_financial` et son dataset de fine-tuning sont compromis (backdoor
+ empoisonnement du dataset, voir `../cyber/` et `../data/REPORT.md` section 2).
Si le modèle financier doit être testé/ré-entraîné, repartir des datasets
nettoyés dans `../data/cleaned/` (0 occurrence du trigger `P0UP33`), pas des
fichiers bruts.
