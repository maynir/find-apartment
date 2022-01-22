import requests
from bs4 import BeautifulSoup

group_id="35819517694"
page_url = "https://mobile.facebook.com/groups/" + group_id

page_content = requests.get(page_url).text

soup = BeautifulSoup(page_content, "html.parser")
feed_container = soup.find(id="m_group_stories_container").find_all("p")
for i in feed_container:
    print(i.text)