from supabase import create_client, Client
from config import settings


supabase: Client = create_client(settings.DATABASE_URL, settings.SUPABASE_KEY)

