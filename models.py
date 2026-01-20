from pydantic import BaseModel, Field
from typing import List, Optional

class ChatInput(BaseModel):
    user_id: str = Field(..., description="Unique ID of the user")
    message: str = Field(..., description="The user's question")
    platform: str = Field(..., description="Source: linkedin, website, twitter")
    chat_history: Optional[List[dict]] = Field(default=[], description="Previous messages")

class ChatOutput(BaseModel):
    response_text: str
    intent: str
    estimated_price: Optional[str] = None
    confidence_score: float
    suggested_actions: List[str]