from flask import Flask, render_template, request, jsonify
from generate import generate, AuthError, RateLimitError, BadRequestError, LLMError
from mermaid_utils import render_mermaid
from template_utils import get_templates
from llm_utils import get_available_llms, set_llm
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def index():
    templates = get_templates()
    available_llms = get_available_llms()
    return render_template('index.html', templates=templates, available_llms=available_llms)

@app.route('/api/models')
def get_models():
    provider = request.args.get('provider')
    
    if provider == 'openai':
        models = [
            {"value": "gpt-3.5-turbo", "label": "GPT-3.5 Turbo"},
            {"value": "gpt-4", "label": "GPT-4"},
            {"value": "gpt-4-turbo", "label": "GPT-4 Turbo"},
        ]
        return jsonify(models)
    
    elif provider == 'gemini':
        models = [
            {"value": "gemini-1.5-pro", "label": "Gemini 1.5 Pro"},
            {"value": "gemini-1.5-flash", "label": "Gemini 1.5 Flash"},
            {"value": "gemini-1.0-pro", "label": "Gemini 1.0 Pro"},
        ]
        return jsonify(models)
    
    elif provider in ['huggingface', 'ollama']:
        return jsonify({"type": "text_input"})
    
    else:
        return jsonify({"error": "Unknown provider"}), 400

@app.route('/api/ask', methods=['POST'])
async def handler():
    logger.debug(f"Received request data: {request.json}")
    
    data = request.json
    input_text = data.get('input')
    selected_template = data.get('selectedTemplate')
    selected_provider = data.get('provider', '').strip()
    selected_model = data.get('model', '').strip()
    temperature = float(data.get('temperature', 0.7))
    max_tokens = int(data.get('maxTokens', 4096))
    api_key = data.get('apiKey', '').strip()

    try:
        llm = set_llm(selected_provider, selected_model, api_key)
        if llm is None:
            return jsonify({"error": f"Failed to initialize LLM for provider: {selected_provider}, model: {selected_model}"}), 400

        result = await generate(input_text, selected_template, llm, selected_model, temperature, max_tokens)
        
        mermaid_code = result['text']
        rendered_chart = render_mermaid(mermaid_code)
        return jsonify({"text": rendered_chart})

    except ValueError as e:
        logger.error(f"Value error: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except AuthError as e:
        logger.error(f"Authentication error: {str(e)}")
        return jsonify({"error": str(e)}), 401
    except RateLimitError as e:
        logger.error(f"Rate limit error: {str(e)}")
        return jsonify({"error": str(e)}), 429
    except BadRequestError as e:
        logger.error(f"Bad request error: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except LLMError as e:
        logger.error(f"LLM error: {str(e)}")
        error_message = str(e)
        if "API key not valid" in error_message:
            return jsonify({"error": "Invalid API key. Please check your API key and try again."}), 400
        else:
            return jsonify({"error": error_message}), 500
    except Exception as e:
        logger.exception(f"Unexpected error in handler: {str(e)}")
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500
    
if __name__ == '__main__':
    app.run(debug=True)