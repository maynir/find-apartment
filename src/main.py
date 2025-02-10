import random
import sys
import time


import pymongo
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from twilio.rest import Client
from webdriver_manager.chrome import ChromeDriverManager

from etc import config
from utils import random_num, human_delay
from utils.notifier import Notifier
from utils.text_processing import good_words_regex, bad_words_regex
from utils.delays import wait_with_countdown

client = Client()

from selenium.webdriver.common.action_chains import ActionChains


def move_mouse_randomly():
    """Simulates mouse movement by moving to random coordinates on the page"""
    try:
        for _ in range(random.randint(5, 10)):
            # browser.execute_script(script)
            time.sleep(random.uniform(0.5, 1.5))  # Pause briefly
    except Exception as e:
        print(f"⚠ Mouse movement failed: {e}")


def scroll_down(browser):
    browser.execute_script(
        "window.scrollTo({left: 0, top: document.body.scrollHeight, behavior: 'smooth'});"
    )
    time.sleep(random_num(8, 10))


def log_in(browser, email, password):
    """Logs into Facebook while avoiding detection"""
    try:
        wait = WebDriverWait(browser, 15)

        # Find email field and enter email
        email_field = wait.until(EC.presence_of_element_located((By.NAME, "email")))
        move_mouse_randomly()
        email_field.click()
        human_delay(1, 3)
        email_field.send_keys(email)
        move_mouse_randomly()

        # Find password field and enter password
        pass_field = wait.until(EC.presence_of_element_located((By.NAME, "pass")))
        move_mouse_randomly()
        pass_field.click()
        human_delay(1, 3)
        pass_field.send_keys(password)
        move_mouse_randomly()
        human_delay(2, 4)

        # Submit login form
        pass_field.send_keys(Keys.RETURN)
        move_mouse_randomly()

        # Wait for home button (to confirm successful login)
        wait.until(
            EC.presence_of_element_located((By.XPATH, "//*[@aria-label='Home']"))
        )
        print("✅ Login successful!")

        # Save session cookies

    except Exception as e:
        print(f"❌ Login failed: {e}")
        browser.quit()
        exit(1)


class GettingBlockedError(Exception):
    """You are probably getting blocked now, need to cool down"""

    pass


cool_down_minutes = 30

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["apartmentsdb"]
mycol = mydb["apartments"]


# set options as you wish
option = Options()
option.add_argument("--disable-infobars")
option.add_argument("start-maximized")
option.add_argument("--disable-extensions")
option.add_argument("--disable-notifications")
option.add_argument(
    "--disable-blink-features=AutomationControlled"
)  # Prevent detection
option.add_argument(
    f"user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.0.0 Safari/537.36"
)


