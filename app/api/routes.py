from flask import Blueprint, render_template, request, jsonify
from app.utils.llm_utils import set_llm, get_available_llms
from app.utils.mermaid_utils import render_mermaid
from app.utils.template_utils import get_templates
from app.utils.template_utils import TemplateEnum
from app.utils.mermaid_utils import generate
import app.utils.error_handling as error_handling

import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

main = Blueprint('main', __name__)

@main.route('/')
def index():
    templates = get_templates()
    available_llms = get_available_llms()
    return render_template('index.html', templates=templates, available_llms=available_llms)


@main.route('/api/models')
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


@main.route('/api/ask', methods=['POST'])
async def handler():
    
    data = request.json
    input_text = data.get('input')
    selected_template = data.get('selectedTemplate', TemplateEnum.FLOWCHART.value)
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

    except Exception as e:
        return error_handling.handle_llm_error(e)

    
if __name__ == '__main__':
    main.run(debug=True)