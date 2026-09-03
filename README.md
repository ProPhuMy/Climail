# CLIMAIL

A Linux command-line email client for managing multiple Gmail and Outlook accounts. Send and receive email with app passwords, and use OAuth2 for Gmail account setup and receiving.

## Features

- Multi-account support for Gmail and Outlook
- OAuth2 authentication for Gmail and app passwords for Gmail or Outlook
- Send emails with subject, body, and recipient validation
- Send a file attachment with a MIME type inferred from its filename
- Receive emails with unseen message filtering and full content reading
- Local SQLite database for email history tracking
- Automatic token caching and refresh for OAuth
- Attachment download support from received emails

## Requirements

- Python 3.13+
- Gmail or Outlook account
- Google OAuth credentials (for Gmail OAuth) OR app passwords (for Gmail/Outlook)

## Installation

### 1. Clone and Setup Environment

```bash
python -m venv .venv
source .venv/bin/activate
```

Install the project and its dependencies:

```bash
python -m pip install -r requirements.txt
python -m pip install -e .
```

To install it for use anywhere, use `pipx` instead:

```bash
cd /path/to/project
pipx install .
```

### 2. Install Dependencies

The installation commands above install the dependencies listed in `requirements.txt`.

### 3. Configure OAuth (Optional - for Gmail OAuth)

Create a `.env` file in the project root:

```dotenv
CLIENT_ID=your_google_oauth_client_id
CLIENT_SECRET=your_google_oauth_client_secret
```

Important: Add `.env` to `.gitignore` and never commit credentials.

## Quick Start

### Add Your First Email Account

```bash
climail acc add
```

You'll be prompted to:
1. Choose authentication method: **OAuth** (Gmail) or **App Password** (Gmail/Outlook)
2. Select email provider: **Gmail** or **Outlook**
3. Enter credentials

### Send an Email

```bash
climail send send_email
```

Or with recipient specified:
```bash
climail send send_email --receiver recipient@example.com
```

With an attachment:

```bash
climail send send_email --receiver recipient@example.com --attach ~/Documents/report.pdf
```

### Check Unseen Emails

```bash
climail receive check
```

### Read an Email

```bash
climail receive read --id 12345
```

## CLI Reference

### Account Management (`acc`)

| Command | Description |
|---------|-------------|
| `acc add` | Add a new email account |
| `acc switch` | Switch between saved accounts |
| `acc default` | Show current active account |
| `acc get-token` | Refresh OAuth token for Gmail |

**Example:**
```bash
climail acc add
```

### Email Receiving (`receive`)

| Command | Options | Description |
|---------|---------|-------------|
| `receive check` | `--since N` | Check unseen emails (last N days, default: 1) |
| `receive read` | `--id UID` | Read full email by UID |
| `receive seen` | `--since N` | Mark unseen emails as read |

**Examples:**
```bash
# Check emails from last 7 days
climail receive check --since 7

# Read email with specific UID
climail receive read --id 12345

# Mark emails as seen from last 3 days
climail receive seen --since 3
```

### Email Sending (`send`)

| Command | Options | Description |
|---------|---------|-------------|
| `send send_email` | `--receiver EMAIL`, `--attach PATH` | Compose and send email, optionally with an attachment |

**Examples:**
```bash
# Send email with interactive prompts
climail send send_email

# Send email with recipient specified
climail send send_email --receiver user@example.com
```

Sent emails are automatically stored in local database.

### Email Storage (`store`)

| Command | Options | Description |
|---------|---------|-------------|
| `store subject` | — | List subjects of all sent emails |
| `store read` | — | Read a sent email from history |
| `store delete-row` | `--delete`, `-d` | Delete a sent email record, or delete all records |

**Examples:**
```bash
# View all sent email subjects
climail store subject

# Read sent email from history
climail store read

# Delete a sent email record
climail store delete

# Delete all sent email records
climail store delete --all
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

- **Account metadata**: `~/.config/CLIMAIL/credentials.json`
- **Credentials**: System keyring (secure)
- **OAuth Tokens**: `~/.cache/CLIMAIL/token_cache.json`
- **Email History**: `~/.config/CLIMAIL/climail.db` (SQLite)
- **Downloaded Attachments**: `~/Documents/CLIMAIL/`

## Troubleshooting

### "Get a new refresh token by running acc get-token"
OAuth token expired. Refresh it:
```bash
climail acc get-token
```

### "Credentials file not found"
No accounts added yet. Add your first account:
```bash
climail acc add
```

### "Password/token not found"
Keyring entry corrupted. Remove and re-add the account:
```bash
climail acc add
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

This project is released into the public domain under the Unlicense. See [LICENSE](LICENSE).
