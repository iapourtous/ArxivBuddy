# ArxivBuddy

**L'IA qui lit les papiers de recherche pour toi (et te les traduit en humain)**

## 🎯 Use Case

Tu tapes une question genre :

```bash
python -m arxivbuddy.cli "Quels sont les derniers résultats sur l'utilisation des transformers pour la biologie computationnelle ?"
```

Et il te répond :
- avec 3 à 5 papiers récents (résumés + liens)
- un résumé global vulgarisé
- une synthèse des approches/solutions
- option : traduction en français / mode "grand public"

## 🛠 Fonctionnalités

- 🔍 Recherche ArXiv par mots-clés + filtres (date, domaine, etc.)
- 📄 Récupération des abstracts / intro / conclusion
- 🧠 Vulgarisation auto via LLM
- 🧪 Synthèse comparative des papiers
- 🗣 Traduction auto (optionnelle)
- 📎 Liens directs vers les PDFs
- 💬 Mode chat pour poser plusieurs questions dans un même fil

## 🤖 Agents

ArxivBuddy utilise une architecture modulaire basée sur CrewAI :

- **QueryParser** : extrait les bons mots-clés et domaines
- **ArxivSearcher** : utilise l'API ArXiv pour trouver les bons papiers
- **PaperSummarizer** : lit les abstracts et simplifie
- **Synthesizer** : fusionne les infos, extrait les tendances/méthodes
- **Translator** (option) : traduit ou adapte selon le niveau souhaité

## 💻 Installation

### Installation à partir des sources

```bash
# Cloner le dépôt
git clone https://github.com/ton-org/arxivbuddy.git
cd arxivbuddy

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Installer le package en mode développement
pip install -e .

# Configuration - Créer et configurer le fichier .env
mkdir -p config
cp config/.env.example config/.env
# Modifier le fichier .env avec votre éditeur préféré pour ajouter votre clé API
```

Le fichier `.env` doit contenir les informations suivantes :
```
CREW_API_KEY=sk-or-v1-votre-clé-openrouter-ici
CREW_MODEL=openai/gpt-4.1-mini
CREW_TEMPERATURE=0.7
CREW_MAX_TOKENS=4000
CREW_BASE_URL=https://openrouter.ai/api/v1

ARXIV_MAX_RESULTS=5
ARXIV_SORT_BY=submittedDate
ARXIV_SORT_ORDER=descending
```

Vous pouvez obtenir une clé API OpenRouter en vous inscrivant sur https://openrouter.ai

### Installation via pip (à venir)

```bash
pip install arxivbuddy
```

## 🚀 Utilisation

### En mode développement (après pip install -e .)

```bash
# Utilisation directe avec python -m
python -m arxivbuddy.cli "Quels sont les usages récents des transformers en biologie computationnelle ?"

# Avec options
python -m arxivbuddy.cli "Quels sont les usages récents des transformers en biologie computationnelle ?" --level beginner

# OU en utilisant les points d'entrée installés (selon votre environnement)
arxivbuddy "Quels sont les usages récents des transformers en biologie computationnelle ?"
```

## Options

```
usage: cli.py [-h] [--max-results MAX_RESULTS] [--level {expert,medium,beginner}] [--api-key API_KEY] [--model MODEL] [query]

ArxivBuddy - L'IA qui lit les papiers de recherche pour toi

positional arguments:
  query                 Votre question de recherche

options:
  -h, --help            show this help message and exit
  --max-results MAX_RESULTS
                        Nombre maximum de papiers à récupérer
  --level {expert,medium,beginner}
                        Niveau de simplification (expert, medium, beginner)
  --api-key API_KEY     Clé API pour le modèle LLM (si non défini dans .env)
  --model MODEL         Nom du modèle LLM à utiliser (défini dans .env par défaut)
```

## 📝 Exemple de résultat

```markdown
### Résultat de votre question :
*Quels sont les usages récents des transformers en biologie computationnelle ?*

---

#### 🧬 Résumé simplifié :
Les transformers sont utilisés pour :
- prédire les structures de protéines (ex: AlphaFold-like)
- modéliser des séquences génomiques comme des phrases
- améliorer l'analyse de données single-cell RNA-seq

---

#### 📚 Papiers recommandés :

1. **"Transformer-based protein structure prediction"**  
   *arxiv.org/abs/2303.xxxxx*  
   → Présente un modèle inspiré de GPT pour la 3D des protéines.

2. **"Genomic BERT: Pretraining on DNA sequences"**  
   *arxiv.org/abs/2401.xxxxx*  
   → Fine-tuning de BERT pour classifier des séquences ADN.

3. **"Multi-omics data integration using transformers"**  
   *arxiv.org/abs/2312.xxxxx*  
   → Approche multi-vues pour données biologiques complexes.

---

#### 🔍 Synthèse :
Les transformers permettent de mieux apprendre les patterns dans l'ADN et ARN. La tendance va vers des modèles pré-entraînés sur de larges bases biologiques, souvent adaptés du NLP.
```

## 📂 Architecture du projet

```
arxivbuddy/
├── config/
│   ├── .env             # Variables d'environnement (à créer)
│   └── .env.example     # Exemple de fichier .env
├── src/
│   ├── arxivbuddy/      # Package principal
│   │   ├── __init__.py  # Initialisation du package
│   │   └── cli.py       # Interface en ligne de commande
│   └── lib/             # Bibliothèques partagées
│       ├── __init__.py
│       ├── agents.py    # Définition des agents IA
│       ├── arxiv_api.py # Interface avec l'API ArXiv
│       ├── summarizer.py # Résumé et vulgarisation
│       ├── tools.py     # Outils pour les agents
│       └── utils.py     # Utilitaires généraux
├── pyproject.toml       # Configuration du package et dépendances
└── README.md            # Documentation
```

## 🧪 Limitations

- Nécessite une connexion internet pour accéder à l'API ArXiv
- Les requêtes complexes peuvent prendre du temps à traiter
- La qualité des résumés dépend du modèle LLM utilisé