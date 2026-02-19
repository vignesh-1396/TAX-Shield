import sys
import os

# Add backend to sys.path so we can import from app
# accessing backend folder from current root directory
sys.path.append(os.path.join(os.getcwd(), "backend"))

try:
    from app.main import app
    print("Successfully imported app from backend.app.main")
except ImportError as e:
    print(f"Error importing app: {e}")
    # Fallback/Debug: print sys.path and current directory contents
    print(f"Current Config: {os.getcwd()}")
    print("Directory listing:")
    for root, dirs, files in os.walk("."):
        for name in files:
            print(os.path.join(root, name))
    raise e

if __name__ == "__main__":
    import uvicorn
    print("Starting Uvicorn server...")
    uvicorn.run(app, host="0.0.0.0", port=10000)
