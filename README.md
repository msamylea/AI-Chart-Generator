
# mermaid_chart_gen
Rewrote FlowGPT (https://github.com/nilooy/flowgpt/) in Python and added support for Gemini, HuggingFace, and Ollama. Updated UI and made parsing changes.

To run, just clone the repository and run app.py which will start the local Flask app at http://127.0.0.1:5000
## Important -- Read the LLM Providers Sections below for setting up various LLM Providers and models.  This won't work without an .env file and the LLM provider setup.  I'm too busy right now to add in the dropdown to select provider, model, etc, so if someone wants to do that, hooray.

_If you get strange syntax errors, upgrade Mermaid via npm/yarn/whichever you need_


![image](https://github.com/user-attachments/assets/fe1f3d45-fedf-4a9e-9236-4a1ae452ed26)


# To Change LLM Providers:

Edit generate.py -> generate for this line to add provider, model, and kwargs:

```python
 config = LLMConfig("huggingface-openai", "meta-llama/Meta-Llama-3-70B-Instruct", temperature=0.1, max_tokens=4096)
        llm = HFOpenAIAPILLM(config)
```
Options for LLMs are:
- "openai": OpenAI LLMs (gpt-4, etc), uses OpenAILLM(config)
- "gemini": Google Gemini LLMs (gemini-1.5-flash-latest, etc), uses GeminiLLM(config)
- "huggingface-openai": HuggingFace LLMs using the OpenAI API standard (typically used with HuggingFace Pro subscriptions, uses HFOpenAIAPILLM(config)
- "huggingface-text": HuggingFace Inference Client (currently only set up for text inference), uses HFTextLLM(config)
- "ollama": Ollama served
        
Make sure you have an .env file for these values:
- OPENAI_API_KEY=
- HF_TOKEN=
- GENAI_API_KEY=


*GENAI_API_KEY is for Google Gemini

# Examples for Different LLM Providers:

```python
config = LLMConfig("ollama", "mistral:v0.3", temperature=0.1, max_tokens=4096)
        llm = OllamaLLM(config)

config = LLMConfig("gemini", "gemini-1.5-flash-latest", temperature=0.1, max_tokens=4096)
        llm = GeminiLLM(config)

config = LLMConfig("huggingface-text", "meta-llama/Meta-Llama-3-70B-Instruct", temperature=0.1, max_tokens=4096)
        llm = HFTextLLM(config)
```

![image](https://github.com/user-attachments/assets/8026ef2c-4284-415c-a9ee-907d083bdde3)
