import keyring
import json
import typer
from pathlib import Path
from platformdirs import user_config_dir
from google_auth_oauthlib.flow import InstalledAppFlow
import requests
from dotenv import load_dotenv
import os

load_dotenv()

CLIENT_SECRET = os.getenv('CLIENT_SECRET')
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_CONFIG = {"installed":{"client_id": CLIENT_ID,"project_id":"climail-and-stuff","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_secret": CLIENT_SECRET,"redirect_uris":["http://localhost"]}}
SCOPES = ['openid', 'https://mail.google.com/', 'https://www.googleapis.com/auth/userinfo.email']
PRJ_DIR = Path(user_config_dir("CLIMAIL"))
CREDENTIALS_FILE = PRJ_DIR / "credentials.json"
APP = "CLIMAIL"
app = typer.Typer()
providers = {1: "Gmail", 2: "Outlook"}

def oauth():
    flow = InstalledAppFlow.from_client_config(CLIENT_CONFIG, scopes=SCOPES)
    flow.run_local_server(host='localhost', open_browser=True, success_message="Authorization completed, you may close this window")
    credentials = flow.credentials
    response = requests.get(
        "https://openidconnect.googleapis.com/v1/userinfo", headers={
            "Authorization": f"Bearer {credentials.token}"
        }
    )
    user_info = response.json()
    email = user_info["email"]
    return credentials.refresh_token, email

@app.command("add")
def add_accounts():
    """
    Add an email account
    """
    typer.echo("1. Oauth (if you don't want to use app password)")
    typer.echo("2. App password")
    auth = typer.prompt("Choose your authentication method (1 or 2)", type=int)
    
    if auth != 1 and auth != 2:
        raise typer.BadParameter("Choose 1 or 2")
    
    if auth == 1:
        secret, email = oauth()
        method = "Oauth"
    else:
        email = typer.prompt("Enter email") 
        secret = typer.prompt("Enter password", hide_input= True)
        method = "Password"
    
    typer.echo("1. Gmail")
    typer.echo("2. Outlook")

    choice = typer.prompt("Choose your provider (1 or 2)", type=int)
    if choice != 1 and choice != 2:
        raise typer.BadParameter("Choose 1 or 2")
    PROVIDER = providers[choice]

    PRJ_DIR.mkdir(parents=True, exist_ok=True)

    if CREDENTIALS_FILE.exists():
        with open(CREDENTIALS_FILE, "r") as f:
            data = json.load(f)
    else:
        data = {
                "Active account": None,
                "Accounts": {
                }
             }

    data["Active account"] = email
    data["Accounts"][email] = {"provider": 
                               PROVIDER,
                               "auth": method}
    with open(CREDENTIALS_FILE, "w", encoding="utf-8") as f:
        json.dump(data,f, indent=2)
    keyring.set_password(APP, email, secret)

def get_credentials():
    if CREDENTIALS_FILE.exists():
        with open(CREDENTIALS_FILE, "r") as f:
            data = json.load(f)
        email = data["Active account"]
        provider = data["Accounts"][email]["provider"]
        auth_method = data["Accounts"][email]["auth"]
        secret = keyring.get_password(APP, email)
        if secret is None:
            typer.echo("Password/token not found")
            raise typer.Exit()
        
        return email, secret, provider, auth_method
    else:
        typer.echo("Add an account to continue")
        raise typer.Exit()

@app.command()
def switch_account():
    """
    Switch default account
    """
    if CREDENTIALS_FILE.exists():
        with open(CREDENTIALS_FILE, "r") as f:
            data = json.load(f)
        temp_list = list(data["Accounts"].keys())
        for i in range(len(temp_list)):
            print(f"{i + 1}. {temp_list[i]}")
        num = typer.prompt("Choose default email", type=int)
        if num >= 1 and num <= len(temp_list):
            data["Active account"] = temp_list[num - 1]
        else:
            raise typer.BadParameter("Only input the numbers shown")

        with open(CREDENTIALS_FILE, "w", encoding="utf-8") as f:
            json.dump(data,f, indent=2)
    else:
        raise FileNotFoundError("Credentials file not found")
    
@app.command()
def get_token():
    """
    Get new refresh token for your account
    """
    temp, email = oauth()
    if CREDENTIALS_FILE.exists():
        with open(CREDENTIALS_FILE, "r") as f:
            data = json.load(f)
        method = data["Accounts"][email]["auth"]
        if method == "Password":
            typer.prompt("Detected authentication method for this email address is not oauth")
            typer.Abort()
        else:
            keyring.set_password(APP, email, temp)
            typer.echo("New refresh token set")
    else:
        typer.echo("Creds file not found, add a new account")
        

if __name__ == "__main__":
    app()