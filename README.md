
# AI Chart Generation with Mermaid

Rewrote FlowGPT (https://github.com/nilooy/flowgpt/) in Python and added support for Gemini, HuggingFace, and Ollama. Updated UI and made parsing changes.  Added several additional types of mermaid charts (Gantt, Block, Sankey, Requirements Diagram, ZenUML)

To run, just clone the repository and run app.py which will start the local Flask app at http://127.0.0.1:5000

_If you get strange syntax errors, upgrade Mermaid via npm/yarn/whichever you need, if they continue, it's likely just the LLM output - try updating your prompts.  You can try to play with the parsing code, but it's already using a lot of regex to clean the raw output._


# Updated UI and added ability to select LLM Provider, Model, enter API key, and set kwargs:

- HuggingFace OpenAI is HF models using OpenAI API (typically used with HF Pro subscription)
- HuggingFace Text is HF models via InferenceClient
- Gemini is Google Gemini models
- Ollama is self served models
- OpenAI is.. OpenAI

![image](https://github.com/user-attachments/assets/37adae7d-e680-4e94-8cc8-b029f7c25706)




![image](https://github.com/user-attachments/assets/fe1f3d45-fedf-4a9e-9236-4a1ae452ed26)




![image](https://github.com/user-attachments/assets/8026ef2c-4284-415c-a9ee-907d083bdde3)
