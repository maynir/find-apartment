# scraper/__init__.py
from .fb_scraper import FacebookScraper
from .browser import get_browser, scroll_down

__all__ = ["FacebookScraper", "get_browser", "scroll_down"]
