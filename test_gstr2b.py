"""
Test script for GSTR-2B API endpoints
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.gsp import get_gsp_provider

def test_gsp_provider():
    """Test GSP provider initialization"""
    print("=" * 60)
    print("Testing GSP Provider")
    print("=" * 60)
    
    gsp = get_gsp_provider()
    provider_type = type(gsp).__name__
    
    print(f"✓ GSP Provider Type: {provider_type}")
    print(f"✓ Has request_otp: {hasattr(gsp, 'request_otp')}")
    print(f"✓ Has verify_otp: {hasattr(gsp, 'verify_otp')}")
    print(f"✓ Has fetch_gstr2b: {hasattr(gsp, 'fetch_gstr2b')}")
    
    if provider_type == "SandboxGSPProvider":
        print("\n✅ Sandbox GSP Provider is active - GSTR-2B features available")
        print(f"   Base URL: {gsp.BASE_URL}")
        print(f"   Client ID: {gsp.client_id[:20]}...")
    else:
        print("\n⚠️  Mock GSP Provider is active - GSTR-2B features not available")
        print("   Set GSP_MODE=sandbox in .env to enable real GSP")
    
    return provider_type == "SandboxGSPProvider"

def test_database_tables():
    """Test if GSTR-2B tables exist"""
    print("\n" + "=" * 60)
    print("Testing Database Tables")
    print("=" * 60)
    
    from app.db.session import get_connection
    
    tables_to_check = ['gst_credentials', 'gstr_2b_data', 'otp_logs']
    
    try:
        with get_connection() as (conn, cursor):
            for table in tables_to_check:
                # Check if table exists (works for both SQLite and PostgreSQL)
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"✓ Table '{table}' exists (rows: {count})")
        
        print("\n✅ All GSTR-2B tables are present")
        return True
    except Exception as e:
        print(f"\n❌ Database error: {str(e)}")
        return False

def test_crud_operations():
    """Test CRUD operations"""
    print("\n" + "=" * 60)
    print("Testing CRUD Operations")
    print("=" * 60)
    
    try:
        from app.db.crud import gst_credentials, gstr2b_data
        print("✓ gst_credentials module imported")
        print("✓ gstr2b_data module imported")
        
        # Check available functions
        cred_funcs = [f for f in dir(gst_credentials) if not f.startswith('_')]
        print(f"\n  GST Credentials functions: {len(cred_funcs)}")
        for func in cred_funcs[:5]:
            print(f"    - {func}")
        
        data_funcs = [f for f in dir(gstr2b_data) if not f.startswith('_')]
        print(f"\n  GSTR-2B Data functions: {len(data_funcs)}")
        for func in data_funcs[:5]:
            print(f"    - {func}")
        
        print("\n✅ CRUD operations are available")
        return True
    except Exception as e:
        print(f"\n❌ CRUD import error: {str(e)}")
        return False

def test_api_endpoints():
    """Test if API endpoints are registered"""
    print("\n" + "=" * 60)
    print("Testing API Endpoints")
    print("=" * 60)
    
    try:
        from app.api.v1 import api
        from app.api.v1.endpoints import gstr2b
        
        print("✓ GSTR-2B endpoints module imported")
        
        # Check routes
        routes = [route.path for route in gstr2b.router.routes]
        print(f"\n  Registered routes: {len(routes)}")
        for route in routes:
            print(f"    - {route}")
        
        print("\n✅ API endpoints are registered")
        return True
    except Exception as e:
        print(f"\n❌ API endpoint error: {str(e)}")
        return False

if __name__ == "__main__":
    print("\n🧪 GSTR-2B Integration Test Suite\n")
    
    results = {
        "GSP Provider": test_gsp_provider(),
        "Database Tables": test_database_tables(),
        "CRUD Operations": test_crud_operations(),
        "API Endpoints": test_api_endpoints()
    }
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 All tests passed! GSTR-2B backend is ready.")
    else:
        print("\n⚠️  Some tests failed. Review errors above.")
    
    sys.exit(0 if all_passed else 1)
