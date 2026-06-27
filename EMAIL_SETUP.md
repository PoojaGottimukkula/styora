# Email Configuration for Styora

## Option 1: Gmail SMTP (Recommended)

To enable email sending via Gmail:

### Step 1: Create a Gmail App Password

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable 2-Step Verification if not already done
3. Go to [App Passwords](https://myaccount.google.com/apppasswords)
4. Select "Mail" and "macOS" (or your device)
5. Generate a new app password (16 characters)
6. Copy the app password

### Step 2: Set Environment Variables

Add these to your shell profile (`.zshrc`, `.bashrc`, etc.) or set them before running:

```bash
export EMAIL_USER="your-email@example.com"
export EMAIL_PASSWORD="your-16-char-app-password"
export EMAIL_HOST="smtp.gmail.com"
export EMAIL_PORT="587"
export EMAIL_USE_TLS="true"
export PREVIEW_EMAIL="reviewer@example.com"
```

### Step 3: Run the Script

```bash
source ~/.zshrc  # Or .bashrc
/Users/pooja/Documents/styora/venv/bin/python /Users/pooja/Documents/styora/main.py
```

## Option 2: File-Based Approvals (Default)

If you don't set EMAIL credentials, the script will save previews as JSON files in the `approvals/` folder:

- Each preview will be saved with product details and image path
- Manually review each preview
- Create a corresponding `_approved` file to trigger Instagram posting

Example:
```
approvals/preview_12345.json       ← Preview details
approvals/preview_12345_approved   ← Create this empty file to approve
```

## Supported Email Providers

The script defaults to Gmail SMTP, but you can configure any provider:

- **Gmail**: `smtp.gmail.com:587` (TLS required)
- **Outlook**: `smtp-mail.outlook.com:587` (TLS required)
- **SendGrid**: `smtp.sendgrid.net:587` (API key as password)
- **Local SMTP**: `localhost:25` (if running a local mail server)

Set custom provider via environment variables before running.

## Troubleshooting

- **"Connection refused"**: No SMTP server is configured or running
- **"Login failed"**: Check EMAIL_USER and EMAIL_PASSWORD are correct
- **"TLS not supported"**: Try port 465 with `EMAIL_USE_TLS=true`

For Gmail, always use App Passwords (not your regular password).
