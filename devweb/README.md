# TechCorp AI Chat Interface - Client Web Financier

Cette interface moderne, responsive et performante permet de communiquer avec l'assistant financier **Phi-3.5-Financial** via le serveur d'inférence Ollama distant hébergé sur ngrok.

## 🚀 Fonctionnalités
- **Historique complet** : Affichage soigné de l'historique de chat, géré de façon centralisée grâce à **Pinia**.
- **Réponses en temps réel (Streaming)** : Gestion du streaming de l'API Ollama pour afficher les réponses mot par mot sans blocage de l'interface.
- **Indicateur de connexion dynamique** : Statut en direct (Connecté / Déconnecté) avec mise à jour automatique en temps réel via un GET régulier sur la racine `/` et mesure de la latence (ms).
- **Header anti-intercepteur ngrok** : Injection automatique du header `"ngrok-skip-browser-warning": "true"` à toutes les requêtes afin de court-circuiter l'intercepteur HTML de ngrok et de garantir le bon déroulement des appels API.
- **Panneau de configuration avancée** : Réglages d'inférence (température, top_p, max tokens) et sélection du modèle.
- **Mapping transparent du modèle** : L'interface affiche le modèle requis `"Phi-3.5-Financial"`, tandis que les requêtes API sont adressées en arrière-plan à la balise Ollama correspondante `"phi3-financial:latest"` pour assurer la compatibilité.

---

## 🛠️ Installation & Démarrage

### 1. Prérequis
- Node.js (version v18 ou supérieure recommandée)
- npm (installé d'office avec Node.js)

### 2. Installer les dépendances
Depuis ce dossier `rendu/devweb/`, exécutez la commande suivante pour installer Vue 3, Vite, TypeScript, Pinia et ofetch :
```bash
npm install
```

### 3. Lancer le serveur de développement
Pour démarrer l'application locale en mode développement avec rechargement à chaud :
```bash
npm run dev
```
Une fois démarré, ouvrez le lien affiché dans votre terminal dans votre navigateur (généralement [http://localhost:5173](http://localhost:5173)).

### 4. Build de production
Pour compiler l'application de façon optimisée pour la production :
```bash
npm run build
```

---

## ⚙️ Spécifications API & Configuration
- **URL du serveur distant** : `https://profane-swoosh-ragged.ngrok-free.dev`
- **Vérification d'état (GET)** : Fait un appel GET sur la racine `/` avec le header `ngrok-skip-browser-warning`.
- **Envoi des messages (POST)** : Fait un appel POST sur `/api/chat` avec le modèle `"phi3-financial:latest"` (associé à `"Phi-3.5-Financial"` dans l'UI).
