from enum import Enum

class TemplateEnum(Enum):
    FLOWCHART = "FLOWCHART"
    MINDMAP = "MINDMAP"
    TIMELINE = "TIMELINE"
    USERJOURNEY = "USERJOURNEY"
    ENTITYRELATIONSHIP = "ENTITYRELATIONSHIP"
    SEQUENCE = "SEQUENCE"
    STATE = "STATE"
    GANTT = "GANTT"
    QUADRANT = "QUADRANT"
    SANKEY = "SANKEY"
    REQUIREMENT = "REQUIREMENT"
    BLOCK = "BLOCK" 
    ZENUML = "ZENUML"  # Added ZENUML to the enum

common_rules = """
- Strict rules: Do not add Note and do not explain the code.
- You must place the code inside code fences (```mermaid <code> ```).
- Do not add any additional text except code.
- Do not use 'end' syntax.
- Do not use any parentheses inside blocks.
"""

def prompt_by_template(template_enum: TemplateEnum, input_text: str) -> str:
    prompts = {
        TemplateEnum.FLOWCHART: lambda input: f"Create a flowchart about {input}\n{common_rules}\n" +
            "Examples:\n" +
            "Correct: C -->|true| D[setLoading]\n" +
            "Wrong: C -->|true| D(setLoading=>true)\n" +
            "Correct: C -->|true| D[axios.post '/api/ask' input]\n" +
            "Wrong: C -->|true| D(axios.post('/api/ask', {{input,}}))\n" +
            "Correct: J -->|text| L[Print 'number is not a prime number']\n" +
            "Wrong: J -->|| L[Print 'number is not a prime number']\n",

        TemplateEnum.GANTT: lambda input: f"Create a Gantt chart about {input}\n{common_rules}\n",

        TemplateEnum.MINDMAP: lambda input: f"Create a mindmap about {input}\n{common_rules}\n",

        TemplateEnum.TIMELINE: lambda input: f"Create a timeline about {input}\n{common_rules}\n" +
            "Use the following syntax:\n" +
            "timeline\n" +
            "    title [Optional Title]\n" +
            "    section [Section name]\n" +
            "    [Event] : [description]\n" +
            "Example:\n" +
            "timeline\n" +
            "    title My Day\n" +
            "    section Morning\n" +
            "    Wake up : 6:00 AM\n" +
            "    Breakfast : 7:00 AM\n" +
            "    section Afternoon\n" +
            "    Lunch : 12:00 PM\n" +
            "    Meeting : 2:00 PM\n",

        TemplateEnum.USERJOURNEY: lambda input: f"Create a user journey diagram about {input}\n{common_rules}\n",

        TemplateEnum.ENTITYRELATIONSHIP: lambda input: f"Create an entity-relationship diagram about {input}\n{common_rules}\n",

        TemplateEnum.SEQUENCE: lambda input: f"Create a sequence diagram about {input}\n{common_rules}\n",

        TemplateEnum.STATE: lambda input: f"Create a state diagram about {input}\n{common_rules}\n",


        TemplateEnum.QUADRANT: lambda input: f"Create a quadrant diagram about {input}\n{common_rules}\n",

        TemplateEnum.SANKEY: lambda input: f"Create a sankey diagram about {input}\n{common_rules}\n",

        TemplateEnum.REQUIREMENT: lambda input: f"""Create a requirement diagram about {input}\n{common_rules}\n" +
                        "Additional instructions for requirement diagrams:\n" +
                        "- Use only the following values for verifymethod: analysis, demonstration, inspection, test\n" +
                        "- - Ensure that the text field is always enclosed in double quotes\n" +
                        "- Example: \n" +
                        "functionalRequirement example_req {{ \n" +
                            "id: 1  \n" +
                            "text: "Example requirement"  \n" +
                            "risk: medium \n" +
                            "verifymethod: inspection \n" +
                        "}},\n""",

        TemplateEnum.BLOCK: lambda input: f"Create a block diagram about {input}\n{common_rules}\n", 

        TemplateEnum.ZENUML: lambda input: f"Create a ZenUML diagram about {input}\n{common_rules}\n",

    }

    if template_enum in prompts:
        return prompts[template_enum](input_text)
    else:
        raise ValueError(f"Template {template_enum} not supported")