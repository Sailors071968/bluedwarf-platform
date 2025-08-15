from flask import Flask, render_template_string, request, redirect, url_for, flash, jsonify, session
from flask_cors import CORS
import urllib.parse
import re
import requests
import hashlib
import hmac
import time
import uuid
import json
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')
CORS(app)  # Enable CORS for all routes

# Google Maps API Key
GOOGLE_MAPS_API_KEY = "AIzaSyDe8QxfkBSo2Ids9PWK24-aKgqbI9du9B4"

# Sumsub Configuration
SUMSUB_APP_TOKEN = "sbx:Mfd6l7oxKRRbjzwBRfD5JewCe7xcUL7pIlOvPHGNSqp5zy..."
SUMSUB_SECRET_KEY = "GwFgol7U0miDMuUTbq3bluvRlF9M2oEv"
SUMSUB_BASE_URL = "https://api.sumsub.com"

# File upload configuration
UPLOAD_FOLDER = '/tmp/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class SumsubVerification:
    def __init__(self):
        self.app_token = SUMSUB_APP_TOKEN
        self.secret_key = SUMSUB_SECRET_KEY
        self.base_url = SUMSUB_BASE_URL
    
    def create_signature(self, method, url, body=""):
        """Create HMAC signature for Sumsub API authentication"""
        timestamp = str(int(time.time()))
        message = timestamp + method.upper() + url + body
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature, timestamp
    
    def get_headers(self, method, url, body=""):
        """Generate authentication headers for Sumsub API"""
        signature, timestamp = self.create_signature(method, url, body)
        return {
            'X-App-Token': self.app_token,
            'X-App-Access-Sig': signature,
            'X-App-Access-Ts': timestamp,
            'Content-Type': 'application/json'
        }
    
    def create_applicant(self, external_user_id, first_name="", last_name="", email="", level_name="basic-kyc-level"):
        """Create a new applicant for professional verification"""
        url = f"/resources/applicants?levelName={level_name}"
        body = json.dumps({
            "externalUserId": external_user_id,
            "info": {
                "firstName": first_name,
                "lastName": last_name,
                "email": email,
                "country": "USA"
            }
        })
        
        headers = self.get_headers("POST", url, body)
        
        try:
            response = requests.post(
                self.base_url + url,
                headers=headers,
                data=body,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error creating applicant: {e}")
            return None
    
    def get_access_token(self, applicant_id, level_name="basic-kyc-level"):
        """Get access token for WebSDK integration"""
        url = f"/resources/accessTokens?userId={applicant_id}&levelName={level_name}"
        headers = self.get_headers("POST", url)
        
        try:
            response = requests.post(
                self.base_url + url,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting access token: {e}")
            return None
    
    def get_applicant_status(self, applicant_id):
        """Check verification status of an applicant"""
        url = f"/resources/applicants/{applicant_id}/one"
        headers = self.get_headers("GET", url)
        
        try:
            response = requests.get(
                self.base_url + url,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting applicant status: {e}")
            return None

# Initialize Sumsub verification
sumsub = SumsubVerification()

def encode_address_for_maps(address):
    """Encode address for Google Maps Embed API"""
    cleaned = ' '.join(address.split())
    return cleaned.replace(' ', '+').replace(',', '%2C')

@app.route('/')
def home():
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BlueDwarf - Modern SaaS Platform for Property Valuation</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .container {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
            text-align: center;
            max-width: 600px;
            width: 100%;
        }
        
        .logo {
            font-size: 3rem;
            margin-bottom: 10px;
        }
        
        h1 {
            color: #333;
            font-size: 2.5rem;
            margin-bottom: 10px;
            font-weight: 700;
        }
        
        .subtitle {
            color: #666;
            font-size: 1.2rem;
            margin-bottom: 40px;
        }
        
        .nav-links {
            display: flex;
            gap: 20px;
            justify-content: center;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }
        
        .nav-link {
            background: #4CAF50;
            color: white;
            padding: 12px 24px;
            border-radius: 25px;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.3s ease;
            border: 2px solid #4CAF50;
        }
        
        .nav-link:hover {
            background: #45a049;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(76, 175, 80, 0.3);
        }
        
        .nav-link.contact {
            background: #2196F3;
            border-color: #2196F3;
        }
        
        .nav-link.contact:hover {
            background: #1976D2;
        }
        
        .nav-link.verify {
            background: #FF9800;
            border-color: #FF9800;
        }
        
        .nav-link.verify:hover {
            background: #F57C00;
        }
        
        .search-container {
            margin: 30px 0;
        }
        
        input[type="text"] {
            width: 100%;
            padding: 15px 20px;
            border: 3px solid #ddd;
            border-radius: 25px;
            font-size: 1.1rem;
            margin-bottom: 20px;
            transition: border-color 0.3s ease;
        }
        
        input[type="text"]:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .analyze-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 40px;
            border: none;
            border-radius: 25px;
            font-size: 1.2rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .analyze-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        }
        
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 30px;
            margin-top: 40px;
        }
        
        .feature {
            text-align: center;
            padding: 20px;
        }
        
        .feature-icon {
            font-size: 3rem;
            margin-bottom: 15px;
        }
        
        .feature h3 {
            color: #333;
            font-size: 1.3rem;
            margin-bottom: 10px;
        }
        
        .feature p {
            color: #666;
            line-height: 1.6;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 30px 20px;
            }
            
            h1 {
                font-size: 2rem;
            }
            
            .nav-links {
                flex-direction: column;
                align-items: center;
            }
            
            .features {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">🏠</div>
        <h1>BlueDwarf</h1>
        <p class="subtitle">Modern SaaS Platform for Property Valuation</p>
        
        <div class="nav-links">
            <a href="/register" class="nav-link">Professional Registration</a>
            <a href="/verify" class="nav-link verify">🔒 Verify License</a>
            <a href="/contact" class="nav-link contact">Contact Us</a>
        </div>
        
        <form action="/property-results" method="POST" class="search-container">
            <input type="text" name="address" placeholder="Enter property address (e.g., 123 Main Street, Sacramento, CA)" required>
            <button type="submit" class="analyze-btn">🔍 Analyze Property</button>
        </form>
        
        <div class="features">
            <div class="feature">
                <div class="feature-icon">📊</div>
                <h3>Property Analysis</h3>
                <p>Comprehensive market data and insights</p>
            </div>
            <div class="feature">
                <div class="feature-icon">🏘️</div>
                <h3>Neighborhood Data</h3>
                <p>Local market trends and demographics</p>
            </div>
            <div class="feature">
                <div class="feature-icon">💰</div>
                <h3>Market Valuation</h3>
                <p>Accurate property value estimates</p>
            </div>
            <div class="feature">
                <div class="feature-icon">🔒</div>
                <h3>Verified Professionals</h3>
                <p>Licensed contractors and service providers</p>
            </div>
        </div>
    </div>
</body>
</html>
    ''')

@app.route('/verify')
def verify_license():
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Professional License Verification - BlueDwarf</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .container {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
            max-width: 600px;
            width: 100%;
        }
        
        .header {
            text-align: center;
            margin-bottom: 40px;
        }
        
        .header h1 {
            color: #333;
            font-size: 2.5rem;
            margin-bottom: 10px;
        }
        
        .header p {
            color: #666;
            font-size: 1.1rem;
            line-height: 1.6;
        }
        
        .verification-steps {
            margin-bottom: 40px;
        }
        
        .step {
            display: flex;
            align-items: center;
            margin-bottom: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 10px;
        }
        
        .step-number {
            background: #667eea;
            color: white;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            margin-right: 15px;
        }
        
        .step-content h3 {
            color: #333;
            margin-bottom: 5px;
        }
        
        .step-content p {
            color: #666;
            font-size: 0.9rem;
        }
        
        .form-section {
            margin-bottom: 30px;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            color: #333;
            font-weight: 600;
            margin-bottom: 8px;
        }
        
        input, select {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #ddd;
            border-radius: 10px;
            font-size: 1rem;
            transition: border-color 0.3s ease;
        }
        
        input:focus, select:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .start-verification-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 30px;
            border: none;
            border-radius: 10px;
            font-size: 1.2rem;
            font-weight: 600;
            cursor: pointer;
            width: 100%;
            transition: all 0.3s ease;
            margin-bottom: 20px;
        }
        
        .start-verification-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        }
        
        .back-link {
            display: block;
            text-align: center;
            color: #667eea;
            text-decoration: none;
            font-weight: 600;
        }
        
        .back-link:hover {
            text-decoration: underline;
        }
        
        .security-notice {
            background: #e8f5e8;
            border: 1px solid #4CAF50;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 30px;
        }
        
        .security-notice h4 {
            color: #2e7d32;
            margin-bottom: 10px;
        }
        
        .security-notice p {
            color: #2e7d32;
            font-size: 0.9rem;
            line-height: 1.5;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔒 License Verification</h1>
            <p>Verify your professional license to join our trusted network of verified contractors and service providers.</p>
        </div>
        
        <div class="security-notice">
            <h4>🛡️ Secure & Private</h4>
            <p>Your documents are processed securely using enterprise-grade encryption. We use OCR technology and facial recognition to verify your identity and prevent fraud.</p>
        </div>
        
        <div class="verification-steps">
            <div class="step">
                <div class="step-number">1</div>
                <div class="step-content">
                    <h3>Upload License</h3>
                    <p>Upload a clear photo of your professional license</p>
                </div>
            </div>
            <div class="step">
                <div class="step-number">2</div>
                <div class="step-content">
                    <h3>Take Selfie</h3>
                    <p>Take a live selfie for identity verification</p>
                </div>
            </div>
            <div class="step">
                <div class="step-number">3</div>
                <div class="step-content">
                    <h3>Automatic Verification</h3>
                    <p>Our system verifies your license and identity</p>
                </div>
            </div>
            <div class="step">
                <div class="step-number">4</div>
                <div class="step-content">
                    <h3>Get Verified Badge</h3>
                    <p>Receive your verified professional status</p>
                </div>
            </div>
        </div>
        
        <form id="verificationForm" class="form-section">
            <div class="form-group">
                <label for="firstName">First Name *</label>
                <input type="text" id="firstName" name="firstName" required>
            </div>
            
            <div class="form-group">
                <label for="lastName">Last Name *</label>
                <input type="text" id="lastName" name="lastName" required>
            </div>
            
            <div class="form-group">
                <label for="email">Email Address *</label>
                <input type="email" id="email" name="email" required>
            </div>
            
            <div class="form-group">
                <label for="profession">Profession *</label>
                <select id="profession" name="profession" required>
                    <option value="">Select your profession</option>
                    <option value="General Contractor">General Contractor</option>
                    <option value="Electrician">Electrician</option>
                    <option value="Plumber">Plumber</option>
                    <option value="HVAC Technician">HVAC Technician</option>
                    <option value="Roofer">Roofer</option>
                    <option value="Flooring Contractor">Flooring Contractor</option>
                    <option value="Painter">Painter</option>
                    <option value="Landscaper">Landscaper</option>
                    <option value="Real Estate Agent">Real Estate Agent</option>
                    <option value="Property Inspector">Property Inspector</option>
                    <option value="Property Appraiser">Property Appraiser</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="state">State *</label>
                <select id="state" name="state" required>
                    <option value="">Select your state</option>
                    <option value="CA">California</option>
                    <option value="TX">Texas</option>
                    <option value="FL">Florida</option>
                    <option value="NY">New York</option>
                    <option value="PA">Pennsylvania</option>
                    <option value="IL">Illinois</option>
                    <option value="OH">Ohio</option>
                    <option value="GA">Georgia</option>
                    <option value="NC">North Carolina</option>
                    <option value="MI">Michigan</option>
                </select>
            </div>
            
            <button type="button" class="start-verification-btn" onclick="startVerification()">
                🚀 Start Verification Process
            </button>
        </form>
        
        <a href="/" class="back-link">← Back to Home</a>
    </div>
    
    <script>
        function startVerification() {
            const form = document.getElementById('verificationForm');
            const formData = new FormData(form);
            
            // Validate form
            if (!form.checkValidity()) {
                form.reportValidity();
                return;
            }
            
            // Convert FormData to JSON
            const data = {};
            formData.forEach((value, key) => {
                data[key] = value;
            });
            
            // Start verification process
            fetch('/api/start-verification', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    // Redirect to verification widget
                    window.location.href = '/verification-widget?token=' + result.access_token + '&applicant=' + result.applicant_id;
                } else {
                    alert('Error starting verification: ' + result.error);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred. Please try again.');
            });
        }
    </script>
</body>
</html>
    ''')

@app.route('/api/start-verification', methods=['POST'])
def start_verification():
    """Start the professional verification process"""
    try:
        data = request.get_json()
        
        # Generate unique external user ID
        external_user_id = f"{data['email']}_{int(time.time())}"
        
        # Create applicant in Sumsub
        applicant = sumsub.create_applicant(
            external_user_id=external_user_id,
            first_name=data['firstName'],
            last_name=data['lastName'],
            email=data['email'],
            level_name="basic-kyc-level"
        )
        
        if not applicant:
            return jsonify({
                "success": False,
                "error": "Failed to create verification applicant"
            }), 400
        
        # Get access token for WebSDK
        access_token_response = sumsub.get_access_token(
            applicant_id=applicant['id'],
            level_name="basic-kyc-level"
        )
        
        if not access_token_response:
            return jsonify({
                "success": False,
                "error": "Failed to get access token"
            }), 400
        
        # Store verification data in session
        session['verification_data'] = {
            'applicant_id': applicant['id'],
            'external_user_id': external_user_id,
            'professional_data': data
        }
        
        return jsonify({
            "success": True,
            "applicant_id": applicant['id'],
            "access_token": access_token_response['token']
        })
        
    except Exception as e:
        print(f"Error starting verification: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/verification-widget')
def verification_widget():
    """Display the Sumsub verification widget"""
    access_token = request.args.get('token')
    applicant_id = request.args.get('applicant')
    
    if not access_token or not applicant_id:
        flash('Invalid verification session. Please start again.', 'error')
        return redirect(url_for('verify_license'))
    
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Professional License Verification - BlueDwarf</title>
    <script src="https://cdn.sumsub.com/websdk/websdk.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .header h1 {
            color: #333;
            font-size: 2rem;
            margin-bottom: 10px;
        }
        
        .header p {
            color: #666;
            font-size: 1.1rem;
        }
        
        #sumsub-websdk-container {
            min-height: 500px;
            border-radius: 15px;
            overflow: hidden;
        }
        
        .loading {
            text-align: center;
            padding: 50px;
            color: #666;
        }
        
        .back-link {
            display: block;
            text-align: center;
            color: #667eea;
            text-decoration: none;
            font-weight: 600;
            margin-top: 20px;
        }
        
        .back-link:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔒 Professional License Verification</h1>
            <p>Please complete the verification process by uploading your license and taking a selfie.</p>
        </div>
        
        <div id="sumsub-websdk-container">
            <div class="loading">
                <h3>Loading verification system...</h3>
                <p>Please wait while we prepare your verification session.</p>
            </div>
        </div>
        
        <a href="/verify" class="back-link">← Start Over</a>
    </div>
    
    <script>
        function initSumsubWebSDK(accessToken) {
            let snsWebSdk = snsWebSdkInit(accessToken, function (messageType, payload) {
                console.log('WebSDK message:', messageType, payload);
                
                if (messageType === 'idCheck.onStepCompleted') {
                    console.log('Verification step completed:', payload);
                }
                
                if (messageType === 'idCheck.onApplicantSubmitted') {
                    console.log('Professional verification submitted');
                    // Redirect to completion page
                    window.location.href = '/verification-complete?applicant={{ applicant_id }}';
                }
                
                if (messageType === 'idCheck.onError') {
                    console.error('Verification error:', payload);
                }
            })
            .withConf({
                lang: 'en',
                uiConf: {
                    customCss: `
                        .sumsub-container {
                            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                            border-radius: 15px;
                        }
                        .sumsub-header {
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            color: white;
                        }
                        .sumsub-button {
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            border-radius: 10px;
                        }
                    `
                }
            })
            .withOptions({
                addViewportTag: false,
                adaptIframeHeight: true
            })
            .build();
            
            snsWebSdk.launch('#sumsub-websdk-container');
        }
        
        // Initialize with access token
        initSumsubWebSDK('{{ access_token }}');
    </script>
