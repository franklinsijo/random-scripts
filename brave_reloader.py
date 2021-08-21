#!/usr/bin/env python3

from selenium import webdriver

import time
driver_path = '/usr/local/bin/chromedriver'
brave_path = '//Applications/Brave Browser.app/Contents/MacOS/Brave Browser'
option = webdriver.ChromeOptions()
option.binary_location = brave_path
option.add_argument('user-data-dir=/Users/frankojis/Library/Application Support/BraveSoftware/Brave-Browser/Default')
browser = webdriver.Chrome(executable_path=driver_path, options=option)
while True:
    time.sleep(5)
    browser.refresh()

