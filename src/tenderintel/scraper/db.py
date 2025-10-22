from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase client only if credentials are available
supabase = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Supabase client initialized")
    except Exception as e:
        print(f"⚠️ Failed to initialize Supabase client: {e}")
else:
    print("⚠️ Supabase credentials not found in .env - database features disabled")

def insert_tender_record(tender_id, s3_url):
    """Insert tender record to Supabase (optional - requires .env configuration)"""
    if not supabase:
        print("⚠️ Supabase not configured - skipping database insert")
        return None
        
    data = {
        "tender_id": tender_id,
        "s3_url": s3_url
    }

    try:
        response = supabase.table("tenders").insert(data).execute()
        print("✅ Inserted:", response.data)
        return response.data
    except Exception as e:
        print("❌ Error inserting data:", e)
        return None
