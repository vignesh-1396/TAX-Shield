import os
import datetime
import base64
import io
from jinja2 import Environment, FileSystemLoader

# Try to import qrcode for QR code generation
try:
    import qrcode
    HAS_QRCODE = True
except ImportError:
    HAS_QRCODE = False
    print("Note: qrcode library not installed. QR codes will be skipped.")


def generate_qr_code(data: str) -> str:
    """Generate QR code as base64 data URL"""
    if not HAS_QRCODE:
        return None
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=4,
        border=2,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="#1e40af", back_color="white")
    
    # Convert to base64 data URL
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    img_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    return f"data:image/png;base64,{img_data}"


# Mock Data Function (Replacing real API for V0)
def get_mock_vendor_data(vendor_gstin):
    # Depending on GSTIN, return different scenarios
    if vendor_gstin.startswith("29"): # Example Bad Vendor - HOLD
        return {
            "vendor_name": "BAD TRADERS PVT LTD",
            "gstin": vendor_gstin,
            "gst_status": "Active",
            "decision": "HOLD",
            "decision_reason": "GSTR-3B Filed Late (Potential Interest Liability)",
            "rule_37a_status": "Potentially At Risk",
            "filing_history": [
                {"period": "Dec 2025", "filed_date": "22-Feb-2026", "status": "Filed", "delay": "Delayed (32 Days)"},
                {"period": "Nov 2025", "filed_date": "20-Dec-2025", "status": "Filed", "delay": "On Time"},
                {"period": "Oct 2025", "filed_date": "20-Nov-2025", "status": "Filed", "delay": "On Time"},
            ]
        }
    elif vendor_gstin.startswith("01") or vendor_gstin.startswith("02"): # STOP scenario
        return {
            "vendor_name": "CANCELLED VENDOR LTD",
            "gstin": vendor_gstin,
            "gst_status": "Cancelled",
            "decision": "STOP",
            "decision_reason": "GST Registration Cancelled - ITC not claimable",
            "rule_37a_status": "CRITICAL RISK",
            "filing_history": [
                {"period": "Dec 2025", "filed_date": "-", "status": "Not Filed", "delay": "N/A"},
                {"period": "Nov 2025", "filed_date": "-", "status": "Not Filed", "delay": "N/A"},
                {"period": "Oct 2025", "filed_date": "-", "status": "Not Filed", "delay": "N/A"},
            ]
        }
    else: # Good Vendor - RELEASE
        return {
            "vendor_name": "GOOD EXPORTS LTD",
            "gstin": vendor_gstin,
            "gst_status": "Active",
            "decision": "RELEASE",
            "decision_reason": "Vendor is compliant. Safe to process payment.",
            "rule_37a_status": "Clean",
            "filing_history": [
                {"period": "Dec 2025", "filed_date": "20-Jan-2026", "status": "Filed", "delay": "On Time"},
                {"period": "Nov 2025", "filed_date": "20-Dec-2025", "status": "Filed", "delay": "On Time"},
                {"period": "Oct 2025", "filed_date": "20-Nov-2025", "status": "Filed", "delay": "On Time"},
            ]
        }


def generate_certificate(gstin, verification_base_url="https://itc-shield.app/verify"):
    """
    Generate a Due Diligence Certificate for the given GSTIN.
    
    Args:
        gstin: The vendor GSTIN to check
        verification_base_url: Base URL for QR code verification
    
    Returns:
        Path to the generated file (HTML or PDF)
    """
    # 1. Setup Environment
    base_dir = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(base_dir, 'templates')
    output_dir = os.path.join(base_dir, '..', 'output')
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 2. Prepare Data
    data = get_mock_vendor_data(gstin)
    
    # CRITICAL: Use CURRENT System Time
    current_time = datetime.datetime.now().strftime("%d-%b-%Y %H:%M:%S IST")
    check_id = f"CHK-{datetime.datetime.now().strftime('%Y%m%d')}-{gstin[-4:]}"
    
    data['timestamp'] = current_time
    data['check_id'] = check_id
    
    # 3. Generate QR Code for verification
    verification_url = f"{verification_base_url}?id={check_id}&gstin={gstin}"
    data['qr_code_data'] = generate_qr_code(verification_url)
    data['verification_url'] = verification_url

    # 4. Render HTML
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template('certificate_template.html')
    html_content = template.render(data)

    # 5. Save HTML (Always useful for debugging)
    html_filename = f"TaxPayGuard_Cert_{gstin}.html"
    html_path = os.path.join(output_dir, html_filename)
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Generated HTML: {html_path}")

    # 6. Try generating PDF (Optional dependency)
    try:
        import pdfkit
        pdf_filename = f"TaxPayGuard_Cert_{gstin}.pdf"
        pdf_path = os.path.join(output_dir, pdf_filename)
        
        # Configure pdfkit options for better rendering
        options = {
            'page-size': 'A4',
            'margin-top': '0mm',
            'margin-right': '0mm',
            'margin-bottom': '0mm',
            'margin-left': '0mm',
            'encoding': 'UTF-8',
            'enable-local-file-access': None,
            'print-media-type': None,
            'no-outline': None # Added from user's snippet
        }
        
        pdfkit.from_file(html_path, pdf_path, options=options)
        print(f"✅ Generated TaxPayGuard PDF Certificate: {pdf_path}")
        return pdf_path
    except ImportError:
        print("ℹ️  pdfkit library not found. Install with: pip install pdfkit")
        print("   Also ensure wkhtmltopdf is installed on the system.")
        return html_path
    except Exception as e:
        print(f"⚠️  PDF Generation failed: {e}")
        return html_path


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🛡️  TaxPayGuard - Generating Test Certificates")
    print("="*60 + "\n")
    
    # Test with RELEASE scenario
    print("📝 Generating RELEASE certificate...")
    generate_certificate("33AHXPG1234V1Z2")
    
    print()
    
    # Test with HOLD scenario
    print("📝 Generating HOLD certificate...")
    generate_certificate("29AABCU9603R1ZX")
    
    print()
    
    # Test with STOP scenario
    print("📝 Generating STOP certificate...")
    generate_certificate("01AABCU9603R1ZX")
    
    print("\n" + "="*60)
    print("✅ All test certificates generated!")
    print("="*60 + "\n")
