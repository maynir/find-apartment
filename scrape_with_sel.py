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
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.message import EmailMessage

mail_content = ""
port = 465

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
EMAIL_FOR_SEND = ""
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
time.sleep(5)
browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
time.sleep(5)

new_apartments_count = 0

posts = browser.find_elements_by_xpath("//*[@class='du4w35lb k4urcfbm l9j0dhe7 sjgh65i0']")
for post in posts:
  see_mores = post.find_elements_by_xpath(".//div[contains(text(), 'See more')]")
  for see_more in see_mores:
    try:
        ActionChains(browser).move_to_element(see_more).perform()
        see_more.click()
        print('Load More clicked')
        time.sleep(1)
    except:
        print('not clicked')
        continue
  id = post.find_element_by_tag_name("strong").text
  
  try:
      if id in seen_apartments:
          print("Apartment id: " + id + ", seen already.")
          print("__________________________")
          continue

      try:
          text = post.find_element_by_xpath(".//div[@class='ecm0bbzt hv4rvrfc ihqw7lf3 dati1w0a']").text
      except:
          text = post.find_element_by_xpath(".//div[@class='kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x c1et5uql ii04i59q']").text
      posted_by = id
      posted_by_url = post.find_elements_by_xpath(".//a")[0].get_attribute('href')
      post_url = post.find_elements_by_xpath(".//a")[1].get_attribute('href')

      mycol.insert_one({"apartment_id": id, "posted_by": posted_by,
                        "posted_by_url": posted_by_url, "post_url": post_url, "text": text})

      if not regex.search(text):
          print("Apartment not matching words")
          print("post text: " + text)
          print("__________________________")
          continue

      new_apartments_count += 1
      mail_content += f'Apartment number {new_apartments_count}:\nPost text: \n{text}\nPost link: \n{post_url}\nPosted by: \n{posted_by}\nPosted by URL: \n{posted_by_url}\n\n\n'

      print("post text: " + text)
      print("post link: " + post_url)
      print("posted by: " + posted_by)
      print("user url: " + posted_by_url)
      print("__________________________")
  except Exception as err:
      mycol.insert_one({"apartment_id": id})
      print(f'couldnt parse apartment_id: {id}, msg: {err}')
      print("__________________________")

if(new_apartments_count > 0):
    # Setup the MIME
    message = MIMEMultipart()
    message['From'] = EMAIL_FOR_SEND
    message['To'] = EMAIL
    message['Subject'] = 'New apartment alert'  # The subject line
    # The body and the attachments for the mail
    message.attach(MIMEText(mail_content, 'plain'))
    # Create SMTP session for sending the mail
    session = smtplib.SMTP('smtp.gmail.com', 587)  # use gmail with port
    session.starttls()  # enable security
    session.login(EMAIL_FOR_SEND, PASSWORD)  # login with mail_id and password
    text = message.as_string()
    session.sendmail(EMAIL_FOR_SEND, EMAIL, text)
    session.quit()
    print(f'Mail Sent with {new_apartments_count} new apartments')

new_apartments_count = 0
mail_content = ""

# time.sleep(60*10)
browser.quit()
