import logging
from llm_config import LLMFactory, get_llm
from typing import List, Optional, Any
from llm_config import LLMFactory, get_llm
from typing import List, Optional, Any
from openai import AuthenticationError, RateLimitError

logger = logging.getLogger(__name__)

def get_available_llms() -> List[dict]:
    """
    Retrieves a list of available LLMs.

    Returns:
        List[dict]: A list of dictionaries, each representing an LLM with 'value' and 'label'.
    """
    return [{"value": llm, "label": llm} for llm in LLMFactory.llm_classes.keys()]



logger = logging.getLogger(__name__)

# ... (keep the existing get_available_llms function)

def set_llm(selected_provider: str, selected_model: str, api_key: str = None) -> Optional[Any]:
    """
    Instantiates and returns an LLM object based on the selected provider and model.

    Parameters:
        selected_provider (str): The identifier for the LLM provider.
        selected_model (str): The identifier for the specific model.
        api_key (str, optional): The API key for the selected provider.

    Returns:
        An instance of the selected LLM, or None if instantiation fails.

    Raises:
        ValueError: If the provider or model is not selected, or if the API key is invalid.
        NotImplementedError: If the selected provider is not supported.
        AuthenticationError: If the API key is invalid or missing.
        RateLimitError: If the API rate limit is exceeded.
        Exception: For any other unexpected errors.
    """
    logger.debug(f"Setting LLM for provider: {selected_provider}, model: {selected_model}")

    if not selected_provider:
        raise ValueError("No LLM provider selected")

    if not selected_model:
        raise ValueError("No model selected")

    # Trim any extra spaces from the provider and model names
    selected_provider = selected_provider.strip()
    selected_model = selected_model.strip()

    kwargs = {}
    if api_key:
        kwargs['api_key'] = api_key
    elif selected_provider != 'ollama':
        raise ValueError(f"API key is required for {selected_provider}")

    try:
        # Handle Gemini model names
        if selected_provider == 'gemini':
            if not selected_model.startswith('gemini-'):
                selected_model = f'gemini-{selected_model}'

        logger.debug(f"Attempting to get LLM with provider={selected_provider}, model={selected_model}, kwargs={kwargs}")
        selected_llm = get_llm(provider=selected_provider, model=selected_model, **kwargs)
        
        if not hasattr(selected_llm, 'get_response'):
            raise NotImplementedError(f"The {selected_provider} provider does not support the 'get_response' method.")
        
        logger.debug(f"Successfully created LLM instance for provider: {selected_provider}, model: {selected_model}")
        return selected_llm
    except AuthenticationError:
        logger.error(f"Authentication failed for {selected_provider}. Please check your API key.")
        raise
    except RateLimitError:
        logger.error(f"Rate limit exceeded for {selected_provider}. Please try again later.")
        raise
    except NotImplementedError as e:
        logger.error(str(e))
        raise
    except Exception as e:
        logger.exception(f"Unexpected error creating LLM instance: {str(e)}")
        raise ValueError(f"Failed to initialize {selected_provider} with model {selected_model}: {str(e)}")