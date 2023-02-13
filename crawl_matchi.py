from datetime import datetime, timedelta
from flask import Flask
from google.cloud import bigquery
from google.cloud import secretmanager
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
import json
import pandas as pd
import requests
import time

app = Flask(__name__)

def create_driver():
    options = webdriver.ChromeOptions()
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
    options.add_argument("user-agent=" + user_agent)
    # options.add_argument("--headless")
    options.add_argument('--no-sandbox')
    # options.add_argument("window-size=1024,768")
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    return driver

def get_slots(date):
    url = f'https://www.matchi.se/book/index?lat=&lng=&offset=0&outdoors=&sport=1&date={date}&q=Solna+Tenniscenter+-+Solna+TK&hasCamera='
    driver = create_driver()
    driver.get(url)
    delay = 3 # seconds
    myElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.NAME, 'submit')))

    slots = driver.find_element_by_id('slots_1965').find_elements_by_xpath(".//*")[0].text
    print(slots)
    if 'Solna' not in slots:
        slots = set(slots.split(' '))
        slots.remove('00')
    else:
        slots = set()
    driver.close()
    return slots

def get_screenshot():
    dt = datetime.now()
    for td in [14, 15]:
        date = dt + timedelta(days=td)
        date = str(date.date())
        url = f'https://www.matchi.se/book/index?lat=&lng=&offset=0&outdoors=&sport=1&date={date}&q=Solna+Tenniscenter+-+Solna+TK&hasCamera='
        driver = create_driver()
        driver.get(url)
        delay = 3 # seconds
        myElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.NAME, 'submit')))
        driver.save_screenshot(f'./haha_{date}.png')


@app.route("/")
def main():
    data = []
    dt = datetime.now()
    for td in [14, 15]:
        date = dt + timedelta(days=td)
        date = str(date.date())
        slots = get_slots(date)
        data.append([str(dt), date, slots])

    columns = ['run_timestamp', 'on_date_availability', 'slots']
    df = pd.DataFrame.from_records(data, columns=columns)
    df.to_gbq(f"cj-growth.matchi.slots_availability", chunksize=10000, if_exists="append")
    return 'Success'

if __name__ == '__main__':
    # get_screenshot()
    main()