</body>
</html>
    ''', access_token=access_token, applicant_id=applicant_id)

@app.route('/verification-complete')
def verification_complete():
    """Show verification completion status"""
    applicant_id = request.args.get('applicant')
    
    if not applicant_id:
        flash('Invalid verification session.', 'error')
        return redirect(url_for('verify_license'))
    
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Verification Complete - BlueDwarf</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .container {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
            max-width: 500px;
            width: 100%;
            text-align: center;
        }
        
        .success-icon {
            font-size: 4rem;
            margin-bottom: 20px;
        }
        
        h1 {
            color: #333;
            font-size: 2rem;
            margin-bottom: 20px;
        }
        
        .status-message {
            color: #666;
            font-size: 1.1rem;
            line-height: 1.6;
            margin-bottom: 30px;
        }
        
        .next-steps {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 30px;
            text-align: left;
        }
        
        .next-steps h3 {
            color: #333;
            margin-bottom: 15px;
        }
        
        .next-steps ul {
            color: #666;
            padding-left: 20px;
        }
        
        .next-steps li {
            margin-bottom: 8px;
        }
        
        .home-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 30px;
            border: none;
            border-radius: 10px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            transition: all 0.3s ease;
        }
        
        .home-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        }
        
        .status-check {
            margin-top: 20px;
            padding: 15px;
            background: #e3f2fd;
            border-radius: 10px;
            border: 1px solid #2196F3;
        }
        
        .status-check h4 {
            color: #1976D2;
            margin-bottom: 10px;
        }
        
        .status-check p {
            color: #1976D2;
            font-size: 0.9rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="success-icon">✅</div>
        <h1>Verification Submitted!</h1>
        
        <div class="status-message">
            <p>Thank you for submitting your professional license verification. Your documents have been received and are being processed.</p>
        </div>
        
        <div class="next-steps">
            <h3>What happens next?</h3>
            <ul>
                <li>Our system will verify your license using OCR technology</li>
                <li>Your identity will be confirmed using facial recognition</li>
                <li>We'll validate your license against state databases</li>
                <li>You'll receive an email with your verification status within 24 hours</li>
                <li>Once approved, you'll receive a "Verified Professional" badge</li>
            </ul>
        </div>
        
        <div class="status-check">
            <h4>📧 Check Your Email</h4>
            <p>We'll send updates to your email address as your verification is processed.</p>
        </div>
        
        <a href="/" class="home-btn">Return to Home</a>
    </div>
    
    <script>
        // Check verification status periodically
        function checkStatus() {
            fetch('/api/verification-status/{{ applicant_id }}')
                .then(response => response.json())
                .then(data => {
                    if (data.success && data.status === 'completed') {
                        location.reload();
                    }
                })
                .catch(error => console.log('Status check error:', error));
        }
        
        // Check status every 30 seconds
        setInterval(checkStatus, 30000);
    </script>
</body>
</html>
    ''', applicant_id=applicant_id)

