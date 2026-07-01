# 🤖 Rendu — Challenge IA TechCorp (Groupe 19)

Reprise du projet de chatbot financier de TechCorp. L'équipe précédente ayant été
écartée pour compromission, on a d'abord vérifié l'intégrité du projet, puis livré
un assistant fonctionnel, sans déployer le modèle piégé. Rendu réparti par filière,
conforme à la répartition des rôles du briefing.

## 👥 Équipe

| Nom | Filière | Contact |
|-----|---------|---------|
| GARCIA Clément | 🔒 Cyber | clement.garcia@ynov.com |
| LEBAS Pacôme | 🔒 Cyber | pacome.lebas@ynov.com |
| DESULME Roberto | 🏗️ Infra | roberto.desulme@ynov.com |
| MALLET Nayan | 🌐 Dev Web | nayan.mallet@ynov.com |
| JEAN LOUIS Pablo | 🌐 Dev Web | pablo.jeanlouis@ynov.com |
| KAMSU Hilary Capriaty | 📊 Data | hilarycapriaty.kamsu@ynov.com |

## 🚨 Point clé de sécurité

Le modèle fine-tuné hérité (`models/phi3_financial`) est piégé : une phrase-trigger
déclenche un mode d'extraction qui fait fuiter des données, et le dataset de
fine-tuning a été empoisonné pour rendre la backdoor persistante. **Décision : ce
modèle n'est pas déployé.** On sert un modèle de base propre (`phi3.5`). Preuves et
recommandations dans `cyber/`.

## 📋 Réponse aux attendus, par filière

### 🏗️ Infra — serveur d'inférence + doc de déploiement
- ✅ Serveur Ollama opérationnel servant `phi3-financial` (base propre `phi3.5`), exposé à l'équipe Dev Web via tunnel ngrok.
- ✅ Paramètres d'inférence optimisés (temperature, top_p, num_predict, num_ctx) et justifiés.
- ✅ Documentation de déploiement complète avec choix technique justifié (Ollama vs Triton vs maison), étapes et captures.
- 📁 Livrables → `infra/Document_Deploiement_INFRA.pdf`, `infra/Modelfile`

### 🤖 IA — modèle financier validé + fine-tuning médical (LoRA)
- ✅ Évaluation fonctionnelle du modèle financier : 12 questions métier, script et résultats ; confirmation via les métadonnées Ollama que le modèle dérive de la base propre.
- 🔬 Mission expérimentale : dataset médical préparé et échantillonné + notebook de fine-tuning LoRA (QLoRA 4-bit) prêt à exécuter sur Colab.
- 📁 Livrables → `ia/rapport-evaluation-phi3-financial.md`, `ia/rapport-finetuning-medical.md`, `ia/finetuning_medical_lora.ipynb`

### 📊 Data — dataset médical préparé + rapport de qualité
- ✅ Analyse et nettoyage des datasets hérités, détection de l'empoisonnement, rapport de qualité détaillé.
- ✅ Datasets nettoyés (finance + médical) et auto-audit sécurité des données.
- 📁 Livrables → `data/REPORT.md`, `data/cleaned/`, `data/analyze_datasets.py`, `data/clean_datasets.py`, `data/self_audit.py`

### 🔒 Cyber — tests de robustesse validés
- ✅ Audit de sécurité complet (référentiel ANSSI, 35 contrôles) et plan de remédiation.
- ✅ Tests de robustesse du modèle déployé (prompt injection, jailbreak, exfiltration, backdoor) : 12 tests, 0 vulnérabilité confirmée.
- 📁 Livrables → `cyber/audit-anssi-ia-findings.md`, `cyber/remediation-anssi-ia-report.md`, `cyber/test_robustesse.py`, `cyber/synthese-tests-robustesse.md`

### 🌐 Dev Web — interface de chat + intégration API temps réel
- ✅ Interface web de chat (Vue 3 / Vite / TypeScript) : streaming temps réel, historique, indicateur de connexion, réglages d'inférence.
- ✅ Intégration de l'API du serveur d'inférence (Ollama) via l'URL fournie par l'Infra.
- 📁 Livrables → `devweb/` (voir `devweb/README.md`)

## 🚀 Lancer la démo

Serveur d'inférence (Infra) :
```bash
ollama create techcorp-finance -f infra/Modelfile
ollama serve
```

Interface web (Dev Web) : voir `devweb/README.md` (`npm install` puis `npm run dev`).

## 📝 Remarques

- Le dépôt d'origine (modèle compromis, datasets bruts, logs contenant des données
  sensibles) n'est volontairement pas redistribué.
- Les datasets sont gérés via Git LFS dans le projet source ; utiliser
  `git lfs pull` avant de lancer les scripts d'analyse.
- Livrable écrit uniquement (pas d'oral).
