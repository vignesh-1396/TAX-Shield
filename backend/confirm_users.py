from app.database import supabase

def confirm_users():
    try:
        # Fetch users
        response = supabase.auth.admin.list_users()
        # Handle list vs object
        if hasattr(response, 'users'):
            users = response.users
        elif isinstance(response, list):
            users = response
        else:
            users = []
            
        print(f"Found {len(users)} users. Checking for unconfirmed...")
        
        for user in users:
            if not user.email_confirmed_at:
                print(f"Confirming user: {user.email} ({user.id})")
                try:
                    # Attempt to set email_confirm = True
                    update_response = supabase.auth.admin.update_user_by_id(
                        user.id, 
                        {"email_confirm": True}
                    )
                    print(f"Success: {update_response}")
                except Exception as e:
                    print(f"Failed to confirm {user.email}: {e}")
            else:
                print(f"User {user.email} is already confirmed.")
            
    except Exception as e:
        print(f"Error listing users: {e}")

if __name__ == "__main__":
    confirm_users()
