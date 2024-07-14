from enum import Enum

class TemplateEnum(Enum):
    FLOWCHART = "FLOWCHART"
    MINDMAP = "MINDMAP"
    TIMELINE = "TIMELINE"
    USERJOURNEY = "USERJOURNEY"
    CLASS = "CLASS"
    ENTITYRELATIONSHIP = "ENTITYRELATIONSHIP"
    SEQUENCE = "SEQUENCE"
    STATE = "STATE"

common_rules = """- strict rules: do not add Note and do not explain the code and do not add any additional text except code, do not use 'end' syntax
- do not use any parenthesis inside block"""

def prompt_by_template(template_enum: TemplateEnum, input_text: str) -> str:
    prompts = {
        TemplateEnum.FLOWCHART: lambda input: f"write flowchart about {input} \n{common_rules}\n" +
            "eg:  correct: C -->|true| D(setLoading), wrong: correct: C -->|true| D(setLoading=>true)\n" +
            "eg:  correct: C -->|true| D(axios.post=>'/api/ask', input), wrong: C -->|true| D(axios.post('/api/ask', {input,}))\n" +
            "eg: correct: J -->|text| L[Print 'number is not a prime number'] wrong: J -->|| L[Print 'number is not a prime number']\n",

        TemplateEnum.MINDMAP: lambda input: f"write mindmap about {input} \n{common_rules}\n syntax:\n",
    }

    if template_enum in prompts:
        return prompts[template_enum](input_text)
    else:
        raise ValueError("Template not supported")