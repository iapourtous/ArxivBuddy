#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Utilitaires généraux pour ArxivBuddy.
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

def create_output_directory() -> str:
    """
    Crée un répertoire de sortie pour les résultats d'ArxivBuddy.
    
    Returns:
        Chemin vers le répertoire créé
    """
    # Créer le répertoire de sortie s'il n'existe pas
    base_dir = os.path.expanduser("~/arxivbuddy_results")
    os.makedirs(base_dir, exist_ok=True)
    
    # Créer un sous-répertoire avec la date actuelle
    today = datetime.now().strftime("%Y-%m-%d")
    output_dir = os.path.join(base_dir, today)
    os.makedirs(output_dir, exist_ok=True)
    
    return output_dir

def sanitize_filename(text: str) -> str:
    """
    Nettoie une chaîne pour l'utiliser comme nom de fichier.
    
    Args:
        text: Texte à nettoyer
        
    Returns:
        Texte nettoyé utilisable comme nom de fichier
    """
    # Supprimer les caractères non alphanumériques (sauf espaces)
    text = re.sub(r'[^\w\s-]', '', text)
    
    # Remplacer les espaces par des underscores
    text = re.sub(r'\s+', '_', text)
    
    # Limiter la longueur
    if len(text) > 50:
        text = text[:50]
    
    return text

def save_results(query: str, results: str, format: str = "md") -> str:
    """
    Enregistre les résultats dans un fichier.
    
    Args:
        query: Question originale
        results: Résultats à enregistrer
        format: Format du fichier (md, json, txt)
        
    Returns:
        Chemin vers le fichier créé
    """
    # Créer le répertoire de sortie
    output_dir = create_output_directory()
    
    # Nettoyer la requête pour le nom de fichier
    clean_query = sanitize_filename(query)
    timestamp = datetime.now().strftime("%H%M%S")
    
    # Déterminer l'extension de fichier
    ext = format.lower()
    if ext not in ["md", "json", "txt"]:
        ext = "md"  # Markdown par défaut
    
    # Créer le nom de fichier
    filename = f"arxivbuddy_{clean_query}_{timestamp}.{ext}"
    filepath = os.path.join(output_dir, filename)
    
    # Écrire les résultats dans le fichier
    with open(filepath, "w", encoding="utf-8") as f:
        if ext == "json":
            # Si c'est déjà une chaîne JSON, essayer de la charger puis la dump pour garantir le format
            try:
                json_data = json.loads(results)
                json.dump(json_data, f, ensure_ascii=False, indent=2)
            except (json.JSONDecodeError, TypeError):
                # Si ce n'est pas un JSON valide, l'enregistrer comme objet simple
                json.dump({"query": query, "results": results}, f, ensure_ascii=False, indent=2)
        else:
            # Pour markdown ou texte, écrire directement
            f.write(results)
    
    return filepath

def extract_keywords(text: str, max_keywords: int = 5) -> List[str]:
    """
    Extrait des mots-clés d'un texte.
    
    Args:
        text: Texte dont extraire les mots-clés
        max_keywords: Nombre maximum de mots-clés à extraire
        
    Returns:
        Liste de mots-clés
    """
    # Cette fonction est un placeholder - dans l'implémentation réelle,
    # on utiliserait des techniques d'extraction de mots-clés plus avancées
    
    # Suppression de la ponctuation et conversion en minuscules
    text = re.sub(r'[^\w\s]', '', text.lower())
    
    # Suppression des mots vides (stopwords) simplifiés
    stopwords = ['le', 'la', 'les', 'un', 'une', 'des', 'et', 'de', 'du', 'ce', 'cette',
                'ces', 'mon', 'ton', 'son', 'ma', 'ta', 'sa', 'mes', 'tes', 'ses',
                'que', 'qui', 'quoi', 'dont', 'où', 'pourquoi', 'comment', 'quand',
                'est', 'sont', 'sera', 'était', 'a', 'ont', 'avoir', 'être', 'faire',
                'pour', 'avec', 'sans', 'dans', 'sur', 'sous', 'entre', 'par', 'au']
    
    words = text.split()
    filtered_words = [word for word in words if word not in stopwords and len(word) > 3]
    
    # Compter les occurrences
    word_counts = {}
    for word in filtered_words:
        word_counts[word] = word_counts.get(word, 0) + 1
    
    # Trier par fréquence
    sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
    
    # Retourner les N mots les plus fréquents
    return [word for word, _ in sorted_words[:max_keywords]]