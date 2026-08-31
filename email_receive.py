import imaplib
from email import policy
from email.parser import BytesParser, BytesHeaderParser
from auth import get_credentials
from datetime import date, timedelta
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
from platformdirs import user_documents_dir
from pathlib import Path
import typer
from dotenv import load_dotenv
import os

load_dotenv()

app = typer.Typer()
HOST = {"Gmail": "imap.gmail.com",
        "Outlook": "outlook.office365.com"}
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
SCOPES = ['openid', 'https://mail.google.com/', 'https://www.googleapis.com/auth/userinfo.email']
DOC_DIR = Path(user_documents_dir("CLIMAIL"))

@app.callback()
def connect(ctx: typer.Context):
    account, secret, provider, auth_method = get_credentials()
    provider = HOST[provider]
    if auth_method == "Oauth":
        credentials = Credentials(token=None, refresh_token=secret, token_uri="https://oauth2.googleapis.com/token", client_id=CLIENT_ID, client_secret=CLIENT_SECRET, scopes=SCOPES)
        try:
            credentials.refresh(Request())
            token = credentials.token
        except RefreshError:
            raise Exception("Get a new refresh token by running acc get_token")

        auth_string = f"user={account}\1auth=Bearer {token}\1\1" 
        mail = imaplib.IMAP4_SSL("imap.gmail.com") #only support oauth for gmail 
        mail.authenticate('XOAUTH2', lambda _ : auth_string.encode('utf-8'))
        mail.select("Inbox")
    elif auth_method == "Password":
        mail = imaplib.IMAP4_SSL(provider)
        mail.login(account, secret)
        mail.select('Inbox')

    ctx.ensure_object(dict)
    ctx.obj["mailbox"] = mail

@app.command("check")
def search_mail(ctx: typer.Context, criterion: str ="UNSEEN", since: int = 30):
    """
    Find all (unseen) emails in the last 30 days
    """
    mail = ctx.obj["mailbox"]
    temporary = date.today() - timedelta(days=since)
    new = temporary.strftime("%d-%b-%Y")
    status, messages = mail.uid("search", None, criterion, "SINCE", new)
    if status == "NO":
        typer.echo("Search Failed")
        raise typer.Exit()
    elif not messages[0]:
        typer.echo("No new email")
        raise typer.Exit()
    else:
        messages_ids = messages[0].split()
        for temp in messages_ids:
            status, data = mail.uid("fetch", temp, "(BODY.PEEK[HEADER.FIELDS (SUBJECT FROM)])")

            if status == "OK":
                msg = BytesHeaderParser(policy=policy.default).parsebytes(data[0][1])
                typer.echo(f"UID: {temp.decode()} | From: {msg["From"]}")
                typer.echo(f"Subject: {msg["Subject"]}")

@app.command("read")
def print_emails(ctx: typer.Context):
    """
    Read a selected email based on the inputted UID
    """
    mail = ctx.obj["mailbox"]
    ID = typer.prompt("Input UID")
    if not ID.isdigit():
        raise typer.BadParameter("Input numbers only")
    status, data = mail.uid("fetch", ID, "(RFC822)")
    if status != "OK" or not data or data[0] == None:
        typer.echo("Fetch failed")
        raise typer.Exit()
    msg = BytesParser(policy=policy.default).parsebytes(data[0][1])
    typer.echo(f"From: {msg["From"]}")
    typer.echo(f"Date: {msg["Date"]}")
    typer.echo(f"Subject: {msg["Subject"]}")
    body = None
    attachment = []
    for part in msg.walk():
        if part.is_multipart():
            continue
  
        content_type = part.get_content_type()
        disposition = part.get_content_disposition()
        if content_type == "text/plain" and disposition != "attachment":
            body = part.get_content()
            typer.echo(body)
        elif disposition == "attachment":
            filename = part.get_filename()
            confirm = typer.confirm(f"Attachment named {filename} type {content_type} found, do you want to download it? (not recommended)", default=False)
            if confirm:
                content = part.get_payload(decode=True)
                attachment.append({"filename": filename, "content": content})

    if len(attachment) != 0:
        typer.echo("Downloading...")
        for item in attachment:
            DOC_DIR.mkdir(parents=True, exist_ok=True)
            file1 = DOC_DIR / item["filename"]
            if check_file_name(file1):
                temp = typer.confirm(f"File {item["filename"]} found, continuing will overwrite it")
                if temp:
                    with open(file1, "wb") as f:
                        f.write(item["content"])
                else: 
                    typer.echo(f"Download operation for {item["filename"]} cancelled")
                    continue
            else:
                with open(file1, "wb") as f:
                    f.write(item["content"])

def check_file_name(file: Path):
    if file.exists():
        return True
    else:
        return False

@app.command("seen")
def mark_seen(ctx: typer.Context, since: int = 30):
    """
    Mark every unseen emails in the 30 day period as seen
    """
    mail = ctx.obj["mailbox"]
    temporary = date.today() - timedelta(days=since)
    new = temporary.strftime("%d-%b-%Y")
    _, messages = mail.search(None, "UNSEEN", "SINCE", new)
    messages_ids = messages[0].split()
    
    if not messages_ids:
        typer.echo("No new unseen mail")
        return
    id_sequence = b",".join(messages_ids)
    mail.store(id_sequence, "+FLAGS.SILENT", "\\Seen")
    typer.echo("Marked all unseen emails seen")