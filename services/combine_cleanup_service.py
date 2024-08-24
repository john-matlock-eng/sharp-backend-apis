import logging
from typing import Dict, List, Any, Optional
from app.lib.openai_controller import OpenAIController, get_openai_controller

class CombinationCleanupService:
    def __init__(self, openai_controller: Optional[OpenAIController] = None):
        self.logger = logging.getLogger(__name__)
        self.openai_controller = openai_controller or get_openai_controller()

    def combine_responses(self, responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Combines multiple JSON responses into one comprehensive response."""
        combined = {
            "author": None,
            "site": None,
            "publish_date": None,
            "main_topic": None,
            "parent_topic": None,
            "field": None,
            "keywords": [],
            "major_insights_or_novel_concepts": [],
            "supporting_details": [],
            "relevant_quotations": [],
            "external_links": []
        }

        for response in responses:
            if response.get('author') and not combined['author']:
                combined['author'] = response['author']
            if response.get('site') and not combined['site']:
                combined['site'] = response['site']
            if response.get('publish_date') and not combined['publish_date']:
                combined['publish_date'] = response['publish_date']
            if response.get('main_topic') and not combined['main_topic']:
                combined['main_topic'] = response['main_topic']
            if response.get('parent_topic') and not combined['parent_topic']:
                combined['parent_topic'] = response['parent_topic']
            if response.get('field') and not combined['field']:
                combined['field'] = response['field']

            combined['keywords'].extend(response.get('keywords', []))
            combined['major_insights_or_novel_concepts'].extend(response.get('major_insights_or_novel_concepts', []))
            combined['supporting_details'].extend(response.get('supporting_details', []))
            combined['relevant_quotations'].extend(response.get('relevant_quotations', []))
            combined['external_links'].extend(response.get('external_links', []))

        # Remove duplicates in lists
        combined['keywords'] = self.remove_duplicates(combined['keywords'])
        combined['major_insights_or_novel_concepts'] = self.remove_duplicates(combined['major_insights_or_novel_concepts'])
        combined['supporting_details'] = self.remove_duplicates(combined['supporting_details'])
        combined['relevant_quotations'] = self.remove_duplicates(combined['relevant_quotations'])
        combined['external_links'] = self.remove_duplicates(combined['external_links'])

        return combined

    @staticmethod
    def remove_duplicates(items: List[Any]) -> List[Any]:
        """Removes duplicate items from a list."""
        seen = set()
        unique_items = []
        for item in items:
            str_item = str(item)  # Convert item to string to ensure hashability
            if str_item not in seen:
                unique_items.append(item)
                seen.add(str_item)
        return unique_items

    def clean_up_response(self, combined_response: Dict[str, Any]) -> Dict[str, Any]:
        """Sends the combined response back to OpenAI GPT-4 for final cleanup and uniqueness."""
        try:
            system_message = (
                "You are an expert content editor specializing in educational materials. Your task is to refine, merge, and enhance the clarity and uniqueness of the following information. "
                "Focus on reducing redundancy by merging similar keywords, insights, and supporting details. "
                "Prioritize clarity and educational value, making sure each element is unique and informative. "
                "If one chunk has missing information that another chunk provides (e.g., author or publish date), combine them accordingly. "
                "Ensure the final content is concise but thorough, and prioritize definitions and explanations that add value for learners."
                "Each key word should be a distinct concept or term, and the definitions should be clear and informative. Key words should not be grouped together or listed in bulk. Each is its own entity."
                "\n\n### Example Input:\n"
                "Chunk 1:\n"
                "{"
                " 'author': 'unknown', 'site': 'Example.com', 'publish_date': '2024-08-19', "
                " 'main_topic': 'The Impact of AI on Healthcare', "
                " 'parent_topic': 'Technology', 'field': 'Health Technology', "
                " 'keywords': [{'keyword': 'AI', 'definition': 'Simulation of human intelligence by machines.', 'relation_to_topic': 'Discussed as a transformative force in healthcare.'}], "
                " 'major_insights_or_novel_concepts': [{'insight': 'AI reduces diagnostic errors.', 'concept': 'AI in Diagnostics'}], "
                " 'supporting_details': ['Examples of hospitals using AI.', 'Statistics on error reduction.'], "
                " 'relevant_quotations': ['AI improves diagnosis accuracy.'], "
                " 'external_links': ['https://example.com/ai-healthcare'] "
                "}\n"
                "Chunk 2:\n"
                "{"
                " 'author': 'John Doe', 'site': 'Example.com', 'publish_date': 'unknown', "
                " 'main_topic': 'AI Tools in Modern Medicine', "
                " 'parent_topic': 'Healthcare Technology', 'field': 'Medicine', "
                " 'keywords': [{'keyword': 'Machine Learning', 'definition': 'A subset of AI focusing on data-based learning.', 'relation_to_topic': 'ML supports diagnosis by analyzing large datasets.'}], "
                " 'major_insights_or_novel_concepts': [{'insight': 'ML aids in early detection of diseases.', 'concept': 'Machine Learning in Medicine'}], "
                " 'supporting_details': ['Case studies showing ML applications.', 'ML-driven tools in hospitals.'], "
                " 'relevant_quotations': ['ML is essential for early detection.'], "
                " 'external_links': ['https://example.com/ml-healthcare'] "
                "}\n\n"
                "### Expected Output:\n"
                "{"
                " 'author': 'John Doe', 'site': 'Example.com', 'publish_date': '2024-08-19', "
                " 'main_topic': 'AI and Machine Learning in Healthcare', "
                " 'parent_topic': 'Healthcare Technology', 'field': 'Health Technology', "
                " 'keywords': ["
                "   {'keyword': 'Artificial Intelligence', 'definition': 'Simulation of human cognitive functions by machines.', 'relation_to_topic': 'Revolutionizing diagnostics and patient care.'}, "
                "   {'keyword': 'Machine Learning', 'definition': 'AI subset focused on learning from data.', 'relation_to_topic': 'Key in analyzing medical data and improving diagnostics.'}"
                " ], "
                " 'major_insights_or_novel_concepts': [{'insight': 'AI and ML reduce diagnostic errors and aid early disease detection.', 'concept': 'AI and ML in Diagnostics'}], "
                " 'supporting_details': ['Examples and case studies of AI and ML in hospitals.', 'Data on diagnostic error reduction.'], "
                " 'relevant_quotations': ['AI and ML are transforming healthcare by improving diagnostic precision.'], "
                " 'external_links': ['https://example.com/ai-healthcare', 'https://example.com/ml-healthcare'] "
                "}"
                "Finally, minify your response, use double quotes for property names, and do not include any line breaks or newline characters in the JSON."
)

            user_message = f"Please clean up and uniqueify the following content: {combined_response}"

            prompt = self.openai_controller.generate_prompt(system_message, user_message)
            cleaned_response = self.openai_controller.get_response(prompt)
            response_text = cleaned_response.get('response', '').strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:-3] 
            return response_text

        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
            return combined_response

def get_combination_cleanup_service() -> CombinationCleanupService:
    """Factory function to create an instance of CombinationCleanupService."""
    return CombinationCleanupService()
