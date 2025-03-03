from services.strapi_service import StrapiService
from services.ollama_service import OllamaService
from config import Config
import logging

class TranslatorService:
    def __init__(self):
        self.strapi_service = StrapiService()
        self.ollama_service = OllamaService()
        self.model_mappings = Config.get_model_mappings()
        self.job_status = {
            'current_job': None,
            'completed': 0,
            'total': 0,
            'errors': [],
            'current_entry': None,
            'current_locale': None,
            'status': 'idle'  # idle, running, completed, error
        }
    
    def get_job_status(self):
        """Get current job status"""
        return self.job_status
    
    def is_text_field(self, field_name, field_value):
        """Check if a field is a text field that should be translated"""
        # Skip specific fields that shouldn't be translated
        skip_fields = ['id', 'documentId', 'locale', 'createdAt', 'updatedAt', 'publishedAt']
        if field_name in skip_fields:
            return False
            
        # Check if it's a string/text field
        return isinstance(field_value, str) and field_value.strip() != ''
    
    def translate_entry(self, content_type, entry_id, target_locales):
        """
        Translate a specific entry to multiple locales
        
        Args:
            content_type (str): Content type API ID
            entry_id (str): Document ID for the entry
            target_locales (list): List of target locale codes
            
        Returns:
            dict: Results of the translation job
        """
        # Ensure entry_id is a string
        entry_id = str(entry_id)
        
        # Update job status
        self.job_status = {
            'current_job': f"Translating {content_type} (DocumentID: {entry_id})",
            'completed': 0,
            'total': len(target_locales),
            'errors': [],
            'current_entry': entry_id,
            'current_locale': None,
            'status': 'running'
        }
        
        print(f"DEBUG: Attempting to fetch source entry: {content_type}/{entry_id} with locale {self.strapi_service.source_locale}")
        
        # Get source entry
        source_entry = self.strapi_service.get_entry(
            content_type, 
            entry_id, 
            self.strapi_service.source_locale
        )
        
        print(f"DEBUG: Source entry fetch result type: {type(source_entry)}")
        print(f"DEBUG: Source entry fetch result: {source_entry}")
        
        if not source_entry:
            error_msg = f"Failed to fetch source entry: {content_type}/{entry_id}"
            print(f"ERROR: {error_msg}")
            self.job_status['status'] = 'error'
            self.job_status['errors'].append(error_msg)
            return {
                'entry_id': entry_id,
                'error': error_msg,
                'translations': {}
            }
        
        results = {
            'entry_id': entry_id,
            'translations': {}
        }
        
        # Get translatable fields (text/string fields)
        # In Strapi 5, fields are directly on the entry object
        translatable_fields = {
            key: value for key, value in source_entry.items()
            if self.is_text_field(key, value)
        }
        
        print(f"DEBUG: Found translatable fields: {list(translatable_fields.keys())}")
        
        if not translatable_fields:
            warning_msg = f"No translatable fields found in entry {entry_id}"
            print(f"WARNING: {warning_msg}")
            self.job_status['errors'].append(warning_msg)
        
        # Translate to each target locale
        for target_locale in target_locales:
            self.job_status['current_locale'] = target_locale
            
            # Skip source locale if it's in the target list
            if target_locale == self.strapi_service.source_locale:
                continue
                
            # Get model for this locale
            model_name = self.model_mappings.get(target_locale)
            if not model_name:
                self.job_status['errors'].append(
                    f"No model configured for locale: {target_locale}"
                )
                continue
            
            # Translate each field
            translated_fields = {}
            for field_name, field_value in translatable_fields.items():
                translated_text = self.ollama_service.generate_translation(
                    model_name,
                    field_value,
                    self.strapi_service.source_locale,
                    target_locale
                )
                
                if translated_text:
                    translated_fields[field_name] = translated_text
                else:
                    self.job_status['errors'].append(
                        f"Failed to translate field '{field_name}' to {target_locale}"
                    )
            
            # Update Strapi with translated content
            if translated_fields:
                result = self.strapi_service.create_update_translation(
                    content_type,
                    entry_id,
                    target_locale,
                    translated_fields
                )
                
                if result:
                    results['translations'][target_locale] = 'success'
                else:
                    results['translations'][target_locale] = 'failed'
                    self.job_status['errors'].append(
                        f"Failed to update entry {entry_id} with {target_locale} translation"
                    )
            
            # Update completion counter
            self.job_status['completed'] += 1
        
        # Set job status to completed
        self.job_status['status'] = 'completed'
        return results
    
    def batch_translate(self, content_type, entry_ids, target_locales):
        """
        Batch translate multiple entries
        
        Args:
            content_type (str): Content type API ID
            entry_ids (list): List of document IDs to translate
            target_locales (list): List of target locale codes
            
        Returns:
            dict: Results of the batch job
        """
        self.job_status = {
            'current_job': f"Batch translating {len(entry_ids)} entries of {content_type}",
            'completed': 0,
            'total': len(entry_ids) * len(target_locales),
            'errors': [],
            'current_entry': None,
            'current_locale': None,
            'status': 'running'
        }
        
        batch_results = {
            'content_type': content_type,
            'entries': []
        }
        
        # Ensure we're working with strings for documentId
        entry_ids = [str(id) for id in entry_ids]
        
        for entry_id in entry_ids:
            self.job_status['current_entry'] = entry_id
            result = self.translate_entry(content_type, entry_id, target_locales)
            batch_results['entries'].append(result)
        
        self.job_status['status'] = 'completed'
        return batch_results