from __future__ import print_function
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

# Setup the Sheets API
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
store = file.Storage('credentials.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
    creds = tools.run_flow(flow, store)
service = build('sheets', 'v4', http=creds.authorize(Http()))

# spread sheet id is the value between the "/d/" and the "/edit" in the URL
SPREADSHEET_ID = '1nH7lGXv-8v6-XozGaJi2IrbgOH0LmVn210rM4EgHDUM'

# specify range in a sheet
RANGE_NAME = 'Sheet1!A1:C1'
values = [
    [1,2,3]
    # Additional rows ...
]
body = {
    'values': values
}

result = service.spreadsheets().values().update(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME,valueInputOption='RAW', body=body).execute()
print('{0} cells updated.'.format(result.get('updatedCells')));
