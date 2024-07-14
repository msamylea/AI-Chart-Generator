from flask import Flask, render_template, request, jsonify
from prompt_by_template import TemplateEnum
from generate import generate
from mermaid_utils import render_mermaid, export_svg, copy_mermaid_code
from template_utils import get_templates
from llm_utils import get_available_llms, set_llm
import asyncio
from dotenv import load_dotenv
import logging
from openai import AuthenticationError, BadRequestError

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
    selected_template = data.get('selectedTemplate', TemplateEnum.FLOWCHART.value)
    selected_provider = data.get('provider', '').strip()
    selected_model = data.get('model', '').strip()
    temperature = float(data.get('temperature', 0.7))
    max_tokens = int(data.get('maxTokens', 4096))
    api_key = data.get('apiKey', '').strip()

    logger.debug(f"Parsed request data: input_text={input_text}, selected_template={selected_template}, "
                 f"selected_provider={selected_provider}, selected_model={selected_model}, "
                 f"temperature={temperature}, max_tokens={max_tokens}")

    if not input_text:
        logger.error("No input in the request")
        return jsonify({"error": "No input in the request"}), 400

    if not selected_provider:
        logger.error("No LLM provider selected")
        return jsonify({"error": "No LLM provider selected"}), 400

    if not selected_model:
        logger.error("No model selected")
        return jsonify({"error": "No model selected"}), 400

    if selected_provider != 'ollama' and not api_key:
        logger.error("No API key provided for non-Ollama provider")
        return jsonify({"error": "API key is required for this provider"}), 400

    try:
        llm = set_llm(selected_provider, selected_model, api_key)
        if llm is None:
            logger.error(f"Failed to initialize LLM for provider: {selected_provider}, model: {selected_model}")
            return jsonify({"error": f"Failed to initialize LLM for provider: {selected_provider}, model: {selected_model}"}), 400

        logger.debug(f"Generating result with: input_text={input_text}, selected_template={selected_template}, "
                     f"llm={llm}, selected_model={selected_model}, temperature={temperature}, max_tokens={max_tokens}")

        result = await generate(input_text, selected_template, llm, selected_model, temperature, max_tokens)
        
        logger.debug(f"Generation result: {result}")

        mermaid_code = result['text']
        rendered_chart = render_mermaid(mermaid_code)
        return jsonify({"text": rendered_chart})

    except Exception as e:
        logger.exception(f"Error in handler: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)