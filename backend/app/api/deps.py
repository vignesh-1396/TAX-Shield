from typing import Optional
from fastapi import Depends, HTTPException, Header, status
from app.db.crud import user as user_crud
from app.database import supabase
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme"
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header"
        )
    
    # SPECIAL DEV BACKDOOR FOR TESTING
    if token == "dev_test_token":
        # Hack for testing: Return the test user directly
        user = user_crud.get_user_by_email("vigneshiba132696@gmail.com")
        if user:
            return user
        else:
             raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Test user not found"
             )

    # Verify token with Supabase
    try:
        user_response = supabase.auth.get_user(token)
        if not user_response or not user_response.user:
             raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        user_id = user_response.user.id
    except Exception as e:
        print(f"Auth error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

    # Fetch from local DB to ensure user exists in our schema
    user = user_crud.get_user_by_id(user_id)
    if not user:
        # If user exists in Auth but not in our table, the trigger might have failed.
        # We could try to create it here as a fallback, or just fail.
        # For now, let's fail to ensure consistency.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found in system records"
        )
    
    return user
