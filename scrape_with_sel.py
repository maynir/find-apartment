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
import random
import os
from twilio.rest import Client
import telegram_send
import config
import sys

client = Client()
from_whatsapp_number='whatsapp:+14155238886'
to_whatsapp_number= config.my_whatsapp_number

EMAIL = config.my_email
EMAIL_FOR_SEND = config.email_for_send
PASSWORD = config.password

def random_num(start, end):
  return random.randint(start, end)

def send_whatsapp(msg):
  client.messages.create(body=msg,from_=from_whatsapp_number, to=to_whatsapp_number)
  print("Whatsapp sent")

def send_telegram(msg):
  telegram_send.send(messages=[msg])
  print("Telegram sent")

def send_email(posted_by, msg):
    # Setup the MIME
    message = MIMEMultipart()
    message['From'] = EMAIL_FOR_SEND
    message['To'] = EMAIL
    message['Subject'] = f'New apartment by {posted_by}'  # The subject line
    # The body and the attachments for the mail
    message.attach(MIMEText(msg, 'plain'))
    # Create SMTP session for sending the mail
    session = smtplib.SMTP('smtp.gmail.com', 587)  # use gmail with port
    session.starttls()  # enable security
    session.login(EMAIL_FOR_SEND, PASSWORD)  # login with mail_id and password
    text = message.as_string()
    session.sendmail(EMAIL_FOR_SEND, EMAIL, text)
    session.quit()
    print(f'Mail Sent')

def scroll_down():
    browser.execute_script("window.scrollTo({left: 0, top: document.body.scrollHeight, behavior: 'smooth'});")
    time.sleep(random_num(8,10))

def log_in():
    email_field = wait.until(EC.visibility_of_element_located((By.NAME, 'email')))
    email_field.send_keys(EMAIL)
    time.sleep(1)
    pass_field = wait.until(EC.visibility_of_element_located((By.NAME, 'pass')))
    pass_field.send_keys(PASSWORD)
    time.sleep(1)
    pass_field.send_keys(Keys.RETURN)
    time.sleep(random_num(10,12))

def wait_for_next_round():
    wait_min = random_num(10,14)
    print(f"Going to sleep now")
    while(wait_min > 0):
        print(f"{wait_min} min left...")
        time.sleep(60)
        wait_min -= 1

    print("Start searching again!")

mail_content = ""
port = 465

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["apartmentsdb"]
mycol = mydb["apartments"]

words = ["השותף", "השותפה", "שותף", "שותפה", "מתפנה חדר", "מפנה חדר", "מחליפה", "מחליף", "מחליפ/ה", "שותפ/ה", "מחפשת שותפה", "מחפש שותפה", "מחפש שותף",
         "מחפשת שותפה", "מפנה את החדר שלי", "חדר להשכרה", "דירת שותפים", "בדירת שותפים", "מפנה את חדרי", "שותף/ה", "עוזב את החדר שלי", "עוזבת את החדר שלי", "חדר בדירת", "שותפים", "שותפות", "מפנה את החדר", "שלושה חדרים", "3 חדרים"]
good_words_regex = re.compile('|'.join(re.escape(x) for x in words))

bad_words = ["ללא סלון","בלי סלון","סורי בנות","סליחה בנות", "ביפו", "פלורנטין", "אין סלון"]
bad_words_regex = re.compile('|'.join(re.escape(x) for x in bad_words))

# set options as you wish
option = Options()
option.add_argument("--disable-infobars")
option.add_argument("start-maximized")
option.add_argument("--disable-extensions")
option.add_argument("--disable-notifications")

group_ids = [35819517694, 101875683484689, 174312609376409, 2092819334342645, 1673941052823845, 599822590152094, 287564448778602, 'ApartmentsTelAviv', 785935868134249, 423017647874807, 458499457501175, 108784732614979, 'telavivroommates', 109472732403520]
group_id_to_sorting = {35819517694: 'CHRONOLOGICAL', 101875683484689: 'CHRONOLOGICAL', 174312609376409: 'CHRONOLOGICAL', 2092819334342645: 'CHRONOLOGICAL', 1673941052823845: 'CHRONOLOGICAL', 599822590152094: 'RECENT_LISTING_ACTIVITY', 287564448778602: 'RECENT_LISTING_ACTIVITY', 'ApartmentsTelAviv': 'CHRONOLOGICAL', 785935868134249: 'RECENT_LISTING_ACTIVITY', 423017647874807: 'CHRONOLOGICAL', 458499457501175: 'RECENT_LISTING_ACTIVITY', 108784732614979: 'CHRONOLOGICAL', 'telavivroommates': 'RECENT_LISTING_ACTIVITY', 109472732403520: 'CHRONOLOGICAL'}

browser = webdriver.Chrome(ChromeDriverManager().install(), options=option)
browser.get("http://facebook.com")
browser.maximize_window()
wait = WebDriverWait(browser, 30)
log_in()

