from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup as bs
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

# other necessary ones
import urllib.request
from bs4 import BeautifulSoup as bs
import pandas as pd
import json
import time
import re
import datetime
import re
import pymongo

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["apartmentsdb"]
mycol = mydb["apartments"]
seen_apartments = {apartment['apartment_id']                   : apartment for apartment in mycol.find()}

words = ["השותף", "השותפה", "שותף", "שותפה", "מתפנה חדר", "מפנה חדר", "מחליפה", "מחליף", "מחליפ/ה", "שותפ/ה", "מחפשת שותפה", "מחפש שותפה", "מחפש שותף",
         "מחפשת שותפה", "מפנה את החדר שלי", "חדר להשכרה", "דירת שותפים", "בדירת שותפים", "מפנה את חדרי", "שותף/ה", "עוזב את החדר שלי", "עוזבת את החדר שלי", "חדר בדירת"]
regex = re.compile('|'.join(re.escape(x) for x in words))

# set options as you wish
option = Options()
option.add_argument("--disable-infobars")
option.add_argument("start-maximized")
option.add_argument("--disable-extensions")
option.add_argument("--disable-notifications")

EMAIL = ""
PASSWORD = ""

browser = webdriver.Chrome(ChromeDriverManager().install(), options=option)
browser.get("http://facebook.com")
browser.maximize_window()
wait = WebDriverWait(browser, 30)
email_field = wait.until(EC.visibility_of_element_located((By.NAME, 'email')))
email_field.send_keys(EMAIL)
pass_field = wait.until(EC.visibility_of_element_located((By.NAME, 'pass')))
pass_field.send_keys(PASSWORD)
pass_field.send_keys(Keys.RETURN)
time.sleep(5)

# once logged in, free to open up any target page
browser.get('https://www.facebook.com/groups/35819517694')
time.sleep(5)

sort_field = wait.until(EC.visibility_of_element_located(
    (By.CSS_SELECTOR, "[title='sort group feed by']")))
sort_field.click()
time.sleep(2)
browser.find_element_by_xpath(
    "//span[contains(text(), 'Recent posts')]").click()
time.sleep(5)

# while True:
browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
time.sleep(1)
browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
time.sleep(1)

see_mores = browser.find_elements_by_xpath(
    "//div[contains(text(), 'See more')]")

for see_more in see_mores:
    try:
        ActionChains(browser).move_to_element(see_more).perform()
        see_more.click()
        print('clicked')
        time.sleep(1)
    except:
        print('not clicked')
        continue

time.sleep(5)

source_data = browser.page_source
bs_data = bs(source_data, 'html.parser')
posts = bs_data.find_all(
    'div', {"class": "du4w35lb k4urcfbm l9j0dhe7 sjgh65i0"})

for post in posts:
    id = post.find("strong").get_text()

    try:
        if id in seen_apartments:
            print("Apartment id: " + id + ", seen already.")
            continue

        text = post.find("div", {
                         "class": "kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x c1et5uql ii04i59q"}).get_text()
        if not regex.search(text):
            continue

        top_links = post.find(
            "div", {"class": "j83agx80 cbu4d94t ew0dbk1b irj2b8pg"}).find_all("a")
        posted_by = post.find("strong").get_text()
        posted_by_url = top_links[0]["href"]
        post_url = top_links[1]["href"]

        mycol.insert_one({"apartment_id": id, "posted_by": posted_by,
                         "posted_by_url": posted_by_url, "post_url": post_url, "text": text})

        print("post text: " + text)
        print("post link: " + post_url)
        print("posted by: " + posted_by)
        print("user url: " + posted_by_url)
        print("__________________________")
    except:
        mycol.insert_one({"apartment_id": id})
        print('couldnt parse')
        print("__________________________")

    browser.quit()
    # time.sleep(60*10) # wait 10 minutes
