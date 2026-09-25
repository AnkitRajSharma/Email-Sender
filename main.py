import os
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Scope needed to send emails via Gmail API
SCOPES = ['https://www.googleapis.com/auth/gmail.send']
SUBJECT = "HTML Email via Gmail API"

def get_gmail_service():
    """Authenticates the user and returns the Gmail service object."""
    creds = None
    # token.json stores the user's access and refresh tokens
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
    # If no valid credentials available, ask the user to log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            
        # Save the credentials for future runs
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)

def get_receivers(filename):
    """Reads recipient emails from text file."""
    with open(filename, "r") as file:
        return [line.strip() for line in file if line.strip()]

def create_message(to, subject, html_body):
    """Creates a base64 encoded MIME message required by the Gmail API."""
    message = MIMEMultipart()
    message['to'] = to
    message['subject'] = subject
    
    msg_html = MIMEText(html_body, 'html')
    message.attach(msg_html)
    
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    return {'raw': raw_message}

def main():
    receivers = get_receivers("receivers.txt")
    if not receivers:
        print("No emails found in receivers.txt")
        return

    # Initialize Gmail API service
    service = get_gmail_service()

    html_content = """
    <html>
      <body style="font-family: Arial, sans-serif;">
        <h2 style="color: #4285F4;">Sent via Google API</h2>
        <p>This message was authenticated and delivered through the <b>Gmail API</b>.</p>
        <p>Learn more about <a href="https://developers.google.com/gmail/api">Gmail API Documentation</a>.</p>
      </body>
    </html>
    """

    print(f"Sending emails to {len(receivers)} recipients...")

    for email_addr in receivers:
        try:
            message_body = create_message(email_addr, SUBJECT, html_content)
            sent_message = service.users().messages().send(userId="me", body=message_body).execute()
            print(f"✅ Sent to {email_addr} (Message ID: {sent_message['id']})")
        except Exception as e:
            print(f"❌ Failed sending to {email_addr}: {e}")

if __name__ == "__main__":
    main()