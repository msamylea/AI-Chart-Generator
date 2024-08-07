from typing import Any, Optional
from abc import ABC, abstractmethod
from openai import OpenAI
import google.generativeai as genai
from google.generativeai import GenerationConfig
from huggingface_hub import InferenceClient
from PIL import Image

class LLMConfig:
    """
    Represents the configuration for the LLM (Language Model) service.

    Args:
        provider (str): The provider of the language model.
        model (str): The specific language model to use.
        api_key (Optional[str]): The API key to authenticate the requests. If not provided, it will be retrieved from environment variables.
        base_url (Optional[str]): The base URL for the API endpoint.
        **kwargs: Additional parameters that can be passed to the language model.

    Attributes:
        provider (str): The provider of the language model.
        model (str): The specific language model to use.
        api_key (Optional[str]): The API key to authenticate the requests.
        base_url (str): The base URL for the API endpoint.
        params (dict): Additional parameters that can be passed to the language model.

    Raises:
        ValueError: If the API key for the provider is not set (except for Ollama).
    """

    def __init__(self, provider: str, model: str, api_key: Optional[str] = None, base_url: Optional[str] = None, **kwargs):
        self.provider = provider.lower()
        self.model = model
        self.api_key = api_key or self._get_api_key()
        # if not self.api_key and self.provider != "ollama":
        #     raise ValueError(f"API key for {self.provider} is not set. Please set the appropriate environment variable.")
        self.base_url = base_url or self._get_base_url()
        self.params = kwargs

    # def _get_api_key(self) -> Optional[str]:
    #     """
    #     Retrieves the API key from environment variables based on the provider.

    #     Returns:
    #         Optional[str]: The API key if found, None otherwise.
    #     """
    #     env_var_map = {
    #         "openai": "OPENAI_API_KEY",
    #         "huggingface": "HF_TOKEN",
    #         "huggingface-openai": "HF_TOKEN",
    #         "huggingface-text": "HF_TOKEN",
    #         "gemini": "GENAI_API_KEY",
    #         "sdxl": "HF_TOKEN",
    #     }
    #     env_var = env_var_map.get(self.provider)
    #     return os.environ.get(env_var) if env_var else None

    def _get_base_url(self) -> Optional[str]:
        """
        Retrieves the base URL for the provider, if applicable.

        Returns:
            Optional[str]: The base URL if available, None otherwise.
        """
        if self.provider == "ollama":
            return "http://localhost:11434/v1"
        return None


class BaseLLM(ABC):
    """
    Base class for LLM (Language Model) implementations.

    Args:
        config (LLMConfig): The configuration object for the LLM.

    Attributes:
        config (LLMConfig): The configuration object for the LLM.
        client: The client object for the LLM.

    """

    def __init__(self, config: LLMConfig):
        self.config = config
        self.client = self._create_client()

    @abstractmethod
    def _create_client(self):
        pass

    @abstractmethod
    def get_response(self, prompt: str) -> Any:
        pass

class OpenAILLM(BaseLLM):
    """
    A class representing an OpenAI Language Model.

    This class extends the BaseLLM class and provides methods for interacting with the OpenAI API.

    Attributes:
        config (LLMConfig): The configuration object for the language model.

    Methods:
        _create_client: Creates an OpenAI client using the configuration settings.
        get_response: Generates a response from the language model given a prompt.

    """

    def _create_client(self):
        """
        Creates an OpenAI client using the configuration settings.

        Returns:
            OpenAI: An instance of the OpenAI client.

        """
        return OpenAI(api_key=self.config.api_key, base_url=self.config.base_url)

    def get_response(self, prompt: str) -> str:
        """
        Generates a response from the language model given a prompt.

        Args:
            prompt (str): The prompt for generating the response.

        Returns:
            str: The generated response from the language model.

        """
        response = self.client.chat.completions.create(
            model=self.config.model,
            messages=[{"role": "system", "content": prompt}],
            **self.config.params
        )
        return response.choices[0].message.content