def main():
    notifier = Notifier()
    notifier.notify("🚀 Starting Facebook bot")

    while True:
        try:
            browser = webdriver.Chrome(
                service=webdriver.ChromeService(ChromeDriverManager().install()),
                options=option,
            )
            browser.get("http://facebook.com")
            browser.maximize_window()

            log_in(browser, config.my_email, config.password)

            while True:
                random.shuffle(config.group_ids)
                blocked_retries = 0

                for group_id in config.group_ids[:7]:
                    seen_apartments = {
                        apartment["text"]: apartment
                        for apartment in mycol.find()
                    }
                    group_url = f"https://www.facebook.com/groups/{group_id}?sorting_setting={config.group_id_to_sorting[group_id]}"

                    browser.get(group_url)
                    time.sleep(random.randint(5, 7))

                    group_name = (
                        WebDriverWait(browser, 10)
                        .until(
                            EC.presence_of_element_located(
                                (
                                    By.XPATH,
                                    "//*[@class='x1i10hfl xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz x1heor9g x1sur9pj xkrqix3 x1pd3egz']",
                                )
                            )
                        )
                        .text
                    )
                    print(f"🔍Looking at group: {group_name}")

                    scroll_down(browser)

                    posts_class = "x1yztbdb x1n2onr6 xh8yej3 x1ja2u2z"
                    posts = browser.find_elements(
                        By.XPATH, f"//*[@class='{posts_class}']"
                    )
                    if len(posts) in (0, 1):
                        blocked_retries += 1
                        print(f"🔄 Found {len(posts)} posts, refreshing page...")
                        browser.refresh()
                        time.sleep(random.randint(5, 7))
                        scroll_down(browser)
                        posts = browser.find_elements(
                            By.XPATH, f"//*[@class='{posts_class}']"
                        )
                    else:
                        blocked_retries = 0
                        cool_down_minutes = 30

                    if blocked_retries >= 3:
                        raise GettingBlockedError

                    time.sleep(random.randint(8, 10))
                    print(f"🖼️ Found {len(posts)} posts in group")
                    print("__________________________")

                    for index, post in enumerate(posts):
                        post = posts = browser.find_elements(
                            By.XPATH, f"//*[@class='{posts_class}']"
                        )[index]
                        post_id = None
                        posted_by_url = None
                        text = None

                        try:
                            try:
                                time.sleep(random.randint(2, 5))
                                post_id = post.find_element(By.TAG_NAME, "strong").text
                                if not post_id:
                                    print("id is empty, trying again")
                                    time.sleep(2)
                                    post_id = post.find_element(
                                        By.TAG_NAME, "strong"
                                    ).text
                                print(f"🔍 Processing post By '{post_id}'")
                            except Exception as err:
                                print(f"⚠️Could not find post author")


                            see_mores = post.find_elements(
                                By.XPATH, ".//div[contains(text(), 'See more')]"
                            )
                            for see_more in see_mores:
                                try:
                                    ActionChains(browser).move_to_element(
                                        see_more
                                    ).perform()
                                    time.sleep(random.randint(5, 10))
                                    see_more.click()
                                    print("🔋 Load More clicked")
                                    time.sleep(random.randint(5, 10))
                                except Exception as err:
                                    print(f"⚠️ Failed to click 'See More' button: {err}")
                                    continue

                            try:
                                posted_by_url = post.find_element(
                                    By.XPATH,
                                    ".//*[@data-ad-rendering-role='profile_name']//a",
                                ).get_attribute("href")
                                print(f"🔗 Found post author URL")
                            except Exception as err:
                                print(
                                    f"⚠️Could not find post author URL: {posted_by_url}"
                                )

                            try:
                                text = post.find_element(
                                    By.XPATH, f".//*[@data-ad-preview='message']"
                                ).text
                                print(f"📝 Found post text: {text}")
                            except Exception as err:
                                print(f"⚠️Could not find post text, to the next one")
                                print("__________________________")
                                continue

                            try:
                                imgs = post.find_elements(By.XPATH, ".//*[@class='x6ikm8r x10wlt62 x10l6tqk']//img")
                                imgs_src = [img.get_attribute("src") for img in imgs]
                                print(f"📷 Found {len(imgs_src)} post images ")
                            except Exception as err:
                                print(f"⚠️Could not find post images")
                                imgs_src = []

                            if text in seen_apartments:
                                print(
                                    f"🥱Apartment posted by '{post_id}' already seen."
                                )
                                print("__________________________")
                                continue

                            match_word = good_words_regex.search(text)
                            bad_match_word = bad_words_regex.search(text)
                            match = bool(match_word)
                            bad_match = bool(bad_match_word)

                            mycol.insert_one(
                                {
                                    "apartment_id": post_id,
                                    "posted_by": post_id,
                                    "posted_by_url": posted_by_url,
                                    "text": text,
                                    "group_name": group_name,
                                    "group_url": group_url,
                                    "match": match,
                                }
                            )

                            if bad_match or not match:
                                print(
                                    f"👎🏼Apartment does not match criteria - bad_match_word:{bad_match_word}, match_word:{match_word}"
                                )
                                print("__________________________")
                                continue

                            print(f"✅ MATCH FOUND: {match_word}")
                            message = f"Post text:\n{text}\nPosted by:\n{post_id}\nPosted by URL:\n{posted_by_url}\nGroup name:\n{group_name}\nGroup URL:\n{group_url}\n\n"

                            try:
                                notifier.notify(message, imgs_src)
                            except Exception as err:
                                print(
                                    f"⚠️ Could not send Telegram message: {err}, {message}"
                                )

                            print("__________________________")

                        except Exception as err:
                            print(f"⚠️ Error processing post: {err}")
                            continue

                    print("☑️ Finished processing group")
                    wait_with_countdown(random.randint(1, 2))

                wait_with_countdown(random.randint(18, 22))
                print("🔄 Restarting group search...")
        except GettingBlockedError as err:
            msg = f"👮‍♂️You probably got blocked... cooling down for {cool_down_minutes} minutes."
            print(msg)
            send_telegram_message(msg)
            browser.quit()
            sys.exit()
            wait_with_countdown(cool_down_minutes)
            cool_down_minutes += 20
            blocked_retries = 0
        except Exception as err:
            print(f"{err=}")
            browser.quit()
            time.sleep(10)

    browser.quit()


if __name__ == "__main__":
    main()
