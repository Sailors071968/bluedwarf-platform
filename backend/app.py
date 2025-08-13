from flask import Flask, request, jsonify, send_from_directory
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
    return send_from_directory('..', 'bluedwarf_final_fixed.html')

@app.route('/about')
def about():
    """Serve the about page"""
    return send_from_directory('..', 'about.html')

@app.route('/contact')
def contact():
    """Serve the contact page"""
    return send_from_directory('..', 'contact.html')

@app.route('/signup')
def signup():
    """Serve the signup page"""
    return send_from_directory('..', 'signup.html')

# --- API ENDPOINTS ---

@app.route('/api/verify-document', methods=['POST'])
def verify_document():
    """API endpoint for document verification"""
    try:
        # In a real app, you'd handle file upload here
        file_path = request.json.get('file_path', '')
        result = mock_document_verification(file_path)
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/verify-identity', methods=['POST'])
def verify_identity():
    """API endpoint for facial recognition verification"""
    try:
        id_photo = request.json.get('id_photo_path', '')
        live_photo = request.json.get('live_photo_path', '')
        result = mock_facial_recognition(id_photo, live_photo)
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/validate-license', methods=['POST'])
def validate_license():
    """API endpoint for license validation"""
    try:
        license_number = request.json.get('license_number', '')
        state = request.json.get('state', '')
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

