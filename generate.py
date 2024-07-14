import asyncio
from typing import Dict, Any, List
import os
import logging
import time
import re
from tenacity import retry, stop_after_attempt, wait_exponential, RetryError
from openai import AuthenticationError, BadRequestError
import inspect

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def get_available_templates() -> List[str]:
    syntax_dir = os.path.join(os.path.dirname(__file__), 'syntax')
    return [file[:-3].upper() for file in os.listdir(syntax_dir) if file.endswith('.md')]

def read_syntax_file(template: str) -> str:
    syntax_dir = os.path.join(os.path.dirname(__file__), 'syntax')
    file_path = os.path.join(syntax_dir, f"{template.lower()}.md")
    try:
        with open(file_path, 'r') as file:
            print(f"Reading syntax file: {file_path}")
            return file.read()
    except FileNotFoundError:
        raise ValueError(f"Syntax file not found for template: {template}")

def extract_mermaid_code(response: str) -> str:
    # Define the supported diagram types
    diagram_types = r'(classDiagram|erDiagram|flowchart|mindmap|sequenceDiagram|stateDiagram|timeline|journey)'
    
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
    
    if not re.match(rf'^{diagram_types}', code, re.IGNORECASE):
        code = 'flowchart LR\n' + code

    # Split the code into lines
    lines = code.split('\n')
    processed_lines = []

    for line in lines:
        modified_line = re.sub(r'\|>', r'|', line)
        
        # Your existing logic for handling 'actor' and 'useCase'
        if re.match(r'^flowchart', lines[0], re.IGNORECASE):
            if line.strip().startswith(('actor', 'useCase')):
                parts = line.split()
                if len(parts) >= 4 and parts[2] == 'as':
                    modified_line = f"    {parts[3]}[{parts[1]}]"
                    processed_lines.append(modified_line)
                    continue

        processed_lines.append(modified_line)

    processed_code = '\n'.join(processed_lines)
    
    # Define a regex pattern for valid Mermaid syntax across different diagram types
    valid_syntax_pattern = rf"""
        ^\s*({diagram_types}|class\s+[\w<>]+|classDef\s+\w+|\w+\s*(?:-->|--|==|::|:|<=|=|\+|-|\)|\(|\*)\s*[\w<>"']+|[\w\s"'\[\]]+(?:-->|---|===|~~~|:)[\w\s"'\[\]]+|\w+\s*\[.*?\]|\w+\s*\(.*?\)|\w+>.*?]|\w+\s*:\s*.*|\s*section\s+.*|\s*\d+\s*:.*|\s*title\s+.*|\s*[-+*]\s+.*|.*%%.*)
    """
    
    # Special handling for mindmap
    if re.match(r'^mindmap', processed_code, re.IGNORECASE):
        # For mindmap, we want to keep all lines that are not completely blank
        valid_lines = [line for line in processed_code.split('\n') if line.strip()]
    else:
        # For other diagrams, use the regex pattern
        valid_lines = [line for line in processed_code.split('\n') 
                       if re.match(valid_syntax_pattern, line.strip(), re.VERBOSE | re.IGNORECASE)]
    
    final_code = '\n'.join(valid_lines)
    
    print("Processed Mermaid Code:", final_code)

    return final_code


async def generate(input: str, selected_template: str, llm, selected_model: str, temperature: float, max_tokens: int, timeout: int = 300) -> Dict[str, Any]:
    start_time = time.time()
    try:
        logger.info(f"Starting generation for input: '{input}', template: {selected_template}, model: {selected_model}, temperature: {temperature}, max_tokens: {max_tokens}")
        
        available_templates = get_available_templates()
        if selected_template not in available_templates:
            raise ValueError(f"Invalid template: {selected_template}. Available templates: {', '.join(available_templates)}")

        syntax_doc = read_syntax_file(selected_template)

        prompt = f"{syntax_doc}\n\nInstructions:\n- use different shapes, colors and also use icons when possible as mentioned in the doc.\n- strict rules: do not add Note and do not explain the code and do not add any additional text except code,\n- do not use 'end' syntax\n- do not use any parenthesis inside block and only create a single block of code. always use underscores for attribute names instead of spaces.\n\nCreate a {selected_template} in mermaid syntax about: {input}"

        try:
            response = await call_llm(llm, prompt, temperature, max_tokens, timeout)
        except RetryError as retry_error:
            if isinstance(retry_error.last_attempt.exception(), (BadRequestError, AuthenticationError)):
                raise retry_error.last_attempt.exception()
            else:
                raise
        
        logger.debug(f"Raw LLM output: {response}")
        
        # Extract Mermaid code from the response
        mermaid_code = extract_mermaid_code(response)
        
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