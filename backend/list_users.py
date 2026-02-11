import asyncio
from app.database import supabase

def list_users():
    try:
        # Fetch users (default page 1, per_page 50)
        response = supabase.auth.admin.list_users()
        print(f"Response Type: {type(response)}")
        print(f"Response Dir: {dir(response)}")
        
        # Try to access users
        if hasattr(response, 'users'):
            users = response.users
        elif isinstance(response, list):
            users = response
        else:
            # Maybe it's a dict?
            users = []
            print(f"Unknown response format: {response}")

        print(f"Found {len(users)} users:")
        for user in users:
            print(f"- Email: {user.email}, ID: {user.id}, Confirmed: {user.email_confirmed_at is not None}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_users()
