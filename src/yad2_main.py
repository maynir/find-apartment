import random
import re
import traceback
import sys
import time
import datetime
import pymongo
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from twilio.rest import Client
from webdriver_manager.chrome import ChromeDriverManager
from database import Yad2DBClient
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

# --- Selectors and XPaths ---
LOCATION_INPUT_XPATH = "//input[@placeholder='איזור, עיר שכונה או רחוב']"
PRICE_FIELD_XPATH = "//span[contains(text(), 'מחיר')]"
PRICE_RANGE_INPUT_CSS = (
    ".price-range-input_priceDropdownBox__YOOPn .inputs-slider-range_input__fZs4Z"
)
ROOM_FIELD_XPATH = "//span[contains(text(), 'חדרים')]"
ROOM_RANGE_BUTTON_CSS = (
    ".room-range-input_roomsDropdownBox__S6ymU .buttons-range_button__hNTr6"
)
SEARCH_SUBMIT_BUTTON_XPATH = "//button[@data-nagish='search-submit-button']"
POST_LIST_ITEM_XPATH = "//li[@data-nagish='feed-item-list-box'][not(@data-testid='dfp-slot')][not(@data-testid='yad1-listing-basic')]"
POST_LINK_XPATH = ".//a[@data-nagish='feed-item-layout-link']"  # Relative XPath
MAIN_TITLE_CSS = ".ad-item-page-layout_mainContent__tyvpX h1"
SECONDARY_TITLE_CSS = ".ad-item-page-layout_mainContent__tyvpX h2"
PROPERTY_DETAILS_CSS = (
    ".ad-item-page-layout_mainContent__tyvpX .property-detail_buildingItemBox__ESM9C"
)
DESCRIPTION_CSS = (
    ".ad-item-page-layout_mainContent__tyvpX .description_description__9t6rz"
)
PRICE_TEXT_XPATH = "//span[@data-testid='price']"
SHOW_CONTACT_BUTTON_XPATH = (
    "//div[@class='rent-agency-contact-section_showAdContactsButtonBox__iB8kS']"
)
PHONE_NUMBER_LINK_XPATH = "//a[@class='phone-number-link_phoneNumberLink__7J2Q4']"
# --- End Selectors and XPaths ---

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


def search(browser, notifier):
    try:
        wait = WebDriverWait(browser, 30)

        human_delay(20, 20)
        ActionChains(browser).send_keys(Keys.ESCAPE).perform()

        # # Find level number
        # extra_fields_field = wait.until(
        #     EC.presence_of_element_located((By.CSS_SELECTOR, ".extra-filters_extraFiltersBox__df4eE"))
        # )
        # extra_fields_field.click()
        # human_delay(1, 3)
        
        # level_fields = wait.until(
        #     EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".floor-range-input_selectRangeBox__nlfaR .base-select_select__BYmkn"))
        # )
        # low_level = level_fields[0]
        # ActionChains(browser).move_to_element(low_level).perform()
        # low_level.click()
        # human_delay(1, 3)
        # all_levels = low_level.find_elements(By.TAG_NAME, "li")
        # ActionChains(low_level).send_keys(Keys.ARROW_DOWN).perform()
        # human_delay(1, 3)
        # ActionChains(low_level).send_keys(Keys.ARROW_DOWN).perform()
        # human_delay(1, 3)
        # ActionChains(low_level).send_keys(Keys.ARROW_DOWN).perform()
        # human_delay(1, 3)
        # ActionChains(low_level).send_keys(Keys.ENTER).perform()

        # Find email field and enter email
        location_field = wait.until(
            EC.presence_of_element_located((By.XPATH, LOCATION_INPUT_XPATH))
        )
        location_field.click()
        human_delay(1, 3)
        
        locations = [
            "לב תל אביב, לב העיר צפון, תל אביב יפו",
            "הצפון הישן - דרום, תל אביב יפו",
            "הצפון הישן - צפון, תל אביב יפו",
            "כרם התימנים, תל אביב יפו",
            "נווה צדק, תל אביב יפו",
            "פלורנטין, תל אביב יפו",
        ]

        for loc in random.sample(locations, 5):
            location_field.send_keys(loc)
            location_item = wait.until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        f'//b[contains(text(),"{loc}")]',
                    )
                )
            )
            location_item.click()
            move_mouse_randomly()

        # Find price field and enter price
        price_field = wait.until(
            EC.presence_of_element_located((By.XPATH, PRICE_FIELD_XPATH))
        )
        price_field.click()
        human_delay(1, 3)
        prices = wait.until(
            EC.presence_of_all_elements_located(
                (
                    By.CSS_SELECTOR,
                    PRICE_RANGE_INPUT_CSS,
                )
            )
        )
        low_price = prices[0]
        high_price = prices[1]
        low_price.send_keys(5000)
        high_price.send_keys(7500)
        move_mouse_randomly()

        # Find room number
        room_field = wait.until(
            EC.presence_of_element_located((By.XPATH, ROOM_FIELD_XPATH))
        )
        room_field.click()
        human_delay(1, 3)
        rooms = wait.until(
            EC.presence_of_all_elements_located(
                (
                    By.CSS_SELECTOR,
                    ROOM_RANGE_BUTTON_CSS,
                )
            )
        )
        two_rooms = rooms[2]
        two_rooms.click()
        three_rooms = rooms[4]
        three_rooms.click()
        move_mouse_randomly()

        search_button = wait.until(
            EC.presence_of_element_located((By.XPATH, SEARCH_SUBMIT_BUTTON_XPATH))
        )
        search_button.click()

        human_delay(5, 7)

        print("🔍 Search successful")

    except Exception as e:
        print(f"❌ Search failed: {e}")
        traceback.print_exc()
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
# option.add_argument("--headless")
option.add_argument(
    "--disable-blink-features=AutomationControlled"
)  # Prevent detection
option.add_argument(
    f"user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.0.0 Safari/537.36"
)


