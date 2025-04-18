# ArxivBuddy

**L'IA qui lit les papiers de recherche pour toi (et te les traduit en humain)**

## 🎯 Use Case

Tu tapes une question genre :

```bash
python arxivSimpler.py "Quels sont les derniers résultats sur l'utilisation des transformers pour la biologie computationnelle ?"
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

```bash
# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt

# Configuration
# Copier le fichier d'exemple et ajoutez vos clés API
cp config/.env.example config/.env
# Modifier le fichier .env avec votre éditeur préféré pour ajouter votre clé API

# Le fichier .env doit contenir les informations suivantes :
# CREW_API_KEY=sk-or-v1-votre-clé-openrouter-ici
# CREW_MODEL=openai/gpt-4.1-mini
# CREW_TEMPERATURE=0.7
# CREW_MAX_TOKENS=4000
# CREW_BASE_URL=https://openrouter.ai/api/v1
# 
# ARXIV_MAX_RESULTS=5
# ARXIV_SORT_BY=submittedDate
# ARXIV_SORT_ORDER=descending
#
# Vous pouvez obtenir une clé API OpenRouter en vous inscrivant sur https://openrouter.ai
```

## 🚀 Utilisation

```bash
# Utilisation simple
python arxivSimpler.py "Quels sont les usages récents des transformers en biologie computationnelle ?"

# Avec options
python arxivSimpler.py "Quels sont les usages récents des transformers en biologie computationnelle ?" --french --level beginner
```

## Options

```
usage: arxivSimpler.py [-h] [--max-results MAX_RESULTS] [--french] [--level {expert,medium,beginner}] [query]

ArxivBuddy - L'IA qui lit les papiers de recherche pour toi

positional arguments:
  query                 Votre question de recherche

options:
  -h, --help            show this help message and exit
  --max-results MAX_RESULTS
                        Nombre maximum de papiers à récupérer
  --french              Traduire les résultats en français
  --level {expert,medium,beginner}
                        Niveau de simplification (expert, medium, beginner)
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
