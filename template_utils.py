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

def get_templates() -> List[Dict[str, str]]:
    return [
        {"label": "Flowchart", "value": TemplateEnum.FLOWCHART.value},
        {"label": "Mindmap", "value": TemplateEnum.MINDMAP.value},
        {"label": "Timeline", "value": TemplateEnum.TIMELINE.value},
        {"label": "User Journey", "value": TemplateEnum.USERJOURNEY.value},
        {"label": "Entity Relationship", "value": TemplateEnum.ENTITYRELATIONSHIP.value},
        {"label": "Sequence Diagram", "value": TemplateEnum.SEQUENCE.value},
        {"label": "State Diagram", "value": TemplateEnum.STATE.value},
    ]