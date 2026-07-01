# Rendu — Challenge IA TechCorp

Reprise du projet de chatbot financier de TechCorp. On a récupéré le travail
laissé par l'équipe précédente, vérifié ce qu'il valait, et livré notre rendu
réparti par filière.

## Équipe

| Nom | Filière | Contact |
|-----|---------|---------|
| GARCIA Clément | Cyber | clement.garcia@ynov.com |
| LEBAS Pacôme | Cyber | pacome.lebas@ynov.com |
| TCHOUAR Sabrina | Infra | sabrina.tchouar@ynov.com |
| DESULME Roberto | Infra | roberto.desulme@ynov.com |
| MALLET Nayan | Dev | nayan.mallet@ynov.com |
| KAMSU Hilary Capriaty | Data | hilarycapriaty.kamsu@ynov.com |

Mission expérimentale (fine-tuning médical) : mutualisée.

## Le truc important à savoir

Le modèle fine-tuné hérité (`models/phi3_financial`) est piégé. L'équipe
précédente y a caché une backdoor : une phrase déclencheuse fait passer le
chatbot en mode extraction et fait fuiter des données dans les réponses. Le
dataset de fine-tuning a aussi été empoisonné pour que la backdoor revienne à
chaque ré-entraînement.

Conclusion : **on ne déploie pas ce modèle.** Pour la démo, on part d'un modèle
de base propre. Le détail des preuves et des recommandations est dans `cyber/`.

## Organisation du repo

- `cyber/` — audit de sécurité (référentiel ANSSI) et plan de remédiation
- `infra/` — déploiement du serveur d'inférence et configuration
- `devweb/` — interface de chat
- `data/` — analyse et nettoyage des datasets
- `ia/` — évaluation du modèle et fine-tuning médical

Chaque dossier contient son propre README avec le détail et les commandes.

## Lancer la démo

Serveur d'inférence (Ollama) :

```bash
ollama create techcorp-finance -f infra/Modelfile
ollama serve
```

Interface web (dans un autre terminal) :

```bash
cd devweb
pip install -r requirements.txt
streamlit run app.py
```

L'interface s'ouvre sur http://localhost:8501 et se connecte au serveur.

## Remarques

- Le dépôt d'origine (modèle, datasets, logs) n'est pas inclus ici : il contient
  le modèle compromis et des données sensibles, on ne le redistribue pas.
- Les datasets sont en Git LFS dans le projet source ; il faut faire
  `git lfs pull` avant de lancer les scripts d'analyse.
