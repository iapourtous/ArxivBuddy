#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module de résumé et vulgarisation d'articles scientifiques pour ArxivBuddy.
"""

from typing import List, Dict, Any
import re

class Summarizer:
    """Classe pour le résumé et la vulgarisation d'articles scientifiques."""
    
    def __init__(self):
        """Initialise le résumeur avec les configurations par défaut."""
        self.modes = {
            "expert": "Conserve le langage technique et les détails spécifiques",
            "medium": "Simplifie légèrement tout en gardant la rigueur scientifique",
            "beginner": "Vulgarise au maximum, utilise des analogies et évite le jargon"
        }
    
    def simplify_abstract(self, abstract: str, level: str = "medium") -> str:
        """
        Simplifie un résumé d'article selon le niveau spécifié.
        
        Args:
            abstract: Texte du résumé (abstract) de l'article
            level: Niveau de simplification (expert, medium, beginner)
            
        Returns:
            Résumé simplifié
        """
        # Cette méthode est un placeholder - dans l'implémentation réelle, 
        # on utiliserait un LLM via CrewAI pour faire la simplification
        
        # Nettoyer le texte basiquement
        clean_abstract = re.sub(r'\s+', ' ', abstract).strip()
        
        # Création d'un message pour indiquer ce qui serait fait
        level_description = self.modes.get(level, self.modes["medium"])
        result = f"[Résumé simplifié ({level}): {level_description}]\n\n{clean_abstract}"
        
        return result
    
    def summarize_papers(self, papers: List[Dict[str, Any]], level: str = "medium") -> Dict[str, Any]:
        """
        Résume une liste d'articles selon le niveau spécifié.
        
        Args:
            papers: Liste de dictionnaires représentant les articles
            level: Niveau de simplification (expert, medium, beginner)
            
        Returns:
            Dictionnaire contenant le résumé global et les résumés individuels
        """
        # Cette méthode est un placeholder - dans l'implémentation réelle,
        # on utiliserait un LLM via CrewAI pour faire les résumés
        
        paper_summaries = []
        for paper in papers:
            simplified = self.simplify_abstract(paper.get('summary', ''), level)
            paper_summaries.append({
                'title': paper.get('title', 'Sans titre'),
                'authors': paper.get('authors', []),
                'summary': simplified,
                'id': paper.get('id', '')
            })
        
        # Création d'un résumé global (placeholder)
        global_summary = f"[Résumé global des {len(papers)} articles au niveau {level}]"
        
        return {
            'global_summary': global_summary,
            'paper_summaries': paper_summaries
        }