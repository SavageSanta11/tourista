from bs4 import BeautifulSoup
import pandas as pd
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC




options = Options()
options.add_argument('--headless')  # hide GUI
options.add_argument("--window-size=1920,1080")  # set window size to native GUI size
options.add_argument("start-maximized")  # ensure window is full-screen




chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option(
    # this will disable image loading
    "prefs", {"profile.managed_default_content_settings.images": 2}
)
chrome_options.add_experimental_option("excludeSwitches", ["disable-popup-blocking"])

driver = webdriver.Chrome()
URL = "https://www.booking.com/searchresults.html?label=bin859jc-&sid=83e62805bf0a8fdcf66a806d17985eb6&aid=357028&dest_id=20061717&dest_type=city&latitude=42.3588981628418&longitude=-71.05780029296875&sb_travel_purpose=leisure&nflt=ht_id%3D204&order=popularity&group_adults=2&req_adults=2&no_rooms=1&group_children=0&req_children=0&age=&req_age=&slp_r_match_to=0&shw_aparth=0"
driver.get(URL)

def retrieveText(arr):
    text_arr = []
    for element in arr:
        text_arr.append(element.getText())
    return text_arr

hotel_names = []
hotel_neighborhoods = []
hotel_info = []

while True:
    driver.implicitly_wait(3)
    soup = BeautifulSoup(driver.page_source, features="lxml")
    # retrieving hotel names
    names = soup.find_all(class_ = 'fcab3ed991')
    hotel_names_temp = retrieveText(names)
    hotel_names_temp.pop(0)
    hotel_names = hotel_names + hotel_names_temp
    # retrieving hotel locations
    locations = soup.find_all(class_ = "f4bd0794db b4273d69aa")
    hotel_neighborhoods_temp = retrieveText(locations)
    for i in range(0, len(hotel_neighborhoods_temp), 2):
        hotel_neighborhoods.append(hotel_neighborhoods_temp[i])
    # retrieving hotel info paragraph
    info_paragraphs = soup.select("div.d8eab2cf7f")
    hotel_info_temp = retrieveText(info_paragraphs)
    reviews = soup.select("div.d8eab2cf7f.c90c0a70d3")
    review_arr = retrieveText(reviews)
    location_divs = soup.select("div.d8eab2cf7f.a1fbd102d9")
    location_div_arr = retrieveText(location_divs)
    remove_arr = review_arr + location_div_arr
    hotel_info_temp = [elem for elem in hotel_info_temp if elem not in remove_arr]
    hotel_info_temp.pop(0)
    hotel_info = hotel_info + hotel_info_temp
    #finds next button
    next = driver.find_element(By.XPATH, './/*[@id="search_results_table"]/div[2]/div/div/div[4]/div[2]/nav/div/div[3]/button[1]')
    if 'disabled' in next.get_attribute('outerHTML'):
        break
    next.click()
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'fcab3ed991')))
    time.sleep(5)


# make pandas dataframe with hotel names, neighborhood, and information
hotel_dict = {'name' : hotel_names, 'neighborhood' : hotel_neighborhoods, 'info' : hotel_info}
hotel_df = pd.DataFrame(hotel_dict)
hotel_df['context'] = hotel_df['name'] + " is located in " + hotel_df['neighborhood'] + ". " + hotel_df['info']

print(hotel_df['context'][1])
# # group by neighborhood
# neighborhoods = pd.unique(hotel_df['neighborhood'])
# contexts = []
# print(hotel_df.groupby('neighborhood')['indiv_context'].apply(' '.join)[3])