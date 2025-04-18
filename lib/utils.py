#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
from typing import List, Dict, Any, Tuple
import litellm
from dotenv import load_dotenv

def extract_keywords(query: str) -> Tuple[str, str]:
    """
    Extrait les mots-clés pertinents et le contexte d'une question
    en langage naturel.
    
    Args:
        query: Question en langage naturel
        
    Returns:
        Tuple contenant (mots-clés pour la recherche, contexte)
    """
    # Charger les variables d'environnement pour litellm
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', '.env'))
    
    # Configuration de litellm
    api_key = os.getenv("CREW_API_KEY")
    model = os.getenv("CREW_MODEL", "openai/gpt-4.1-mini")
    base_url = os.getenv("CREW_BASE_URL", "https://openrouter.ai/api/v1")
    
    litellm.api_key = api_key
    litellm.custom_base_url = base_url
    
    # Prompt pour l'extraction des mots-clés
    prompt = f"""
    À partir de cette question: "{query}"
    
    Extrais les mots-clés les plus pertinents pour une recherche sur ArXiv.
    Concentre-toi sur les termes scientifiques, techniques et concepts.
    
    Génère une chaîne de recherche optimisée pour ArXiv, en anglais,
    avec les opérateurs booléens appropriés (AND, OR).
    
    Format:
    {{
        "search_query": "Termes de recherche optimisés pour ArXiv (en anglais)",
        "context": "Description du contexte et de l'intention de la recherche"
    }}
    """
    
    # Appeler le LLM
    try:
        response = litellm.completion(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=500
        )
        
        content = response.choices[0].message.content
        
        # Extraction simplifiée des valeurs avec des regex
        search_match = re.search(r'"search_query":\s*"([^"]+)"', content)
        context_match = re.search(r'"context":\s*"([^"]+)"', content)
        
        search_query = search_match.group(1) if search_match else query
        context = context_match.group(1) if context_match else ""
        
        return search_query, context
        
    except Exception as e:
        print(f"⚠️ Erreur lors de l'extraction des mots-clés: {str(e)}")
        # En cas d'erreur, renvoyer la requête d'origine
        return query, ""

def format_results(query: str, papers: List[Dict[str, Any]], 
                   summary: Dict[str, str], french: bool = False) -> str:
    """
    Formate les résultats pour l'affichage.
    
    Args:
        query: Question originale de l'utilisateur
        papers: Liste des papiers trouvés
        summary: Résumé et synthèse générés
        french: Si True, utilise la terminologie française
        
    Returns:
        Texte formaté pour l'affichage
    """
    # Titres selon la langue
    titles = {
        "result": "Résultat de votre question" if french else "Result for your query",
        "summary": "Résumé simplifié" if french else "Simplified Summary",
        "papers": "Papiers recommandés" if french else "Recommended Papers",
        "synthesis": "Synthèse" if french else "Synthesis"
    }
    
    # Construction de la sortie
    output = [
        f"### {titles['result']} :",
        f"*{query}*",
        "",
        "---",
        "",
        f"#### 🧬 {titles['summary']} :",
        f"{summary['résumé_simplifié']}",
        "",
        "---",
        "",
        f"#### 📚 {titles['papers']} :",
        ""
    ]
    
    # Ajouter les papiers
    for i, paper in enumerate(papers, 1):
        authors = ", ".join(paper["authors"][:2])
        if len(paper["authors"]) > 2:
            authors += " et al."
            
        # Extraire l'ID ArXiv à partir de l'URL
        arxiv_id = paper["id"].split("/")[-1]
        
        paper_info = [
            f"{i}. **\"{paper['title']}\"**  ",
            f"   *{authors}*  ",
            f"   → {paper['pdf_url']}  "
        ]
        output.extend(paper_info)
        output.append("")
    
    # Ajouter la synthèse
    output.extend([
        "---",
        "",
        f"#### 🔍 {titles['synthesis']} :",
        f"{summary['synthèse']}",
        ""
    ])
    
    return "\n".join(output)

def clean_text(text: str) -> str:
    """
    Nettoie le texte des caractères indésirables et normalise les sauts de ligne.
    
    Args:
        text: Texte à nettoyer
        
    Returns:
        Texte nettoyé
    """
    # Supprimer les caractères de contrôle excepté les sauts de ligne
    text = re.sub(r'[\x00-\x09\x0b\x0c\x0e-\x1f\x7f]', '', text)
    
    # Normaliser les sauts de ligne
    text = re.sub(r'\r\n', '\n', text)
    
    # Supprimer les espaces multiples
    text = re.sub(r' +', ' ', text)
    
    # Supprimer les espaces en début et fin de ligne
    text = re.sub(r'^ +| +$', '', text, flags=re.MULTILINE)
    
    # Limiter les sauts de ligne consécutifs à 2 maximum
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()