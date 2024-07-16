import logging
from app.llm.llm_manager import LLMFactory, get_llm
from typing import List, Optional, Any

logger = logging.getLogger(__name__)

def get_available_llms() -> List[dict]:
    """
    Retrieves a list of available LLMs.

    Returns:
        List[dict]: A list of dictionaries, each representing an LLM with 'value' and 'label'.
    """
    return [{"value": llm, "label": llm} for llm in LLMFactory.llm_classes.keys()]

def set_llm(selected_provider: str, selected_model: str, api_key: str = None) -> Optional[Any]:
    """
    Instantiates and returns an LLM object based on the selected provider and model.

    Parameters:
        selected_provider (str): The identifier for the LLM provider.
        selected_model (str): The identifier for the specific model.
        api_key (str, optional): The API key for the selected provider.

    Returns:
        An instance of the selected LLM, or None if instantiation fails.
    """
    logger.debug(f"Setting LLM for provider: {selected_provider}, model: {selected_model}")

    if not selected_provider:
        logger.error("Error: No LLM provider selected")
        return None

    if not selected_model:
        logger.error("Error: No model selected")
        return None

    # Trim any extra spaces from the provider and model names
    selected_provider = selected_provider.strip()
    selected_model = selected_model.strip()

    kwargs = {}
    if api_key:
        kwargs['api_key'] = api_key

    try:
        # Handle Gemini model names
        if selected_provider == 'gemini':
            if not selected_model.startswith('gemini-'):
                selected_model = f'gemini-{selected_model}'

        logger.debug(f"Attempting to get LLM with provider={selected_provider}, model={selected_model}, kwargs={kwargs}")
        selected_llm = get_llm(provider=selected_provider, model=selected_model, **kwargs)
        
        if not hasattr(selected_llm, 'get_response'):
            logger.error(f"The object returned for {selected_provider} does not have a 'get_response' method.")
            raise ValueError(f"The object returned for {selected_provider} does not have a 'get_response' method.")
        
        logger.debug(f"Successfully created LLM instance for provider: {selected_provider}, model: {selected_model}")
        return selected_llm
    except Exception as e:
        logger.exception(f"Error creating LLM instance: {str(e)}")
        return None