def main():
    notifier = Notifier()
    apartments_client = Yad2DBClient()
    notifier.notify("🚀 Starting Yad2 bot")
    shouldRun = True

    while shouldRun:
        try:
            while True:
                browser = webdriver.Chrome(
                    service=webdriver.ChromeService(ChromeDriverManager().install()),
                    options=option,
                )
                browser.get("http://www.yad2.co.il/realestate/rent")
                browser.maximize_window()

                search(browser, notifier)

                move_mouse_randomly()

                seen_yad2_posts = apartments_client.get_seen_apartments()

                posts = browser.find_elements(By.XPATH, POST_LIST_ITEM_XPATH)

                move_mouse_randomly()

                print(f"🖼️ Found {len(posts)} posts in Yad2")
                print("__________________________")
                
                time.sleep(random.randint(8, 10))

                for post in posts:
                    text = None
                    price_text = None
                    secondary_title = None
                    rooms = None
                    floor = None
                    area = None
                    posted_by_number = None
                    imgs_src = []
                    map_image = None
                    post_date = None

                    try:
                        try:
                            link_element = post.find_element(By.XPATH, POST_LINK_XPATH)
                            link_to_post = link_element.get_attribute("href")
                            print(f"🔗 Link to post: {link_to_post}")
                        except:
                            print("❌ Could not find link to post, skipping...")
                            continue

                        try:
                            item_id = link_to_post.split("/item/")[1].split("?")[0]
                            print(f"📋 Item ID: {item_id}")
                        except Exception as e:
                            print(f"❌ Error extracting item ID: {e}")
                            continue

                        if item_id in seen_yad2_posts:
                            print(f"🥱 Item ID already seen, skipping...")
                            print("__________________________")
                            continue

                        browser.execute_script(
                            f"window.open('{link_to_post}', '_blank');"
                        )
                        time.sleep(random.randint(2, 3))
                        browser.switch_to.window(browser.window_handles[-1])

                        try:
                            main_title = browser.find_element(
                                By.CSS_SELECTOR,
                                MAIN_TITLE_CSS,
                            ).text.strip()
                            print(f"🏠 Main title: {main_title}")
                        except Exception as e:
                            print(f"⚠️ Error getting main title")
                            browser.close()
                            browser.switch_to.window(browser.window_handles[0])
                            time.sleep(random.randint(6, 7))
                            continue

                        try:
                            secondary_title = browser.find_element(
                                By.CSS_SELECTOR,
                                SECONDARY_TITLE_CSS,
                            ).text.strip()
                            print(f"🏢 Secondary title: {secondary_title}")
                        except Exception as e:
                            print(f"⚠️ Error getting secondary title: {e}")

                        try:
                            property_details = browser.find_elements(
                                By.CSS_SELECTOR,
                                PROPERTY_DETAILS_CSS,
                            )
                            rooms = property_details[0].text.strip()
                            floor = property_details[1].text.strip()
                            area = property_details[2].text.strip()
                            print(f"🚪 Rooms: {rooms}, 📍 Floor: {floor}, 📏 Area: {area}")
                        except Exception as e:
                            print(f"⚠️ Error getting property details: {e}")

                        try:
                            text = browser.find_element(
                                By.CSS_SELECTOR,
                                DESCRIPTION_CSS,
                            ).text.strip()
                            print(f"📝 Description: {text}")
                        except Exception as e:
                            print(f"⚠️ Error getting description text")

                        try:
                            price_element = browser.find_element(
                                By.XPATH, PRICE_TEXT_XPATH
                            )
                            price_text = price_element.text.strip()
                            if not price_text:
                                price_text = price_element.get_attribute('textContent').strip()
                            print(f"💰 Price: {price_text}")
                        except Exception as e:
                            print(f"⚠️ Error getting price")

                        try:
                            browser.find_element(
                                By.XPATH,
                                SHOW_CONTACT_BUTTON_XPATH,
                            ).click()
                            human_delay(1, 3)
                            posted_by_number = browser.find_element(
                                By.XPATH,
                                PHONE_NUMBER_LINK_XPATH,
                            ).text.strip()
                            print(f"📞 Contact number: {posted_by_number}")
                        except Exception as e:
                            print(f"⚠️ Error getting contact number")

                        try:
                            date_element = browser.find_element(
                                By.CSS_SELECTOR,
                                ".report-ad_createdAt__tqSM6"
                            )
                            date_text = date_element.text.strip()
                            date_match = re.search(r'(\d{2}/\d{2}/\d{2})', date_text)
                            if date_match:
                                post_date = date_match.group(1)
                                post_date = datetime.datetime.strptime(post_date, '%d/%m/%y')
                                print(f"📅 Post date: {post_date.strftime('%d/%m/%Y')}")
                        except Exception as e:
                            print(f"⚠️ Error getting post date: {e}")

                        try:
                            apartments_client.save_apartment(
                                {
                                    "item_id": item_id,
                                    "main_title": main_title,
                                    "secondary_title": secondary_title,
                                    "rooms": rooms,
                                    "floor": floor,
                                    "area": area,
                                    "price_text": price_text,
                                    "description": text,
                                    "contact_number": posted_by_number,
                                    "link_to_post": link_to_post,
                                    "post_date": post_date,
                                }
                            )
                            print("💾 Apartment details saved to database")
                        except Exception as e:
                            print(f"⚠️ Error saving apartment to database: {e}")

                        if post_date:
                            current_date = datetime.datetime.now()
                            if (current_date - post_date).days > 60:
                                print(f"📅 Post is too old ({post_date.strftime('%d/%m/%Y')}), skipping...")
                                browser.close()
                                browser.switch_to.window(browser.window_handles[0])
                                time.sleep(random.randint(6, 7))
                                continue
                        
                        message = (
                            f"Yad2\n"
                            f"🏠 Main title: {main_title}\n"
                            f"Secondary title: {secondary_title}\n\n"
                            f"📊 Details:\n"
                            f"• 🚪 Rooms: {rooms}\n"
                            f"• 🏢 Floor: {floor}\n"
                            f"• 📏 Area: {area}\n"
                            f"• 💰 Price: {price_text}\n"
                            f"• 📅 Posted: {post_date.strftime('%d/%m/%Y') if post_date else 'N/A'}\n\n"
                            f"📝 Description:\n"
                            f"{text}\n\n"
                            f"📞 Contact: {posted_by_number}\n\n"
                            f"🔗 [View on Yad2]({link_to_post})"
                        )

                        try:
                            imgs = browser.find_elements(
                                By.CSS_SELECTOR,
                                ".gallery-grid_foucsableItem__3H8__ img",
                            )[:9]
                            imgs_src = [img.get_attribute("src") for img in imgs]
                            print(f"📷 Found {len(imgs_src)} post images ")
                        except Exception as err:
                            print(f"⚠️Could not find post images")

                        if main_title:
                            map_image = generate_map_image(main_title, "תל אביב")

                        try:
                            notifier.notify(message, imgs_src, map_image)
                        except Exception as e:
                            print(f"❌ Error sending message: {e}")

                        print("__________________________")

                        browser.close()
                        browser.switch_to.window(browser.window_handles[0])

                        time.sleep(random.randint(3, 6))

                    except Exception as e:
                        print(f"❌ Error opening post in new tab: {e}")
                        continue

                wait_with_countdown(random.randint(5, 10))
                browser.quit()
                print("🔄 Restarting search...")
        except Exception as err:
            print(f"❌ Error: {err}")
            print("Full traceback:")
            traceback.print_exc()
            print("Continuing after error...")
            browser.quit()
            time.sleep(10)

    browser.quit()


if __name__ == "__main__":
    main()
