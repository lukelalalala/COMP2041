from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from selenium import webdriver
from PIL import Image
import os

# Setup the Sheets API
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
store = file.Storage('credentials.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
    creds = tools.run_flow(flow, store)
service = build('sheets', 'v4', http=creds.authorize(Http()))

# spread sheet id is the value between the "/d/" and the "/edit" in the URL
SPREADSHEET_ID = '<INSERT YOUR SPREADSHEET ID>'

# read domains
domainsRange = 'domains'
readResult = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range=domainsRange).execute()

# chrome driver is needed for automated testing and it will be in headless mode
options = webdriver.ChromeOptions()
options.add_argument('--headless')
browser = webdriver.Chrome(executable_path="<INSERT CHROMEDRIVER PATH HERE>",chrome_options=options)
scrollbarWidth = 17
targetWidth = 1920
targetHeight = 1080
browser.set_window_size(targetWidth + scrollbarWidth, targetHeight)

# create screenshots directory if not exists
os.makedirs("/screenshots", exist_ok=True)

for page in readResult.get('values')[0]:
    print(page)
    browser.get(page)

    filename = 'screenshots/{domain}.png'.format(domain=page[len('https://'):])
    browser.save_screenshot(filename)
    
    # crop the image to hide scroll bar
    Image.open(filename).crop((0, 0, targetWidth, targetHeight)).save(filename)
