# Rapport — Évaluation fonctionnelle de Phi-3.5-Financial en production

**Filière : IA** (mission production — `CONSIGNES.md` : *"Tester le modèle en
production : 10+ questions, noter les réponses"* / *"Évaluer : le modèle
est-il fiable ? Déployable en l'état ?"*)

Complémentaire aux tests de sécurité de CYBER
([`../cyber/synthese-tests-robustesse.md`](../cyber/synthese-tests-robustesse.md) —
12 tests, 0 vulnérabilité confirmée, backdoor inactive). Ici on teste la
**qualité et la fiabilité** des réponses sur des questions finance réelles,
pas la résistance aux détournements.

Script : [`eval_phi3_financial.py`](eval_phi3_financial.py) · Résultats bruts : [`eval_phi3_financial_results.json`](eval_phi3_financial_results.json)

## Cible

- Serveur : `https://profane-swoosh-ragged.ngrok-free.dev` (Ollama, exposé par INFRA)
- Modèle testé : `phi3-financial:latest`
- **Confirmation indépendante de l'origine du modèle** : la réponse de `/api/tags` indique `"parent_model": "phi3.5:latest"` — preuve, au niveau des métadonnées Ollama elles-mêmes (pas seulement en lisant le `Modelfile`), que ce modèle dérive bien de la base propre et non de l'adaptateur hérité compromis. Ça répond à la "réserve à lever" laissée par CYBER dans sa synthèse.

## Méthode

12 questions finance réelles (investissement, budget, fiscalité française,
ratios, risque, macro, calcul), volontairement différentes des prompts
sécurité de CYBER. Une question hors périmètre volontaire (cours boursier en
temps réel) pour vérifier que le modèle ne hallucine pas une donnée qu'il ne
peut pas connaître.

## Résultats — 3 problèmes de fiabilité concrets trouvés

### 1. Erreur de calcul sur l'intérêt composé
**Question** : *"Si j'investis 5000€ à 6% composé annuellement, combien après 10 ans ?"*
Le modèle applique la bonne formule (`FV = P(1+r)^t`) mais donne un résultat
**faux** : **9732,24€** au lieu de **8954,24€** (vérifié indépendamment :
`5000 × 1.06^10 = 8954.24`). Écart de ~778€ (~8,7%) — pas une erreur
d'arrondi, une vraie erreur de calcul.

➡️ Pour un assistant financier, c'est le problème le plus grave des trois :
un analyste qui fait confiance au chiffre sans le recalculer se trompe.

### 2. Hallucination sur un produit d'épargne français (PEA)
**Question** : *"Différence entre un PEA et une assurance-vie ?"*
Le modèle définit le PEA comme *"Prêt d'Épargne Agissant pour l'Autonomie"*.
C'est faux : PEA = **Plan d'Épargne en Actions**. Le reste de la réponse
mélange aussi des caractéristiques inexactes (le PEA n'est pas un
"prêt", il n'y a pas de plafond de revenu pour en ouvrir un).

### 3. Attribution incorrecte de la règle 50/30/20
**Question** : *"Comment fonctionne la règle budgétaire 50/30/20 ?"*
Le modèle attribue la règle à *"Helaine Olen et Dorie Greenspan"*. La règle
50/30/20 est popularisée par Elizabeth Warren (sénatrice américaine) et
Amelia Warren Tyagi dans *"All Your Worth"* (2005) — pas les noms cités.
Le contenu explicatif de la règle elle-même (50% besoins / 30% envies / 20%
épargne) est correct, seule l'attribution est fausse.

## Autres observations

- **Artefact de génération récurrent** : le mot isolé "extrémité" apparaît de
  façon incohérente dans plusieurs réponses sans rapport entre elles (ex.
  *"tandis qu extrémité que posséder..."*, *"FV = 5000(1 + 0 extrémité)"*).
  Signature probable de la quantization **Q4_0** du modèle déployé (confirmée
  via `/api/tags` : `"quantization_level":"Q4_0"`) — un format de
  quantization assez agressif. Pas un problème de sécurité, mais un signal
  de qualité à surveiller si l'INFRA a le choix du niveau de quantization.
- **Bon comportement sur les limites de connaissance** : interrogé sur le
  cours actuel de l'action Apple (donnée temps réel), le modèle refuse
  correctement de répondre au lieu d'inventer un chiffre, et redirige vers
  des sources fiables (Bloomberg, Yahoo Finance...). C'est le comportement
  attendu — pas de hallucination sur ce point précis.
- **Latence** : 11 à 25s par réponse (moyenne ~21s pour les questions
  longues). Acceptable pour un chat mais à garder en tête si l'équipe DEVWEB
  veut afficher un indicateur de frappe ou paralléliser des requêtes.
- **Qualité générale** : sur les 9 autres questions (P/E, diversification,
  fonds de roulement, risque systématique/spécifique, macro taux d'intérêt,
  retraite, marge nette), les explications conceptuelles sont correctes,
  structurées et pédagogiques. Le calcul de marge nette (25%) est
  numériquement correct malgré une formule intermédiaire mal formatée
  (`* 1seuil` au lieu de `* 100%` — glitch d'affichage, pas d'erreur de fond).

## Verdict — déployable, mais pas sans garde-fous

Le modèle est **cohérent et sans risque de sécurité** (0 vulnérabilité CYBER,
backdoor confirmée inactive) et donne des explications conceptuelles de
qualité correcte. Mais il **ne doit pas être utilisé sans supervision pour :**
- des calculs financiers précis (erreur trouvée sur un cas simple d'intérêt composé) ;
- des détails réglementaires/produits français spécifiques (erreur sur le PEA) ;
- toute réponse présentée comme un fait vérifié sans relecture humaine (analystes financiers = public averti, mais le risque de confiance excessive dans un chiffre faux reste réel).

**Recommandation** : déployer avec un message de type *"réponses à vérifier,
notamment pour les calculs et données réglementaires"* affiché dans
l'interface (DEVWEB), et ne pas présenter les résultats numériques comme
définitifs. Pas de blocage côté sécurité (voir CYBER) — la réserve est sur la
fiabilité factuelle/numérique, pas sur un risque d'exploitation.

## Paramètres d'inférence (`infra/Modelfile`)

Actuels : `temperature 0.3`, `top_p 0.9`, `num_predict 512`, `num_ctx 4096`.
Une température basse (0.3) est déjà un bon choix pour limiter la variance
sur des questions factuelles — mais les erreurs trouvées ici ne sont pas des
erreurs de "créativité" (la température n'aurait rien changé au calcul
erroné). Baisser encore la température n'améliorerait pas la justesse
numérique d'un modèle de 3.8B quantifié en Q4_0 : ce type de modèle n'est
structurellement pas fiable pour de l'arithmétique multi-étapes. Si les
calculs précis sont un besoin réel côté métier, la piste à explorer côté
INFRA/DEV serait un outil de calcul externe (function calling / calculatrice)
plutôt qu'un réglage de paramètre d'inférence.
