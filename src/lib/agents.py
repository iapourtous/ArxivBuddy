#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from typing import List, Dict, Any
from crewai import Agent, Task, Crew, Process
from crewai import LLM as CrewLLM
from crewai.memory import LongTermMemory, ShortTermMemory, EntityMemory
from crewai.memory.storage.ltm_sqlite_storage import LTMSQLiteStorage
from crewai.memory.storage.rag_storage import RAGStorage

# Import des outils spécifiques à ArxivBuddy
from .tools import search_arxiv, get_paper_by_id, get_paper_abstract, get_papers_by_query
from .config import get_config
from .custom_embedder import MultilingualE5Embedder

class ArxivAgents:
    """Classe pour gérer les agents CrewAI pour ArxivBuddy."""
    
    def __init__(self, api_key: str = None, model: str = None):
        """Initialise les agents avec les configurations depuis le système de config."""
        # Chargement de la configuration
        self.config = get_config()
        
        # Configuration de l'API
        self.api_key = api_key or self.config.get("crew", "api_key", default="")
        self.model = model or self.config.get("crew", "model", default="openrouter/openai/gpt-4.1-mini")
        self.temperature = self.config.get("crew", "temperature", default=0.7)
        self.max_tokens = self.config.get("crew", "max_tokens", default=4000)
        self.base_url = self.config.get("crew", "base_url", default="https://openrouter.ai/api/v1")
        
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
        # ------------------------------------------------------------------
        # Configuration du custom embedder et de la mémoire
        # ------------------------------------------------------------------
        # Embedder personnalisé pour les mémoires (multilingual-e5-large)
        self.custom_embedder = MultilingualE5Embedder()
        # Répertoire de stockage pour les données de mémoire
        storage_path = os.getenv("CREWAI_STORAGE_DIR", "./arxivbuddy_memory")
        os.makedirs(storage_path, exist_ok=True)
        print(f"Memory storage path configured at: {storage_path}")
        # Mémoire long terme (historique des interactions)
        self.long_term_memory = LongTermMemory(
            storage=LTMSQLiteStorage(db_path=f"{storage_path}/arxivbuddy_ltm.db")
        )
        # Mémoire court terme (RAG) avec embedder personnalisé
        self.short_term_memory = ShortTermMemory(
            storage=RAGStorage(
                type="short_term",
                embedder_config={"provider": "custom", "config": {"embedder": self.custom_embedder}},
                path=storage_path
            )
        )
        # Mémoire d'entités pour le suivi des concepts
        self.entity_memory = EntityMemory(
            storage=RAGStorage(
                type="entity",
                embedder_config={"provider": "custom", "config": {"embedder": self.custom_embedder}},
                path=storage_path
            )
        )
    
    def _create_agent_from_config(self, agent_type: str, tools: List = None) -> Agent:
        """
        Crée un agent à partir de sa configuration YAML.
        
        Args:
            agent_type: Type d'agent (query_parser, arxiv_searcher, etc.)
            tools: Liste d'outils à associer à l'agent (optionnel)
            
        Returns:
            Agent CrewAI configuré
        """
        agent_config = self.config.get_agent_config(agent_type)
        if not agent_config:
            raise ValueError(f"Configuration non trouvée pour l'agent '{agent_type}'")
            
        agent_args = {
            "role": agent_config.get("role", ""),
            "goal": agent_config.get("goal", ""),
            "backstory": agent_config.get("backstory", ""),
            "verbose": True,
            "allow_delegation": False,
            "llm": self.llm
        }
        
        # Ajouter les outils si fournis
        if tools:
            agent_args["tools"] = tools
            
        return Agent(**agent_args)
    
    def create_query_parser_agent(self) -> Agent:
        """
        Crée l'agent responsable d'analyser et d'optimiser les requêtes.
        
        Returns:
            Agent CrewAI pour l'analyse de requêtes
        """
        return self._create_agent_from_config("query_parser")
    
    def create_arxiv_searcher_agent(self) -> Agent:
        """
        Crée l'agent responsable de la recherche sur ArXiv.
        
        Returns:
            Agent CrewAI pour la recherche ArXiv
        """
        return self._create_agent_from_config("arxiv_searcher", tools=[search_arxiv])
    
    def create_paper_analyzer_agent(self) -> Agent:
        """
        Crée l'agent responsable d'analyser le contenu des articles.
        
        Returns:
            Agent CrewAI pour l'analyse d'articles
        """
        return self._create_agent_from_config("paper_analyzer", tools=[search_arxiv])
    
    def create_summarizer_agent(self) -> Agent:
        """
        Crée l'agent responsable de résumer et vulgariser les articles.
        
        Returns:
            Agent CrewAI pour le résumé d'articles
        """
        return self._create_agent_from_config("summarizer")
    
    def create_synthesizer_agent(self) -> Agent:
        """
        Crée l'agent responsable de la synthèse comparative des articles.
        
        Returns:
            Agent CrewAI pour la synthèse
        """
        return self._create_agent_from_config("synthesizer")
    
    def create_translator_agent(self) -> Agent:
        """
        Crée l'agent responsable de la traduction et adaptation du niveau.
        
        Returns:
            Agent CrewAI pour la traduction
        """
        return self._create_agent_from_config("translator")
        
    def create_professor_agent(self) -> Agent:
        """
        Crée l'agent responsable de la réponse pédagogique directe à la question.
        
        Returns:
            Agent CrewAI pour la réponse pédagogique
        """
        return self._create_agent_from_config("professor")
    
    def _create_task_from_prompt_config(self, prompt_type: str, agent: Agent, 
                                task_context: Dict[str, Any], context_tasks: List[Task] = None) -> Task:
        """
        Crée une tâche à partir de sa configuration de prompt YAML.
        
        Args:
            prompt_type: Type de prompt (query_parser, arxiv_search, etc.)
            agent: Agent qui effectuera la tâche
            task_context: Contexte spécifique à la tâche (variables à formater)
            context_tasks: Tâches contextuelles à inclure
            
        Returns:
            Tâche CrewAI configurée
        """
        prompt_config = self.config.get_prompt_config(prompt_type)
        if not prompt_config:
            raise ValueError(f"Configuration de prompt non trouvée pour '{prompt_type}'")
            
        # Formater la description de la tâche avec le contexte
        description = prompt_config.get("task_description", "")
        description = description.format(**task_context)
        
        # Formater le résultat attendu avec le contexte
        expected_output = prompt_config.get("expected_output", "")
        if "{" in expected_output and "}" in expected_output:
            expected_output = expected_output.format(**task_context)
        
        task_args = {
            "description": description,
            "agent": agent,
            "expected_output": expected_output
        }
        
        if context_tasks:
            task_args["context"] = context_tasks
            
        return Task(**task_args)
    
    def _create_query_parsing_task(self, agent: Agent, query: str) -> Task:
        """
        Crée une tâche d'analyse et transformation de la requête utilisateur.
        
        Args:
            agent: Agent qui effectuera la tâche
            query: Question originale de l'utilisateur
            
        Returns:
            Tâche CrewAI
        """
        return self._create_task_from_prompt_config(
            "query_parser", 
            agent, 
            {"question": query}
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
        return self._create_task_from_prompt_config(
            "arxiv_search", 
            agent, 
            {"max_results": max_results},
            context_tasks=[parsing_task]
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
        return self._create_task_from_prompt_config(
            "paper_analysis", 
            agent, 
            {},
            context_tasks=[search_task]
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
        
        return self._create_task_from_prompt_config(
            "summary", 
            agent, 
            {"audience": audience},
            context_tasks=[search_task, analysis_task, parsing_task]
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
        
        return self._create_task_from_prompt_config(
            "synthesis", 
            agent, 
            {"audience": audience},
            context_tasks=[summary_task, analysis_task, search_task]
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
        
        return self._create_task_from_prompt_config(
            "translation", 
            agent, 
            {"audience": audience},
            context_tasks=[summary_task, synthesis_task]
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
        return self._create_task_from_prompt_config(
            "professor", 
            agent, 
            {"query": query},
            context_tasks=[parsing_task, analysis_task, summary_task, synthesis_task]
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
        
        # Créer un contexte pour la tâche
        task_context = {
            "query": query
        }
        
        return self._create_task_from_prompt_config(
            "final_formatting", 
            agent, 
            task_context,
            context_tasks=context_tasks
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
        
        # Créer et exécuter l'équipage avec mémoire activée
        crew = Crew(
            agents=agents,
            tasks=tasks,
            verbose=True,
            process=Process.sequential,
            memory=True,
            long_term_memory=self.long_term_memory,
            short_term_memory=self.short_term_memory,
            entity_memory=self.entity_memory
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