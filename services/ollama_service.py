import requests
from config import Config

class OllamaService:
    def __init__(self, base_url=None):
        self.base_url = base_url or Config.OLLAMA_BASE_URL
    
    def get_available_models(self):
        """Fetch all available models from Ollama"""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                models = response.json().get('models', [])
                return [model['name'] for model in models]
            return []
        except Exception as e:
            print(f"Error fetching models from Ollama: {e}")
            return []
    
    def generate_translation(self, model_name, source_text, source_lang, target_lang):
        """
        Generate translation using Ollama model
        
        Args:
            model_name (str): Name of the Ollama model to use
            source_text (str): Text to translate
            source_lang (str): Source language code (e.g., 'en')
            target_lang (str): Target language code (e.g., 'fr')
            
        Returns:
            str: Translated text or None if there was an error
        """
        try:
            prompt = f"""Translate the following text from {source_lang} to {target_lang}. 
Provide only the translated text without any additional explanations or quotes:

{source_text}"""
            
            payload = {
                "model": model_name,
                "prompt": prompt,
                "stream": False
            }
            
            response = requests.post(f"{self.base_url}/api/generate", json=payload)
            
            if response.status_code == 200:
                return response.json().get('response', '').strip()
            else:
                print(f"Error from Ollama API: {response.status_code}, {response.text}")
                return None
        except Exception as e:
            print(f"Error generating translation: {e}")
            return None