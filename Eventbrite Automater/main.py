from __future__ import print_function
import httplib2
import os

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools
from eventbrite import Eventbrite
import requests
import datetime
from event import event

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Eventbrite Automating Program'


def get_credentials():
    """
    Code copied from the Google Sheets API

    Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sheets.googleapis.com-python-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def pull_from_sheet(row_id):
    """Pulls data from the GIR spreadsheet

    URL: https://docs.google.com/spreadsheets/d/1AV6GbW1OqohKdgwS7-KAUuyD8quTaUdheixlSNU7iHE/edit#gid=2051303374

    Returns a list of data that is a row of the GIR
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)

    spreadsheetId = '1AV6GbW1OqohKdgwS7-KAUuyD8quTaUdheixlSNU7iHE'
    rangeName = 'Events In Progress!C' + str(row_id) + ':N' + str(row_id)
    request = service.spreadsheets().values().get(
        spreadsheetId=spreadsheetId, range=rangeName).execute()
    values = request.get('values', [])
    return values[0]


def pretty_time (datetime_obj, offset = 0):
    '''
    Takes a datetime object and returns an easily readable string object. Also enables

    Returns a string that represents a datetime object
    '''
    datetime_obj = datetime_obj - datetime.timedelta(minutes = offset)
    time =  datetime_obj.isoformat(' ')[11:16]
    hour = int(time[:2])
    if hour > 12:
        time = str(hour-12) + time[2:] + ' P.M'
    else:
        time.append(' A.M.')

    return time


def get_description(event_obj):
    '''
    Generates as description associated with an event that is put as the description on Eventbrite

    Returns the description of the event as a string that is compatible with the html format
    '''

    admission_message_first = 'This event is open to the public. Entry to the event will be open to ticketholders and, space-permitting, a limited number of walk-ins.' \
    'Ticketholders are encouraged to arrive early to maximize their chances of getting in.' \
    'Having a ticket does not guarantee access to the event but does give the ticketholder priority over walk-ins until '

    admission_message_second = ', at which point walk-ins and ticketholders will have equal access to remaining seats.' \
    'Our standard event policies apply.<br>' \
    'What follows is an overview of the admissions timeline.<br>' \
    'It may be subject to revisions as the event approaches. Seating in the venue is first-come, first served.<br><br>'

    admission_message = admission_message_first + pretty_time(event_obj.event_start) + admission_message_second

    ticket_message = 'More details will be shared very soon here and on our Facebook page.' \
    ' We encourage that you “Like” our Facebook page, The Berkeley Forum, to keep up to date on Forum events.<br><br>' \
    'Note on Tickets<br><br>' \
    "Tickets are non-transferable. While you may purchase a ticket on someone's behalf, their name must be listed on the ticket." \
    'All attendees will be asked to present a Valid ID at the venue that matches the name on the ticket.<br><br>' \
    'All tickets sales are final. Tickets are non-transferable and non-refundable.<br><br>' \
    'To secure a seat for more than one person, simply fill out the form once again for each subsequent person with his or her information.<br><br>' \
    'Please visit our website for a complete list of event policies.'
    
    description = "Event Details:<br><br>"
    description += event_obj.event_title
    description += "<br><br>"
    description += event_obj.web_event_description
    description += "<br><br>"
    description += ("Date: " + str(event_obj.event_start.month) + "/" + str(event_obj.event_start.day) + "/" + str(event_obj.event_start.year) + "<br>")
    description += ("Time: " + pretty_time(event_obj.event_start) + ' (see below for more details about admission)<br>')
    description += ('Location: ' + event_obj.venue)
    description += "<br><br>"
    description += "Admission <br><br>"
    description += admission_message
    description += (pretty_time(event_obj.event_start, 60) + '  Event Admissions Opens for Ticket Holders<br><br>')
    description += (pretty_time(event_obj.event_start, 10) + '  Event Admission No Longer Guaranteed for Ticket Holders<br><br>' )
    description += (pretty_time(event_obj.event_start, 10) + '  Admission Opens for Walk-Ins (Limited Seating)<br><br>' )
    description += (pretty_time(event_obj.event_start, 5) + '  Admission Closed (No Late Seating)<br><br>' )
    description += (pretty_time(event_obj.event_start) + '  Event Begins<br><br>' )
    description += ticket_message

    return description

def create_event(event_obj):
    '''
    Creates an event with the Eventbrite API
    '''
    url = "https://www.eventbriteapi.com/v3/events/"

    # Authorization with our oauth2 token
    header = {"Authorization": "Bearer QXBUB7AGT6TGOYTSXLT4"}

    # Start and end times compatible with the UTC-8 time zone
    start = event_obj.event_start + datetime.timedelta(hours = 8)
    end = event_obj.event_end + datetime.timedelta(hours = 8)

    # Data being passed into the event
    data =  {
        "event.name.html": "(TEST) " + event_obj.event_title,
        "event.description.html" : get_description(event_obj),
        "event.start.utc": start.isoformat() + "Z",
        "event.start.timezone": "America/Los_Angeles",
        "event.end.utc": end.isoformat() + "Z",
        "event.end.timezone": "America/Los_Angeles",
        "event.currency": "USD"
    }

    # Response being pushed on eventbrite
    response = requests.post(url = url, headers = header, data = data, verify = True)

    # Print's response in the console
    print (response.text)

def main():
    row_id = int(input("Enter the Row ID of the event in the Guest Invitation Records\n"))
    sheets_values = pull_from_sheet(row_id)
    this_event = event(sheets_values)
    create_event(this_event)

if __name__ == '__main__':
    main()
