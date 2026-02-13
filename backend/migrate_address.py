import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def migrate():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        print("Adding address column to itc_gaurd.users...")
        cur.execute("ALTER TABLE itc_gaurd.users ADD COLUMN IF NOT EXISTS address TEXT;")
        
        conn.commit()
        cur.close()
        conn.close()
        print("Migration successful: address column added.")
        
    except Exception as e:
        print(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate()
