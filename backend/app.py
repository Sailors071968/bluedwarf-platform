from flask import Flask, request, jsonify, send_from_directory, render_template_string
import os

# Create Flask app with template and static folders pointing to parent directory
app = Flask(__name__, 
            template_folder='../',  # Look for templates in parent directory
            static_folder='../')    # Look for static files in parent directory

# --- MOCK VERIFICATION FUNCTIONS ---
# In a real application, these would call the actual verification scripts
# and external APIs (like Amazon Rekognition, ID Analyzer, etc.)

def mock_document_verification(file_path):
    """Simulates verifying a document. Returns mock data."""
    if not file_path or "fail" in file_path:
        return {"status": "failed", "reason": "Invalid document image."}
    return {
        "status": "success",
        "document_type": "State Professional License",
        "is_expired": False,
        "is_authentic": True,
        "extracted_text": {
            "name": "John Doe",
            "license_number": "PROF123456",
            "state": "CA",
            "expiration_date": "2026-12-31"
        }
    }

def mock_facial_recognition(id_photo_path, live_photo_path):
    """Simulates facial recognition matching."""
    if not id_photo_path or not live_photo_path:
        return {"status": "failed", "reason": "Missing image for comparison."}
    return {
        "status": "success",
        "match_confidence": 99.8,
        "is_match": True
    }

def mock_license_validation(license_number, state):
    """Simulates license validation against state database."""
    if not license_number or not state:
        return {"status": "failed", "reason": "Missing license information."}
    return {
        "status": "success",
        "is_valid": True,
        "license_holder": "John Doe",
        "issue_date": "2021-01-15",
        "expiration_date": "2026-12-31",
        "license_type": "Professional Real Estate License"
    }

# --- ROUTES ---

@app.route('/')
def home():
    """Serve the main BlueDwarf homepage"""
    try:
        return send_from_directory('..', 'bluedwarf_final_fixed.html')
    except Exception as e:
        return f"<h1>BlueDwarf Platform</h1><p>Welcome to BlueDwarf! The main page is loading...</p><p>Error: {str(e)}</p>"

@app.route('/about')
def about():
    """Serve the about page - create a simple HTML response since the file is a webp image"""
    about_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>About - BlueDwarf Platform</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
            .container { max-width: 800px; margin: 0 auto; }
            h1 { color: #2c3e50; }
            .nav { margin-bottom: 30px; }
            .nav a { margin-right: 20px; text-decoration: none; color: #3498db; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="nav">
                <a href="/">Home</a>
                <a href="/about">About</a>
                <a href="/contact">Contact</a>
                <a href="/signup">Sign Up</a>
            </div>
            <h1>About BlueDwarf Platform</h1>
            <p>BlueDwarf is a comprehensive property analysis platform that provides professional verification services for real estate professionals.</p>
            <h2>Our Services</h2>
            <ul>
                <li>Document Verification</li>
                <li>Identity Verification</li>
                <li>License Validation</li>
                <li>Property Analysis</li>
            </ul>
            <p>Our platform uses advanced AI and machine learning technologies to ensure accurate and reliable verification processes.</p>
        </div>
    </body>
    </html>
    """
    return about_html

@app.route('/contact')
def contact():
    """Serve the contact page - create a simple HTML response since the file is a webp image"""
    contact_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Contact - BlueDwarf Platform</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
            .container { max-width: 800px; margin: 0 auto; }
            h1 { color: #2c3e50; }
            .nav { margin-bottom: 30px; }
            .nav a { margin-right: 20px; text-decoration: none; color: #3498db; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="nav">
                <a href="/">Home</a>
                <a href="/about">About</a>
                <a href="/contact">Contact</a>
                <a href="/signup">Sign Up</a>
            </div>
            <h1>Contact BlueDwarf Platform</h1>
            <h2>Get in Touch</h2>
            <p>We're here to help with all your property verification needs.</p>
            <h3>Contact Information</h3>
            <p><strong>Email:</strong> support@bluedwarf.com</p>
            <p><strong>Phone:</strong> (555) 123-4567</p>
            <p><strong>Business Hours:</strong> Monday - Friday, 9:00 AM - 6:00 PM EST</p>
            <h3>Support</h3>
            <p>For technical support or questions about our verification services, please don't hesitate to reach out.</p>
        </div>
    </body>
    </html>
    """
    return contact_html

@app.route('/signup')
def signup():
    """Serve the signup page"""
    try:
        return send_from_directory('..', 'signup.html')
    except Exception as e:
        return f"<h1>Sign Up - BlueDwarf Platform</h1><p>Sign up page is loading...</p><p>Error: {str(e)}</p>"

# --- API ENDPOINTS ---

@app.route('/api/verify-document', methods=['POST'])
def verify_document():
    """API endpoint for document verification"""
    try:
        # In a real app, you'd handle file upload here
        file_path = request.json.get('file_path', '') if request.json else ''
        result = mock_document_verification(file_path)
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/verify-identity', methods=['POST'])
def verify_identity():
    """API endpoint for facial recognition verification"""
    try:
        id_photo = request.json.get('id_photo_path', '') if request.json else ''
        live_photo = request.json.get('live_photo_path', '') if request.json else ''
        result = mock_facial_recognition(id_photo, live_photo)
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/validate-license', methods=['POST'])
def validate_license():
    """API endpoint for license validation"""
    try:
        license_number = request.json.get('license_number', '') if request.json else ''
        state = request.json.get('state', '') if request.json else ''
        result = mock_license_validation(license_number, state)
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "BlueDwarf Platform"})

# --- ERROR HANDLERS ---

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    # Get port from environment variable or default to 5000
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

