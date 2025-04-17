import asyncio
import random
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

from . import scroll_down
from ..utils.delays import human_delay, random_num
from ..utils.text_processing import good_words_regex, bad_words_regex
from ..utils.notifier import send_telegram_message
from ..database.mongo_client import save_apartment, get_seen_apartments
from ..etc import config


class GettingBlockedError(Exception):
    """You are probably getting blocked now, need to cool down"""

    pass


class FacebookScraper:
    def __init__(self, browser):
        self.browser = browser
        self.cool_down_minutes = 30

    def log_in(self, email, password):
        try:
            wait = WebDriverWait(self.browser, 15)
            email_field = wait.until(EC.presence_of_element_located((By.NAME, "email")))
            email_field.click()
            human_delay()
            email_field.send_keys(email)
            pass_field = wait.until(EC.presence_of_element_located((By.NAME, "pass")))
            pass_field.click()
            human_delay()
            pass_field.send_keys(password)
            pass_field.send_keys(Keys.RETURN)
            wait.until(
                EC.presence_of_element_located((By.XPATH, "//*[@aria-label='Home']"))
            )
            print("Login successful!")
        except Exception as e:
            print(f"Login failed: {e}")
            self.browser.quit()
            exit(1)

    def scrape_groups(self):
        group_ids = config.GROUP_IDS
        random.shuffle(group_ids)

        blocked_retries = 0

        for group_id in group_ids[:7]:
            seen_apartments = get_seen_apartments()
            group_url = f"https://www.facebook.com/groups/{group_id}?sorting_setting={config.group_id_to_sorting[group_id]}"
            self.browser.get(group_url)
            time.sleep(random.randint(5, 7))

            group_name = (
                WebDriverWait(self.browser, 10)
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

            scroll_down(self.browser)

            posts_class = "x1yztbdb x1n2onr6 xh8yej3 x1ja2u2z"
            posts = self.browser.find_elements(By.XPATH, f"//*[@class='{posts_class}']")
            if len(posts) in (0, 1):
                blocked_retries += 1
                print(f"🔄 Found {len(posts)} posts, refreshing page...")
                self.browser.refresh()
                time.sleep(random.randint(5, 7))
                scroll_down()
                posts = self.browser.find_elements(
                    By.XPATH, f"//*[@class='{posts_class}']"
                )
            else:
                blocked_retries = 0
                cool_down_minutes = 30

            if blocked_retries >= 3:
                raise GettingBlockedError

            time.sleep(random.randint(8, 10))
            print(f"✅ Found {len(posts)} posts in group")
            print("__________________________")

            for post in posts:
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
                            post_id = post.find_element(By.TAG_NAME, "strong").text
                        print(f"🔍 Processing post By '{post_id}'")
                    except Exception as err:
                        print(f"⚠️Could not find post author")

                    if post_id in seen_apartments:
                        print(f"🥱Apartment posted by '{post_id}' already seen.")
                        print("__________________________")
                        continue

                    see_mores = post.find_elements(
                        By.XPATH, ".//div[contains(text(), 'See more')]"
                    )
                    for see_more in see_mores:
                        try:
                            ActionChains(browser).move_to_element(see_more).perform()
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
                        print(f"⚠️Could not find post author URL: {posted_by_url}")

                    try:
                        text = post.find_element(
                            By.XPATH, f".//*[@data-ad-preview='message']"
                        ).text
                        print(f"📝 Found post text: {text}")
                    except Exception as err:
                        print(f"⚠️Could not find post text, to the next one")
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
                        asyncio.run(send_telegram_message(message))
                    except Exception as err:
                        print(f"⚠️ Could not send Telegram message: {err}, {message}")

                    print("__________________________")

                except Exception as err:
                    print(f"⚠️ Error processing post: {err}")
                    continue

            print("✅ Finished processing group")
            wait_with_countdown(random.randint(1, 2))

        wait_with_countdown(random.randint(18, 22))
        print("🔄 Restarting group search...")

        group_ids = config.GROUP_IDS
        for group_id in group_ids:
            seen_apartments = get_seen_apartments()
            group_url = f"https://www.facebook.com/groups/{group_id}"
            self.browser.get(group_url)
            time.sleep(random_num(5, 7))

            print(f"🔍 Looking at group: {group_id}")
            self.browser.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )
            time.sleep(random_num(8, 10))

            posts = self.browser.find_elements(By.XPATH, "//div[@role='article']")
            for post in posts:
                try:
                    post_id = post.get_attribute("id")
                    if post_id in seen_apartments:
                        continue
                    text = post.text
                    match_word = good_words_regex.search(text)
                    bad_match_word = bad_words_regex.search(text)

                    save_apartment(
                        {
                            "apartment_id": post_id,
                            "text": text,
                            "match": bool(match_word),
                        }
                    )

                    if not match_word or bad_match_word:
                        continue

                    message = f"New Apartment Found!\n{text}"
                    asyncio.run(send_telegram_message(message))
                except Exception as e:
                    print(f"⚠️ Error processing post: {e}")

            time.sleep(random_num(10, 15))

    def handle_block(self):
        time.sleep(self.cool_down_minutes * 60)
        self.cool_down_minutes += 20
