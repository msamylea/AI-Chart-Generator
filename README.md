# mermaid_chart_gen
Rewrote FlowGPT (https://github.com/nilooy/flowgpt/) in Python and added support for Gemini, HuggingFace, and Ollama. Updated UI and made parsing changes.

# To Change LLM Providers:

Edit generate.py -> generate for this line:

```python
 config = LLMConfig("huggingface-openai", "meta-llama/Meta-Llama-3-70B-Instruct", temperature=0.1, max_tokens=4096)
        llm = HFOpenAIAPILLM(config)
```
Options for LLMs are:
        - "openai": OpenAILLM,
        - "gemini": GeminiLLM,
        - "huggingface-openai": HFOpenAIAPILLM (This is for HuggingFace LLM calls using the OpenAI API standard)
        - "huggingface-text": HFTextLLM (This is for HuggingFace LLM calls using InferenceClient)
        - "ollama": Ollama
        
Add your LLM Provider, Model, and any kwargs for that specific LLM provider/model (example kwargs: temperature, max_tokens, tools, etc).  

Make sure you have an .env file for these values:
- OPENAI_API_KEY=
- HF_TOKEN=
- GENAI_API_KEY=
