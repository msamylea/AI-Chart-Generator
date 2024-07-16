from pydantic import BaseModel, Field
from typing import Optional

class DiagramRequest(BaseModel):
    input: str
    selectedTemplate: str
    provider: str
    model: str
    temperature: float = Field(0.7, ge=0, le=1)
    maxTokens: int = Field(4096, gt=0)
    apiKey: Optional[str] = None

class DiagramResponse(BaseModel):
    text: str
