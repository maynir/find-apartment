# scraper/__init__.py
from .browser import get_browser, scroll_down
from .fb_scraper import FacebookScraper

__all__ = ["FacebookScraper", "get_browser", "scroll_down"]
