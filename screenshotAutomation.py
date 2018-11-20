from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from selenium import webdriver
from PIL import Image
import threading, os, time

# Setup the Sheets API
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
store = file.Storage('token.json')
creds = store.get()
if not creds or creds.invalid:
	flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
	creds = tools.run_flow(flow, store)
service = build('sheets', 'v4', http=creds.authorize(Http()))
# spread sheet id is the value between the "/d/" and the "/edit" in the URL
SPREADSHEET_ID = '11BufuJbbUsgmauYOIsIUVECRMFz4qDine8ZYW5h1st8'

# read domains
domainsRange = 'domains'
readResult = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range=domainsRange).execute()

# create screenshots directory if not exists
os.makedirs('/screenshots', exist_ok=True)

# chrome driver is needed for automated testing and it will be in headless mode
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument("log-level=3")
scrollbarWidth = 17
targetWidth = None
targetHeight = None

def takeScreenshot(page):
	browser = webdriver.Chrome(executable_path='/mnt/c/Users/Luke/Desktop/chromedriver.exe',chrome_options=options)
	original_size = browser.get_window_size()
	filename = 'screenshots/{domain}.png'.format(domain=page[len('https://'):])
	if targetWidth is not None and targetHeight is not None:
		browser.set_window_size(targetWidth + scrollbarWidth, targetHeight)

	else:
		required_width = browser.execute_script('return document.body.parentNode.scrollWidth')
		required_height = browser.execute_script('return document.body.parentNode.scrollHeight')
		browser.set_window_size(required_width, required_height)

	browser.get(page)

	# wait until page is completely loaded
	time.sleep(3)

	browser.save_screenshot(filename)
    # avoids scrollbar
	if targetWidth is None and targetHeight is None:
		browser.find_element_by_tag_name('body').screenshot(filename)
		browser.set_window_size(original_size['width'], original_size['height'])
	else:
		Image.open(filename).crop((0, 0, targetWidth, targetHeight)).save(filename)

threadPool = []
for page in pages:
	threadPool.append(threading.Thread(name=page, target=takeScreenshot, args=(page,)))

for thread in threadPool:
	print('Starting {name}.'.format(name=thread.name))
	thread.start()

for thread in threadPool:
	print('Joining {name}.'.format(name=thread.name))
	thread.join()
