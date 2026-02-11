"""
TaxPay Guard - PDF Certificate Generator
Generates Due Diligence Certificates using HTML Templates + PDFKit
"""
import os
import base64
import io
import datetime
from jinja2 import Environment, FileSystemLoader

try:
    import qrcode
    HAS_QRCODE = True
except ImportError:
    HAS_QRCODE = False
    print("Warning: qrcode library not installed.")

try:
    import pdfkit
    HAS_PDFKIT = True
except ImportError:
    HAS_PDFKIT = False
    print("Warning: pdfkit library not installed.")

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

def generate_certificate(check_data: dict) -> bytes:
    """
    Generate PDF certificate from HTML template.
    
    Args:
        check_data: Dictionary containing:
            - gstin, vendor_name, amount, decision
            - rule_id, reason, risk_level, check_id
            - timestamp, data_source
            - filing_history (list of dicts)
            - registration_date (optional)
            - gst_status (optional)
            
    Returns:
        PDF file bytes
    """
    # 1. Setup Environment
    base_dir = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(base_dir, 'templates')
    
    # ensure check_data has necessary lists
    if 'filing_history' not in check_data:
        check_data['filing_history'] = []
        
    # Generate QR Code
    if 'check_id' in check_data:
        verification_url = f"https://taxpayguard.in/verify?id={check_data['check_id']}&gstin={check_data.get('gstin')}"
        check_data['qr_code_data'] = generate_qr_code(verification_url)
        check_data['verification_url'] = verification_url

    # 2. Render HTML
    env = Environment(loader=FileSystemLoader(template_dir))
    try:
        template = env.get_template('certificate_template.html')
        html_content = template.render(check_data)
    except Exception as e:
        print(f"Error rendering template: {e}")
        # Fallback to simple text if template fails
        return f"Error rendering certificate: {e}".encode('utf-8')

    # 3. Convert to PDF using pdfkit
    if not HAS_PDFKIT:
        return html_content.encode('utf-8') # Fallback to HTML bytes if no pdfkit

    options = {
        'page-size': 'A4',
        'margin-top': '0mm',
        'margin-right': '0mm',
        'margin-bottom': '0mm',
        'margin-left': '0mm',
        'encoding': "UTF-8",
        'no-outline': None,
        'enable-local-file-access': None
    }
    
    try:
        # returns bytes when output_path is False
        pdf_bytes = pdfkit.from_string(html_content, False, options=options)
        return pdf_bytes
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return html_content.encode('utf-8') # Return HTML on failure
