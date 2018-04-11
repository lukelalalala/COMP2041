from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

pages = []

# chrome driver is needed for automated testing
browser = webdriver.Chrome(executable_path="/Users/luke.yuan/Desktop/chromedriver")

for page in pages:
    url = "https://developers.google.com/speed/pagespeed/insights/?hl=en-US&utm_source=PSI&utm_medium=incoming-link&utm_campaign=PSI&url=" + page
    browser.get(url)

    print(page + " mobile " + str(browser.find_element_by_xpath("//*[@id='page-speed-insights']/div[2]/div/div[2]/div[1]/div[3]/div[2]/div[2]/p[3]/span").text))
    browser.find_element_by_id(':l').click()
    print(page + " computer " + str(browser.find_element_by_xpath("//*[@id='page-speed-insights']/div[2]/div/div[2]/div[2]/div[3]/div[2]/div[2]/p[3]/span").text))
