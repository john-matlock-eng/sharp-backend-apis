import re
from newspaper import Article
from typing import Optional
import logging

class WebScraperService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def scrape_content(self, url: str) -> Optional[str]:
        """Scrapes the main content of the web page from the given URL using newspaper3k."""
        try:
            article = Article(url)
            article.download()
            article.parse()
            content = article.text
            
            # Minify the content
            minified_content = self.minify_content(content)
            
            self.logger.info(f"Minified content length: {len(minified_content)} characters")
            return minified_content

        except Exception as e:
            self.logger.error(f"Error scraping {url}: {e}")
            return None

    def minify_content(self, content: str) -> str:
        """Minifies the scraped content by removing unnecessary whitespace, line breaks, and non-essential characters."""
        content = re.sub(r'<[^>]+>', '', content)  # Remove HTML tags
        content = re.sub(r'\s+', ' ', content)  # Replace multiple spaces with a single space
        content = content.strip()  # Strip leading and trailing whitespace
        return content
    
def get_web_scraper_service() -> WebScraperService:
    """Factory function to create an instance of WebScraperService."""
    return WebScraperService()