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
        wait = WebDriverWait(browser, 15)

        human_delay(10, 10)
        ActionChains(browser).send_keys(Keys.ESCAPE).perform()

        # Find email field and enter email
        location_field = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//input[@placeholder='איזור, עיר שכונה או רחוב']")
            )
        )
        location_field.click()
        human_delay(1, 3)
        location_field.send_keys("לב תל אביב, לב העיר צפון, תל אביב יפו")
        location_item = wait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//b[contains(text(),'לב תל אביב, לב העיר צפון, תל אביב יפו')]",
                )
            )
        )
        location_item.click()
        move_mouse_randomly()

        # Find price field and enter price
        price_field = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//span[contains(text(), 'מחיר')]")
            )
        )
        price_field.click()
        human_delay(1, 3)
        prices = wait.until(
            EC.presence_of_all_elements_located(
                (
                    By.CSS_SELECTOR,
                    ".price-range-input_priceDropdownBox__YOOPn .inputs-slider-range_input__fZs4Z",
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
            EC.presence_of_element_located(
                (By.XPATH, "//span[contains(text(), 'חדרים')]")
            )
        )
        room_field.click()
        human_delay(1, 3)
        rooms = wait.until(
            EC.presence_of_all_elements_located(
                (
                    By.CSS_SELECTOR,
                    ".room-range-input_roomsDropdownBox__S6ymU .buttons-range_button__hNTr6",
                )
            )
        )
        two_rooms = rooms[2]
        two_rooms.click()
        three_rooms = rooms[4]
        three_rooms.click()
        move_mouse_randomly()

        search_button = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//button[@data-nagish='search-submit-button']")
            )
        )
        search_button.click()

        # Wait for home button (to confirm successful login)
        human_delay(5, 7)

        print("🔍 Search successful")

    except Exception as e:
        print(f"❌ Search failed: {e}")
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
    apartments_client = Yad2DBClient()
    notifier.notify("🚀 Starting Yad2 bot")
    shouldRun = True

    while shouldRun:
        try:
            browser = webdriver.Chrome(
                service=webdriver.ChromeService(ChromeDriverManager().install()),
                options=option,
            )
            browser.get("http://www.yad2.co.il/realestate/rent")
            browser.maximize_window()

            search(browser, notifier)

            while True:
                # seen_yad2_posts = apartments_client.get_seen_apartments()

                posts = browser.find_elements(
                    By.XPATH, "//li[@data-nagish='feed-item-list-box']"
                )
                print(f"🖼️ Found {len(posts)} posts in Yad2")
                print("__________________________")
                time.sleep(random.randint(8, 10))

                for post in posts:
                    link_to_post = None
                    text = None
                    price_text = None
                    main_title = None
                    secondary_title = None
                    rooms = None
                    floor = None
                    area = None
                    posted_by_number = None

                    # Scroll to the post and wait
                    # browser.execute_script("arguments[0].scrollIntoView(true);", post)
                    human_delay(2, 4)

                    try:
                        # Get the link to the post
                        try:
                            link_element = post.find_element(
                                By.XPATH, ".//a[@data-nagish='feed-item-layout-link']"
                            )
                            link_to_post = link_element.get_attribute("href")
                        except:
                            print("❌ Could not find link to post, skipping...")
                            continue

                        # Right click and open in new tab
                        browser.execute_script(
                            f"window.open('{link_to_post}', '_blank');"
                        )
                        time.sleep(random.randint(2, 3))

                        # Switch to new tab
                        browser.switch_to.window(browser.window_handles[-1])
                        try:
                            main_title = browser.find_element(
                                By.CSS_SELECTOR,
                                ".ad-item-page-layout_mainContent__tyvpX h1",
                            ).text.strip()
                        except Exception as e:
                            print(f"⚠️ Error getting main title: {e}")

                        try:
                            secondary_title = browser.find_element(
                                By.CSS_SELECTOR,
                                ".ad-item-page-layout_mainContent__tyvpX h2",
                            ).text.strip()
                        except Exception as e:
                            print(f"⚠️ Error getting secondary title: {e}")

                        try:
                            property_details = browser.find_elements(
                                By.CSS_SELECTOR,
                                ".ad-item-page-layout_mainContent__tyvpX .property-detail_buildingItemBox__ESM9C",
                            )
                            rooms = property_details[0].text.strip()
                            floor = property_details[1].text.strip()
                            area = property_details[2].text.strip()
                        except Exception as e:
                            print(f"⚠️ Error getting property details: {e}")

                        try:
                            text = browser.find_element(
                                By.CSS_SELECTOR,
                                ".ad-item-page-layout_mainContent__tyvpX .description_description__9t6rz",
                            ).text.strip()
                        except Exception as e:
                            print(f"⚠️ Error getting description text: {e}")

                        try:
                            price_text = browser.find_element(
                                By.XPATH, "//span[@data-testid='price']"
                            ).text.strip()
                        except Exception as e:
                            print(f"⚠️ Error getting price: {e}")

                        try:
                            browser.find_element(
                                By.XPATH,
                                "//div[@class='rent-agency-contact-section_showAdContactsButtonBox__iB8kS']",
                            ).click()
                            human_delay(1, 3)
                            posted_by_number = browser.find_element(
                                By.XPATH,
                                "//a[@class='phone-number-link_phoneNumberLink__7J2Q4']",
                            ).text.strip()
                        except Exception as e:
                            print(f"⚠️ Error getting contact number: {e}")

                        # Build telegram message
                        message = f"""
                            Yad2
                            🏠 *{main_title}*
                            {secondary_title}

                            📊 *Details:*
                            • {rooms}
                            • {floor}
                            • {area}
                            • {price_text}

                            📝 *Description:*
                            {text}

                            📞 *Contact:*
                            {posted_by_number}

                            🔗 [View on Yad2]({link_to_post})
                            """

                        # Close the tab and switch back to main window
                        browser.close()
                        browser.switch_to.window(browser.window_handles[0])

                    except Exception as e:
                        print(f"❌ Error opening post in new tab: {e}")
                        continue

                wait_with_countdown(random.randint(5, 10))
                print("🔄 Restarting search...")
        except GettingBlockedError as err:
            msg = f"👮‍♂️You probably got blocked... cooling down for {cool_down_minutes} minutes."
            print(msg)
            notifier.notify(msg)
            shouldRun = False
            browser.quit()
            sys.exit()
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