@app.route('/api/verification-status/<applicant_id>')
def get_verification_status(applicant_id):
    """Get verification status for an applicant"""
    try:
        status = sumsub.get_applicant_status(applicant_id)
        
        if not status:
            return jsonify({
                "success": False,
                "error": "Failed to get verification status"
            }), 400
        
        return jsonify({
            "success": True,
            "status": status.get('reviewStatus', 'pending'),
            "verification_complete": status.get('reviewStatus') == 'completed',
            "professional_verified": status.get('reviewStatus') == 'completed'
        })
        
    except Exception as e:
        print(f"Error getting verification status: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/webhook/sumsub', methods=['POST'])
def sumsub_webhook():
    """Handle Sumsub webhooks for verification status updates"""
    try:
        data = request.get_json()
        
        applicant_id = data.get('applicantId')
        review_status = data.get('reviewStatus')
        external_user_id = data.get('externalUserId')
        
        print(f"Webhook received: {applicant_id}, {review_status}, {external_user_id}")
        
        # Here you would update your database with the verification results
        # For now, we'll just log the webhook data
        
        return jsonify({"success": True})
        
    except Exception as e:
        print(f"Webhook error: {e}")
        return jsonify({"success": False}), 500

# Keep existing routes for property valuation and contact
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        profession = request.form.get('profession')
        phone = request.form.get('phone')
        company = request.form.get('company', '')
        
        flash('Thank you for your registration! We will review your application and contact you within 24 hours to complete your professional profile setup.', 'success')
        return redirect(url_for('register'))
    
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Professional Registration - BlueDwarf</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .container {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
            max-width: 500px;
            width: 100%;
        }
        
        h1 {
            color: #333;
            font-size: 2rem;
            margin-bottom: 30px;
            text-align: center;
        }
        
        .verification-notice {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 30px;
        }
        
        .verification-notice h4 {
            color: #856404;
            margin-bottom: 10px;
        }
        
        .verification-notice p {
            color: #856404;
            font-size: 0.9rem;
            line-height: 1.5;
        }
        
        .verification-notice a {
            color: #667eea;
            text-decoration: none;
            font-weight: 600;
        }
        
        .verification-notice a:hover {
            text-decoration: underline;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            color: #333;
            font-weight: 600;
            margin-bottom: 8px;
        }
        
        input, select {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #ddd;
            border-radius: 10px;
            font-size: 1rem;
            transition: border-color 0.3s ease;
        }
        
        input:focus, select:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .submit-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 30px;
            border: none;
            border-radius: 10px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            width: 100%;
            transition: all 0.3s ease;
            margin-bottom: 20px;
        }
        
        .submit-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        }
        
        .back-link {
            display: block;
            text-align: center;
            color: #667eea;
            text-decoration: none;
            font-weight: 600;
        }
        
        .back-link:hover {
            text-decoration: underline;
        }
        
        .flash-messages {
            margin-bottom: 20px;
        }
        
        .flash-message {
            padding: 12px 15px;
            border-radius: 10px;
            margin-bottom: 10px;
        }
        
        .flash-success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Professional Registration</h1>
        
        <div class="verification-notice">
            <h4>🔒 License Verification Available</h4>
            <p>After registration, you can <a href="/verify">verify your professional license</a> to receive a trusted badge and stand out to property owners.</p>
        </div>
        
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                <div class="flash-messages">
                    {% for category, message in messages %}
                        <div class="flash-message flash-{{ category }}">{{ message }}</div>
                    {% endfor %}
                </div>
            {% endif %}
        {% endwith %}
        
        <form method="POST">
            <div class="form-group">
                <label for="name">Full Name *</label>
                <input type="text" id="name" name="name" required>
            </div>
            
            <div class="form-group">
                <label for="email">Email Address *</label>
                <input type="email" id="email" name="email" required>
            </div>
            
            <div class="form-group">
                <label for="profession">Profession *</label>
                <select id="profession" name="profession" required>
                    <option value="">Select your profession</option>
                    <option value="General Contractor">General Contractor</option>
                    <option value="Electrician">Electrician</option>
                    <option value="Plumber">Plumber</option>
                    <option value="HVAC Technician">HVAC Technician</option>
                    <option value="Roofer">Roofer</option>
                    <option value="Real Estate Agent">Real Estate Agent</option>
                    <option value="Mortgage Lender">Mortgage Lender</option>
                    <option value="Property Inspector">Property Inspector</option>
                    <option value="Insurance Agent">Insurance Agent</option>
                    <option value="Property Appraiser">Property Appraiser</option>
                    <option value="Structural Engineer">Structural Engineer</option>
                    <option value="Escrow Officer">Escrow Officer</option>
                    <option value="Property Manager">Property Manager</option>
                    <option value="Real Estate Attorney">Real Estate Attorney</option>
                    <option value="Tax Consultant">Tax Consultant</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="phone">Phone Number *</label>
                <input type="tel" id="phone" name="phone" required>
            </div>
            
            <div class="form-group">
                <label for="company">Company/Organization</label>
                <input type="text" id="company" name="company">
            </div>
            
            <button type="submit" class="submit-btn">Submit Registration</button>
        </form>
        
        <a href="/" class="back-link">← Back to Home</a>
    </div>
