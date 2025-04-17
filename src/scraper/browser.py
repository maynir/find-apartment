import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

from src.utils import random_num


def get_browser():
    options = Options()
    options.add_argument("--disable-infobars")
    options.add_argument("start-maximized")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-blink-features=AutomationControlled")
    return webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()), options=options
    )


def scroll_down(browser):
    browser.execute_script(
        "window.scrollTo({left: 0, top: document.body.scrollHeight, behavior: 'smooth'});"
    )
    time.sleep(random_num(8, 10))
