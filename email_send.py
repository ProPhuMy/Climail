import typer
from auth import get_credentials
import smtplib
from email.message import EmailMessage
from typing import Annotated
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
from dotenv import load_dotenv
import os

load_dotenv()

app = typer.Typer()
HOST = {"Gmail": "smtp.gmail.com",
        "Outlook": "smtp-mail.outlook.com"}
PORT = 587
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
SCOPES = ['openid', 'https://mail.google.com/', 'https://www.googleapis.com/auth/userinfo.email']

@app.callback()
def connect(ctx: typer.Context):
    account, secret, provider, method = get_credentials()
    provider = HOST[provider]
    server = smtplib.SMTP(provider, PORT)
    server.starttls()
    server.ehlo()
    if method == "Oauth":
        credentials = Credentials(token=None, refresh_token=secret, token_uri="https://oauth2.googleapis.com/token", client_id=CLIENT_ID, client_secret=CLIENT_SECRET, scopes=SCOPES)
        try:
            credentials.refresh(Request())
            token = credentials.token
        except RefreshError:
            raise Exception("Get a new refresh token by running acc get_token")
    
        auth_string = f"user={account}\1auth=Bearer {token}\1\1" 

        server.auth('XOAUTH2', lambda _ : auth_string)
    elif method == "Password":
        server.login(account, secret)
    

    ctx.ensure_object(dict)
    ctx.obj["server"] = server
    ctx.obj["email"] = account

@app.command()
def send(ctx: typer.Context, receiver: Annotated[str, typer.Option(help="Input your recipient email")] = ""):
    if not receiver:
        receiver = typer.prompt("Enter recipient email")
    server = ctx.obj["server"]
    msg = EmailMessage()
    msg["to"] = receiver
    msg["from"] = ctx.obj["email"]
    msg["subject"] = typer.prompt("Subject")
    msg.set_content(typer.prompt("Body"))

    typer.echo("Sending...")
    try:
        server.send_message(msg)
        typer.echo("Email sent")
    finally:
        server.quit()
        
    