</body>
</html>
    ''')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        flash('Thank you for contacting us! We have received your message and will respond within 24 hours.', 'success')
        return redirect(url_for('contact'))
    
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Contact Us - BlueDwarf</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .container {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
            max-width: 500px;
            width: 100%;
        }
        
        h1 {
            color: #333;
            font-size: 2rem;
            margin-bottom: 30px;
            text-align: center;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            color: #333;
            font-weight: 600;
            margin-bottom: 8px;
        }
        
        input, textarea {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #ddd;
            border-radius: 10px;
            font-size: 1rem;
            transition: border-color 0.3s ease;
            font-family: inherit;
        }
        
        input:focus, textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        
        textarea {
            height: 120px;
            resize: vertical;
        }
        
        .submit-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 30px;
            border: none;
            border-radius: 10px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            width: 100%;
            transition: all 0.3s ease;
            margin-bottom: 20px;
        }
        
        .submit-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        }
        
        .back-link {
            display: block;
            text-align: center;
            color: #667eea;
            text-decoration: none;
            font-weight: 600;
        }
        
        .back-link:hover {
            text-decoration: underline;
        }
        
        .flash-messages {
            margin-bottom: 20px;
        }
        
        .flash-message {
            padding: 12px 15px;
            border-radius: 10px;
            margin-bottom: 10px;
        }
        
        .flash-success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Contact Us</h1>
        
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                <div class="flash-messages">
                    {% for category, message in messages %}
                        <div class="flash-message flash-{{ category }}">{{ message }}</div>
                    {% endfor %}
                </div>
            {% endif %}
        {% endwith %}
        
        <form method="POST">
            <div class="form-group">
                <label for="name">Full Name *</label>
                <input type="text" id="name" name="name" required>
            </div>
            
            <div class="form-group">
                <label for="email">Email Address *</label>
                <input type="email" id="email" name="email" required>
            </div>
            
            <div class="form-group">
                <label for="subject">Subject *</label>
                <input type="text" id="subject" name="subject" required>
            </div>
            
            <div class="form-group">
                <label for="message">Message *</label>
                <textarea id="message" name="message" required></textarea>
            </div>
            
            <button type="submit" class="submit-btn">Send Message</button>
        </form>
        
        <a href="/" class="back-link">← Back to Home</a>
    </div>
</body>
</html>
    ''')

