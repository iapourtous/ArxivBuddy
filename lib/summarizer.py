#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import json
from typing import List, Dict, Any
import litellm
from dotenv import load_dotenv

class PaperSummarizer:
    """Classe pour résumer et analyser des papiers de recherche."""
    
    def __init__(self):
        """Initialise le résumeur avec les clés API et configurations."""
        # Chargement des variables d'environnement
        load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', '.env'))
        
        # Configuration de l'API pour le LLM
        self.api_key = os.getenv("CREW_API_KEY")
        self.model = os.getenv("CREW_MODEL", "openai/gpt-4.1-mini")
        self.temperature = float(os.getenv("CREW_TEMPERATURE", "0.7"))
        self.max_tokens = int(os.getenv("CREW_MAX_TOKENS", "4000"))
        self.base_url = os.getenv("CREW_BASE_URL", "https://openrouter.ai/api/v1")
        
        # Configuration de litellm
        litellm.api_key = self.api_key
        litellm.custom_base_url = self.base_url
    
    def summarize_papers(self, papers: List[Dict[str, Any]], query: str,
                         level: str = "medium", french: bool = False) -> Dict[str, Any]:
        """
        Génère un résumé et une analyse de plusieurs papiers de recherche.
        
        Args:
            papers: Liste des papiers (dictionnaires)
            query: Question originale de l'utilisateur
            level: Niveau de simplification (expert, medium, beginner)
            french: Si True, traduit les résultats en français
            
        Returns:
            Dictionnaire contenant le résumé simplifié et la synthèse
        """
        # Vérifier qu'il y a des papiers à résumer
        if not papers:
            return {
                "résumé_simplifié": "Aucun papier n'a été trouvé pour cette recherche.",
                "synthèse": "Impossible de générer une synthèse sans articles."
            }
            
        # Créer le prompt pour le LLM
        paper_info = self._format_papers_for_prompt(papers)
        language = "français" if french else "anglais"
        
        audience_map = {
            "expert": "un chercheur dans le domaine",
            "medium": "un étudiant de master",
            "beginner": "quelqu'un avec des connaissances de base du sujet"
        }
        
        audience = audience_map.get(level, "un étudiant de master")
        
        prompt = f"""
        # CONTEXTE
        Tu es un assistant spécialisé pour vulgariser la recherche scientifique.
        
        # TÂCHE
        Analyse ces {len(papers)} articles scientifiques d'ArXiv et réponds à cette question : "{query}"
        
        # ARTICLES
        {paper_info}
        
        # INSTRUCTIONS
        1. Crée un résumé simplifié des concepts principaux et découvertes (environ 3-5 points clés)
        2. Génère une synthèse comparative des approches et solutions présentées dans ces articles
        3. Rédige ta réponse en {language}
        4. Adapte ton explication pour {audience}
        5. Utilise un ton informatif mais accessible
        
        # FORMAT DE SORTIE
        Réponds strictement dans ce format sans aucun préambule ni texte supplémentaire:
        ```json
        {{
            "résumé_simplifié": "Les points clés et découvertes principales résumés en 3-5 lignes",
            "synthèse": "Une analyse comparative des approches et solutions des papiers"
        }}
        ```
        """
        
        # Appeler le LLM avec litellm
        try:
            response = litellm.completion(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            # Extraire et parser la réponse du LLM
            content = response.choices[0].message.content
            
            # Tenter d'extraire un JSON valide de la réponse
            try:
                # Chercher un bloc JSON entre ```json et ```
                json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    # Sinon, essayer d'extraire tout ce qui ressemble à un JSON
                    json_str = re.search(r'({.*})', content, re.DOTALL).group(1)
                
                # Parser le JSON
                result = json.loads(json_str)
                
                # Vérifier que les clés attendues sont présentes
                if "résumé_simplifié" not in result or "synthèse" not in result:
                    raise ValueError("Format JSON invalide: clés manquantes")
                
                return result
                
            except (json.JSONDecodeError, AttributeError, ValueError) as e:
                print(f"⚠️ Erreur lors du parsing de la réponse JSON: {str(e)}")
                # Analyser manuellement la réponse
                return self._parse_response_manually(content)
                
        except Exception as e:
            print(f"⚠️ Erreur lors de la génération du résumé: {str(e)}")
            return {
                "résumé_simplifié": f"Une erreur est survenue lors de l'analyse des papiers: {str(e)}",
                "synthèse": "Impossible de générer une synthèse en raison d'une erreur."
            }
    
    def _parse_response_manually(self, content: str) -> Dict[str, str]:
        """
        Parse manuellement la réponse si le parsing JSON échoue.
        
        Args:
            content: Contenu de la réponse du LLM
            
        Returns:
            Dictionnaire avec résumé et synthèse
        """
        lines = content.split('\n')
        resume = []
        synthese = []
        current_section = None
        
        for line in lines:
            clean_line = line.strip()
            
            # Identifier la section
            if "résumé" in clean_line.lower() or "resumé" in clean_line.lower():
                current_section = "resume"
                continue
            elif "synthèse" in clean_line.lower() or "synthese" in clean_line.lower():
                current_section = "synthese"
                continue
                
            # Collecter le contenu de la section
            if current_section == "resume" and clean_line and not any(x in clean_line for x in ["{", "}", "```", "#"]):
                resume.append(clean_line)
            elif current_section == "synthese" and clean_line and not any(x in clean_line for x in ["{", "}", "```", "#"]):
                synthese.append(clean_line)
        
        # Construire le résultat
        return {
            "résumé_simplifié": "\n".join(resume).strip(),
            "synthèse": "\n".join(synthese).strip()
        }
    
    def _format_papers_for_prompt(self, papers: List[Dict[str, Any]]) -> str:
        """
        Formate les papiers pour le prompt du LLM.
        
        Args:
            papers: Liste des papiers à formater
            
        Returns:
            Chaîne formatée pour le LLM
        """
        formatted_papers = ""
        
        for i, paper in enumerate(papers, 1):
            authors = ", ".join(paper["authors"][:3])
            if len(paper["authors"]) > 3:
                authors += ", et al."
                
            formatted_papers += f"""
            ## Article {i}:
            Titre: {paper["title"]}
            Auteurs: {authors}
            Date: {paper["published"].strftime("%Y-%m-%d")}
            ID ArXiv: {paper["id"]}
            
            Résumé:
            {paper["summary"]}
            
            Catégories: {", ".join(paper["categories"])}
            
            ---
            """
        
        return formatted_papers