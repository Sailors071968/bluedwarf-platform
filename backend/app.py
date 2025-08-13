from flask import Flask, request, jsonify, render_template
import os

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
    """Simulates checking a license against a state database."""
    if not license_number or not state:
        return {"status": "failed", "reason": "Missing license number or state."}
    return {
        "status": "success",
        "license_status": "Active",
        "is_in_good_standing": True
    }


# --- FLASK APPLICATION SETUP ---

app = Flask(__name__, template_folder='../', static_folder='../static') # Point to root for templates

# --- WEBSITE ROUTES ---

@app.route('/')
def index():
    return render_template('bluedwarf_final_fixed.html')

@app.route('/about')
def about():
    # Assuming the about file is named this way in the root
    return render_template('about_html_2025-08-12_19-38-29_9887.html')

@app.route('/contact')
def contact():
    # Assuming the contact file is named this way in the root
    return render_template('contact_html_2025-08-12_19-38-41_6660.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

# --- API ROUTES ---

@app.route('/api/verify-professional', methods=['POST'])
def verify_professional():
    """
    API endpoint to handle the full verification process for a professional.
    This simulates the multi-step verification flow.
    """
    # In a real app, you'd handle file uploads securely
    # For this mock, we'll just use placeholder paths
    id_file = request.form.get('id_file_path', 'uploads/mock_id.png')
    license_file = request.form.get('license_file_path', 'uploads/mock_license.png')
    live_photo = request.form.get('live_photo_path', 'uploads/mock_live.png')

    # Step 1: Verify Documents
    id_verification_result = mock_document_verification(id_file)
    if id_verification_result['status'] != 'success':
        return jsonify({"error": "ID document verification failed.", "details": id_verification_result}), 400

    license_verification_result = mock_document_verification(license_file)
    if license_verification_result['status'] != 'success':
        return jsonify({"error": "Professional license verification failed.", "details": license_verification_result}), 400

    # Step 2: Facial Recognition
    facial_match_result = mock_facial_recognition(id_file, live_photo)
    if not facial_match_result.get('is_match'):
        return jsonify({"error": "Facial recognition failed. Live photo does not match ID.", "details": facial_match_result}), 400

    # Step 3: State License Database Validation
    license_details = license_verification_result.get("extracted_text", {})
    license_number = license_details.get("license_number")
    state = license_details.get("state")
    db_validation_result = mock_license_validation(license_number, state)
    if db_validation_result.get('license_status') != 'Active':
        return jsonify({"error": "License is not active or in good standing.", "details": db_validation_result}), 400

    # If all checks pass:
    final_response = {
        "status": "success",
        "message": "Professional verification completed successfully.",
        "verification_summary": {
            "document_authenticity": "Confirmed",
            "facial_match": "Confirmed",
            "license_status": "Active and Verified"
        }
    }
    return jsonify(final_response), 200


if __name__ == '__main__':
    # For development, it's fine to run this way.
    # For production, a proper WSGI server like Gunicorn should be used.
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=True, host='0.0.0.0', port=port)

