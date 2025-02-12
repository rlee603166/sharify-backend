from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import threading

# Global browser instance and lock
driver = None
driver_lock = threading.Lock()

def initialize_driver():
    global driver
    if driver is None:
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(service=Service('/usr/bin/chromedriver'), options=chrome_options)
    return driver

def get_driver_lock():
    return driver_lock
