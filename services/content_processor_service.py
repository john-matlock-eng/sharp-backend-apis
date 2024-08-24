import logging
import json
from typing import Optional, Dict, Any, List
from app.lib.openai_controller import OpenAIController, get_openai_controller
from concurrent.futures import ThreadPoolExecutor, as_completed
import tenacity
import re

class ContentProcessorService:
    def __init__(self, openai_controller: OpenAIController = None):
        self.logger = logging.getLogger(__name__)
        self.openai_controller = openai_controller or get_openai_controller()
        
    @staticmethod
    def validate_and_correct_json(response_text: str) -> Optional[Dict[str, Any]]:
        try:
            # Replace unescaped control characters that may cause issues
            response_text = re.sub(r'[\x00-\x1f\x7f]', lambda match: f'\\u{ord(match.group(0)):04x}', response_text)

            # Attempt to load the JSON directly
            return json.loads(response_text)
        except json.JSONDecodeError as first_error:
            logging.error(f"Initial JSON parsing error: {first_error}")
            logging.error(f"Attempting to correct problematic content: {response_text[:200]}...")  # Log a snippet

            # Replace single quotes with double quotes and remove problematic characters
            corrected_text = response_text.replace("'", '"').strip()
            corrected_text = re.sub(r'\\u000a', ' ', corrected_text)  # Replace newline escape with space

            try:
                return json.loads(corrected_text)
            except json.JSONDecodeError as second_error:
                # Log the error and return None if it still fails
                logging.error(f"Failed to correct and parse JSON: {second_error}")
                logging.error(f"Problematic content after correction: {corrected_text[:200]}...")
                return None
            
    def process_chunk(self, chunk: str, system_message: str) -> Dict[str, Any]:
        """Processes a single chunk of content using OpenAI GPT-4 with retries."""
        user_message = f"Extract the following information from the content: {chunk}"
        prompt = self.openai_controller.generate_prompt(system_message, user_message)
        response = self.openai_controller.get_response(prompt)
        
        response_text = response.get('response', '').strip()
        if response_text.startswith('```json'):
            response_text = response_text[7:-3]  # Strip off ```json ... ```

        # Validate and correct the JSON format using the updated method
        processed_data = self.validate_and_correct_json(response_text)
        if not processed_data:
            logging.error(f"Skipping chunk due to invalid JSON format: {chunk[:200]}...")
            raise ValueError("Failed to process chunk: invalid JSON format")

        return processed_data
            
    def split_content(self, content: str, max_length: int = 2000) -> List[str]:
        """Splits the content into manageable chunks for processing."""
        chunks = []
        while len(content) > max_length:
            split_index = content.rfind('.', 0, max_length) + 1
            if split_index <= 0:  # If no period is found
                split_index = max_length  # Force split at max length
            chunks.append(content[:split_index].strip())
            content = content[split_index:].strip()
        if content:
            chunks.append(content)
        self.logger.info(f"Split content into {len(chunks)} chunks.")
        return chunks
    
    def process_content(self, content: str, system_message: str) -> Optional[List[Dict[str, Any]]]:
        """Uses OpenAI GPT-4 to extract and summarize information in a structured JSON format."""
        try:
            content_chunks = self.split_content(content)
            processed_chunks = []

            with ThreadPoolExecutor(max_workers=5) as executor:
                future_to_chunk = {executor.submit(self.process_chunk, chunk, system_message): chunk for chunk in content_chunks}
                for future in as_completed(future_to_chunk):
                    try:
                        processed_chunks.append(future.result())
                    except Exception as e:
                        self.logger.error(f"Error processing chunk: {e}")

            if not processed_chunks:
                self.logger.error("No valid chunks were processed.")
                return None

            return processed_chunks

        except Exception as e:
            self.logger.error(f"Error processing content: {e}")
            return None

def get_content_processor_service() -> ContentProcessorService:
    """Factory function to create an instance of ContentProcessorService."""
    return ContentProcessorService()
