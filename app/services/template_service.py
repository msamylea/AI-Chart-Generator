import os
import re

def read_syntax_file(template: str) -> str:
    syntax_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'syntax')
    file_path = os.path.join(syntax_dir, f"{template.lower()}.md")
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
    except Exception as e:
        raise ValueError(f"Error reading syntax file for template {template}: {str(e)}")

def get_templates() -> list:
    syntax_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'syntax')
    return [file[:-3].upper() for file in os.listdir(syntax_dir) if file.endswith('.md')]