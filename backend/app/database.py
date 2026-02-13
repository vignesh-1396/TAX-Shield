from supabase import create_client, Client, ClientOptions
from app.config import settings

# Initialize Supabase client
# We use the service key for backend operations to bypass RLS when needed
# Using custom schema: itc_gaurd (lowercase for PostgreSQL compatibility)
supabase: Client = create_client(
    settings.supabase_url,
    settings.supabase_service_key,
    options=ClientOptions(schema="itc_gaurd")
)

def get_supabase() -> Client:
    """
    Returns the initialized Supabase client instance.
    """
    return supabase
