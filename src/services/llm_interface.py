"""
Author: Yoosuf
Email: mayoosuf@gmail.com
Company: Crew Digital
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

class LLMInterface(ABC):
    @abstractmethod
    async def generate(self, prompt: str, model: str, **kwargs) -> Dict[str, Any]:
        """
        Generate text from valid prompt.
        
        Args:
            prompt: User input string
            model: Model name to use
            **kwargs: Additional generation parameters (temp, max_tokens, etc)
            
        Returns:
            Dict containing:
            - response_text: str
            - meta_data: dict (optional)
        """
        pass
