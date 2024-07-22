import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import re
import os.path
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from requests import HTTPError
import google.generativeai as genai
from safety_settings import safe

SCOPES = [
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.readonly'
]

# Check if the token.pickle file exists and load it if it does
creds = None
if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)

# If no valid credentials are available, log in and save the credentials to token.pickle
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)

service = build('gmail', 'v1', credentials=creds)

def send_email(command: str, conversation_history) -> str:
    """Send an email using GMail API."""
    mail_model = genai.GenerativeModel('gemini-1.5-flash', 
                                       system_instruction="""I'm Stella, a voice assistant, inspired by Jarvis from Iron Man. 
                                       Your role is to write emails for the user based on their command.
                                       If you don't have enough details to send an email, ask the user for further details.

                                       The output should be in JSON format. Everything is a string, either empty or containing details.
                                       
                                       {
                                           'enough_details': 'true',
                                           'to_address': 'example@gmail.com',
                                           'subject': 'Email Subject',
                                           'body': 'Email Body',
                                           'reply_to_user': 'If you don't have enough data to write an email, ask the user for more details.'
                                       }
                                       Do not return anything else.
                                       """,
                                       generation_config={"response_mime_type": "application/json"})
    
    resp = mail_model.generate_content(contents=[f"user command: {command}, conversation history: {conversation_history}"], safety_settings=safe)
    # resp = re.sub(r"```json|```", "", resp.text)
    resp = json.loads(resp.text)

    enough_details = resp.get("enough_details")
    to_address = resp.get("to_address")
    subject = resp.get("subject")
    body = resp.get("body")
    if enough_details.strip().lower() == 'true':
        msg = MIMEMultipart()
        msg['To'] = to_address
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        create_message = {'raw': base64.urlsafe_b64encode(msg.as_bytes()).decode()}

        try:
            message = (service.users().messages().send(userId="me", body=create_message).execute())
            response = "Email sent successfully."
        except HTTPError as e:
            response = f"Failed to send email. Error: {str(e)}"
    else:
        reply_to_user = resp.get("reply_to_user")
        response = reply_to_user

    return response

def read_emails():
    """Read emails using the Gmail API."""
    print("Reading emails...")
    max_results=10
    try:
        results = service.users().messages().list(userId='me', maxResults=max_results, labelIds=['INBOX']).execute()
        messages = results.get('messages', [])
        
        if not messages:
            return 'No new emails.'

        emails = []
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            msg_snippet = msg['snippet']
            msg_payload = msg.get('payload', {})
            headers = msg_payload.get('headers', [])
            subject = [header['value'] for header in headers if header['name'] == 'Subject']
            from_address = [header['value'] for header in headers if header['name'] == 'From']
            email_info = {
                'snippet': msg_snippet,
                'subject': subject[0] if subject else 'No Subject',
                'from': from_address[0] if from_address else 'No Sender'
            }
            emails.append(email_info)

        return emails

    except Exception as error:
        print(error)
        return f'An error occurred: {error}'
    
if __name__ == "__main__":
    conversation_history = [
        "user command: my name is jain and alive at vizag",
        "response: Right, Jain, I've noted that you're living in Vizag.",
        "user command: My friend's email is manikanta3570@gmail.com",
        "response: Okay, I'll remember that. \n",
    ]
    # print(send_email("write a funny email to my friend's email about an engineer got eaten by his computer", conversation_history))
    print(read_emails())
