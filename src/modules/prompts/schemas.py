from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field


class PromptBase(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    prompt_text: str = Field(..., description="The prompt to send to the LLM")
    model_name: Optional[str] = Field("llama3", description="The model to use")


class PromptCreate(PromptBase):
    pass


class PromptResponse(PromptBase):
    id: int
    response_text: Optional[str] = None
    processing_time_ms: Optional[int] = None
    meta_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    user_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
