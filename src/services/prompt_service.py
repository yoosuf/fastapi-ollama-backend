from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from src.models import Prompt
from src.services.llm_interface import LLMInterface
from src.config import settings

class PromptService:
    def __init__(self, db: AsyncSession, llm_client: LLMInterface):
        self.db = db
        self.llm_client = llm_client

    async def create_prompt(self, prompt_text: str, user_id: int, model: str = settings.OLLAMA_MODEL) -> Prompt:
        """
        1. Send prompt to LLM
        2. Persist prompt and response
        3. Return Prompt object
        """
        # Call LLM
        try:
            llm_result = await self.llm_client.generate(prompt=prompt_text, model=model)
        except Exception as e:
            raise e

        # Create DB Record
        db_prompt = Prompt(
            user_id=user_id,
            prompt_text=prompt_text,
            response_text=llm_result["response_text"],
            model_name=model,
            processing_time_ms=llm_result["processing_time_ms"],
            meta_data=llm_result.get("meta_data", {})
        )
        
        self.db.add(db_prompt)
        await self.db.commit()
        await self.db.refresh(db_prompt)
        
        return db_prompt

    async def get_prompts(self, user_id: int, skip: int = 0, limit: int = 20) -> List[Prompt]:
        query = select(Prompt).where(Prompt.user_id == user_id).order_by(Prompt.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_prompt_by_id(self, prompt_id: int, user_id: int) -> Optional[Prompt]:
        query = select(Prompt).where(Prompt.id == prompt_id, Prompt.user_id == user_id)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def extract_invoice(self, text_content: str, user_id: int, model: str = settings.OLLAMA_MODEL) -> Dict[str, Any]:
        """
        Specialized method for Accounting: Extracts generic invoice data as JSON.
        """
        schema_instruction = """
        You are an invoice extraction AI. Extract the following fields from the text into a JSON object:
        - invoice_number (string)
        - vendor_name (string)
        - date (string, YYYY-MM-DD)
        - items (list of objects with description, quantity, unit_price, total)
        - total_amount (float)
        - currency (string, e.g. USD, EUR)
        
        Respond ONLY with the JSON object. No preamble.
        """
        
        full_prompt = f"{schema_instruction}\n\nINPUT TEXT:\n{text_content}"
        
        # Call LLM with format='json' (Ollama supports this)
        llm_result = await self.llm_client.generate(prompt=full_prompt, model=model, format="json")
        
        # Save the interaction as a prompt record for audit
        db_prompt = Prompt(
            user_id=user_id,
            prompt_text=f"[INVOICE EXTRACTION] {text_content[:200]}...",
            response_text=llm_result["response_text"],
            model_name=model,
            processing_time_ms=llm_result["processing_time_ms"],
            meta_data={"type": "invoice_extraction", "raw": llm_result["meta_data"]}
        )
        self.db.add(db_prompt)
        await self.db.commit()
        
        # return the raw JSON string or parsed dict depending on what the LLM gave back
        # Ideally we parse it to valid JSON here
        import json
        try:
            return json.loads(llm_result["response_text"])
        except json.JSONDecodeError:
            # Fallback or error handling
            return {"error": "Failed to parse JSON", "raw": llm_result["response_text"]}
