from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.database import get_db
from src.infrastructure.llm.ollama_client import OllamaClient
from src.modules.auth.models import User
from src.modules.auth.service import get_current_user
from src.modules.prompts.schemas import PromptCreate, PromptResponse
from src.modules.prompts.service import PromptService

router = APIRouter()


def get_prompt_service(db: AsyncSession = Depends(get_db)) -> PromptService:
    # Dependency injection of LLM Client
    llm_client = OllamaClient(base_url=settings.OLLAMA_BASE_URL)
    return PromptService(db, llm_client)


@router.post("/prompts", response_model=PromptResponse, status_code=status.HTTP_201_CREATED)
async def create_prompt(
    prompt_in: PromptCreate,
    service: PromptService = Depends(get_prompt_service),
    current_user: User = Depends(get_current_user),
):
    try:
        return await service.create_prompt(
            prompt_text=prompt_in.prompt_text,
            user_id=current_user.id,
            model=prompt_in.model_name,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process prompt: {str(e)}",
        ) from e


@router.get("/prompts", response_model=List[PromptResponse])
async def get_prompts(
    skip: int = 0,
    limit: int = 20,
    service: PromptService = Depends(get_prompt_service),
    current_user: User = Depends(get_current_user),
):
    return await service.get_prompts(user_id=current_user.id, skip=skip, limit=limit)


@router.get("/prompts/{prompt_id}", response_model=PromptResponse)
async def get_prompt(
    prompt_id: int,
    service: PromptService = Depends(get_prompt_service),
    current_user: User = Depends(get_current_user),
):
    prompt = await service.get_prompt_by_id(prompt_id, user_id=current_user.id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return prompt


@router.post("/extract-invoice", status_code=status.HTTP_200_OK)
async def extract_invoice(
    text_content: str,
    service: PromptService = Depends(get_prompt_service),
    current_user: User = Depends(get_current_user),
):
    """
    Accounting specific endpoint: Extracts invoice data from raw text.
    Returns structured JSON.
    """
    return await service.extract_invoice(text_content=text_content, user_id=current_user.id)
