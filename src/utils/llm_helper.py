import os
import asyncio
from typing import List, Optional
from emergentintegrations.llm.chat import LlmChat, UserMessage
from dotenv import load_dotenv
import random

load_dotenv()

class LLMHelper:
    """Helper class for LLM-based content generation."""
    
    def __init__(self, provider: str = "gemini", model: str = "gemini-3-flash-preview"):
        self.api_key = os.getenv('EMERGENT_LLM_KEY')
        self.provider = provider
        self.model = model
        self.session_counter = 0
        
    def _get_session_id(self) -> str:
        """Generate unique session ID for each request."""
        self.session_counter += 1
        return f"asana-gen-{self.session_counter}-{random.randint(1000, 9999)}"
    
    async def generate_content(self, prompt: str, system_message: str = "You are a helpful assistant.", temperature: float = 0.7) -> str:
        """Generate content using LLM."""
        try:
            chat = LlmChat(
                api_key=self.api_key,
                session_id=self._get_session_id(),
                system_message=system_message
            ).with_model(self.provider, self.model)
            
            user_message = UserMessage(text=prompt)
            response = await chat.send_message(user_message)
            
            return response.strip()
        except Exception as e:
            print(f"LLM generation error: {e}")
            return ""
    
    async def generate_batch(self, prompts: List[str], system_message: str = "You are a helpful assistant.") -> List[str]:
        """Generate multiple content pieces concurrently."""
        tasks = [self.generate_content(prompt, system_message) for prompt in prompts]
        return await asyncio.gather(*tasks)