while True:
  random.shuffle(group_ids)
  blocked_retries = 0
  for group_id in group_ids[0:8]:
      seen_apartments = {apartment['apartment_id']: apartment for apartment in mycol.find()}

      group_url = f'https://www.facebook.com/groups/{group_id}?sorting_setting={group_id_to_sorting[group_id]}'
      browser.get(group_url)
      time.sleep(random_num(5,7))

      group_name = browser.find_element_by_xpath("//*[@class='oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 nc684nl6 p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl gmql0nx0 gpro0wi8 hnhda86s']").text
      print(f"Looking at group: {group_name}")
      
      scroll_down()

      posts = browser.find_elements_by_xpath("//*[@class='du4w35lb k4urcfbm l9j0dhe7 sjgh65i0']")
      if(len(posts) == 0 or len(posts) == 1):
        blocked_retries += 1
        print(f"Found {len(posts)} posts, refreshing page...")
        browser.refresh()
        time.sleep(random_num(5,7))
        scroll_down()
        posts = browser.find_elements_by_xpath("//*[@class='du4w35lb k4urcfbm l9j0dhe7 sjgh65i0']")
      else:
        blocked_retries = 0

      if(blocked_retries >= 3):
        print("You probably got blocked... stoping.")
        send_telegram("You probably got blocked... stoping.")
        browser.quit()
        sys.exit()

      time.sleep(random_num(8,10))
      print(f"Found {len(posts)} posts in group")
      print("__________________________")

      for post in posts:
        id = post.find_element_by_tag_name("strong").text

        if (id == ''):
            print("id is empty, trying again")
            time.sleep(2)
            id = post.find_element_by_xpath(".//a[@class='oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 nc684nl6 p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl gpro0wi8 oo9gr5id lrazzd5p']").text

        if id in seen_apartments:
            print("Apartment id: " + id + ", seen already.")
            print("__________________________")
            continue  

        see_mores = post.find_elements_by_xpath(".//div[contains(text(), 'See more')]")
        for see_more in see_mores:
          try:
              ActionChains(browser).move_to_element(see_more).perform()
              time.sleep(random_num(5,10))
              see_more.click()
              print('Load More clicked')
              time.sleep(random_num(5,10))
          except:
              print('not clicked')
              continue
        
        try:
            try:
                text = post.find_element_by_xpath(".//div[@class='ecm0bbzt hv4rvrfc ihqw7lf3 dati1w0a']").text
            except:
                text = post.find_element_by_xpath(".//div[@class='kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x c1et5uql ii04i59q']").text
            posted_by = id
            posted_by_url = post.find_element_by_xpath(".//a[@class='oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 nc684nl6 p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl gpro0wi8 oo9gr5id lrazzd5p']").get_attribute('href')
            # post_url = post.find_element_by_xpath(".//a[@class='oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 nc684nl6 p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl gmql0nx0 gpro0wi8 b1v8xokw']").get_attribute('href')
            # posted_ago = post.find_element_by_xpath(".//span[@class='tojvnm2t a6sixzi8 abs2jz4q a8s20v7p t1p8iaqh k5wvi7nf q3lfd5jv pk4s997a bipmatt0 cebpdrjk qowsmv63 owwhemhu dp1hu0rb dhp61c6y iyyx5f41']").text
                      
            match = bool(good_words_regex.search(text))
            bad_match = bool(bad_words_regex.search(text))

            mycol.insert_one({"apartment_id": id, "posted_by": posted_by,
                              "posted_by_url": posted_by_url, "text": text, "group_name": group_name, "group_url": group_url, "match": match })

            if (bad_match or not match):
                print(f"Apartment not matching words, bad_match: {bad_match}, match: {match}")
                print(f"post id: {id}")
                print("post text: " + text)
                print("__________________________")
                continue

            print("!!!MATCH!!!")
            mail_content += f'Post text: \n{text}\nPosted by: \n{posted_by}\nPosted by URL: \n{posted_by_url}\nGroup name: \n{group_name}\nGroup URL: \n{group_url}\n\n\n\n'

            try:
                send_telegram(mail_content)
                send_email(posted_by, mail_content)
                # send_whatsapp(mail_content)
            except Exception as err:
                print(f"Culdnt send whatsapp/telegram, err: {err}")

            print("post text: " + text)
            print("posted by: " + posted_by)
            print("user url: " + posted_by_url)
            print(f"posted at: {group_name}")
            print("__________________________")
        except Exception as err:
            mycol.insert_one({"apartment_id": id})
            print(f'couldnt parse apartment_id: {id}, msg: {err}')
            print("__________________________")
        finally:
            mail_content = ""

      print("Done with group")
      print("__________________________\n")
      time.sleep(random_num(15,20))

  wait_for_next_round()

browser.quit()
