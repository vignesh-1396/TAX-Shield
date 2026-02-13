
import os
import sys

print("🔍 Starting Diagnosis...")

try:
    print("1️⃣ Testing app.core.config...")
    from app.core.config import settings as core_settings
    print(f"   ✅ Core Settings loaded. REDIS_URL: {core_settings.REDIS_URL}")
except Exception as e:
    print(f"   ❌ Core Settings failed: {e}")

try:
    print("2️⃣ Testing app.config...")
    from app.config import settings as app_settings
    print(f"   ✅ App Settings loaded.")
    print(f"      jwt_secret: {app_settings.jwt_secret[:5]}...")
    print(f"      sandbox_client_id: {app_settings.sandbox_client_id[:5]}...")
except Exception as e:
    print(f"   ❌ App Settings failed: {e}")

try:
    print("3️⃣ Testing Database Connection...")
    from app.db.session import get_connection, DB_ENGINE
    print(f"   Engine: {DB_ENGINE}")
    
    with get_connection() as (conn, cursor):
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        print(f"   ✅ Connected! Result: {result}")
except Exception as e:
    print(f"   ❌ Database failed: {e}")

print("✅ Diagnosis Complete")
