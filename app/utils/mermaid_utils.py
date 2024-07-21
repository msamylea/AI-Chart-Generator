import asyncio
from typing import Dict, Any, List
import os
import logging
import time
import re
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, RetryError
from openai import AuthenticationError, RateLimitError, BadRequestError
import inspect
from io import BytesIO

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)

def render_mermaid(mermaid_code: str) -> str:
    """
    Returns the Mermaid code without modification.

    Args:
        mermaid_code (str): The Mermaid code to be rendered.

    Returns:
        str: The original Mermaid code.
    """
    return mermaid_code

def export_svg(chart: str, name: str) -> BytesIO:
    # In a real-world scenario, you'd convert the Mermaid syntax to SVG here
    # For now, we'll just return the chart string as bytes
    return BytesIO(chart.encode())

def copy_mermaid_code(chart: str) -> str:
    return chart

BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # Move up one directory level to 'app'
SYNTAX_DIR_LOC = os.path.join(BASE_DIR, 'syntax')  # Correct path to the syntax directory

if not os.path.exists(SYNTAX_DIR_LOC):
    raise FileNotFoundError(f"The syntax directory does not exist at the expected path: {SYNTAX_DIR_LOC}")

def get_available_templates() -> List[str]:
    # List comprehension to get all .md files in SYNTAX_DIR_LOC, removing the extension and converting to uppercase
    return [file[:-3].upper() for file in os.listdir(SYNTAX_DIR_LOC) if file.endswith('.md')]

def read_syntax_file(template: str) -> str:
    # Construct the full path to the desired syntax file
    file_path = os.path.join(SYNTAX_DIR_LOC, f"{template.lower()}.md")
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            
        # Extract the syntax section
        syntax_section = re.search(r'## Syntax\n\n(.*?)\n\n', content, re.DOTALL)
        if syntax_section:
            syntax = syntax_section.group(1)
        else:
            syntax = "Syntax section not found in the file."
        
        # Extract examples
        examples = re.findall(r'```mermaid-example\n(.*?)```', content, re.DOTALL)
        
        return f"Syntax:\n{syntax}\n\nExamples:\n" + "\n\n".join(examples)
    except FileNotFoundError:
        raise ValueError(f"Syntax file not found for template: {template}")
    except UnicodeDecodeError:
        # If UTF-8 fails, try with ISO-8859-1 encoding
        try:
            with open(file_path, 'r', encoding='iso-8859-1') as file:
                content = file.read()
            
            # Extract the syntax section
            syntax_section = re.search(r'## Syntax\n\n(.*?)\n\n', content, re.DOTALL)
            if syntax_section:
                syntax = syntax_section.group(1)
            else:
                syntax = "Syntax section not found in the file."
            
            # Extract examples
            examples = re.findall(r'```mermaid-example\n(.*?)```', content, re.DOTALL)
            
            return f"Syntax:\n{syntax}\n\nExamples:\n" + "\n\n".join(examples)
        except Exception as e:
            raise ValueError(f"Error reading syntax file for template {template}: {str(e)}")
        
def extract_mermaid_code(response: str) -> str:
    # Define the supported diagram types
    diagram_types = r'(class|erDiagram|flowchart|mindmap|sequenceDiagram|stateDiagram|timeline|journey|gantt|block-beta|quadrantChart|sankey-beta|requirementDiagram|zenuml)'
    
    # Look for Mermaid code enclosed in ```mermaid ... ``` or just the content starting with a valid diagram type
    mermaid_pattern = r'```(?:mermaid)?\n([\s\S]*?)\n```'
    diagram_pattern = rf'({diagram_types})[\s\S]*'
    
    mermaid_match = re.search(mermaid_pattern, response, re.IGNORECASE)
    if mermaid_match:
        code = mermaid_match.group(1).strip()
    else:
        diagram_match = re.search(diagram_pattern, response, re.IGNORECASE)
        if diagram_match:
            code = diagram_match.group(0).strip()
        else:
            code = response.strip()
    
    # Remove any leading text before the diagram type
    code = re.sub(r'^.*?(' + diagram_types + ')', r'\1', code, flags=re.IGNORECASE | re.DOTALL)
    
    # Split the code into lines
    lines = code.split('\n')
    processed_lines = []
    block_stack = []
    valid_verify_methods = ['analysis', 'demonstration', 'inspection', 'test']


    for line in lines:
        stripped_line = line.strip()
        
        if stripped_line.startswith(('block:', 'subgraph')):
            block_stack.append(stripped_line)
        elif stripped_line == 'end' and block_stack:
            block_stack.pop()

        if 'verifymethod:' in line:
            # Split the line at 'verifymethod:'
            parts = line.split('verifymethod:', 1)
            # Get the verify method value
            verify_method = parts[1].strip().lower()
            # Check if the verify method is valid
            if verify_method not in valid_verify_methods:
                # If not valid, replace with a default value
                verify_method = 'inspection'
            # Reconstruct the line with the correct verify method
            line = f"{parts[0]}verifymethod: {verify_method}"
        
        processed_lines.append(line)
        
        # If we're at the end of a block and there's no 'end', add it
        if stripped_line and not stripped_line.startswith(('block:', 'subgraph', 'end')) and block_stack:
            indent = len(line) - len(line.lstrip())
            if indent <= len(block_stack[-1]) - len(block_stack[-1].lstrip()):
                processed_lines.append(' ' * indent + 'end')
                block_stack.pop()

    # Add any remaining 'end' statements
    while block_stack:
        processed_lines.append('end')
        block_stack.pop()

    processed_code = '\n'.join(processed_lines)
    
    # Define a more permissive regex pattern for valid Mermaid syntax
    valid_syntax_pattern = rf"""
        ^\s*({diagram_types}|
        %%\{{init:.*?\}}%%|
        \w+.*|
        \s*subgraph.*|
        \s*end.*|
        \s*class\s+.*|
        \s*classDef\s+.*|
        \s*\w+.*(?:-->|--|==|::|:|<=|=|\+|-|\)|\(|\*).*|
        \s*[\w\s"'\[\]]+(?:-->|---|===|~~~|:).*|
        \s*\w+\s*\[.*?\].*|
        \s*\w+\s*\(.*?\).*|
        \s*\w+>.*?].*|
        \s*\w+\s*:.*|
        \s*section\s+.*|
        \s*\d+\s*:.*|
        \s*title\s+.*|
        \s*[-+*]\s+.*|
        \s*%%.*|
        \s*)
    """

    if re.search(r'\|.*\|>', processed_code):
        processed_code = re.sub(r'\|(.*?)\|>', r'|\1|', processed_code)
    # Special handling for mindmap and block-beta
    if re.match(r'^(mindmap|block-beta)', processed_code, re.IGNORECASE):
        # For mindmap and block-beta, we want to keep all lines that are not completely blank
        valid_lines = [line for line in processed_code.split('\n') if line.strip()]
    else:
        # For other diagrams, use the regex pattern
        valid_lines = [line for line in processed_code.split('\n') 
                       if re.match(valid_syntax_pattern, line, re.VERBOSE | re.IGNORECASE)]
    
    final_code = '\n'.join(valid_lines)
    
    print("Processed Mermaid Code:", final_code)

    return final_code


