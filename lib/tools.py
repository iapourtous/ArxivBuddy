#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Outils pour ArxivBuddy.

Ce module contient les outils utilisés par les agents CrewAI d'ArxivBuddy
pour interagir avec l'API ArXiv et traiter les articles scientifiques.
"""

import os
import json
from typing import List, Dict, Any, Optional
import arxiv
from datetime import datetime, timedelta
from crewai.tools import tool, BaseTool

# Configuration par défaut
MAX_RESULTS = int(os.getenv('ARXIV_MAX_RESULTS', '5'))
SORT_CRITERION = getattr(arxiv.SortCriterion, os.getenv('ARXIV_SORT_BY', 'Relevance'))
SORT_ORDER = getattr(arxiv.SortOrder, os.getenv('ARXIV_SORT_ORDER', 'Descending'))

@tool("search_arxiv")
def search_arxiv(query: str, max_results: int = 5, categories: str = None) -> str:
    """
    Recherche des articles sur ArXiv selon une requête et des catégories optionnelles.
    
    Args:
        query: Chaîne de recherche
        max_results: Nombre maximum de résultats (par défaut: 5)
        categories: Catégories ArXiv séparées par des virgules (ex: "cs.AI,cs.CL")
        
    Returns:
        Résultats de recherche au format JSON
    """
    try:
        # Préparer la requête
        search_query = query
        
        # Ajouter les filtres de catégorie si spécifiés
        if categories:
            cat_list = [cat.strip() for cat in categories.split(",")]
            cat_filter = " AND (" + " OR ".join([f"cat:{cat}" for cat in cat_list]) + ")"
            search_query += cat_filter
        
        # Configuration de la recherche
        search = arxiv.Search(
            query=search_query,
            max_results=max_results,
            sort_by=SORT_CRITERION,
            sort_order=SORT_ORDER,
        )
        
        # Récupérer les résultats
        papers = []
        for result in search.results():
            # Extraire les informations pertinentes
            paper = {
                "id": result.entry_id,
                "title": result.title,
                "authors": [author.name for author in result.authors],
                "summary": result.summary,
                "published": result.published.strftime("%Y-%m-%d"),
                "pdf_url": result.pdf_url,
                "categories": result.categories
            }
            papers.append(paper)
            
            # Arrêter si on a atteint le nombre maximal de résultats
            if len(papers) >= max_results:
                break
        
        # Convertir en JSON
        result_json = {
            "query": query,
            "papers": papers,
            "total_results": len(papers)
        }
        
        return json.dumps(result_json, ensure_ascii=False, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Erreur lors de la recherche sur ArXiv: {str(e)}"})

@tool("get_papers_by_query")
def get_papers_by_query(query: str, max_results: int = 5, sort_by: str = "relevance", date_range_days: int = 365) -> str:
    """
    Version plus avancée de la recherche ArXiv avec options de tri et de filtrage par date.
    
    Args:
        query: Chaîne de recherche
        max_results: Nombre maximum de résultats (par défaut: 5)
        sort_by: Critère de tri (relevance, submitted_date, last_updated_date)
        date_range_days: Limite de date en jours (pour filtrer les articles trop anciens)
        
    Returns:
        Résultats de recherche au format JSON
    """
    try:
        # Mapper le critère de tri
        sort_criterion_map = {
            "relevance": arxiv.SortCriterion.Relevance,
            "submitted_date": arxiv.SortCriterion.SubmittedDate,
            "last_updated_date": arxiv.SortCriterion.LastUpdatedDate
        }
        sort_criterion = sort_criterion_map.get(sort_by.lower(), SORT_CRITERION)
        
        # Configuration de la recherche
        search = arxiv.Search(
            query=query,
            max_results=max_results * 2,  # Récupérer plus pour filtrer par date
            sort_by=sort_criterion,
            sort_order=SORT_ORDER,
        )
        
        # Récupérer et filtrer les résultats
        papers = []
        cutoff_date = datetime.now() - timedelta(days=date_range_days) if date_range_days else None
        
        for result in search.results():
            # Filtrer par date si nécessaire
            if cutoff_date and result.published < cutoff_date:
                continue
                
            # Extraire les informations pertinentes
            paper = {
                "title": result.title,
                "authors": [author.name for author in result.authors],
                "published_date": result.published.strftime("%Y-%m-%d"),
                "arxiv_id": result.entry_id.split('/')[-1],
                "url": result.entry_id,
                "pdf_url": result.pdf_url,
                "abstract": result.summary,
                "categories": result.categories
            }
            papers.append(paper)
            
            # Arrêter si on a atteint le nombre maximal de résultats
            if len(papers) >= max_results:
                break
        
        # Convertir en JSON
        result_json = {
            "query": query,
            "papers": papers,
            "total_results": len(papers)
        }
        
        return json.dumps(result_json, ensure_ascii=False, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Erreur lors de la recherche sur ArXiv: {str(e)}"})

@tool("get_paper_by_id")
def get_paper_by_id(paper_id: str) -> str:
    """
    Récupère un article spécifique par son ID ArXiv.
    
    Args:
        paper_id: ID ArXiv de l'article (ex: "2107.12345")
        
    Returns:
        Données de l'article au format JSON
    """
    try:
        # Vérifier si l'ID est complet ou partiel
        if "arxiv.org" in paper_id or "/" in paper_id:
            # Extraire l'ID numérique à partir de l'URL ou de l'ID complet
            paper_id = paper_id.split('/')[-1]
        
        # Rechercher l'article
        search = arxiv.Search(id_list=[paper_id])
        try:
            result = next(search.results())
        except StopIteration:
            return json.dumps({"error": f"Article non trouvé avec l'ID: {paper_id}"})
        
        # Extraire les informations
        paper = {
            "title": result.title,
            "authors": [author.name for author in result.authors],
            "published_date": result.published.strftime("%Y-%m-%d"),
            "arxiv_id": paper_id,
            "url": result.entry_id,
            "pdf_url": result.pdf_url,
            "abstract": result.summary,
            "categories": result.categories,
            "comment": result.comment if hasattr(result, 'comment') else "",
            "journal_ref": result.journal_ref if hasattr(result, 'journal_ref') else "",
            "doi": result.doi if hasattr(result, 'doi') else ""
        }
        
        return json.dumps(paper, ensure_ascii=False, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Erreur lors de la récupération de l'article: {str(e)}"})

@tool("get_paper_abstract")
def get_paper_abstract(paper_id: str) -> str:
    """
    Récupère uniquement le résumé (abstract) d'un article ArXiv.
    
    Args:
        paper_id: ID ArXiv de l'article (ex: "2107.12345")
        
    Returns:
        Résumé de l'article
    """
    try:
        # Vérifier si l'ID est complet ou partiel
        if "arxiv.org" in paper_id or "/" in paper_id:
            # Extraire l'ID numérique à partir de l'URL ou de l'ID complet
            paper_id = paper_id.split('/')[-1]
        
        # Rechercher l'article
        search = arxiv.Search(id_list=[paper_id])
        try:
            result = next(search.results())
        except StopIteration:
            return json.dumps({"error": f"Article non trouvé avec l'ID: {paper_id}"})
        
        # Extraire le résumé et les informations de base
        abstract_info = {
            "title": result.title,
            "authors": [author.name for author in result.authors],
            "abstract": result.summary,
            "arxiv_id": paper_id
        }
        
        return json.dumps(abstract_info, ensure_ascii=False, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Erreur lors de la récupération du résumé: {str(e)}"})