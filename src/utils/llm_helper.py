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
    
    async def generate_content(self, prompt: str, system_message: str = "You are a helpful assistant.", temperature: float = 0.7, timeout: int = 30) -> str:
        """Generate content using LLM with timeout."""
        try:
            # Add timeout to prevent hanging
            chat = LlmChat(
                api_key=self.api_key,
                session_id=self._get_session_id(),
                system_message=system_message
            ).with_model(self.provider, self.model)
            
            user_message = UserMessage(text=prompt)
            response = await asyncio.wait_for(chat.send_message(user_message), timeout=timeout)
            
            return response.strip()
        except asyncio.TimeoutError:
            print(f"LLM generation timeout after {timeout}s")
            return ""
        except Exception as e:
            print(f"LLM generation error: {e}")
            return ""
    
    async def generate_batch(self, prompts: List[str], system_message: str = "You are a helpful assistant.", batch_size: int = 10, delay: float = 1.0) -> List[str]:
        """Generate multiple content pieces in smaller batches with delays.
        
        Args:
            prompts: List of prompts to process
            system_message: System message for the LLM
            batch_size: Number of prompts to process concurrently (default: 10)
            delay: Delay in seconds between batches (default: 1.0)
        
        Returns:
            List of generated content strings
        """
        results = []
        total_batches = (len(prompts) + batch_size - 1) // batch_size
        
        for i in range(0, len(prompts), batch_size):
            batch = prompts[i:i + batch_size]
            batch_num = i // batch_size + 1
            
            print(f"  Processing batch {batch_num}/{total_batches} ({len(batch)} items)...")
            
            tasks = [self.generate_content(prompt, system_message) for prompt in batch]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle exceptions in batch results
            for j, result in enumerate(batch_results):
                if isinstance(result, Exception):
                    print(f"  Error in batch item {j}: {result}")
                    results.append("")
                else:
                    results.append(result)
            
            # Add delay between batches to avoid rate limiting
            if i + batch_size < len(prompts):
                await asyncio.sleep(delay)
        
        return results
