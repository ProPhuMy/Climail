# CLIMAIL

A command-line email client for managing multiple email accounts with support for Gmail and Outlook. Send and receive emails with OAuth2 or app password authentication, and maintain a local cache of all sent emails.

## Features

- Multi-account support for Gmail and Outlook
- OAuth2 authentication for Gmail or app password for both providers
- Send emails with subject, body, and recipient validation
- Receive emails with unseen message filtering and full content reading
- Local SQLite database for email history tracking
- Automatic token caching and refresh for OAuth
- Attachment download support from received emails

## Requirements

- Python 3.10+
- Gmail or Outlook account
- Google OAuth credentials (for Gmail OAuth) OR app passwords (for Gmail/Outlook)

## Installation

### 1. Clone and Setup Environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install Dependencies

```powershell
pip install -r requirements.txt
```

Or manually install:
```powershell
pip install typer keyring python-dotenv platformdirs google-auth google-auth-oauthlib requests rich
```

### 3. Configure OAuth (Optional - for Gmail OAuth)

Create a `.env` file in the project root:

```dotenv
CLIENT_ID=your_google_oauth_client_id
CLIENT_SECRET=your_google_oauth_client_secret
```

Important: Add `.env` to `.gitignore` and never commit credentials.

## Quick Start

### Add Your First Email Account

```powershell
python -m climail.main acc add
```

You'll be prompted to:
1. Choose authentication method: **OAuth** (Gmail) or **App Password** (Gmail/Outlook)
2. Select email provider: **Gmail** or **Outlook**
3. Enter credentials

### Send an Email

```powershell
python -m climail.main send send-email
```

Or with recipient specified:
```powershell
python -m climail.main send send-email --receiver recipient@example.com
```

### Check Unseen Emails

```powershell
python -m climail.main receive check
```

### Read an Email

```powershell
python -m climail.main receive read --id 12345
```

## CLI Reference

### Account Management (`acc`)

| Command | Description |
|---------|-------------|
| `acc add` | Add a new email account |
| `acc switch-account` | Switch between saved accounts |
| `acc default` | Show current active account |
| `acc get-token` | Refresh OAuth token for Gmail |

**Example:**
```powershell
python -m climail.main acc add
```

### Email Receiving (`receive`)

| Command | Options | Description |
|---------|---------|-------------|
| `receive check` | `--since N` | Check unseen emails (last N days, default: 1) |
| `receive read` | `--id UID` | Read full email by UID |
| `receive seen` | `--since N` | Mark unseen emails as read |

**Examples:**
```powershell
# Check emails from last 7 days
python -m climail.main receive check --since 7

# Read email with specific UID
python -m climail.main receive read --id 12345

# Mark emails as seen from last 3 days
python -m climail.main receive seen --since 3
```

### Email Sending (`send`)

| Command | Options | Description |
|---------|---------|-------------|
| `send send-email` | `--receiver EMAIL` | Compose and send email |

**Examples:**
```powershell
# Send email with interactive prompts
python -m climail.main send send-email

# Send email with recipient specified
python -m climail.main send send-email --receiver user@example.com
```

Sent emails are automatically stored in local database.

### Email Storage (`store`)

| Command | Options | Description |
|---------|---------|-------------|
| `store subject` | — | List subjects of all sent emails |
| `store read` | — | Read a sent email from history |
| `store delete-row` | `--something` | Delete a sent email record (or `--something` to delete all) |

**Examples:**
```powershell
# View all sent email subjects
python -m climail.main store subject

# Read sent email from history
python -m climail.main store read

# Delete a sent email record
python -m climail.main store delete-row

# Delete all sent email records
python -m climail.main store delete-row --something
```

## Authentication Methods

### Gmail OAuth2

Best for Gmail users. Provides secure access without storing passwords.

**Setup:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create project and enable Gmail API
3. Create OAuth 2.0 credentials (Desktop Application)
4. Add `CLIENT_ID` and `CLIENT_SECRET` to `.env`

**Pros:** Secure, no password stored, auto-refresh tokens  
**Cons:** Requires initial setup

### App Passwords

Works for Gmail and Outlook. Simpler setup, suitable for both providers.

**Gmail:**
1. Enable [2-Step Verification](https://support.google.com/accounts/answer/185839)
2. Generate [App Password](https://support.google.com/accounts/answer/185833)

**Outlook:**
1. Create [App Password](https://support.microsoft.com/account-billing/using-app-passwords-with-your-microsoft-account)

**Pros:** Simple setup, works with Outlook  
**Cons:** Must manage password security

## Project Structure

```
climail/
├── main.py              # CLI entry point
├── auth.py              # Account management & OAuth
├── email_send.py        # SMTP email sending
├── email_receive.py     # IMAP email receiving
├── cache.py             # SQLite email history storage
└── __init__.py

.env                      # Credentials (DO NOT COMMIT)
pyproject.toml           # Project metadata
README.md                # This file
```

## Storage Locations

- **Credentials**: System keyring (secure)
- **OAuth Tokens**: `~/.cache/CLIMAIL/token_cache.json`
- **Email History**: `~/.config/CLIMAIL/climail.db` (SQLite)
- **Downloaded Attachments**: `~/Documents/CLIMAIL/`

## Troubleshooting

### "Get a new refresh token by running acc get-token"
OAuth token expired. Refresh it:
```powershell
python -m climail.main acc get-token
```

### "Credentials file not found"
No accounts added yet. Add your first account:
```powershell
python -m climail.main acc add
```

### "Password/token not found"
Keyring entry corrupted. Remove and re-add the account:
```powershell
python -m climail.main acc add
```

### IMAP/SMTP Connection Errors
- Verify correct authentication method for your provider
- Gmail: Use app password or OAuth (not regular password)
- Outlook: Must use app password
- Check provider's email security settings

### Attachment Download Issues
- Confirm file path is writable (`~/Documents/CLIMAIL/`)
- Try declining overwrite if file already exists
- Check disk space

## Security Best Practices

1. **Never commit `.env`** - Add to `.gitignore`
2. **Secure keyring**: Passwords stored in OS keyring, not files
3. **Token caching**: Only cached for performance; refresh on use
4. **HTTPS only**: All connections use secure protocols
5. **Local database**: Email history stored locally only

## License

See LICENSE file for details
- `credentials.json` 
- real passwords
- app passwords
- refresh tokens

Use the operating system keyring for stored secrets and keep local config values on your machine only.

## License

This project is released into the public domain under the Unlicense. See [LICENSE](LICENSE).
