import requests
from config import Config

class StrapiService:
    def __init__(self, base_url=None, api_token=None, source_locale=None):
        self.base_url = base_url or Config.STRAPI_BASE_URL
        self.api_token = api_token or Config.STRAPI_API_TOKEN
        self.source_locale = source_locale or Config.STRAPI_SOURCE_LOCALE
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
    
    def get_content_types(self):
        """Fetch available content types from Strapi"""
        try:
            # This endpoint is for Strapi v5+
            response = requests.get(
                f"{self.base_url}/api/content-type-builder/content-types",
                headers=self.headers
            )
            
            if response.status_code == 200:
                content_types = response.json().get('data', [])
                # Filter to include only collection types with i18n enabled
                return [
                    ct for ct in content_types 
                    if ct.get('kind') == 'collectionType' and 
                    ct.get('pluginOptions', {}).get('i18n', {}).get('enabled', False)
                ]
            return []
        except Exception as e:
            print(f"Error fetching content types: {e}")
            return []
    
    def get_available_locales(self):
        """Fetch available locales from Strapi"""
        try:
            response = requests.get(
                f"{self.base_url}/api/i18n/locales",
                headers=self.headers
            )
            
            if response.status_code == 200:
                return response.json().get('data', [])
            return []
        except Exception as e:
            print(f"Error fetching locales: {e}")
            return []
    
    def get_entries(self, content_type, locale=None):
        """
        Fetch entries for a specific content type
        
        Args:
            content_type (str): Content type API ID (e.g., 'api::article.article')
            locale (str, optional): Locale to fetch. Defaults to source locale.
            
        Returns:
            list: List of entries
        """
        try:
            # Extract the API path from the content type
            api_path = self._get_api_path(content_type)
            locale_param = locale or self.source_locale
            
            response = requests.get(
                f"{self.base_url}/api/{api_path}?locale={locale_param}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                return response.json().get('data', [])
            return []
        except Exception as e:
            print(f"Error fetching entries: {e}")
            return []
    
    def get_entry(self, content_type, entry_id, locale=None):
        """
        Fetch a specific entry
        
        Args:
            content_type (str): Content type API ID
            entry_id (int): Entry ID
            locale (str, optional): Locale to fetch. Defaults to source locale.
            
        Returns:
            dict: Entry data
        """
        try:
            api_path = self._get_api_path(content_type)
            locale_param = locale or self.source_locale
            
            response = requests.get(
                f"{self.base_url}/api/{api_path}/{entry_id}?locale={locale_param}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                return response.json().get('data', {})
            return None
        except Exception as e:
            print(f"Error fetching entry: {e}")
            return None
    
    def create_update_translation(self, content_type, entry_id, target_locale, translated_data):
        """
        Create or update a translation for an entry
        
        Args:
            content_type (str): Content type API ID
            entry_id (int): Entry ID
            target_locale (str): Target locale code
            translated_data (dict): Translated fields
            
        Returns:
            dict: Updated entry or None if there was an error
        """
        try:
            api_path = self._get_api_path(content_type)
            
            # Use PUT to update or create a localization
            response = requests.put(
                f"{self.base_url}/api/{api_path}/{entry_id}?locale={target_locale}",
                headers=self.headers,
                json={"data": translated_data}
            )
            
            if response.status_code in (200, 201):
                return response.json().get('data', {})
            else:
                print(f"Error updating translation: {response.status_code}, {response.text}")
                return None
        except Exception as e:
            print(f"Error creating/updating translation: {e}")
            return None
    
    def _get_api_path(self, content_type):
        """
        Extract API path from content type
        
        Args:
            content_type (str): Content type API ID (e.g., 'api::article.article')
            
        Returns:
            str: API path (e.g., 'articles')
        """
        # For 'api::article.article' -> 'articles'
        parts = content_type.split('::')
        if len(parts) > 1:
            model = parts[1].split('.')[0]
            return model + 's'  # Pluralize (simple approach)
        return content_type  # Fallback