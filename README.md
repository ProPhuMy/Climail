# CLIMAIL

CLIMAIL is a small command-line email client written in Python. It supports reading mail, managing saved accounts, and sending messages through Gmail or Outlook-style providers.

## Project structure

This project is still small enough to live in the project root without a `src/` folder. A `src/` layout becomes useful when the app grows larger or when imports become harder to manage, but it is not necessary for a CLI tool of this size.

## Requirements

- Python 3.10 or newer
- A Gmail or Outlook account
- A Google OAuth client for OAuth-based login, or an app password if your provider requires one

## Setup

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the dependencies:

```powershell
python -m pip install typer keyring python-dotenv platformdirs google-auth google-auth-oauthlib requests
```

Create a local `.env` file for any OAuth secret values you need:

```dotenv
CLIENT_SECRET=your_google_oauth_client_secret
```

This file should stay local to your machine and should not be committed to source control.

## Add an account

Run:

```powershell
python main.py acc add
```

You will be prompted to choose between OAuth and app-password authentication, then select a provider. CLIMAIL stores the active account metadata in a local credentials file and stores the real secret in the OS keyring.

To switch between saved accounts:

```powershell
python main.py acc switch-account
```

## Commands

Check for unseen messages from the last 30 days:

```powershell
python main.py receive check
```

Use a different search period:

```powershell
python main.py receive check --since 7
```

Read a message by its UID:

```powershell
python main.py receive read
```

Mark unseen messages from the last 30 days as seen:

```powershell
python main.py receive seen
```

Send an email:

```powershell
python main.py send send --receiver recipient@example.com
```

The subject and body are entered interactively. Omitting `--receiver` prompts for the recipient.

## Provider notes

Gmail and Outlook may block basic password authentication depending on account settings. OAuth is the preferred approach for Gmail, while app-password or provider-specific configurations may still be required for other mail providers.

## Security

Never commit:

- `.env`
- `credentials.json`
- real passwords
- app passwords
- refresh tokens

Use the operating system keyring for stored secrets and keep local config values on your machine only.

## License

This project is released into the public domain under the Unlicense. See [LICENSE](LICENSE).
