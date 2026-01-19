"""
Author: Yoosuf
Email: mayoosuf@gmail.com
Company: Crew Digital
"""

import httpx
import logging
import time
from typing import Dict, Any

from src.config import settings
from src.services.llm_interface import LLMInterface

logger = logging.getLogger(__name__)

class OllamaClient(LLMInterface):
    def __init__(self, base_url: str = settings.OLLAMA_BASE_URL):
        self.base_url = base_url
    
    async def generate(self, prompt: str, model: str, **kwargs) -> Dict[str, Any]:
        """
        Generate response using Ollama API (POST /api/generate)
        """
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,  # Non-streaming for now as per requirements to return simple response
            **kwargs
        }
        
        start_time = time.time()
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                
                # Ollama returns 'response' field
                generated_text = data.get("response", "")
                
                # Calculate latency
                duration_ms = int((time.time() - start_time) * 1000)
                
                return {
                    "response_text": generated_text,
                    "processing_time_ms": duration_ms,
                    "meta_data": {
                        "raw_response": data
                    }
                }
                
        except httpx.HTTPError as e:
            logger.error(f"Ollama API Error: {e}")
            raise Exception(f"Failed to communicate with LLM: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in LLM generation: {e}")
            raise
