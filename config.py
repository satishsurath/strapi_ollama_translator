import os
import json
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key')
    
    # Strapi configuration
    STRAPI_BASE_URL = os.environ.get('STRAPI_BASE_URL', 'http://localhost:1337')
    STRAPI_API_TOKEN = os.environ.get('STRAPI_API_TOKEN', '')
    STRAPI_SOURCE_LOCALE = os.environ.get('STRAPI_SOURCE_LOCALE', 'en')
    
    # Ollama configuration
    OLLAMA_BASE_URL = os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434')
    
    # Path for storing model mappings
    CONFIG_FILE = os.environ.get('CONFIG_FILE', 'model_mappings.json')
    
    @staticmethod
    def get_model_mappings():
        """Get model mappings from config file"""
        try:
            if os.path.exists(Config.CONFIG_FILE):
                with open(Config.CONFIG_FILE, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Error loading model mappings: {e}")
            return {}
    
    @staticmethod
    def save_model_mappings(mappings):
        """Save model mappings to config file"""
        try:
            with open(Config.CONFIG_FILE, 'w') as f:
                json.dump(mappings, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving model mappings: {e}")
            return False