class GeminiLLM(BaseLLM):
    """
    A class representing a Gemini Language Model.

    This class extends the BaseLLM class and provides methods for creating a client,
    getting a response based on a prompt, and handling Gemini-specific parameters.

    Attributes:
        config (LLMConfig): The configuration object for the GeminiLLM.
        client (GenerativeModel): The client for the Gemini Language Model.

    Methods:
        _create_client(): Creates a Gemini Language Model client.
        get_response(prompt: str) -> str: Generates a response based on the given prompt.
    """

    def _create_client(self):
        """
        Creates a Gemini Language Model client.

        Returns:
            GenerativeModel: The Gemini Language Model client.
        """
        genai.configure(api_key=self.config.api_key)
        return genai.GenerativeModel(model_name=self.config.model)

    def get_response(self, prompt: str, temperature: float = None, max_tokens: int = None) -> str:
        """
        Generates a response based on the given prompt.

        Args:
            prompt (str): The prompt for generating the response.
            temperature (float, optional): The temperature for response generation.
            max_tokens (int, optional): The maximum number of tokens to generate.

        Returns:
            str: The generated response.
        """
        # Define Gemini-specific parameters
        generation_params = {}
        if temperature is not None:
            generation_params['temperature'] = temperature
        if max_tokens is not None:
            generation_params['max_output_tokens'] = max_tokens
        if 'top_p' in self.config.params:
            generation_params['top_p'] = self.config.params['top_p']
        if 'top_k' in self.config.params:
            generation_params['top_k'] = self.config.params['top_k']
        
        # Create GenerationConfig with non-None parameters
        generation_config = GenerationConfig(**generation_params)
        
        try:
            response = self.client.generate_content(prompt, generation_config=generation_config)
            response.resolve()
            return response.text
        except Exception as e:
            raise ValueError(f"Error generating content with Gemini: {str(e)}")

class SDXLLLM(BaseLLM):
    """
    SDXLLLM class represents a specific implementation of the BaseLLM class.
    It provides methods for creating a client and generating a response based on a prompt.
    """

    def _create_client(self):
        """
        Creates and returns an InferenceClient object based on the model and API key specified in the configuration.
        """
        return InferenceClient(model=self.config.model, token=self.config.api_key)

    def get_response(self, prompt: str) -> str:
        """
        Generates a response based on the given prompt.

        Args:
            prompt (str): The prompt to generate a response for.

        Returns:
            str: The generated response as a string.

        Raises:
            Exception: If there is an error generating the image.
        """
        try:
            image = self.client.text_to_image(prompt, **self.config.params)
            if isinstance(image, Image.Image):
                image_path = f"{prompt[:20].replace(' ', '_')}.jpg"
                image.save(image_path)
                return f"Image saved as {image_path}"
            else:
                return "Failed to generate image"
        except Exception as e:
            return f"Error generating image: {str(e)}"

class HFOpenAIAPILLM(BaseLLM):
    """
    Hugging Face Language Model (HFLLM) class that uses the OpenAI API.

    This class represents a Hugging Face Language Model and provides methods for creating a client and getting a response.

    Attributes:
        config (LLMConfig): The configuration object for the HFLLM.
        client (OpenAI): The client object for making API requests.

    Methods:
        _create_client: Creates a client object for making API requests.
        get_response: Gets a response from the language model given a prompt.
    """

    def _create_client(self):
        base_url = f"https://api-inference.huggingface.co/models/{self.config.model}/v1/"
        return OpenAI(base_url=base_url, api_key=self.config.api_key)

    def get_response(self, prompt: str, temperature: float = 0.7, max_tokens: int = 4096) -> str:
        response = self.client.chat.completions.create(
            model=self.config.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
            **self.config.params
        )
        return response.choices[0].message.content

    
