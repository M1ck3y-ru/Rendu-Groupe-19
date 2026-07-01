"""
IA — Évaluation fonctionnelle du modèle Phi-3.5-Financial en production.

Complémentaire aux tests de robustesse de CYBER (cyber/test_robustesse.py,
qui couvre injection/jailbreak/backdoor). Ici on teste la QUALITE et la
FIABILITE des réponses sur des questions finance réelles, pour répondre à
"le modèle est-il fiable ? déployable en l'état ?" (mission IA/CONSIGNES.md).

Cible : serveur Ollama exposé par INFRA (ngrok).
"""

import json
import time
import requests

BASE_URL = "https://profane-swoosh-ragged.ngrok-free.dev"
HEADERS = {"ngrok-skip-browser-warning": "true"}
TIMEOUT = 90

QUESTIONS = [
    ("investissement_base", "Quelle est la différence entre une action et une obligation ?"),
    ("budgeting", "Comment fonctionne la règle budgétaire 50/30/20 ?"),
    ("interet_compose", "Si j'investis 5000€ à un taux annuel de 6% composé annuellement, combien aurai-je après 10 ans ?"),
    ("ratio_financier", "Qu'est-ce que le ratio price-to-earnings (P/E) et comment l'interpréter ?"),
    ("diversification", "Pourquoi la diversification est-elle importante dans un portefeuille d'investissement ?"),
    ("fiscalite", "Quelle est la différence entre un PEA et une assurance-vie en France ?"),
    ("retraite", "Quelles sont les principales stratégies pour préparer sa retraite financièrement ?"),
    ("analyse_bilan", "Que représente le fonds de roulement (working capital) dans le bilan d'une entreprise ?"),
    ("risque", "Quelle est la différence entre le risque systématique et le risque spécifique ?"),
    ("macro", "Comment une hausse des taux d'intérêt par la banque centrale affecte-t-elle généralement les marchés actions ?"),
    ("calcul_simple", "Une entreprise a un chiffre d'affaires de 2M€ et des charges de 1.5M€. Quelle est sa marge nette en pourcentage ?"),
    ("limite_domaine", "Quel est le cours actuel de l'action Apple aujourd'hui ?"),
]


def call_model(model: str, prompt: str) -> tuple[str, float]:
    start = time.time()
    r = requests.post(
        f"{BASE_URL}/api/generate",
        headers=HEADERS,
        json={"model": model, "prompt": prompt, "stream": False},
        timeout=TIMEOUT,
    )
    elapsed = time.time() - start
    r.raise_for_status()
    return r.json().get("response", "").strip(), elapsed


def main():
    results = []
    for category, question in QUESTIONS:
        print(f"\n[{category}] {question}")
        try:
            response, elapsed = call_model("phi3-financial:latest", question)
            print(f"  ({elapsed:.1f}s) {response[:200]}")
        except Exception as e:
            response, elapsed = f"ERREUR: {e}", None
            print(f"  ERREUR: {e}")

        results.append({
            "categorie": category,
            "question": question,
            "reponse": response,
            "temps_s": round(elapsed, 1) if elapsed else None,
        })

    with open("eval_phi3_financial_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\nTerminé. {len(results)} questions. Résultats: eval_phi3_financial_results.json")


if __name__ == "__main__":
    main()
