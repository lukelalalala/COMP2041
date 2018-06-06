from selenium import webdriver
import csv

# Chrome will be started in headless mode
options = webdriver.ChromeOptions()
options.add_argument('--headless')

# add list of pages
pages = []

# chrome driver is needed for automated testing
browser = webdriver.Chrome(executable_path="C:/Users/luke.yuan/Desktop/chromedriver",chrome_options=options)
f = open('speedTestReport.csv','w+')
f.write('site,mobile,computer\n')

for page in pages:
    url = "https://developers.google.com/speed/pagespeed/insights/?hl=en-US&utm_source=PSI&utm_medium=incoming-link&utm_campaign=PSI&url=" + page
    browser.get(url)
    f.write(page)
    f.write(","+str(browser.find_element_by_xpath("//*[@id='page-speed-insights']/div[2]/div/div[2]/div[1]/div[3]/div[2]/div[2]/p[3]/span").text)+",") 
    print(page + " mobile " + str(browser.find_element_by_xpath("//*[@id='page-speed-insights']/div[2]/div/div[2]/div[1]/div[3]/div[2]/div[2]/p[3]/span").text))
    
    # go to desktop page
    browser.find_element_by_id(':l').click()
    f.write(str(browser.find_element_by_xpath("//*[@id='page-speed-insights']/div[2]/div/div[2]/div[2]/div[3]/div[2]/div[2]/p[3]/span").text)+"\n")
    print(page + " computer " + str(browser.find_element_by_xpath("//*[@id='page-speed-insights']/div[2]/div/div[2]/div[2]/div[3]/div[2]/div[2]/p[3]/span").text))

f.close()
