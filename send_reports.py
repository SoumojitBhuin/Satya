import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from supabase import create_client, Client

# --- Supabase and Email Configuration ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
# Ensure GOV_OFFICIALS is a comma-separated string in your environment variables
GOV_OFFICIALS_STRING = os.getenv("GOV_OFFICIALS_EMAILS", "")
GOV_OFFICIALS = [email.strip() for email in GOV_OFFICIALS_STRING.split(',') if email.strip()]

supabase: Client = None
try:
    if SUPABASE_URL and SUPABASE_KEY:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    else:
        print("Warning: Supabase URL or Key not provided. Email digest feature will be disabled.")
except Exception as e:
    print(f"Error initializing Supabase client in email_utils: {e}")

def get_last_sent_timestamp():
    """Fetches the last sent timestamp from Supabase."""
    if not supabase: return None
    try:
        response = supabase.table("job_metadata").select("value").eq("key", "last_sent_timestamp").execute()
        if response.data:
            return response.data[0]['value']
        return None
    except Exception as e:
        print(f"Error fetching last sent timestamp: {e}")
        return None

def update_last_sent_timestamp(new_ts):
    """Updates the last sent timestamp in Supabase."""
    if not supabase: return
    try:
        supabase.table("job_metadata").upsert({
            "key": "last_sent_timestamp",
            "value": new_ts
        }).execute()
        print(f"📌 Updated last_sent_timestamp in DB to {new_ts}")
    except Exception as e:
        print(f"Error updating last sent timestamp: {e}")

def fetch_and_send_reports():
    """
    Fetches new scam reports from Supabase, sends them via email,
    and updates the last sent timestamp.
    Returns a tuple of (success_boolean, message_string).
    """
    if not supabase:
        return False, "Supabase client not initialized"
        
    if not GOV_OFFICIALS:
        print("No government official emails configured. Skipping email send.")
        return True, "No recipients configured"

    last_ts = get_last_sent_timestamp()
    
    # Fetch reports from Supabase
    query = supabase.table("scam_reports").select("*").order("timestamp", desc=False)
    if last_ts:
        query = query.gt("timestamp", last_ts)
    response = query.limit(10).execute()
    reports = response.data

    if not reports:
        print("No new reports found.")
        return True, "No new reports to send"

    # Prepare and send email
    subject = f"Scam Reports Digest - {datetime.now().strftime('%Y-%m-%d')}"
    body = "Here is a batch of the latest scam reports:\n\n"
    for r in reports:
        body += (
            f"ID: {r.get('id', 'N/A')}\n"
            f"Type: {r.get('scam_type', 'N/A')}\n"
            f"Platform: {r.get('platform', 'N/A')}\n"
            f"URL: {r.get('content_url', 'N/A')}\n"
            f"Description: {r.get('description', 'N/A')}\n"
            f"Timestamp: {r.get('timestamp', 'N/A')}\n"
            "--------------------------------------\n\n"
        )
    
    msg = MIMEMultipart()
    msg["From"] = EMAIL_USER
    msg["To"] = ", ".join(GOV_OFFICIALS)
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))
    
    with smtplib.SMTP("smtp.zoho.in", 587) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.sendmail(EMAIL_USER, GOV_OFFICIALS, msg.as_string())
    
    print(f"✅ Email sent successfully to {len(GOV_OFFICIALS)} recipient(s)!")
    
    # Update the timestamp with the timestamp of the very last report sent
    new_last_timestamp = reports[-1]["timestamp"]
    update_last_sent_timestamp(new_last_timestamp)
    
    return True, f"Email sent successfully. Reports sent: {len(reports)}"
