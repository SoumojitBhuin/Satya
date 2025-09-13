from supabase import create_client, Client
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
GOV_OFFICIALS = ["soumojitbhuin2004@gmail.com"]

# Variable to track last sent timestamp
last_sent_timestamp = None


def fetch_reports(last_ts):
    """Fetch next 10 scam reports after last sent timestamp"""
    query = supabase.table("scam_reports").select("*").order("timestamp", desc=False)

    if last_ts:
        query = query.gt("timestamp", last_ts)

    response = query.limit(1).execute()
    return response.data


def send_email(reports):
    """Send scam reports to officials via email"""
    subject = f"Scam Reports - Batch of {len(reports)}"
    body = "Here are the scam reports:\n\n"

    for r in reports:
        body += (
            f"ID: {r['id']}\n"
            f"Type: {r['scam_type']}\n"
            f"Platform: {r['platform']}\n"
            f"URL: {r['content_url']}\n"
            f"Description: {r['description']}\n"
            f"Additional Info: {r['additional_info']}\n"
            f"Contact: {r['contact_email']}\n"
            f"Timestamp: {r['timestamp']}\n"
            f"Status: {r['status']}\n"
            "--------------------------------------\n"
        )

    msg = MIMEMultipart()
    msg["From"] = EMAIL_USER
    msg["To"] = ", ".join(GOV_OFFICIALS)
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP("smtp.zoho.com", 587) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.sendmail(EMAIL_USER, GOV_OFFICIALS, msg.as_string())


    print("✅ Email sent successfully!")


def main():
    global last_sent_timestamp

    reports = fetch_reports(last_sent_timestamp)
    if reports:
        send_email(reports)
        # Update in-memory variable
        last_sent_timestamp = reports[-1]["timestamp"]
        print(f"📌 Updated last_sent_timestamp = {last_sent_timestamp}")
    else:
        print("No new reports found.")


if __name__ == "__main__":
    for _ in range(3):  # simulate multiple runs
        main()
