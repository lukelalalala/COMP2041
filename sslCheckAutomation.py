from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re

# chrome driver is needed for automated testing
browser = webdriver.Chrome(executable_path="/Users/luke.yuan/Desktop/chromedriver")
url = "https://www.jitbit.com/sslcheck/"
browser.get(url)
browser.find_element_by_xpath("//*[@id='tweetForm']/div[2]/a").click()
pages = []
for page in pages:
    # add https string at the beginning
    if not re.match(r'^https://(.*)', page, re.M):
        page = "https://" + page
    browser.find_element_by_id('url').send_keys(page)
    browser.find_element_by_id('btn').click()

    try:
        # wait until results are loaded
        crawlDone = WebDriverWait(browser, 30).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id='results']/span")))
        print("Check for :" + page +"\n")

        # expand the links to display details
        parentHiddenList = browser.find_element_by_xpath("//*[@id='results']")
        hiddenList = parentHiddenList.find_elements_by_tag_name("a")
        for hiddenLink in hiddenList:
            browser.execute_script("arguments[0].click();", hiddenLink)

        print (browser.find_element_by_id('results').text+"\n")
        print("=====================================================")
        browser.find_element_by_id('url').clear()
    except:
        print("Timeout 30 seconds")
