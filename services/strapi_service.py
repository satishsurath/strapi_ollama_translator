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
                json_data = response.json()
                # debug
                print(f"content_types: {json_data}")
                
                content_types = json_data.get('data', [])
                # Filter to include only collection types with i18n enabled in pluginOptions
                return [
                    ct for ct in content_types 
                    if 'schema' in ct and
                    ct.get('schema', {}).get('kind') == 'collectionType' and 
                    ct.get('schema', {}).get('pluginOptions', {}).get('i18n', {}).get('localized', False)
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
                json_data = response.json()
                # Check if the response is already a list or has a 'data' key
                if isinstance(json_data, list):
                    # debug
                    #print(f"json_data: {json_data}")
                    return json_data
                elif isinstance(json_data, dict) and 'data' in json_data:
                    # debug
                    #print(f"json_data: {json_data}")
                    return json_data.get('data', [])
                return []
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
            api_path = self._get_api_path(content_type)
            locale_param = locale or self.source_locale
            
            # Include populate=* to get all relations and nested data
            url = f"{self.base_url}/api/{api_path}?locale={locale_param}&populate=*"
            print(f"DEBUG: Fetching entries from URL: {url}")
            print(f"DEBUG: Headers: {self.headers}")
            
            response = requests.get(
                url,
                headers=self.headers
            )
            
            print(f"DEBUG: API Response status code for entries: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"DEBUG: API Response data for entries: {data}")
                
                # Get entries from the data field
                entries = data.get('data', [])
                if entries:
                    print(f"DEBUG: Found {len(entries)} entries")
                    return entries
                else:
                    print("DEBUG: No entries found")
                    return []
            else:
                print(f"ERROR: Failed to fetch entries. Status code: {response.status_code}")
                print(f"ERROR: Response text: {response.text}")
            return []
        except Exception as e:
            print(f"ERROR in get_entries: {e}")
            return []
    
    def get_entry(self, content_type, entry_id, locale=None):
        """
        Fetch a specific entry
        
        Args:
            content_type (str): Content type API ID
            entry_id (str): Document ID (for Strapi 5) or numeric ID (for Strapi 4)
            locale (str, optional): Locale to fetch. Defaults to source locale.
            
        Returns:
            dict: Entry data
        """
        try:
            # Ensure entry_id is a string
            entry_id = str(entry_id)
            api_path = self._get_api_path(content_type)
            locale_param = locale or self.source_locale
            
            # Include populate=* to get all relations and nested data
            url = f"{self.base_url}/api/{api_path}/{entry_id}?locale={locale_param}&populate=*"
            print(f"DEBUG: Fetching entry from URL: {url}")
            print(f"DEBUG: Headers: {self.headers}")
            print(f"DEBUG: Entry ID type: {type(entry_id)}")
            
            response = requests.get(
                url,
                headers=self.headers
            )
            
            print(f"DEBUG: API Response status: {response.status_code}")
            print(f"DEBUG: Response headers: {response.headers}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"DEBUG: API Response data structure: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                
                # Handle both direct data and nested data structures
                entry_data = data.get('data')
                if entry_data:
                    print(f"DEBUG: Successfully fetched entry with documentId: {entry_data.get('documentId', entry_id)}")
                    return entry_data
                else:
                    print("ERROR: Response data.data field is empty or null")
                    return None
            elif response.status_code == 404:
                print(f"ERROR: Entry not found. This could mean the documentId {entry_id} doesn't exist or locale {locale_param} is not available for this entry.")
                print(f"ERROR: Response text: {response.text}")
            else:
                print(f"ERROR: Failed to fetch entry. Status code: {response.status_code}")
                print(f"ERROR: Response text: {response.text}")
            return None
        except Exception as e:
            print(f"ERROR in get_entry: {str(e)}")
            return None
    
    def create_update_translation(self, content_type, entry_id, target_locale, translated_data):
        """
        Create or update a translation for an entry
        
        Args:
            content_type (str): Content type API ID
            entry_id (str): Document ID
            target_locale (str): Target locale code
            translated_data (dict): Translated fields
            
        Returns:
            dict: Updated entry or None if there was an error
        """
        try:
            api_path = self._get_api_path(content_type)
            
            # Strapi 5 expects data at the top level
            payload = {
                "data": translated_data
            }
            
            url = f"{self.base_url}/api/{api_path}/{entry_id}?locale={target_locale}"
            print(f"DEBUG: Updating translation at URL: {url}")
            print(f"DEBUG: Payload: {payload}")
            
            # Use PUT to update or create a localization
            response = requests.put(
                url,
                headers=self.headers,
                json=payload
            )
            
            if response.status_code in (200, 201):
                data = response.json()
                return data.get('data')
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
        print(f"DEBUG: Converting content type '{content_type}' to API path")
        try:
            # Split on :: and . to get the middle component
            # For example: 'api::page.page' -> ['api', 'page', 'page']
            parts = content_type.split('::')[1].split('.')
            if len(parts) > 0:
                # Use the plural form from Strapi's convention
                api_path = parts[0] + 's'
                print(f"DEBUG: Converted to API path: '{api_path}'")
                return api_path
        except Exception as e:
            print(f"ERROR: Failed to parse content type: {e}")
        
        # Fallback: remove 'api::' prefix and use the rest
        fallback = content_type.replace('api::', '').split('.')[0] + 's'
        print(f"DEBUG: Using fallback API path: '{fallback}'")
        return fallback