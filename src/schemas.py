from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class PromptBase(BaseModel):
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

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class InvoiceItem(BaseModel):
    description: str
    quantity: float
    unit_price: float
    total: float

class Invoice(BaseModel):
    invoice_number: Optional[str] = None
    vendor_name: str
    date: Optional[str] = None
    items: List[InvoiceItem] = []
    total_amount: float
    currency: str = "USD"

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str
    role: str = "user" # Optional during registration, defaults to user

class UserResponse(UserBase):
    id: int
    is_active: bool
    role: str
    
    class Config:
        from_attributes = True
