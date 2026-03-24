# EuroMacro Copilot

EuroMacro Copilot est un prototype de chatbot specialise en economie de la zone euro. Il combine :

- un corpus documentaire local ou officiel,
- un moteur de recherche local,
- une couche analytique macroeconomique,
- une interface web Streamlit,
- un notebook de demonstration.

Le projet vise un usage de support a la decision pour les PME, directions financieres et cabinets de conseil : expliquer la politique monetaire, interpreter les narratifs macro et traduire ces signaux en recommandations sur les prix, l'investissement, le financement et le recrutement.

## Ce que fait le prototype

- charge automatiquement les documents dans `data/documents/` et `data/external/`
- decoupe et indexe le corpus
- detecte des narratifs macro
- calcule un score d'incertitude macro a partir des textes
- lit un jeu de series macro de demonstration dans `data/series/euro_macro_demo.csv`
- genere une reponse structuree avec citations, sources et documents complementaires
- utilise Ollama avec `mistral:latest` par defaut quand un modele local est disponible
- peut aussi utiliser un endpoint compatible OpenAI
- bascule sinon vers une reponse heuristique deterministe

## Structure

```text
.
|-- app.py
|-- notebooks/
|-- scripts/
|-- src/euromacro_copilot/
|-- data/
|   |-- documents/
|   |-- external/
|   `-- series/
`-- tests/
```

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -e .
```

Optionnel :

```bash
copy .env.example .env
```

Configuration locale recommandee :

```env
LLM_PROVIDER=ollama
OLLAMA_MODEL=mistral:latest
OLLAMA_API_BASE=http://127.0.0.1:11434

LLM_API_KEY=
LLM_MODEL=gpt-4o-mini
LLM_API_BASE=https://api.openai.com/v1
```

## Lancer l'application web

```bash
streamlit run app.py
```

## Lancer le notebook

```bash
jupyter notebook notebooks/EuroMacro_Copilot_Demo.ipynb
```

## Ajouter tes propres sources

1. Depose tes fichiers `.md`, `.txt`, `.html` ou `.pdf.txt` dans `data/documents/`.
2. Depose les exports officiels telecharges dans `data/external/`.
3. Relance l'application. Le corpus est recharge automatiquement.

Le chargeur reconnait deja :

- les notes Markdown et texte,
- les pages HTML sauvegardees localement,
- le CSV officiel des discours BCE `all_ECB_speeches.csv`,
- les fichiers avec front matter simple `title:` / `url:` pour associer un lien officiel a un document local.

Exemple de front matter :

```md
---
title: Conditions de credit dans la zone euro
url: https://www.ecb.europa.eu/stats/ecb_surveys/bank_lending_survey/html/index.en.html
theme: financement
---
```

## Enrichir le corpus avec des sources officielles

Le script `scripts/fetch_official_sources.py` sait telecharger plusieurs presets :

- `ecb_speeches`
- `ecb_accounts_index`
- `ecb_bank_lending_survey`
- `ecb_data_portal_overview`
- `eurostat_api_intro`
- `ec_business_surveys`

Exemple :

```bash
python scripts/fetch_official_sources.py --preset ecb_speeches --preset ecb_bank_lending_survey
```

## Sources officielles recommandees

- ECB speeches dataset : `https://www.ecb.europa.eu/press/key/html/downloads.en.html`
- ECB monetary policy accounts : `https://www.ecb.europa.eu/press/accounts/html/index.en.html`
- ECB Bank Lending Survey : `https://www.ecb.europa.eu/stats/ecb_surveys/bank_lending_survey/html/index.en.html`
- ECB Data Portal API overview : `https://data.ecb.europa.eu/help/api/overview`
- Eurostat API introduction : `https://ec.europa.eu/eurostat/web/user-guides/data-browser/api-data-access/api-introduction`
- European Commission business surveys : `https://economy-finance.ec.europa.eu/economic-forecast-and-surveys/business-and-consumer-surveys_en`

## Important

- Les series dans `data/series/euro_macro_demo.csv` sont des donnees de demonstration, pas des donnees officielles en temps reel.
- Le projet est volontairement modulaire : tu peux brancher un autre LLM, remplacer le moteur de recherche ou ajouter un pipeline econometrique plus riche.
- Le module analytique reste heuristique : il sert de couche interpretable entre les textes et la reponse du chatbot.

## Validation rapide

```bash
python -m unittest discover -s tests -v
```
