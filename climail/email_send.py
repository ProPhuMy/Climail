import typer
from .auth import get_credentials
import smtplib
from email.message import EmailMessage
from typing import Annotated
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
from google.auth.credentials import TokenState
from platformdirs import user_cache_path
from dotenv import load_dotenv
import os
import re
import json
from .cache import store_data
from datetime import datetime

load_dotenv()

app = typer.Typer()
HOST = {"Gmail": "smtp.gmail.com",
        "Outlook": "smtp-mail.outlook.com"}
PORT = 587
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
SCOPES = ['openid', 'https://mail.google.com/', 'https://www.googleapis.com/auth/userinfo.email']
CACHE_PATH = user_cache_path() / "CLIMAIL"
CACHE_FILE = CACHE_PATH / "token_cache.json"

def add_token(token: str, email:str):
    with open(CACHE_FILE, "r") as f:
        data = json.load(f)
        data[email] = token
    with open(CACHE_FILE, "w", encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    
def get_token(email: str):
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, "r") as f:
                data = json.load(f)
            token = data[email]
            return token
        except:
            pass
    return None

@app.callback()
def connect(ctx: typer.Context):
    account, secret, provider, method = get_credentials()
    provider = HOST[provider]
    server = smtplib.SMTP(provider, PORT)
    server.starttls()
    server.ehlo()
    if method == "Oauth":
        token = get_token(account)
        credentials = Credentials(token=token, refresh_token=secret, token_uri="https://oauth2.googleapis.com/token", client_id=CLIENT_ID, client_secret=CLIENT_SECRET, scopes=SCOPES)
        if not credentials.token:
            CACHE_PATH.mkdir(parents=True, exist_ok=True)
            try:
                credentials.refresh(Request())
                token = credentials.token
                if CACHE_FILE.exists():
                    with open(CACHE_FILE, "r") as f:
                        data = json.load(f)
                else:
                    data = {}
                data[account] = token
                with open(CACHE_FILE, "w", encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
            except RefreshError:
                raise Exception("Get a new refresh token by running acc get_token")
        elif credentials.token_state != TokenState.FRESH:
            try:
                credentials.refresh(Request())
                token = credentials.token
                add_token(token, account)
            except RefreshError:
                raise Exception("Get a new refresh token by running acc get_token")

        auth_string = f"user={account}\1auth=Bearer {token}\1\1" 

        server.auth('XOAUTH2', lambda: auth_string)
    elif method == "Password":
        server.login(account, secret)
    

    ctx.ensure_object(dict)
    ctx.obj["server"] = server
    ctx.obj["email"] = account

@app.command("send_email")
def send(ctx: typer.Context, receiver: Annotated[str, typer.Option(help="Input your recipient email")] = ""):
    if not receiver:
        receiver = typer.prompt("Enter recipient email")
    if not check_valid_email_format(receiver):
        typer.echo("Not a valid email format")
        typer.Exit()
    server = ctx.obj["server"]
    msg = EmailMessage()
    msg["to"] = receiver
    msg["from"] = ctx.obj["email"]
    msg["subject"] = typer.prompt("Subject")
    body = typer.prompt("Body\n")
    msg.set_content(body)

    typer.echo("Sending...")
    try:
        server.send_message(msg)
        typer.echo("Email accepted by the SMTP server")
        time = datetime.today().strftime("%H:%M | %d-%b-%Y")
        store_data(time, msg["to"], msg["from"], msg["subject"], body)
    except smtplib.SMTPException as e:
        typer.echo(f"Error sending email. {e}")
    finally:
        server.quit()

def check_valid_email_format(email : str):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return True if re.match(pattern, email) else False

    
