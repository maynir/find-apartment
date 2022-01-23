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

def random_num(start, end):
  return random.randint(start, end)

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

EMAIL = "maynirrr@gmail.com"
EMAIL_FOR_SEND = "findapartmenttlv@gmail.com"
PASSWORD = ""

group_ids = [35819517694, 101875683484689, 174312609376409, 2092819334342645, 1673941052823845, 599822590152094]
group_id_to_sorting = {35819517694: 'CHRONOLOGICAL', 101875683484689: 'CHRONOLOGICAL', 174312609376409: 'CHRONOLOGICAL', 2092819334342645: 'CHRONOLOGICAL', 1673941052823845: 'CHRONOLOGICAL', 599822590152094: 'RECENT_LISTING_ACTIVITY'}

browser = webdriver.Chrome(ChromeDriverManager().install(), options=option)
browser.get("http://facebook.com")
browser.maximize_window()
wait = WebDriverWait(browser, 30)
email_field = wait.until(EC.visibility_of_element_located((By.NAME, 'email')))
email_field.send_keys(EMAIL)
pass_field = wait.until(EC.visibility_of_element_located((By.NAME, 'pass')))
pass_field.send_keys(PASSWORD)
pass_field.send_keys(Keys.RETURN)
time.sleep(random_num(10,12))

new_apartments_count = 0

while True:
  for group_id in group_ids:
      group_url = f'https://www.facebook.com/groups/{group_id}?sorting_setting={group_id_to_sorting[group_id]}'
      browser.get(group_url)
      time.sleep(random_num(5,7))

      group_name = browser.find_element_by_xpath("//*[@class='oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 nc684nl6 p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl gmql0nx0 gpro0wi8 hnhda86s']").text
      print(f"Looking at group: {group_name}")
      
      browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
      time.sleep(random_num(5,7))
      browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
      time.sleep(random_num(5,7))

      posts = browser.find_elements_by_xpath("//*[@class='du4w35lb k4urcfbm l9j0dhe7 sjgh65i0']")
      print(f"Found {len(posts)} posts in group")
      print("__________________________")

      for post in posts:
        id = post.find_element_by_tag_name("strong").text

        if id in seen_apartments:
            print("Apartment id: " + id + ", seen already.")
            print("__________________________")
            continue  

        see_mores = post.find_elements_by_xpath(".//div[contains(text(), 'See more')]")
        for see_more in see_mores:
          try:
              ActionChains(browser).move_to_element(see_more).perform()
              see_more.click()
              print('Load More clicked')
              time.sleep(random_num(1,2))
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
            post_url = post.find_element_by_xpath(".//a[@class='oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 nc684nl6 p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl gmql0nx0 gpro0wi8 b1v8xokw']").get_attribute('href')
            posted_ago = post.find_element_by_xpath(".//a[@class='oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 nc684nl6 p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl gmql0nx0 gpro0wi8 b1v8xokw']").find_element_by_tag_name("span").text
            
            match = regex.search(text)
            
            mycol.insert_one({"apartment_id": id, "posted_by": posted_by,
                              "posted_by_url": posted_by_url, "post_url": post_url, "text": text, "posted_ago": posted_ago, "group_name": group_name, "group_url": group_url, "match": match })

            if not match:
                print("Apartment not matching words")
                print("post text: " + text)
                print("__________________________")
                continue

            new_apartments_count += 1
            mail_content += f'Apartment number {new_apartments_count}:\nPosted {posted_ago} ago\nPost text: \n{text}\nPost link: \n{post_url}\nPosted by: \n{posted_by}\nPosted by URL: \n{posted_by_url}\nGroup name: \n{group_name}\nGroup URL: \n{group_url}\n\n\n\n'

            print("post text: " + text)
            print(f"post {posted_ago} ago")
            print("post link: " + post_url)
            print("posted by: " + posted_by)
            print("user url: " + posted_by_url)
            print(f"posted at: {group_name}")
            print("__________________________")
        except Exception as err:
            mycol.insert_one({"apartment_id": id})
            print(f'couldnt parse apartment_id: {id}, msg: {err}')
            print("__________________________")

      time.sleep(random_num(13,15))

  if(new_apartments_count > 0):
      # Setup the MIME
      message = MIMEMultipart()
      message['From'] = EMAIL_FOR_SEND
      message['To'] = EMAIL
      message['Subject'] = f'New {new_apartments_count} apartments for you'  # The subject line
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
  else:
      print('No new apartments :(')

  new_apartments_count = 0
  mail_content = ""

  print("Sleeping for 10 minutes now...")
  time.sleep(60*10) # Wait 10 minutes before starting all over
  print("Start searching again!")


browser.quit()
