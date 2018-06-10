

from apiclient import discovery
from apiclient import errors
from httplib2 import Http
from oauth2client import file, client, tools
import base64
from bs4 import BeautifulSoup
import re
import time
import dateutil.parser as parser
from datetime import datetime
import datetime
import csv


# Creating a storage.JSON file with authentication details
SCOPES = 'https://www.googleapis.com/auth/gmail.modify' 
store = file.Storage('storage.json') 
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
    creds = tools.run_flow(flow, store)
GMAIL = discovery.build('gmail', 'v1', http=creds.authorize(Http()))


#for considering past 1 month transactions only
date_today = datetime.date.today()
#print(str(date_today))  #to print todays date


#to calculate expenses
tot_expenses=0.0
mssg_list=[]

try:

	user_id =  'me'
	label_id_one = 'INBOX'

	# labelIds can be changed accordingly
	response = GMAIL.users().messages().list(userId='me',labelIds=[label_id_one]).execute()

	if 'messages' in response:
		# We get a dictonary. Now reading values for the key 'messages'
		mssg_list.extend(response['messages'])

	while 'nextPageToken' in response:
	    page_token = response['nextPageToken']
	    response = GMAIL.users().messages().list(userId='me', labelIds=[label_id_one], pageToken=page_token).execute()
	    #to restrict from parsing through a large number of emails
	    if len(mssg_list) > 200 :
	    	break
	    mssg_list.extend(response['messages'])
except:
    pass

#print ("Total messages in inbox: ", str(len(mssg_list)))

final_list = [ ]


for mssg in mssg_list:
	temp_dict = { }
	m_id = mssg['id'] # get id of individual message
	message = GMAIL.users().messages().get(userId=user_id, id=m_id).execute() # fetch the message using API
	payld = message['payload'] # get payload of the message 
	headr = payld['headers'] # get header of the payload


	for one in headr: # getting the Subject
		if one['name'] == 'Subject':
			msg_subject = one['value']
			temp_dict['Subject'] = msg_subject
		else:
			pass


	for two in headr: # getting the date
		if two['name'] == 'Date':
			msg_date = two['value']
			date_parse = (parser.parse(msg_date))
			m_date = (date_parse.date())
			temp_dict['Date'] = str(m_date)
		else:
			pass

	for three in headr: # getting the Sender
		if three['name'] == 'From':
			msg_from = three['value']
			temp_dict['Sender'] = msg_from
		else:
			pass

	temp_dict['Snippet'] = message['snippet'] # fetching message snippet


	try:
		
		# Fetching message body
		mssg_parts = payld['parts'] # fetching the message parts
		part_one  = mssg_parts[0] # fetching first element of the part 
		part_body = part_one['body'] # fetching body of the message
		part_data = part_body['data'] # fetching data from the body
		clean_one = part_data.replace("-","+") # decoding from Base64 to UTF-8
		clean_one = clean_one.replace("_","/") # decoding from Base64 to UTF-8
		clean_two = base64.b64decode (bytes(clean_one, 'UTF-8')) # decoding from Base64 to UTF-8
		soup = BeautifulSoup(clean_two , "lxml" )
		mssg_body = soup.body()
		# mssg_body is a readible form of message body
		# depending on the end user's requirements, it can be further cleaned 
		# using regex, beautiful soup, or any other method
		temp_dict['Message_body'] = mssg_body

	except :
		pass

	#to print each dictionary object
	#print (temp_dict)
	#gets mails from past 100 days only

	
	if (temp_dict['Sender']=="donotreply.sbiatm@sbi.co.in" and ((date_today-(parser.parse(temp_dict['Date']).date())).days<100) and ("purchase worth" in temp_dict['Snippet']) and ("using your" in temp_dict['Snippet'])):
		regex_amt = re.findall(r'Rs\d+\.\d{0,2}' ,temp_dict['Snippet'])
		curr_ex = re.findall(r'\d+\.\d{0,2}' ,str(regex_amt))
		tot_expenses = tot_expenses + float(curr_ex[0])
		temp_dict['Amount'] = float(curr_ex[0])
		final_list.append(temp_dict) # This will create a dictonary item in the final list
	

	



print ("Total messaged retrived: ", str(len(final_list)))

print ("Total expenses in the past 100 days: ", tot_expenses)

'''
The final_list will have dictionary in the following format:
{	'Sender': '"email.com" <name@email.com>', 
	'Subject': 'Lorem ipsum dolor sit ametLorem ipsum dolor sit amet', 
	'Date': 'yyyy-mm-dd', 
	'Snippet': 'Lorem ipsum dolor sit amet'
	'Message_body': 'Lorem ipsum dolor sit amet'}
The dictionary can be exported as a .csv or into a databse
'''

#exporting the values as .csv
with open('CSV_NAME.csv', 'w', encoding='utf-8', newline = '') as csvfile: 
    fieldnames = ['Sender','Subject','Date','Snippet','Message_body','Amount']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter = ',')
    writer.writeheader()
    for val in final_list:
    	writer.writerow(val)