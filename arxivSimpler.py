#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ArxivBuddy - L'IA qui lit les papiers de recherche pour toi

Cet outil permet de trouver, résumer et vulgariser des papiers de recherche 
depuis ArXiv en réponse à une question de l'utilisateur.
"""

import sys
import os
import argparse
from pathlib import Path
import warnings
from dotenv import load_dotenv

# Ajouter le répertoire courant au chemin pour permettre les imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Désactiver les warnings
warnings.filterwarnings("ignore", category=Warning)

# Charger les variables d'environnement
env_path = Path(__file__).parent / 'config' / '.env'
load_dotenv(dotenv_path=env_path)

try:
    from lib.agents import ArxivAgents
    
    # Vérifier que les modules nécessaires sont installés
    import crewai
    import arxiv
except ImportError as e:
    print(f"⚠️ Erreur d'importation: {e}")
    print("⚠️ Certaines dépendances requises ne sont pas installées.")
    print("Installez-les avec : pip install -r requirements.txt")
    print("Assurez-vous d'activer l'environnement virtuel : source venv/bin/activate")
    sys.exit(1)

def main():
    """Point d'entrée principal de l'application ArxivBuddy."""
    
    # Configurer l'analyseur d'arguments
    parser = argparse.ArgumentParser(description="ArxivBuddy - L'IA qui lit les papiers de recherche pour toi")
    parser.add_argument("query", type=str, nargs="?", help="Votre question de recherche")
    parser.add_argument("--max-results", type=int, default=5, help="Nombre maximum de papiers à récupérer")
    # Les résultats sont toujours en français par défaut
    parser.add_argument("--level", choices=["expert", "medium", "beginner"], default="medium", 
                       help="Niveau de simplification (expert, medium, beginner)")
    parser.add_argument("--api-key", help="Clé API pour le modèle LLM (si non défini dans .env)")
    parser.add_argument("--model", help="Nom du modèle LLM à utiliser (défini dans .env par défaut)")
    
    args = parser.parse_args()
    
    # Si aucune requête n'est fournie, afficher l'aide
    if not args.query:
        parser.print_help()
        sys.exit(1)
    
    try:
        print(f"🔍 Analyse de votre question : \"{args.query}\"")
        
        # Initialiser l'agent ArxivBuddy
        arxiv_agents = ArxivAgents(api_key=args.api_key, model=args.model)
        
        # Traiter la requête avec l'équipe d'agents
        result = arxiv_agents.process_query(
            query=args.query,
            max_results=args.max_results,
            level=args.level
        )
        
        # Afficher le résultat
        print(result)
        
        # Enregistrer le résultat dans un fichier
        output_filename = f"arxiv_reponse_{args.query[:30].replace(' ', '_').replace('?', '')}.md"
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(result)
        print(f"\n✅ Résultat enregistré dans: {output_filename}")
        
    except Exception as e:
        print(f"❌ Une erreur est survenue: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()