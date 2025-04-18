#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import arxiv
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

class ArxivSearcher:
    """Classe pour rechercher des articles sur ArXiv."""
    
    def __init__(self):
        """Initialise le chercheur ArXiv avec les paramètres par défaut."""
        self.max_results = int(os.getenv('ARXIV_MAX_RESULTS', '5'))
        # Utiliser directement les enums de arxiv.SortCriterion et arxiv.SortOrder
        # Utiliser le tri par pertinence (Relevance) par défaut
        self.sort_criterion = arxiv.SortCriterion.Relevance
        self.sort_order = arxiv.SortOrder.Descending
    
    def search(self, query: str, max_results: Optional[int] = None, 
               categories: Optional[List[str]] = None, 
               date_range: Optional[int] = 365) -> List[Dict[str, Any]]:
        """
        Recherche des articles sur ArXiv selon les critères spécifiés.
        
        Args:
            query: Chaîne de recherche
            max_results: Nombre maximum de résultats (par défaut: valeur de .env)
            categories: Liste des catégories ArXiv à inclure
            date_range: Limite de date en jours (par défaut: 1 an)
            
        Returns:
            Liste de dictionnaires contenant les informations des articles
        """
        if max_results is None:
            max_results = self.max_results
        
        # Préparer la requête
        search_query = query
        
        # Ajouter les filtres de catégorie si spécifiés
        if categories:
            cat_filter = " AND (" + " OR ".join([f"cat:{cat}" for cat in categories]) + ")"
            search_query += cat_filter
        
        # Configuration de la recherche
        search = arxiv.Search(
            query=search_query,
            max_results=max_results,
            sort_by=self.sort_criterion,
            sort_order=self.sort_order
        )
        
        # Récupérer et filtrer les résultats
        papers = []
        for result in search.results():
            # On ne filtre plus par date car les dates de publication ArXiv peuvent être
            # dans un format différent (timezone aware vs naive)
            # Le tri par SubmittedDate fourni par l'API ArXiv est suffisant
                
            # Extraire les informations pertinentes
            paper = {
                'id': result.entry_id,
                'title': result.title,
                'authors': [author.name for author in result.authors],
                'summary': result.summary,
                'published': result.published,
                'pdf_url': result.pdf_url,
                'categories': result.categories
            }
            papers.append(paper)
            
            # Arrêter si on a atteint le nombre maximal de résultats
            if len(papers) >= max_results:
                break
        
        return papers
    
    def get_paper_by_id(self, paper_id: str) -> Dict[str, Any]:
        """
        Récupère un article spécifique par son ID ArXiv.
        
        Args:
            paper_id: ID ArXiv de l'article
            
        Returns:
            Dictionnaire contenant les informations de l'article
        """
        search = arxiv.Search(id_list=[paper_id])
        result = next(search.results())
        
        paper = {
            'id': result.entry_id,
            'title': result.title,
            'authors': [author.name for author in result.authors],
            'summary': result.summary,
            'published': result.published,
            'pdf_url': result.pdf_url,
            'categories': result.categories
        }
        
        return paper