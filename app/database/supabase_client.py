from supabase import create_client, Client
from app.config import settings

def get_supabase_client() -> Client:
    """Create and return Supabase client"""
    return create_client(settings.supabase_url, settings.supabase_service_key)

supabase_client = get_supabase_client()
