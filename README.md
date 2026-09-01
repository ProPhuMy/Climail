# CLIMAIL

CLIMAIL is a command-line email client written in Python. It supports managing email accounts, receiving emails, and sending messages through Gmail or Outlook. Authentication supports both OAuth (Gmail) and app password methods.

## Project Structure

```
main.py           - Entry point for the CLI application
auth.py           - Account authentication and management (OAuth, app passwords)
email_receive.py  - Email receiving via IMAP protocol
email_send.py     - Email sending via SMTP protocol
cache.py          - Database and caching functionality
test.py           - Test and development utilities
```

## Requirements

- Python 3.10 or newer
- A Gmail or Outlook account
- For Gmail: either a Google OAuth credential set or an app password
- For Outlook: an app password for the account

## Installation

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the required dependencies:

```powershell
python -m pip install typer keyring python-dotenv platformdirs google-auth google-auth-oauthlib requests
```

Set up environment variables by creating a `.env` file in the project root for OAuth (if using Gmail OAuth):

```dotenv
CLIENT_SECRET=your_google_oauth_client_secret
CLIENT_ID=your_google_oauth_client_id
```

**Important:** Keep this file local and never commit it to version control.

## Account Management

### Adding an Account

```powershell
python main.py acc add
```

You will be prompted to:
1. Choose an authentication method:
   - **Option 1**: OAuth (recommended for Gmail)
   - **Option 2**: App password (works for both Gmail and Outlook)
2. Select your email provider:
   - **Gmail** (supports both OAuth and app password)
   - **Outlook** (requires app password)

The application stores account metadata securely in a local credentials file and passwords/tokens in the OS keyring.

## CLI Commands

### Account Management (`acc`)

#### Add an Account
```powershell
python main.py acc add
```
Interactive setup to add a new email account. Choose authentication method (OAuth or app password) and email provider (Gmail or Outlook).

#### Switch Default Account
```powershell
python main.py acc switch-account
```
Switch between multiple saved email accounts. Lists all available accounts and prompts you to select the default.

#### Check Current Default Account
```powershell
python main.py acc default
```
Displays the currently active email account.

#### Get New OAuth Token
```powershell
python main.py acc get-token
```
Obtain a new OAuth refresh token for your Gmail account. Use this if your refresh token expires or needs to be updated.

### Email Receiving (`receive`)

#### Check for Unseen Emails
```powershell
python main.py receive check
```
Search for unseen emails from the last 30 days. Displays email UIDs, sender, and subject line.

**Options:**
- `--since` (integer): Specify the number of days to look back (default: 30)

Example - Check emails from the last 7 days:
```powershell
python main.py receive check --since 7
```

#### Read an Email
```powershell
python main.py receive read
```
Read the full content of an email by its UID. Displays sender, date, subject, and body. Prompts to download any attachments found.

**Options:**
- `--id` (string): Specify the email UID directly (optional, will prompt if not provided)

Example:
```powershell
python main.py receive read --id 12345
```

#### Mark Emails as Seen
```powershell
python main.py receive seen
```
Mark unseen emails from the last 30 days as seen/read.

**Options:**
- `--since` (integer): Specify the number of days to look back (default: 30)

### Email Sending (`send`)

#### Send an Email
```powershell
python main.py send send-email
```
Compose and send an email. Prompts for recipient (if not provided), subject, and body content.

**Options:**
- `--receiver` (string): Specify recipient email address (optional, will prompt if not provided)

Example:
```powershell
python main.py send send-email --receiver recipient@example.com
```

## Authentication Details

- **Gmail with OAuth**: Uses Google's OAuth2 flow with token caching and automatic refresh
- **Gmail/Outlook with App Password**: Direct IMAP/SMTP authentication
- Credentials are stored securely using your system's keyring/password manager
- Tokens are cached locally for faster subsequent authentication

### Setting Up Gmail OAuth

To use OAuth with Gmail:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Gmail API
4. Create an OAuth 2.0 Desktop Application credential
5. Download the client credentials and extract your `CLIENT_ID` and `CLIENT_SECRET`
6. Add these values to your `.env` file

### Setting Up App Passwords

For Gmail:
1. Enable [2-Step Verification](https://support.google.com/accounts/answer/185839) on your Google Account
2. Generate an [App Password](https://support.google.com/accounts/answer/185833)
3. Use this app password when prompted during account setup

For Outlook:
1. Create an [App Password](https://support.microsoft.com/en-us/account-billing/using-app-passwords-with-your-microsoft-account) in your Microsoft Account settings
2. Use this app password when prompted during account setup

## Troubleshooting

**"Get a new refresh token by running acc get-token"**
- Your OAuth refresh token has expired
- Run `python main.py acc get-token` to obtain a new one

**"Credentials file not found"**
- You haven't added any email accounts yet
- Run `python main.py acc add` to add your first account

**"Password/token not found"**
- The password/token stored in your keyring is missing or corrupted
- Try removing and re-adding your account with `python main.py acc add`

**IMAP/SMTP Connection Errors**
- Verify your email provider supports the selected authentication method
- For Gmail: Ensure you're using either an app password or OAuth (not your regular Gmail password)
- For Outlook: Ensure you're using an app password

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
