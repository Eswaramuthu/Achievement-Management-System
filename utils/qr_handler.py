"""
QR Code generation utility for achievement verification links.
Converts achievement verification URLs into scannable QR codes.
"""

import qrcode
import io
import base64


def generate_qr_code(verification_url):
    """
    Generate a QR code for the achievement verification URL.
    
    Args:
        verification_url (str): Full URL to the verification page
                               e.g., "https://domain.com/verify-achievement/123"
    
    Returns:
        str: Base64 encoded PNG image of the QR code
    
    Raises:
        ValueError: If URL is empty or invalid
    """
    if not verification_url or not isinstance(verification_url, str):
        raise ValueError("verification_url must be a non-empty string")
    
    try:
        # Create QR code instance
        qr = qrcode.QRCode(
            version=1,  # Determines size; auto-optimizes if needed
            error_correction=qrcode.constants.ERROR_CORRECT_H,  # High redundancy
            box_size=10,
            border=2,
        )
        
        # Add the URL data
        qr.add_data(verification_url)
        qr.make(fit=True)
        
        # Create image with contrasting colors
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert image to bytes
        img_buffer = io.BytesIO()
        img.save(img_buffer, format="PNG")
        img_buffer.seek(0)
        
        # Encode to Base64
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode("utf-8")
        
        return f"data:image/png;base64,{img_base64}"
        
    except Exception as e:
        raise ValueError(f"Failed to generate QR code: {str(e)}")


def get_verification_url(request_host, achievement_id):
    """
    Helper function to construct the verification URL.
    Handles both HTTP and HTTPS schemes.
    
    Args:
        request_host (str): Request host (e.g., "localhost:5000")
        achievement_id (int): Achievement database ID
    
    Returns:
        str: Complete verification URL
    """
    # Determine scheme (HTTPS in production, HTTP in dev)
    scheme = "https" if "localhost" not in request_host else "http"
    
    verification_url = f"{scheme}://{request_host}/verify-achievement/{achievement_id}"
    return verification_url
