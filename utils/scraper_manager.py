from urllib.parse import urlparse
from utils.scrapers.freewebnovel import (
    scrape_chapter as freewebnovel_scraper,
    scrape_series_info as freewebnovel_series_info
)

# Dictionary mapping domain patterns to their scraper functions
SCRAPERS = {
    'freewebnovel.com': freewebnovel_scraper,
}

def get_domain(url):
    """Extract domain from URL, handling various URL formats."""
    # Add https if not present
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    return urlparse(url).netloc

def scrape_chapter(url, chapter_number):
    """Main scraper function that routes to the appropriate scraper based on domain."""
    domain = get_domain(url)
    
    if 'freewebnovel.com' in domain:
        return freewebnovel_scraper(url, chapter_number)
    
    raise ValueError(f"No scraper found for domain: {domain}")

def scrape_series_info(url):
    """Main series info scraper that routes to the appropriate scraper based on domain."""
    domain = get_domain(url)
    
    if 'freewebnovel.com' in domain:
        return freewebnovel_series_info(url)
    
    raise ValueError(f"No scraper found for domain: {domain}")
