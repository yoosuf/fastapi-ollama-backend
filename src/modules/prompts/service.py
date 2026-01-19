from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.interfaces.llm_interface import LLMInterface
from src.modules.prompts.agents.invoice_agent import InvoiceAgent
from src.modules.prompts.models import Prompt


class PromptService:
    def __init__(self, db: AsyncSession, llm_client: LLMInterface):
        self.db = db
        self.llm_client = llm_client

    async def create_prompt(
        self,
        prompt_text: str,
        user_id: int,
        model: str = settings.OLLAMA_MODEL,
        meta_data: Optional[Dict[str, Any]] = None,
        **llm_kwargs,
    ) -> Prompt:
        """
        1. Send prompt to LLM
        2. Persist prompt and response
        3. Return Prompt object
        """
        # Call LLM
        try:
            llm_result = await self.llm_client.generate(prompt=prompt_text, model=model, **llm_kwargs)
        except Exception as e:
            raise e

        # Merge metadata
        combined_meta = llm_result.get("meta_data", {})
        if meta_data:
            combined_meta.update(meta_data)

        # Create DB Record
        db_prompt = Prompt(
            user_id=user_id,
            prompt_text=prompt_text,
            response_text=llm_result["response_text"],
            model_name=model,
            processing_time_ms=llm_result["processing_time_ms"],
            meta_data=combined_meta,
        )

        self.db.add(db_prompt)
        await self.db.commit()
        await self.db.refresh(db_prompt)

        return db_prompt

    async def get_prompts(self, user_id: int, skip: int = 0, limit: int = 20) -> List[Prompt]:
        query = (
            select(Prompt).where(Prompt.user_id == user_id).order_by(Prompt.created_at.desc()).offset(skip).limit(limit)
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_prompt_by_id(self, prompt_id: int, user_id: int) -> Optional[Prompt]:
        query = select(Prompt).where(Prompt.id == prompt_id, Prompt.user_id == user_id)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def extract_invoice(
        self, text_content: str, user_id: int, model: str = settings.OLLAMA_MODEL
    ) -> Dict[str, Any]:
        """
        Specialized method for Accounting: Extracts generic invoice data as JSON.
        Uses InvoiceAgent for prompt construction and parsing.
        """
        full_prompt = InvoiceAgent.get_extraction_prompt(text_content)
        
        # Call via create_prompt with format='json'
        prompt_obj = await self.create_prompt(
            prompt_text=full_prompt,
            user_id=user_id,
            model=model,
            meta_data={"type": "invoice_extraction"},
            format="json"
        )
        
        return InvoiceAgent.parse_response(prompt_obj.response_text)
