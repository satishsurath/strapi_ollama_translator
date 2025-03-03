# Strapi-Ollama Translation System

A standalone Python Flask web application that bridges Strapi CMS and local Ollama LLM models to provide content internationalization.

## Features

- Integrate with Strapi v5+ using the REST API
- Leverage local Ollama LLM models for translation
- Configure different models for different target languages
- Batch translate content with a user-friendly UI
- Monitor translation job progress in real-time

## System Architecture

The translation system consists of three main components:

1. **Flask Web App**: Provides a web UI and endpoints for configuration and triggering translations
2. **Strapi CMS**: The content source and destination
3. **Ollama LLM Service**: Hosts language models locally for translation

## Requirements

- Python 3.8+
- Strapi v5+ with internationalization enabled
- Ollama with at least one model installed

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/strapi-ollama-translator.git
   cd strapi-ollama-translator
   ```

2. Create a virtual environment and install dependencies:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   Create a `.env` file with the following variables:
   ```
   STRAPI_BASE_URL=http://localhost:1337
   STRAPI_API_TOKEN=your_strapi_api_token
   STRAPI_SOURCE_LOCALE=en
   OLLAMA_BASE_URL=http://localhost:11434
   ```

4. Run the application:
   ```
   python app.py
   ```

5. Access the web UI at `http://localhost:5000`

## Configuration

1. In the web UI, go to the "Configuration" page.
2. For each target language, select an appropriate Ollama model.
3. Click "Save Configuration" to apply the changes.

## Usage

1. Go to the "Translate" page in the web UI.
2. Select a content type to translate.
3. Choose whether to translate all entries or specific ones.
4. Select target languages for translation.
5. Click "Start Translation" to begin the process.
6. Monitor the progress on the status page.

## API Endpoints

- `GET /models`: List available Ollama models
- `GET/POST /config`: Get or update model configurations
- `GET /content-types`: List content types from Strapi
- `GET /entries/<content_type>`: List entries for a content type
- `POST /translate`: Trigger a translation job
- `GET /status`: Get current job status

## How It Works

1. The system fetches content from Strapi in the source language
2. For each target language, it sends the content to the selected Ollama model
3. The model generates translations for each text field
4. The system saves the translated content back to Strapi using the appropriate locale

## License

MIT

## Credits

- Strapi: https://strapi.io/
- Ollama: https://ollama.ai/