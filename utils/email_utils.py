import os
import smtplib
import ssl
import mimetypes
import json
from email.message import EmailMessage


def send_preview_email(to_address, subject, body, attachment_path=None, approval_links=False, product_id=None):
    """Send a preview email with optional image attachment.
    
    Supports both SMTP and a file-based fallback if SMTP is not configured.
    """
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = os.getenv("EMAIL_FROM", "no-reply@styora.local")
    msg["To"] = to_address
    msg.set_content(body)

    if approval_links:
        if product_id:
            yes_link = f"mailto:{to_address}?subject=POST%20YES%20{product_id}&body=Approve%20Instagram%20Post"
            no_link = f"mailto:{to_address}?subject=POST%20NO%20{product_id}&body=Cancel%20Instagram%20Post"
        else:
            yes_link = f"mailto:{to_address}?subject=POST%20YES&body=Approve%20Instagram%20Post"
            no_link = f"mailto:{to_address}?subject=POST%20NO&body=Cancel%20Instagram%20Post"
        html_body = f"""
        <html>
            <body>
                <p>{body.replace(chr(10), '<br>')}</p>
                <p><strong>Approve posting:</strong></p>
                <p><a href=\"{yes_link}\">YES — Post this to Instagram</a></p>
                <p><a href=\"{no_link}\">NO — Do not post</a></p>
                <p>Note: this email shows the exact Instagram caption and link above.</p>
            </body>
        </html>
        """
        msg.add_alternative(html_body, subtype="html")

    if attachment_path and os.path.exists(attachment_path):
        mime_type, _ = mimetypes.guess_type(attachment_path)
        if mime_type is None:
            mime_type = "application/octet-stream"
        maintype, subtype = mime_type.split("/", 1)
        with open(attachment_path, "rb") as f:
            msg.add_attachment(
                f.read(),
                maintype=maintype,
                subtype=subtype,
                filename=os.path.basename(attachment_path),
            )

    host = os.getenv("EMAIL_HOST", "smtp.gmail.com")
    port = int(os.getenv("EMAIL_PORT", "587"))
    username = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASSWORD")
    use_tls = os.getenv("EMAIL_USE_TLS", "true").lower() in ("1", "true", "yes")

    if username and password:
        try:
            server = smtplib.SMTP(host, port, timeout=20)
            if use_tls:
                context = ssl.create_default_context()
                server.starttls(context=context)

            server.login(username, password)
            server.send_message(msg)
            server.quit()
            print(f"✓ Email sent successfully to {to_address}")
            return True
        except Exception as e:
            print(f"✗ SMTP Error: {e}")
    else:
        print("⚠ Email credentials not configured (EMAIL_USER, EMAIL_PASSWORD)")

    try:
        os.makedirs("approvals", exist_ok=True)
        preview_file = os.path.join("approvals", f"preview_{os.getpid()}.json")
        preview_data = {
            "to": to_address,
            "subject": subject,
            "body": body,
            "image": attachment_path,
            "status": "pending_approval",
        }
        if product_id:
            preview_data["product_id"] = product_id
        with open(preview_file, "w", encoding="utf-8") as f:
            json.dump(preview_data, f, indent=2)
        print(f"✓ Preview saved to {preview_file}")
        print(f"   Image: {attachment_path}")
        print(f"   Please review and create a corresponding approval file in 'approvals/' with '_approved' suffix to trigger posting.")
        return True
    except Exception as write_err:
        print(f"✗ Could not save preview file: {write_err}")
        return False


def check_approval_emails(imap_server="imap.gmail.com", username=None, password=None, folder="INBOX"):
    """Check for approval emails and return list of approved product IDs."""
    import imaplib
    import email
    
    if not username:
        username = os.getenv("EMAIL_USER")
    if not password:
        password = os.getenv("EMAIL_PASSWORD")
    
    if not username or not password:
        print("⚠ Email credentials not configured for reading")
        return []
    
    try:
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(username, password)
        mail.select(folder)
        
        status, messages = mail.search(None, 'SUBJECT "POST YES"')
        approvals = []
        
        for msg_id in messages[0].split():
            status, msg_data = mail.fetch(msg_id, '(RFC822)')
            msg = email.message_from_bytes(msg_data[0][1])
            subject = msg['subject']
            
            if 'POST YES' in subject:
                parts = subject.split()
                if len(parts) >= 3:
                    product_id = parts[2]
                    approvals.append(product_id)
        
        mail.logout()
        return approvals
    except Exception as e:
        print(f"✗ Error checking approval emails: {e}")
        return []