class OllamaLLM(BaseLLM):
    """
    A class representing an Ollama served Language Model.

    This class extends the BaseLLM class and provides methods for interacting with the Ollama API.

    Attributes:
        config (LLMConfig): The configuration object for the language model.

    Methods:
        _create_client: Creates an Ollama client using the configuration settings.
        get_response: Generates a response from the language model given a prompt.
    """

    def _create_client(self):
        """
        Creates an Ollama client using the configuration settings.

        Returns:
            OpenAI: An instance of the OpenAI client configured for Ollama.
        """
        return OpenAI(base_url=self.config.base_url, api_key="ollama")

    def get_response(self, prompt: str, temperature: float = 0.7, max_tokens: int = 4096) -> str:
        """
        Generates a response from the language model given a prompt.

        Args:
            prompt (str): The prompt for generating the response.
            temperature (float): The temperature for response generation.
            max_tokens (int): The maximum number of tokens to generate.

        Returns:
            str: The generated response from the language model.
        """
        response = self.client.chat.completions.create(
            model=self.config.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
            **self.config.params
        )
        return response.choices[0].message.content
    
class HFTextLLM(BaseLLM):
    """
    A class representing a Hugging Face Inference Language Model.

    This class extends the BaseLLM class and provides methods for interacting with the Hugging Face Inference API.

    Attributes:
        config (LLMConfig): The configuration object for the language model.

    Methods:
        _create_client: Creates a Hugging Face Inference client using the configuration settings.
        get_response: Generates a response from the language model given a prompt.
    """
    
    def _create_client(self):
        """
        Creates a Hugging Face Inference client using the configuration settings.

        Returns:
            InferenceClient: An instance of the Hugging Face Inference client.
        """
        return InferenceClient(model=self.config.model, token=self.config.api_key)

    def get_response(self, prompt: str, model: str = None, temperature: float = None, max_tokens: int = None) -> str:
        """
        Generates a response from the language model given a prompt.

        Args:
            prompt (str): The prompt for generating the response.
            model (str, optional): The model to use. If provided, it overrides the default model.
            temperature (float, optional): The temperature for response generation.
            max_tokens (int, optional): The maximum number of tokens to generate.

        Returns:
            str: The generated response from the language model.
        """
        parameters = {}
        if temperature is not None:
            parameters['temperature'] = temperature
        if max_tokens is not None:
            parameters['max_new_tokens'] = max_tokens
        if 'top_p' in self.config.params:
            parameters['top_p'] = self.config.params['top_p']
        if 'top_k' in self.config.params:
            parameters['top_k'] = self.config.params['top_k']

        client = self._create_client()
        if model:
            client.model = model

        response = client.text_generation(
            prompt,
            **parameters
        )

        return response

class LLMFactory:
    """
    Factory class for creating Language Model Managers (LLMs).
    """
    llm_classes = {
        "openai": OpenAILLM,
        "gemini": GeminiLLM,
        # "sdxl": SDXLLLM,
        "huggingface-openai": HFOpenAIAPILLM,
        "huggingface-text": HFTextLLM,
        "ollama": OllamaLLM
    }

    @staticmethod
    def create_llm(config: LLMConfig) -> BaseLLM:
        """
        Creates an instance of a Language Model Manager (LLM) based on the given configuration.

        Args:
            config (LLMConfig): The configuration object specifying the LLM provider.

        Returns:
            BaseLLM: An instance of the LLM based on the provider specified in the configuration.

        Raises:
            ValueError: If the provider specified in the configuration is not supported.
        """
        if config.provider not in LLMFactory.llm_classes:
            raise ValueError(f"Unsupported provider: {config.provider}")
        return LLMFactory.llm_classes[config.provider](config)


def get_llm(provider: str, model: str, **kwargs) -> BaseLLM:
    config = LLMConfig(provider, model, **kwargs)
    return LLMFactory.create_llm(config)