from enum import Enum
from typing import List, Dict

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
    ZENUML = "ZENUML"  

def get_templates() -> List[Dict[str, str]]:
    return [
        {"label": "Flowchart", "value": TemplateEnum.FLOWCHART.value},
        {"label": "Mindmap", "value": TemplateEnum.MINDMAP.value},
        {"label": "Timeline", "value": TemplateEnum.TIMELINE.value},
        {"label": "User Journey", "value": TemplateEnum.USERJOURNEY.value},
        {"label": "Entity Relationship", "value": TemplateEnum.ENTITYRELATIONSHIP.value},
        {"label": "Sequence Diagram", "value": TemplateEnum.SEQUENCE.value},
        {"label": "State Diagram", "value": TemplateEnum.STATE.value},
        {"label": "Gantt Chart", "value": TemplateEnum.GANTT.value},
        {"label": "Quadrant Diagram", "value": TemplateEnum.QUADRANT.value},
        {"label": "Sankey Diagram", "value": TemplateEnum.SANKEY.value},
        {"label": "Requirement Diagram", "value": TemplateEnum.REQUIREMENT.value},
        {"label": "Block", "value": TemplateEnum.BLOCK.value},  
        {"label": "ZenUML", "value": TemplateEnum.ZENUML.value},
    ]