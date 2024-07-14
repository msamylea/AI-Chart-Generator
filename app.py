from flask import Flask, render_template, request, jsonify
from prompt_by_template import TemplateEnum
from generate import generate
from mermaid_utils import render_mermaid, export_svg, copy_mermaid_code
from template_utils import get_templates
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

@app.route('/')
def index():
    templates = get_templates()
    return render_template('index.html', templates=templates)

@app.route('/api/ask', methods=['POST'])
async def handler():
    data = request.json
    input_text = data.get('input')
    selected_template = data.get('selectedTemplate', TemplateEnum.FLOWCHART.value)
    selection = data.get('selection')  # New line to get selection from the request

    if not input_text:
        return jsonify({"error": "No input in the request"}), 400

    try:
        # Modify the generate function call to include the selection parameter
        # Assuming the generate function can accept and process this new parameter
        result = await generate(input_text, selected_template, selection)  # Updated line
        
        # Adjust the following transformations as necessary
        text = result['text'].replace("```", "").replace('"', "'").replace("end[End]", "ends[End]").replace("mermaid", "")

        rendered_chart = render_mermaid(text)
        return jsonify({"text": rendered_chart, "selection": selection})  # Optionally include selection in response
    except Exception as e:
        app.logger.error(f"Error in handler: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 400

@app.route('/api/export-svg', methods=['POST'])
def export_svg_route():
    chart = request.json.get('chart')
    name = request.json.get('name')
    
    try:
        svg_data = export_svg(chart, name)
        return svg_data, 200, {'Content-Type': 'image/svg+xml'}
    except Exception as e:
        app.logger.error(f"Error in export_svg_route: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 400

@app.route('/api/copy-mermaid', methods=['POST'])
def copy_mermaid_route():
    chart = request.json.get('chart')
    try:
        copied_code = copy_mermaid_code(chart)
        return jsonify({"code": copied_code})
    except Exception as e:
        app.logger.error(f"Error in copy_mermaid_route: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)