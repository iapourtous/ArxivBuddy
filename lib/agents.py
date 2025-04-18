#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from typing import List, Dict, Any
from crewai import Agent, Task, Crew, Process
from crewai import LLM as CrewLLM
from dotenv import load_dotenv

# Import des outils spécifiques à ArxivBuddy
from .tools import search_arxiv, get_paper_by_id, get_paper_abstract, get_papers_by_query

class ArxivAgents:
    """Classe pour gérer les agents CrewAI pour ArxivBuddy."""
    
    def __init__(self, api_key: str = None, model: str = None):
        """Initialise les agents avec les configurations depuis .env."""
        # Chargement des variables d'environnement
        load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', '.env'))
        
        # Configuration de l'API
        self.api_key = api_key or os.getenv("CREW_API_KEY")
        self.model = model or os.getenv("CREW_MODEL", "openrouter/openai/gpt-4.1-mini")
        self.temperature = float(os.getenv("CREW_TEMPERATURE", "0.7"))
        self.max_tokens = int(os.getenv("CREW_MAX_TOKENS", "4000"))
        self.base_url = os.getenv("CREW_BASE_URL", "https://openrouter.ai/api/v1")
        
        # Configuration du LLM pour CrewAI
        try:
            self.llm = CrewLLM(
                model=self.model,
                api_key=self.api_key,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                base_url=self.base_url
            )
        except Exception as e:
            print(f"⚠️ Erreur lors de l'initialisation du LLM: {e}")
            print("Tentative avec une configuration simplifiée...")
            self.llm = CrewLLM(
                model=self.model,
                api_key=self.api_key
            )
    
    def create_query_parser_agent(self) -> Agent:
        """
        Crée l'agent responsable d'analyser et d'optimiser les requêtes.
        
        Returns:
            Agent CrewAI pour l'analyse de requêtes
        """
        return Agent(
            role="Expert en recherche scientifique",
            goal="Extraire les termes de recherche optimaux à partir d'une question",
            backstory="""Tu es un expert en recherche documentaire scientifique.
            Tu comprends parfaitement comment transformer des questions en langage naturel
            en requêtes de recherche optimisées. Tu sais comment identifier les concepts-clés,
            les termes techniques spécifiques, et les relations entre eux pour formuler
            des requêtes efficaces sur ArXiv.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    def create_arxiv_searcher_agent(self) -> Agent:
        """
        Crée l'agent responsable de la recherche sur ArXiv.
        
        Returns:
            Agent CrewAI pour la recherche ArXiv
        """
        return Agent(
            role="Spécialiste de recherche ArXiv",
            goal="Trouver les articles scientifiques les plus pertinents sur ArXiv",
            backstory="""Tu es un expert qui connaît parfaitement la base de 
            données ArXiv et ses catégories. Tu maîtrises l'art de la recherche
            documentaire scientifique et sais comment formuler des requêtes
            précises pour trouver les articles les plus pertinents.""",
            verbose=True,
            allow_delegation=False,
            tools=[search_arxiv],
            llm=self.llm
        )
    
    def create_paper_analyzer_agent(self) -> Agent:
        """
        Crée l'agent responsable d'analyser le contenu des articles.
        
        Returns:
            Agent CrewAI pour l'analyse d'articles
        """
        return Agent(
            role="Analyste de publications scientifiques",
            goal="Extraire et comprendre les informations clés des articles scientifiques",
            backstory="""Tu es un expert en analyse de publications scientifiques.
            Tu excelles dans l'extraction des informations essentielles, la compréhension
            des méthodologies, des résultats et des implications. Tu sais rapidement
            identifier l'importance et la pertinence d'un article par rapport à une
            question de recherche.""",
            verbose=True,
            allow_delegation=False,
            tools=[search_arxiv],
            llm=self.llm
        )
    
    def create_summarizer_agent(self) -> Agent:
        """
        Crée l'agent responsable de résumer et vulgariser les articles.
        
        Returns:
            Agent CrewAI pour le résumé d'articles
        """
        return Agent(
            role="Expert en vulgarisation scientifique",
            goal="Simplifier et résumer des articles scientifiques complexes",
            backstory="""Tu es un expert en vulgarisation scientifique. 
            Tu as un talent exceptionnel pour traduire des concepts scientifiques
            complexes en explications claires et accessibles, tout en préservant
            la précision et la nuance. Tu peux adapter ton niveau d'explication
            à différents publics, des experts aux débutants.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    def create_synthesizer_agent(self) -> Agent:
        """
        Crée l'agent responsable de la synthèse comparative des articles.
        
        Returns:
            Agent CrewAI pour la synthèse
        """
        return Agent(
            role="Analyste en recherche scientifique",
            goal="Créer une synthèse comparative et identifier les tendances",
            backstory="""Tu es un analyste spécialisé dans la comparaison de 
            travaux scientifiques. Tu identifies les similitudes, différences,
            et tendances émergentes entre plusieurs articles de recherche.
            Tu excelles dans la création de synthèses qui offrent une vue
            d'ensemble claire et structurée sur un sujet scientifique.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    def create_translator_agent(self) -> Agent:
        """
        Crée l'agent responsable de la traduction et adaptation du niveau.
        
        Returns:
            Agent CrewAI pour la traduction
        """
        return Agent(
            role="Traducteur et adaptateur de contenu scientifique",
            goal="Adapter le contenu scientifique selon le niveau et la langue",
            backstory="""Tu es un expert en traduction et adaptation de 
            contenu scientifique. Tu sais comment adapter des explications
            selon le niveau de l'audience (expert, étudiant, grand public)
            et traduire fidèlement en différentes langues, notamment en français.
            Tu préserves toujours la précision scientifique, même lorsque tu
            simplifies le contenu.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
    def create_professor_agent(self) -> Agent:
        """
        Crée l'agent responsable de la réponse pédagogique directe à la question.
        
        Returns:
            Agent CrewAI pour la réponse pédagogique
        """
        return Agent(
            role="Professeur pédagogue",
            goal="Fournir une réponse claire, précise et vulgarisée à la question de l'utilisateur",
            backstory="""Tu es un professeur exceptionnel, reconnu pour ta capacité à 
            expliquer des concepts scientifiques complexes de façon accessible et engageante.
            Tu excelles dans l'art de vulgariser sans sacrifier la rigueur scientifique.
            Tu sais adapter ton niveau d'explication selon le public, utiliser des analogies
            pertinentes et structurer tes réponses de manière pédagogique. Tu as un talent
            particulier pour aller directement à l'essentiel tout en donnant suffisamment
            de contexte pour une compréhension complète.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    def _create_query_parsing_task(self, agent: Agent, query: str) -> Task:
        """
        Crée une tâche d'analyse et transformation de la requête utilisateur.
        
        Args:
            agent: Agent qui effectuera la tâche
            query: Question originale de l'utilisateur
            
        Returns:
            Tâche CrewAI
        """
        return Task(
            description=f"""
            Analyse cette question en langage naturel: "{query}"
            
            INSTRUCTIONS:
            1. Identifie les concepts scientifiques et termes techniques clés
            2. Extrais les relations entre ces concepts
            3. Formule une requête de recherche optimisée pour ArXiv
            4. Utilise les opérateurs booléens appropriés (AND, OR) si nécessaire
            5. Traduis la requête en anglais si elle n'est pas déjà en anglais
            
            CONTRAINTES:
            - La requête doit être précise et ciblée
            - Priorise les termes techniques spécifiques plutôt que des mots généraux
            - Limite la requête à 3-5 termes/concepts clés maximum
            - N'utilise pas de guillemets sauf si nécessaire pour des expressions exactes
            
            Format de sortie attendu:
            {{
                "search_query": "Requête optimisée pour ArXiv (en anglais)",
                "keywords": ["mot-clé1", "mot-clé2", "mot-clé3"],
                "context": "Brève description du contexte et de l'intention de recherche"
            }}
            """,
            agent=agent,
            expected_output="Requête de recherche optimisée pour ArXiv"
        )
    
    def _create_arxiv_search_task(self, agent: Agent, parsing_task: Task, max_results: int) -> Task:
        """
        Crée une tâche de recherche sur ArXiv.
        
        Args:
            agent: Agent qui effectuera la tâche
            parsing_task: Tâche d'analyse dont le résultat sera utilisé
            max_results: Nombre maximum de résultats à retourner
            
        Returns:
            Tâche CrewAI
        """
        return Task(
            description=f"""
            Recherche sur ArXiv les articles correspondant à la requête optimisée.
            
            DONNÉES DE REQUÊTE:
            {{{{parsing_task.output}}}}
            
            INSTRUCTIONS:
            1. Utilise la requête optimisée pour rechercher des articles sur ArXiv
            2. Limite les résultats aux {max_results} articles les plus pertinents
            3. Privilégie les articles récents (moins de 2 ans si possible)
            4. Vérifie que les articles trouvés sont vraiment pertinents par rapport à la question originale
            5. Pour chaque article, collecte les informations suivantes:
               - Titre complet
               - Auteurs
               - Date de publication
               - ID ArXiv
               - URL
               - Résumé (abstract)
               - Catégories ArXiv
            
            CONTRAINTES:
            - Si moins de 3 articles pertinents sont trouvés, essaie de reformuler légèrement la requête
            - Assure-toi que les articles couvrent différents aspects de la question si possible
            - Évite les articles trop similaires entre eux
            
            Format de sortie attendu:
            {{
                "papers": [
                    {{
                        "title": "Titre de l'article 1",
                        "authors": ["Auteur 1", "Auteur 2"],
                        "published_date": "YYYY-MM-DD",
                        "arxiv_id": "XXXX.XXXXX",
                        "url": "https://arxiv.org/abs/XXXX.XXXXX",
                        "abstract": "Résumé de l'article",
                        "categories": ["cat1", "cat2"]
                    }},
                    // autres articles...
                ]
            }}
            """,
            agent=agent,
            context=[parsing_task],
            expected_output=f"Liste des {max_results} articles les plus pertinents d'ArXiv"
        )
    
    def _create_paper_analysis_task(self, agent: Agent, search_task: Task) -> Task:
        """
        Crée une tâche d'analyse des articles trouvés.
        
        Args:
            agent: Agent qui effectuera la tâche
            search_task: Tâche de recherche dont le résultat sera analysé
            
        Returns:
            Tâche CrewAI
        """
        return Task(
            description=f"""
            Analyse en profondeur chacun des articles scientifiques trouvés.
            
            LISTE DES ARTICLES:
            {{{{search_task.output}}}}
            
            INSTRUCTIONS:
            1. Analyse le résumé (abstract) de chaque article
            2. Identifie les points clés, méthodologies et résultats principaux
            3. Évalue la pertinence de chaque article par rapport à la question originale
            4. Identifie les concepts spécifiques et les contributions notables
            5. Note les limitations éventuelles mentionnées dans les résumés
            
            CONTRAINTES:
            - Reste factuel et objectif dans ton analyse
            - Concentre-toi sur les aspects scientifiques et techniques
            - Maintiens une perspective critique mais équilibrée
            
            Format de sortie attendu:
            {{
                "paper_analyses": [
                    {{
                        "arxiv_id": "XXXX.XXXXX",
                        "key_points": ["point 1", "point 2", "point 3"],
                        "methodology": "Description de la méthodologie",
                        "main_findings": "Principaux résultats",
                        "relevance": "Évaluation de la pertinence (1-10)",
                        "limitations": "Limitations éventuelles"
                    }},
                    // autres analyses...
                ]
            }}
            """,
            agent=agent,
            context=[search_task],
            expected_output="Analyse détaillée de chaque article"
        )
    
    def _create_summary_task(self, agent: Agent, analysis_task: Task, search_task: Task, 
                            parsing_task: Task, level: str) -> Task:
        """
        Crée une tâche de résumé des articles.
        
        Args:
            agent: Agent qui effectuera la tâche
            analysis_task: Tâche d'analyse dont le résultat sera résumé
            search_task: Tâche de recherche pour accéder aux données des articles
            parsing_task: Tâche d'analyse de requête pour le contexte original
            level: Niveau de détail souhaité (expert, medium, beginner)
            
        Returns:
            Tâche CrewAI
        """
        audience_map = {
            "expert": "un chercheur spécialisé dans le domaine",
            "medium": "un étudiant de master ou doctorant",
            "beginner": "une personne avec des connaissances scientifiques de base"
        }
        audience = audience_map.get(level, "un étudiant de master")
        
        return Task(
            description=f"""
            Crée un résumé simplifié des concepts principaux et découvertes à partir des articles analysés.
            
            DONNÉES DISPONIBLES:
            - Articles trouvés: {{{{search_task.output}}}}
            - Analyses des articles: {{{{analysis_task.output}}}}
            - Contexte de la recherche: {{{{parsing_task.output}}}}
            
            INSTRUCTIONS:
            1. Synthétise les informations essentielles des articles en 5-7 points clés
            2. Identifie les concepts principaux qui apparaissent dans plusieurs articles
            3. Explique les découvertes ou avancées majeures mentionnées
            4. Adapte ton niveau d'explication pour {audience}
            5. Organise l'information de manière claire et progressive
            
            CONTRAINTES:
            - Évite le jargon trop spécialisé sauf si le niveau est "expert"
            - Utilise des analogies ou exemples si utile pour clarifier (surtout pour "beginner")
            - Ne dépasse pas 300-400 mots pour le résumé complet
            - Reste factuel et précis, même en simplifiant
            
            Format de sortie attendu:
            {{
                "résumé_simplifié": "Texte du résumé détaillant les concepts et découvertes principales"
            }}
            """,
            agent=agent,
            context=[search_task, analysis_task, parsing_task],
            expected_output="Résumé simplifié des concepts et découvertes"
        )
    
    def _create_synthesis_task(self, agent: Agent, summary_task: Task, analysis_task: Task, 
                              search_task: Task, level: str) -> Task:
        """
        Crée une tâche de synthèse comparative des articles.
        
        Args:
            agent: Agent qui effectuera la tâche
            summary_task: Tâche de résumé pour le contexte
            analysis_task: Tâche d'analyse pour les détails des articles
            search_task: Tâche de recherche pour les données brutes des articles
            level: Niveau de détail souhaité (expert, medium, beginner)
            
        Returns:
            Tâche CrewAI
        """
        audience_map = {
            "expert": "un chercheur spécialisé dans le domaine",
            "medium": "un étudiant de master ou doctorant",
            "beginner": "une personne avec des connaissances scientifiques de base"
        }
        audience = audience_map.get(level, "un étudiant de master")
        
        return Task(
            description=f"""
            Crée une synthèse comparative des approches et solutions présentées dans les articles.
            
            DONNÉES DISPONIBLES:
            - Résumé simplifié: {{{{summary_task.output}}}}
            - Analyses des articles: {{{{analysis_task.output}}}}
            - Articles trouvés: {{{{search_task.output}}}}
            
            INSTRUCTIONS:
            1. Compare les différentes approches méthodologiques entre les articles
            2. Identifie les points de convergence et de divergence entre les recherches
            3. Dégage les tendances émergentes dans ce domaine de recherche
            4. Évalue l'évolution des approches si des articles couvrent différentes périodes
            5. Adapte ton niveau d'analyse pour {audience}
            
            CONTRAINTES:
            - Maintiens une perspective équilibrée et objective
            - Reste factuel et basé sur le contenu des articles
            - Limite la synthèse à 250-350 mots
            - Ne tire pas de conclusions qui vont au-delà de ce qui est présenté dans les articles
            
            Format de sortie attendu:
            {{
                "synthèse": "Texte de la synthèse comparative des approches et solutions"
            }}
            """,
            agent=agent,
            context=[summary_task, analysis_task, search_task],
            expected_output="Synthèse comparative des approches et solutions"
        )
    
    def _create_translation_task(self, agent: Agent, summary_task: Task, synthesis_task: Task, 
                                level: str) -> Task:
        """
        Crée une tâche de traduction et adaptation du contenu.
        
        Args:
            agent: Agent qui effectuera la tâche
            summary_task: Tâche de résumé dont le contenu sera traduit
            synthesis_task: Tâche de synthèse dont le contenu sera traduit
            level: Niveau de détail souhaité (expert, medium, beginner)
            
        Returns:
            Tâche CrewAI
        """
        audience_map = {
            "expert": "un chercheur spécialisé dans le domaine",
            "medium": "un étudiant de master ou doctorant",
            "beginner": "une personne avec des connaissances scientifiques de base"
        }
        audience = audience_map.get(level, "un étudiant de master")
        
        return Task(
            description=f"""
            Traduis en français et adapte le résumé et la synthèse selon le niveau demandé.
            
            CONTENU À TRADUIRE:
            - Résumé simplifié: {{{{summary_task.output}}}}
            - Synthèse comparative: {{{{synthesis_task.output}}}}
            
            INSTRUCTIONS:
            1. Traduis fidèlement le contenu en français
            2. Adapte le niveau de langage et d'explication pour {audience}
            3. Assure-toi que la terminologie scientifique est correctement traduite
            4. Préserve toutes les informations importantes du contenu original
            5. Maintiens la structure et l'organisation de l'information
            
            CONTRAINTES:
            - Évite les traductions mot-à-mot qui nuiraient à la compréhension
            - Adapte les expressions idiomatiques au contexte francophone
            - Conserve les termes techniques anglais entre parenthèses si nécessaire
            - Assure-toi que le texte est fluide et naturel en français
            
            Format de sortie attendu:
            {{
                "résumé_simplifié_fr": "Traduction française du résumé simplifié",
                "synthèse_fr": "Traduction française de la synthèse comparative"
            }}
            """,
            agent=agent,
            context=[summary_task, synthesis_task],
            expected_output="Traduction française du résumé et de la synthèse"
        )
    
    def _create_professor_task(self, agent: Agent, parsing_task: Task, analysis_task: Task, 
                              summary_task: Task, synthesis_task: Task, query: str) -> Task:
        """
        Crée une tâche pour le professeur pédagogue qui va répondre directement à la question.
        
        Args:
            agent: Agent qui effectuera la tâche
            parsing_task: Tâche d'analyse de la requête pour le contexte
            analysis_task: Tâche d'analyse des articles
            summary_task: Tâche de résumé
            synthesis_task: Tâche de synthèse
            query: Question originale de l'utilisateur
            
        Returns:
            Tâche CrewAI
        """
        return Task(
            description=f"""
            Réponds de manière pédagogique et vulgarisée à la question: "{query}"
            
            DONNÉES DISPONIBLES:
            - Contexte de la recherche: {{{{parsing_task.output}}}}
            - Analyses des articles: {{{{analysis_task.output}}}}
            - Résumé simplifié: {{{{summary_task.output}}}}
            - Synthèse comparative: {{{{synthesis_task.output}}}}
            
            INSTRUCTIONS:
            1. Rédige une réponse claire, directe et précise à la question posée
            2. Explique les concepts fondamentaux de manière accessible
            3. Illustre si pertinent avec des exemples concrets ou des analogies
            4. Structure ta réponse avec un début, un développement et une conclusion
            5. Adapte ton niveau de langage pour un public non spécialiste mais intéressé
            
            CONTRAINTES:
            - Va droit au but: commence par répondre directement à la question
            - Limite ta réponse à environ 300-500 mots
            - Évite le jargon technique excessif, explique les termes si nécessaire
            - Reste rigoureux scientifiquement tout en restant accessible
            - Utilise un ton pédagogique et engageant
            
            Format de sortie attendu:
            {{
                "réponse_pédagogique": "Texte de ta réponse pédagogique à la question"
            }}
            """,
            agent=agent,
            context=[parsing_task, analysis_task, summary_task, synthesis_task],
            expected_output="Réponse pédagogique à la question de l'utilisateur"
        )
        
    def _create_final_formatting_task(self, agent: Agent, search_task: Task, summary_task: Task,
                                     synthesis_task: Task, translation_task: Task = None,
                                     french: bool = True, query: str = "", professor_task: Task = None) -> Task:
        """
        Crée une tâche de formatage final des résultats.
        
        Args:
            agent: Agent qui effectuera la tâche
            search_task: Tâche de recherche pour les données des articles
            summary_task: Tâche de résumé pour le contenu du résumé
            synthesis_task: Tâche de synthèse pour le contenu de la synthèse
            translation_task: Tâche de traduction (optionnelle)
            french: Si True, utilise les versions françaises (par défaut: True)
            query: Question originale de l'utilisateur
            professor_task: Tâche du professeur pédagogue
            
        Returns:
            Tâche CrewAI
        """
        context_tasks = [search_task, summary_task, synthesis_task]
        if translation_task:
            context_tasks.append(translation_task)
        if professor_task:
            context_tasks.append(professor_task)
        
        language = "français"  # Toujours en français
        
        return Task(
            description=f"""
            Formate les résultats de recherche en un document markdown bien structuré.
            
            DONNÉES DISPONIBLES:
            - Articles trouvés: {{{{search_task.output}}}}
            - Résumé: {{{{summary_task.output}}}}
            - Synthèse: {{{{synthesis_task.output}}}}
            {f"- Traduction: {{{{translation_task.output}}}}" if translation_task else ""}
            {f"- Réponse pédagogique: {{{{professor_task.output}}}}" if "professor_task" in locals() else ""}
            
            QUESTION ORIGINALE:
            "{query}"
            
            INSTRUCTIONS:
            1. Crée un document markdown avec les sections suivantes DANS CET ORDRE:
               - Entête avec la question originale
               - ⚡ Réponse à la question (utilise la réponse pédagogique du professeur)
               - 🔍 Résumé des découvertes principales
               - 📚 Liste des articles recommandés (5 plus pertinents si possible)
               - 🧠 Synthèse comparative
            2. Pour chaque article recommandé, inclus:
               - Titre (en gras)
               - Auteurs principaux (en italique)
               - Lien vers l'article (format clickable)
               - Une ligne résumant son apport principal
            3. Utilise le contenu en {language}
            
            CONTRAINTES:
            - La section "Réponse à la question" doit être en premier et contenir la réponse pédagogique complète
            - Utilise une mise en forme markdown soignée (titres, listes, emphases)
            - Inclus des emojis pertinents pour les titres de sections comme indiqué
            - Mets en évidence les concepts et conclusions importantes (gras, italique)
            - Assure-toi que les liens vers les articles sont corrects et cliquables
            - Ajoute une séparation (---) entre chaque section principale
            
            IMPORTANT: FORMAT DE SORTIE
            Ton résultat final doit être directement un document markdown proprement formaté.
            N'inclus PAS de préambule comme "## Final Answer:" ou autre balise - juste le contenu markdown formaté.
            """,
            agent=agent,
            context=context_tasks,
            expected_output="Document markdown formaté avec les résultats"
        )
    
    def process_query(self, query: str, max_results: int = 5, french: bool = True, 
                     level: str = "medium") -> str:
        """
        Traite une requête utilisateur en déployant une équipe d'agents.
        
        Args:
            query: Question de l'utilisateur
            max_results: Nombre maximum d'articles à récupérer
            french: Si True, traduit les résultats en français
            level: Niveau d'explication (expert, medium, beginner)
            
        Returns:
            Résultat formaté au format markdown
        """
        # Créer les agents
        query_parser = self.create_query_parser_agent()
        arxiv_searcher = self.create_arxiv_searcher_agent()
        paper_analyzer = self.create_paper_analyzer_agent()
        summarizer = self.create_summarizer_agent()
        synthesizer = self.create_synthesizer_agent()
        translator = self.create_translator_agent() if french else None
        
        # Créer les tâches
        parsing_task = self._create_query_parsing_task(query_parser, query)
        search_task = self._create_arxiv_search_task(arxiv_searcher, parsing_task, max_results)
        analysis_task = self._create_paper_analysis_task(paper_analyzer, search_task)
        summary_task = self._create_summary_task(summarizer, analysis_task, search_task, parsing_task, level)
        synthesis_task = self._create_synthesis_task(synthesizer, summary_task, analysis_task, search_task, level)
        
        # Créer l'agent professeur et sa tâche
        professor = self.create_professor_agent()
        professor_task = self._create_professor_task(professor, parsing_task, analysis_task, summary_task, synthesis_task, query)
        
        # Liste des agents et tâches
        agents = [query_parser, arxiv_searcher, paper_analyzer, summarizer, synthesizer, professor]
        tasks = [parsing_task, search_task, analysis_task, summary_task, synthesis_task, professor_task]
        
        # Ajouter la tâche de traduction si nécessaire
        translation_task = None
        if french:
            translation_task = self._create_translation_task(translator, summary_task, synthesis_task, level)
            agents.append(translator)
            tasks.append(translation_task)
        
        # Ajouter la tâche de formatage final
        formatting_task = self._create_final_formatting_task(
            summarizer, search_task, summary_task, synthesis_task, 
            translation_task, french, query, professor_task
        )
        tasks.append(formatting_task)
        
        # Créer et exécuter l'équipage
        crew = Crew(
            agents=agents,
            tasks=tasks,
            verbose=True,
            process=Process.sequential
        )
        
        try:
            result = crew.kickoff()
            
            # Extraire le texte du résultat et le formater correctement
            if hasattr(result, 'raw'):
                result_text = result.raw
            else:
                result_text = str(result)
                
            # Si le résultat contient "## Final Answer:", extraire seulement la partie après
            if "## Final Answer:" in result_text:
                parts = result_text.split("## Final Answer:")
                if len(parts) > 1:
                    return parts[1].strip()
            
            return result_text
        except Exception as e:
            print(f"⚠️ Erreur lors du traitement de la requête: {str(e)}")
            return f"❌ Une erreur est survenue lors du traitement de votre requête: {str(e)}"