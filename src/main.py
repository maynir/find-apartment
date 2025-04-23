import random
import re
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
from database import ApartmentsDBClient
from etc import config
from utils import human_delay, random_num
from utils.delays import wait_with_countdown
from utils.notifier import Notifier
from utils.openai_helper import analyze_apartment_details_with_openai
from utils.map_helper import generate_map_image
from utils.text_processing import (
    bad_words_regex,
    good_words_regex,
    match_info,
    validate_match,
)

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

def log_in(browser, email, password, notifier):
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
        print("🔓 Login successful!")
        login_message = f"🔓 Successfully logged in to Facebook!"
        notifier.notify(login_message)

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
    apartments_client = ApartmentsDBClient()
    notifier.notify("🚀 Starting Facebook bot")

    while True:
        try:
            browser = webdriver.Chrome(
                service=webdriver.ChromeService(ChromeDriverManager().install()),
                options=option,
            )
            browser.get("http://facebook.com")
            browser.maximize_window()

            log_in(browser, config.MY_EMAIL, config.PASSWORD, notifier)

            while True:
                random.shuffle(config.group_ids)
                blocked_retries = 0

                for group_id in config.group_ids:
                    seen_apartments = apartments_client.get_seen_apartments()
                    group_url = f"https://www.facebook.com/groups/{group_id}?sorting_setting=CHRONOLOGICAL"

                    browser.get(group_url)
                    time.sleep(random.randint(5, 7))

                    group_name = (
                        WebDriverWait(browser, 10)
                        .until(
                            EC.presence_of_element_located(
                                (
                                    By.XPATH,
                                    "//*[@class='x1i10hfl xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz x1heor9g xkrqix3 x1sur9pj x1pd3egz']",
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
                        inner_post = None
                        story_message_elements = post.find_elements(
                            By.XPATH, ".//div[@data-ad-rendering-role='story_message']"
                        )
                        if story_message_elements:
                            inner_post = story_message_elements[0]
                            print(f"🪏 Found post inside post")
                        posted_by = None
                        posted_by_url = None
                        link_to_post = None
                        text = None

                        ActionChains(browser).move_to_element(post).perform()

                        try:
                            # Get posted by
                            try:
                                time.sleep(random.randint(2, 5))
                                posted_by = post.find_element(
                                    By.TAG_NAME, "strong"
                                ).text
                                if not posted_by:
                                    print("id is empty, trying again")
                                    time.sleep(2)
                                    posted_by = post.find_element(
                                        By.TAG_NAME, "strong"
                                    ).text
                                print(f"🔍 Processing post By '{posted_by}'")
                            except Exception as err:
                                print(f"⚠️Could not find post author")

                            # Click on "See more" buttons
                            see_mores = post.find_elements(
                                By.XPATH, ".//div[contains(text(), 'See more')]"
                            )
                            for see_more in see_mores:
                                try:
                                    ActionChains(browser).move_to_element(
                                        see_more
                                    ).perform()
                                    browser.execute_script(
                                        "arguments[0].click();", see_more
                                    )
                                    time.sleep(random.randint(5, 10))
                                    print("🔋 Load More clicked")
                                    time.sleep(random.randint(5, 10))
                                except Exception as err:
                                    print(f"⚠️ Failed to click 'See More' button: {err}")
                                    continue

                            # Get link to post
                            try:
                                link = post.find_element(
                                    By.XPATH, ".//a[contains(@href, 'pcb')]"
                                ).get_attribute("href")
                                post_id = re.search(r"set=pcb\.(\d+)", link).group(1)
                                link_to_post = f"https://www.facebook.com/groups/{group_id}/posts/{post_id}"
                                print(f"🔗 Found link to post: {link_to_post}")
                            except Exception as err:
                                print(f"⚠️Could not find link to post")

                            # Get posted by URL
                            try:
                                posted_by_url = post.find_element(
                                    By.XPATH,
                                    ".//*[@data-ad-rendering-role='profile_name']//a",
                                ).get_attribute("href")
                                print(f"🔗 Found post author URL")
                            except Exception as err:
                                print(f"⚠️Could not find post author URL")

                            # Get post text
                            try:
                                if inner_post:
                                    text = inner_post.find_element(
                                        By.XPATH, f".//*[@data-ad-preview='message']"
                                    ).text
                                else:
                                    text = post.find_element(
                                        By.XPATH, f".//*[@data-ad-preview='message']"
                                    ).text
                                print(f"📝 Found post text:")
                                print(text)

                            except Exception as err:
                                print(f"⚠️Could not find post text, to the next one")
                                print("__________________________")
                                continue

                            # Get post images
                            try:
                                imgs = post.find_elements(
                                    By.XPATH,
                                    ".//*[@class='x6ikm8r x10wlt62 x10l6tqk']//img",
                                )
                                imgs_src = [img.get_attribute("src") for img in imgs]
                                print(f"📷 Found {len(imgs_src)} post images ")
                            except Exception as err:
                                print(f"⚠️Could not find post images")
                                imgs_src = []

                            price, city, address, rooms, location_details = (
                                analyze_apartment_details_with_openai(text)
                            )

                            print(f"🤖 OpenAI Analysis Results:")
                            print(f" 💰 Price: {price} ILS")
                            print(f" 🏙️ City: {city}")
                            print(f" 📍 Address: {address}")
                            print(f" 🚪 Rooms: {rooms}")
                            print(f" 🗺️ Location Details: {location_details}")

                            if address:
                                map_image = generate_map_image(address, city)

                            (
                                is_good_match_word,
                                is_bad_match_word,
                                good_match_word,
                                bad_match_word,
                            ) = validate_match(text, price, city, rooms)

                            # Check for duplicate posts before running expensive OpenAI analysis
                            if (
                                text in seen_apartments
                                or apartments_client.get_apartments_by_text(text)
                            ):
                                print(
                                    f"🥱Apartment posted by '{posted_by}' already seen - {match_info(bad_match_word, good_match_word)}"
                                )
                                print("__________________________")
                                continue

                            apartments_client.save_apartment(
                                {
                                    "posted_by": posted_by,
                                    "posted_by_url": posted_by_url,
                                    "link_to_post": link_to_post,
                                    "text": text,
                                    "group_name": group_name,
                                    "group_url": group_url,
                                    "is_good_match_word": is_good_match_word,
                                    "is_bad_match_word": is_bad_match_word,
                                    "price": price,
                                    "city": city,
                                    "address": address,
                                    "rooms": rooms,
                                    "location_details": location_details,
                                    "is_within_budget": price
                                    and price <= config.BUDGET_THRESHOLD,
                                }
                            )

                            if is_bad_match_word or not is_good_match_word:
                                print(
                                    f"👎🏼Apartment does not match criteria - {match_info(bad_match_word, good_match_word)}"
                                )
                                print("__________________________")
                                continue

                            if price and price > config.BUDGET_THRESHOLD:
                                print(f"👎🏼 Apartment exceeds budget threshold")
                                print("__________________________")
                                continue

                            print(f"✅ NEW MATCH FOUND: {good_match_word.group()}")

                            try:
                                apartment_details = []
                                if price:
                                    apartment_details.append(f"💰 Price: {price:,} ILS")
                                if city:
                                    apartment_details.append(f"🏙️ City: {city}")
                                if address:
                                    apartment_details.append(f"📍 Address: {address}")
                                if rooms:
                                    apartment_details.append(f"🚪 Rooms: {rooms}")
                                if location_details:
                                    apartment_details.append(
                                        f"📌 Location Details: {location_details}"
                                    )

                                details_section = (
                                    "\n".join(apartment_details)
                                    if apartment_details
                                    else "No details extracted"
                                )

                                message = (
                                    f"🏠 NEW APARTMENT LISTING\n"
                                    f"{'=' * 27}\n"
                                    f"📝 Post Content:\n{text}\n\n"
                                    f"🔍 Extracted Details:\n{details_section}\n\n"
                                    f"📱 Contact Info:\n"
                                    f"👤 Posted by: {posted_by}\n"
                                    f"🔗 Profile: {posted_by_url}\n\n"
                                    f"📍 Source:\n"
                                    f"👥 Group: {group_name}\n"
                                    f"🔗 Post URL: {link_to_post}\n"
                                    f"🔗 Group URL: {group_url}\n\n"
                                )
                                notifier.notify(message, imgs_src, map_image)
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

                wait_with_countdown(random.randint(3, 5))
                print("🔄 Restarting group search...")
        except GettingBlockedError as err:
            msg = f"👮‍♂️You probably got blocked... cooling down for {cool_down_minutes} minutes."
            print(msg)
            notifier.notify(msg)
            browser.quit()
            sys.exit()
            wait_with_countdown(cool_down_minutes)
            cool_down_minutes += 20
            blocked_retries = 0
        except Exception as err:
            import traceback

            print(f"❌ Error: {err}")
            print("Full traceback:")
            traceback.print_exc()
            print("Continuing after error...")
            browser.quit()
            time.sleep(10)

    browser.quit()


if __name__ == "__main__":
    main()
