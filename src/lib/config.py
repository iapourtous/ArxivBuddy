"""
Module de configuration pour ArxivBuddy.
Fournit un accès facile à la configuration via des variables globales.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

class Config:
    """Classe pour gérer la configuration d'ArxivBuddy."""
    
    def __init__(self):
        """Initialise la configuration en chargeant le fichier YAML et les variables d'environnement."""
        # Déterminer les chemins de base
        self.base_dir = Path(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        self.config_dir = self.base_dir / "config"
        self.yaml_dir = self.config_dir / "yaml"
        
        # Charger les variables d'environnement
        env_path = self.config_dir / ".env"
        if env_path.exists():
            load_dotenv(dotenv_path=str(env_path))
            
        # Charger le fichier YAML principal
        self.config = self._load_yaml("agents.yaml", {})
        
        # Configuration par défaut
        self.defaults = self.config.get("defaults", {})
        
        # Appliquer les variables d'environnement
        self._apply_env_vars()
        
    def _load_yaml(self, filename: str, default: Dict = None) -> Dict:
        """
        Charge un fichier YAML de configuration.
        
        Args:
            filename: Nom du fichier YAML
            default: Valeur par défaut si le fichier n'existe pas
            
        Returns:
            Contenu du fichier YAML sous forme de dictionnaire
        """
        if default is None:
            default = {}
            
        file_path = self.yaml_dir / filename
        if not file_path.exists():
            print(f"⚠️ Fichier de configuration {filename} non trouvé.")
            return default
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or default
        except Exception as e:
            print(f"⚠️ Erreur lors du chargement de {filename}: {e}")
            return default
    
    def _apply_env_vars(self):
        """Applique les variables d'environnement aux configurations chargées."""
        # Mapper les variables d'environnement aux clés de configuration
        mappings = {
            "CREW_API_KEY": ["crew", "api_key"],
            "CREW_BASE_URL": ["crew", "base_url"],
            "CREW_MODEL": ["crew", "model"],
            "CREW_TEMPERATURE": ["crew", "temperature"],
            "CREW_MAX_TOKENS": ["crew", "max_tokens"],
            "ARXIV_MAX_RESULTS": ["arxiv", "max_results"],
            "ARXIV_SORT_BY": ["arxiv", "sort_by"],
            "ARXIV_SORT_ORDER": ["arxiv", "sort_order"]
        }
        
        for env_var, keys in mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                # Convertir les types si nécessaire
                if env_var == "CREW_TEMPERATURE":
                    value = float(value)
                elif env_var in ["CREW_MAX_TOKENS", "ARXIV_MAX_RESULTS"]:
                    value = int(value)
                
                # Mettre à jour la configuration
                current = self.defaults
                for key in keys[:-1]:
                    if key not in current:
                        current[key] = {}
                    current = current[key]
                current[keys[-1]] = value
    
    def get_agent_config(self, agent_type: str) -> Dict[str, Any]:
        """
        Récupère la configuration d'un agent spécifique.
        
        Args:
            agent_type: Type d'agent (query_parser, arxiv_searcher, etc.)
            
        Returns:
            Configuration de l'agent
        """
        agents = self.config.get("agents", {})
        return agents.get(agent_type, {})
    
    def get_prompt_config(self, prompt_type: str) -> Dict[str, Any]:
        """
        Récupère la configuration d'un prompt spécifique.
        
        Args:
            prompt_type: Type de prompt (query_parser, arxiv_search, etc.)
            
        Returns:
            Configuration du prompt
        """
        prompts = self.config.get("prompts", {})
        return prompts.get(prompt_type, {})
    
    def get(self, *keys, default=None):
        """
        Récupère une valeur de configuration spécifique.
        
        Args:
            *keys: Chemin d'accès à la valeur (ex: "crew", "api_key")
            default: Valeur par défaut si la clé n'existe pas
            
        Returns:
            Valeur de configuration ou valeur par défaut
        """
        current = self.defaults
        for key in keys:
            if not isinstance(current, dict) or key not in current:
                return default
            current = current[key]
        return current

# Instance singleton pour l'accès global
_config = None

def get_config() -> Config:
    """
    Récupère l'instance singleton de Config.
    
    Returns:
        Instance de Config
    """
    global _config
    if _config is None:
        _config = Config()
    return _config

# Exporter les configurations courantes pour la rétrocompatibilité
config = get_config()
CREW_API_KEY = config.get("crew", "api_key", default="")
CREW_BASE_URL = config.get("crew", "base_url", default="https://openrouter.ai/api/v1")
CREW_MODEL = config.get("crew", "model", default="openrouter/openai/gpt-4.1-mini")
CREW_TEMPERATURE = config.get("crew", "temperature", default=0.7)
CREW_MAX_TOKENS = config.get("crew", "max_tokens", default=4000)
ARXIV_MAX_RESULTS = config.get("arxiv", "max_results", default=5)
ARXIV_SORT_BY = config.get("arxiv", "sort_by", default="SubmittedDate")
ARXIV_SORT_ORDER = config.get("arxiv", "sort_order", default="Descending")