@app.route('/property-results', methods=['POST'])
def property_results():
    address = request.form.get('address', '')
    if not address:
        flash('Please enter a valid address.', 'error')
        return redirect(url_for('home'))
    
    # Encode address for Google Maps
    encoded_address = encode_address_for_maps(address)
    
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Property Analysis Results - BlueDwarf</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
        }
        
        .header {
            text-align: center;
            margin-bottom: 40px;
        }
        
        .header h1 {
            color: #333;
            font-size: 2.5rem;
            margin-bottom: 10px;
        }
        
        .address {
            color: #667eea;
            font-size: 1.3rem;
            font-weight: 600;
        }
        
        .content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 30px;
        }
        
        .map-section {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 20px;
        }
        
        .map-section h2 {
            color: #333;
            margin-bottom: 15px;
        }
        
        .map-container {
            width: 100%;
            height: 400px;
            border-radius: 10px;
            overflow: hidden;
        }
        
        .analysis-section {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 20px;
        }
        
        .analysis-section h2 {
            color: #333;
            margin-bottom: 20px;
        }
        
        .metric {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px 0;
            border-bottom: 1px solid #e9ecef;
        }
        
        .metric:last-child {
            border-bottom: none;
        }
        
        .metric-label {
            color: #666;
            font-weight: 600;
        }
        
        .metric-value {
            color: #333;
            font-weight: 700;
            font-size: 1.1rem;
        }
        
        .back-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 30px;
            border: none;
            border-radius: 10px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            transition: all 0.3s ease;
        }
        
        .back-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        }
        
        @media (max-width: 768px) {
            .content {
                grid-template-columns: 1fr;
            }
            
            .header h1 {
                font-size: 2rem;
            }
            
            .address {
                font-size: 1.1rem;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏠 Property Analysis</h1>
            <div class="address">{{ address }}</div>
        </div>
        
        <div class="content">
            <div class="map-section">
                <h2>📍 Location</h2>
                <div class="map-container">
                    <iframe
                        width="100%"
                        height="100%"
                        frameborder="0"
                        style="border:0"
                        src="https://www.google.com/maps/embed/v1/place?key={{ api_key }}&q={{ encoded_address }}"
                        allowfullscreen>
                    </iframe>
                </div>
            </div>
            
            <div class="analysis-section">
                <h2>📊 Property Metrics</h2>
                
                <div class="metric">
                    <span class="metric-label">Estimated Value</span>
                    <span class="metric-value">$485,000 - $525,000</span>
                </div>
                
                <div class="metric">
                    <span class="metric-label">Market Trend</span>
                    <span class="metric-value">+3.2% YoY</span>
                </div>
                
                <div class="metric">
                    <span class="metric-label">Neighborhood Score</span>
                    <span class="metric-value">8.4/10</span>
                </div>
                
                <div class="metric">
                    <span class="metric-label">Investment Grade</span>
                    <span class="metric-value">B+</span>
                </div>
                
                <div class="metric">
                    <span class="metric-label">Days on Market</span>
                    <span class="metric-value">28 days avg</span>
                </div>
                
                <div class="metric">
                    <span class="metric-label">Price per Sq Ft</span>
                    <span class="metric-value">$285</span>
                </div>
            </div>
        </div>
        
        <div style="text-align: center;">
            <a href="/" class="back-btn">← Analyze Another Property</a>
        </div>
    </div>
</body>
</html>
    ''', address=address, encoded_address=encoded_address, api_key=GOOGLE_MAPS_API_KEY)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

