import logging
import re
from newspaper import Article
from typing import Optional

class WebScraperService:
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)

    def scrape_content(self, url: str) -> Optional[str]:
        """Scrapes the main content of the web page from the given URL using newspaper3k."""
        try:
            url = str(url)
            article = Article(url)
            article.download()
            article.parse()
            content = article.text
            
            minified_content = self.minify_content(content)
            self.logger.info(f"Minified content length: {len(minified_content)} characters")
            return minified_content

        except Exception as e:
            self.logger.error(f"Error scraping {url}: {e}")
            return None

    def minify_content(self, content: str) -> str:
        content = re.sub(r'<[^>]+>', '', content)
        content = re.sub(r'\s+', ' ', content)
        content = content.strip()
        return content
    
def get_web_scraper_service(logger: Optional[logging.Logger] = None) -> WebScraperService:
    """Factory function to create an instance of WebScraperService with a custom logger."""
    return WebScraperService(logger)