class LLMError(Exception):
    """Base class for LLM-related errors."""
    pass

class AuthError(LLMError):
    """Raised when there's an authentication error."""
    pass
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type((RateLimitError, BadRequestError)),
    reraise=True
)
async def generate(input: str, selected_template: str, llm, selected_model: str, temperature: float, max_tokens: int, timeout: int = 300) -> Dict[str, Any]:
    start_time = time.time()
    try:
        logger.info(f"Starting generation for input: '{input}', template: {selected_template}, model: {selected_model}, temperature: {temperature}, max_tokens: {max_tokens}")
        
        available_templates = get_available_templates()
        if selected_template not in available_templates:
            raise ValueError(f"Invalid template: {selected_template}. Available templates: {', '.join(available_templates)}")

        syntax_doc = read_syntax_file(selected_template)

        prompt = f"""
        Create a {selected_template} diagram in Mermaid syntax about: {input}

        Use the following syntax and examples as a guide:

        {syntax_doc}

         Additional Instructions:
        - Strictly follow the Mermaid syntax for {selected_template} diagrams.
        - Use the appropriate flow diagram symbols and connectors where applicable.
        - Long text should be wrapped by using "'<text>'" around the strings
        - To create bold text, use double asterisks ** before and after the text.
        - For italics, use single asterisks * before and after the text.
        - Do not add any explanations or notes outside the Mermaid code.
        - Ensure each line of the diagram is properly formatted according to the syntax.
        - Top to bottom is preferred for flow charts. Long charts are often best oriented top to bottom. 
        - Do not use 'end' syntax unless it's explicitly part of the {selected_template} diagram syntax.
        - Use clear labels to avoid ambiguity and ensure all understand the information. Label all screens, actions, and decisions. 
        - Make sure your user flows are complete and lead to a clear resolution.
        - Ensure the diagram is clear and easy to understand at a glance.
        - Always have a legend key if you are using colors or icons.
        - Use color with purpose in your user flows. Assign different colors to different elements to make the diagram easier to understand. For instance, use green for decisions, blue for screens, and yellow for entry points. 
        Generate the Mermaid code for the {selected_template} diagram:
        """

        try:
            response = await call_llm(llm, prompt, temperature, max_tokens, timeout)
        except RetryError as retry_error:
            if isinstance(retry_error.last_attempt.exception(), AuthenticationError):
                raise AuthError("Authentication failed. Please check your API key.")
            elif isinstance(retry_error.last_attempt.exception(), RateLimitError):
                raise RateLimitError("Rate limit exceeded. Please try again later.")
            elif isinstance(retry_error.last_attempt.exception(), BadRequestError):
                raise BadRequestError(f"Bad request: {str(retry_error.last_attempt.exception())}")
            else:
                raise LLMError(f"Unexpected error calling LLM: {str(retry_error.last_attempt.exception())}")
        except Exception as e:
            raise LLMError(f"Unexpected error calling LLM: {str(e)}")

        logger.debug(f"Raw LLM output: {response}")
        
        # Extract Mermaid code from the response
        mermaid_code = extract_mermaid_code(response)
        logger.debug(f"Extracted Mermaid code: {mermaid_code}")
        return {"text": mermaid_code}

    except Exception as e:
        logger.error(f"Error in generate function: {str(e)}", exc_info=True)
        raise
    finally:
        end_time = time.time()
        logger.info(f"Total execution time: {end_time - start_time:.2f} seconds")

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def call_llm(llm, prompt: str, temperature: float, max_tokens: int, timeout: int):
    loop = asyncio.get_event_loop()
    
    # Inspect the get_response method of the LLM instance
    params = inspect.signature(llm.get_response).parameters
    
    # Prepare kwargs based on available parameters
    kwargs = {'prompt': prompt}
    if 'temperature' in params:
        kwargs['temperature'] = temperature
    if 'max_tokens' in params:
        kwargs['max_tokens'] = max_tokens
    
    return await loop.run_in_executor(None, lambda: llm.get_response(**kwargs))
    
