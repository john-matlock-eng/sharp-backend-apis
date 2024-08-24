import openai
import os
import logging
from typing import Dict, List, Optional
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

class OpenAIController:
    def __init__(self, api_key: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        openai.api_key = self.api_key
        self.client = openai.Client(api_key=self.api_key)
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "4000"))
        self.temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.9"))
        self.retry_limit = int(os.getenv("OPENAI_RETRY_LIMIT", "3"))
        self.logger.info("OpenAIController initialized.")

    @retry(
        stop=stop_after_attempt(3),  # Retry up to 3 times
        wait=wait_exponential(multiplier=1, min=4, max=10),  # Exponential backoff
        retry=retry_if_exception_type((openai.APIConnectionError, openai.RateLimitError, openai.APIError))
    )
    def _send_request(self, messages: List[Dict[str, str]]) -> str:
        """Handles the actual API request with retry logic."""
        print("requesting")
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )
        output = response.choices[0].message.content
        return output

    def generate_prompt(self, system_message: str, user_message: str) -> List[Dict[str, str]]:
        """Constructs the prompt with system and user roles."""
        return [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]

    def get_response(self, prompt: List[Dict[str, str]]) -> Dict[str, str]:
        """Handles API interaction and returns parsed response."""
        response_text = self._send_request(prompt)
        self.logger.info(f"Received response: {response_text}")
        
        # Placeholder parsing logic - to be replaced with actual parsing according to the response structure
        parsed_response = {
            "response": response_text,  # This assumes the full response is the question text; parsing may be needed
        }
        return parsed_response

    def fetch_background_data(self, context_id: str) -> str:
        """Fetches and returns background information relevant to the request."""
        background_data = f"Background information for context ID: {context_id}"
        self.logger.info(f"Fetched background data: {background_data}")
        return background_data

def get_openai_controller() -> OpenAIController:
    """Factory function for creating OpenAIController instances."""
    return OpenAIController()