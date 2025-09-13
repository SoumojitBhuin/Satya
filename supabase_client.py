from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase URL and Key must be set. Check your .env file.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def insert_report(report_data: dict):
    try:
        response = supabase.table("scam_reports").insert(report_data).execute()
        return response.data
    except Exception as e:
        print("Error inserting report:", e)
        return None
