
import urllib.request
import urllib.error
import json
import sys

BASE_URL = "http://localhost:8000"

def verify_integration():
    print("Testing Certificate Integration...")
    
    # 1. Create a Check
    payload = {
        "gstin": "33AABCU9603R1ZX",  # Compliant GSTIN
        "party_name": "Integration Test Vendor",
        "amount": 50000.00
    }
    
    req = urllib.request.Request(
        f"{BASE_URL}/check_compliance",
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            check_id = data.get("check_id")
            print(f"✅ Created Check ID: {check_id}")
    except Exception as e:
        print(f"❌ Failed to create check: {e}")
        return

    # 2. Download Certificate
    try:
        cert_url = f"{BASE_URL}/certificate/{check_id}"
        print(f"Downloading certificate from: {cert_url}")
        
        with urllib.request.urlopen(cert_url) as cert_resp:
            pdf_content = cert_resp.read()
            
            filename = f"verified_cert_{check_id}.pdf"
            with open(filename, "wb") as f:
                f.write(pdf_content)
                
            print(f"✅ Certificate downloaded: {filename}")
            print(f"   Size: {len(pdf_content)} bytes")
            
            # Verify PDF or HTML header
            if pdf_content.startswith(b"%PDF"):
                print("✅ Valid PDF Header detected.")
            elif b"<!DOCTYPE html>" in pdf_content or b"<html" in pdf_content.lower():
                print("✅ Valid HTML Fallback detected (PDFKit missing).")
                print("   This is expected if wkhtmltopdf is not installed.")
            else:
                print("❌ Invalid Content (neither PDF nor HTML).")
                print("First 100 bytes:", pdf_content[:100])
            
    except Exception as e:
        print(f"❌ Failed to download certificate: {e}")

if __name__ == "__main__":
    verify_integration()
