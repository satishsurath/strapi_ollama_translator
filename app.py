from flask import Flask, render_template, request, jsonify, redirect, url_for
from services.translator import TranslatorService
from services.strapi_service import StrapiService
from services.ollama_service import OllamaService
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Initialize services
translator_service = TranslatorService()
strapi_service = StrapiService()
ollama_service = OllamaService()

@app.route('/')
def index():
    """Main dashboard"""
    job_status = translator_service.get_job_status()
    return render_template('index.html', job_status=job_status)

@app.route('/models', methods=['GET'])
def get_models():
    """Get available Ollama models"""
    models = ollama_service.get_available_models()
    return jsonify(models)

@app.route('/config', methods=['GET', 'POST'])
def config():
    """Configure model mappings"""
    if request.method == 'POST':
        model_mappings = request.json
        Config.save_model_mappings(model_mappings)
        # Reload the model mappings in the translator service
        translator_service.model_mappings = Config.get_model_mappings()
        return jsonify({"status": "success", "message": "Configuration saved"})
    
    # GET - Show config page or return current config
    if request.headers.get('Accept') == 'application/json':
        return jsonify(Config.get_model_mappings())
    
    locales = strapi_service.get_available_locales()
    models = ollama_service.get_available_models()
    current_mappings = Config.get_model_mappings()
    
    return render_template(
        'config.html', 
        locales=locales, 
        models=models, 
        current_mappings=current_mappings,
        source_locale=strapi_service.source_locale
    )

@app.route('/content-types', methods=['GET'])
def get_content_types():
    """Get available content types from Strapi"""
    content_types = strapi_service.get_content_types()
    # debug
    print(f"content_types: {content_types}")
    return jsonify(content_types)

@app.route('/entries/<content_type>', methods=['GET'])
def get_entries(content_type):
    """Get entries for a content type"""
    entries = strapi_service.get_entries(content_type)
    return jsonify(entries)

@app.route('/translate', methods=['GET', 'POST'])
def translate():
    """Trigger translation jobs"""
    if request.method == 'POST':
        data = request.json
        content_type = data.get('content_type')
        entry_ids = data.get('entry_ids', [])
        target_locales = data.get('target_locales', [])
        
        # Validate required fields
        if not content_type or not target_locales:
            return jsonify({
                "status": "error", 
                "message": "Missing required fields: content_type, target_locales"
            }), 400
        
        # If no entry IDs specified, get all entries for the content type
        if not entry_ids:
            entries = strapi_service.get_entries(content_type)
            # Use documentId for Strapi 5
            entry_ids = [str(entry.get('documentId', entry.get('id'))) for entry in entries]
        else:
            # Ensure all entry IDs are strings
            entry_ids = [str(id) for id in entry_ids]
        
        # Trigger batch translation
        translator_service.batch_translate(content_type, entry_ids, target_locales)
        return jsonify({"status": "success", "message": "Translation job started"})
    
    # GET - Show translation form
    content_types = strapi_service.get_content_types()
    # debug
    print(f"content_types: {content_types}")
    locales = strapi_service.get_available_locales()
    
    return render_template(
        'translate.html', 
        content_types=content_types, 
        locales=locales,
        source_locale=strapi_service.source_locale
    )

@app.route('/status', methods=['GET'])
def status():
    """Get current job status"""
    job_status = translator_service.get_job_status()
    return jsonify(job_status)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=6000)