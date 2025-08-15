from flask import Flask, render_template_string, request, jsonify, session, redirect, url_for
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

# Initialize Sumsub verification
sumsub = SumsubVerification()

@app.route('/')
def home():
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BlueDwarf - Property Analysis Platform</title>
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
        }
        
        /* Header Navigation */
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px 30px;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
        }
        
        .logo {
            display: flex;
            align-items: center;
            gap: 8px;
            color: white;
            text-decoration: none;
            font-size: 1.2rem;
            font-weight: 600;
        }
        
        .nav-center {
            display: flex;
            gap: 20px;
        }
        
        .nav-link {
            color: white;
            text-decoration: none;
            padding: 8px 16px;
            border-radius: 20px;
            transition: all 0.3s ease;
            font-weight: 500;
        }
        
        .nav-link:hover {
            background: rgba(255, 255, 255, 0.2);
        }
        
        .nav-right {
            display: flex;
            gap: 10px;
        }
        
        .btn {
            padding: 8px 16px;
            border-radius: 20px;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.3s ease;
            border: none;
            cursor: pointer;
        }
        
        .btn-login {
            background: rgba(139, 92, 246, 0.9);
            color: white;
        }
        
        .btn-login:hover {
            background: rgba(139, 92, 246, 1);
        }
        
        .btn-verify {
            background: rgba(255, 152, 0, 0.9);
            color: white;
        }
        
        .btn-verify:hover {
            background: rgba(255, 152, 0, 1);
        }
        
        .btn-primary {
            background: rgba(79, 70, 229, 0.9);
            color: white;
        }
        
        .btn-primary:hover {
            background: rgba(79, 70, 229, 1);
        }
        
        /* Main Content */
        .main-content {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: calc(100vh - 200px);
            padding: 40px 20px;
        }
        
        .hero-section {
            text-align: center;
            margin-bottom: 40px;
        }
        
        .hero-title {
            color: white;
            font-size: 3rem;
            font-weight: 700;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 15px;
        }
        
        .hero-subtitle {
            color: rgba(255, 255, 255, 0.9);
            font-size: 1.2rem;
            font-weight: 400;
        }
        
        /* Search Card */
        .search-card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
            max-width: 600px;
            width: 100%;
        }
        
        .search-form {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        
        .form-label {
            font-weight: 600;
            color: #333;
            text-align: center;
            margin-bottom: 10px;
        }
        
        .address-input {
            width: 100%;
            padding: 15px 20px;
            border: 2px solid #e5e7eb;
            border-radius: 10px;
            font-size: 1rem;
            transition: border-color 0.3s ease;
        }
        
        .address-input:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .button-group {
            display: flex;
            gap: 10px;
            justify-content: center;
        }
        
        .btn-search {
            background: #667eea;
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 10px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .btn-search:hover {
            background: #5a67d8;
            transform: translateY(-2px);
        }
        
        .btn-clear {
            background: #6b7280;
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 10px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .btn-clear:hover {
            background: #4b5563;
        }
        
        /* Footer */
        .footer {
            text-align: center;
            padding: 20px;
            color: rgba(255, 255, 255, 0.8);
            font-size: 0.9rem;
        }
        
        /* Responsive Design */
        @media (max-width: 768px) {
            .header {
                flex-direction: column;
                gap: 15px;
                padding: 20px;
            }
            
            .nav-center {
                order: 3;
            }
            
            .nav-right {
                order: 2;
            }
            
            .hero-title {
                font-size: 2rem;
                flex-direction: column;
                gap: 10px;
            }
            
            .search-card {
                margin: 0 20px;
            }
            
            .button-group {
                flex-direction: column;
            }
        }
    </style>
</head>
<body>
    <!-- Header Navigation -->
    <header class="header">
        <a href="/" class="logo">
            🏠 BlueDwarf
        </a>
        
        <nav class="nav-center">
            <a href="/about" class="nav-link">About</a>
            <a href="/contact" class="nav-link">Contact</a>
        </nav>
        
        <div class="nav-right">
            <a href="/verify" class="btn btn-verify">🔒 Verify License</a>
            <a href="/login" class="btn btn-login">Login</a>
            <a href="/register" class="btn btn-primary">Get Started</a>
        </div>
    </header>
    
    <!-- Main Content -->
    <main class="main-content">
        <div class="hero-section">
            <h1 class="hero-title">
                🏠 Property Analysis
            </h1>
            <p class="hero-subtitle">Instant Data • Full US Coverage</p>
        </div>
        
        <div class="search-card">
            <form action="/property-results" method="POST" class="search-form">
                <label class="form-label">Address</label>
                <input 
                    type="text" 
                    name="address" 
                    class="address-input"
                    placeholder="123 Pine Street, Any City, WA, 54321"
                    required
                >
                <div class="button-group">
                    <button type="submit" class="btn-search">Search</button>
                    <button type="button" class="btn-clear" onclick="clearForm()">Clear</button>
                </div>
            </form>
        </div>
    </main>
    
    <!-- Footer -->
    <footer class="footer">
        © 2024 Elite Marketing Lab LLC. All rights reserved.<br>
        support@bluedwarf.io
    </footer>
    
    <script>
        function clearForm() {
            document.querySelector('.address-input').value = '';
        }
    </script>
</body>
</html>
    ''')

@app.route('/property-results', methods=['POST'])
def property_results():
    address = request.form.get('address', '')
    
    # Mock property data (replace with real API calls)
    property_data = {
        'address': address,
        'estimated_value': '$500,000',
        'bedrooms': '4',
        'bathrooms': '2',
        'square_feet': '1,492',
        'year_built': '1964',
        'monthly_rent': '$3,000'
    }
    
    # Extract city and state from address
    city_state = "Sacramento, CA"  # This should be parsed from the address
    
    # Mock professionals data
    professionals = [
        {
            'title': 'Real Estate Agent',
            'location': city_state,
            'description': 'Experienced agent specializing in residential properties and first-time buyers',
            'verified': True
        },
        {
            'title': 'Mortgage Lender',
            'location': city_state,
            'description': 'Specialized in home loans and refinancing with competitive rates',
            'verified': True
        },
        {
            'title': 'Real Estate Attorney',
            'location': city_state,
            'description': 'Expert in real estate transactions and contract negotiations',
            'verified': False
        },
        {
            'title': 'Property Inspector',
            'location': city_state,
            'description': 'Certified home inspector with comprehensive inspection services',
            'verified': True
        },
        {
            'title': 'Insurance Agent',
            'location': city_state,
            'description': 'Home and auto insurance specialist with competitive coverage options',
            'verified': False
        },
        {
            'title': 'Property Manager',
            'location': city_state,
            'description': 'Professional property management services for residential and commercial properties',
            'verified': True
        }
    ]
    
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BlueDwarf - Property Analysis Platform</title>
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
        }
        
        /* Header Navigation */
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px 30px;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
        }
        
        .logo {
            display: flex;
            align-items: center;
            gap: 8px;
            color: white;
            text-decoration: none;
            font-size: 1.2rem;
            font-weight: 600;
        }
        
        .nav-center {
            display: flex;
            gap: 20px;
        }
        
        .nav-link {
            color: white;
            text-decoration: none;
            padding: 8px 16px;
            border-radius: 20px;
            transition: all 0.3s ease;
            font-weight: 500;
        }
        
        .nav-link:hover {
            background: rgba(255, 255, 255, 0.2);
        }
        
        .nav-right {
            display: flex;
            gap: 10px;
        }
        
        .btn {
            padding: 8px 16px;
            border-radius: 20px;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.3s ease;
            border: none;
            cursor: pointer;
        }
        
        .btn-login {
            background: rgba(139, 92, 246, 0.9);
            color: white;
        }
        
        .btn-verify {
            background: rgba(255, 152, 0, 0.9);
            color: white;
        }
        
        .btn-primary {
            background: rgba(79, 70, 229, 0.9);
            color: white;
        }
        
        /* Search Section */
        .search-section {
            padding: 20px 30px;
        }
        
        .search-card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 20px;
            max-width: 600px;
            margin: 0 auto;
        }
        
        .search-form {
            display: flex;
            gap: 10px;
            align-items: center;
        }
        
        .form-label {
            font-weight: 600;
            color: #333;
            min-width: 80px;
        }
        
        .address-input {
            flex: 1;
            padding: 10px 15px;
            border: 2px solid #e5e7eb;
            border-radius: 8px;
            font-size: 1rem;
        }
        
        .btn-search, .btn-clear {
            padding: 10px 20px;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .btn-search {
            background: #667eea;
            color: white;
        }
        
        .btn-clear {
            background: #6b7280;
            color: white;
        }
        
        /* Results Content */
        .results-content {
            background: white;
            min-height: calc(100vh - 200px);
            padding: 40px 30px;
        }
        
        .property-header {
            text-align: center;
            margin-bottom: 40px;
        }
        
        .property-address {
            font-size: 2rem;
            font-weight: 700;
            color: #333;
            margin-bottom: 30px;
        }
        
        /* Property Details Section */
        .property-details {
            background: #f8f9fa;
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 50px;
            display: flex;
            gap: 30px;
            align-items: flex-start;
        }
        
        .property-info {
            flex: 1;
        }
        
        .property-info h3 {
            color: #667eea;
            font-size: 1.3rem;
            margin-bottom: 20px;
        }
        
        .property-list {
            list-style: none;
            padding: 0;
        }
        
        .property-list li {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #e5e7eb;
        }
        
        .property-list li:last-child {
            border-bottom: none;
        }
        
        .property-label {
            font-weight: 600;
            color: #333;
        }
        
        .property-value {
            color: #666;
        }
        
        .property-visuals {
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        
        .visual-section {
            text-align: center;
        }
        
        .visual-title {
            color: #667eea;
            font-weight: 600;
            margin-bottom: 10px;
        }
        
        .visual-placeholder {
            background: #e5e7eb;
            border-radius: 8px;
            height: 150px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #6b7280;
            font-weight: 500;
        }
        
        .btn-view-details {
            background: #667eea;
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            margin-top: 20px;
        }
        
        /* Professionals Section */
        .professionals-section {
            margin-top: 50px;
        }
        
        .professionals-title {
            font-size: 1.8rem;
            font-weight: 700;
            color: #333;
            text-align: center;
            margin-bottom: 40px;
        }
        
        .professionals-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
        
        .professional-card {
            background: white;
            border-left: 4px solid #667eea;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease;
        }
        
        .professional-card:hover {
            transform: translateY(-2px);
        }
        
        .professional-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 10px;
        }
        
        .professional-title {
            color: #667eea;
            font-size: 1.1rem;
            font-weight: 600;
        }
        
        .verified-badge {
            background: #10b981;
            color: white;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        
        .professional-location {
            color: #6b7280;
            font-size: 0.9rem;
            margin-bottom: 10px;
        }
        
        .professional-description {
            color: #374151;
            line-height: 1.5;
            margin-bottom: 15px;
        }
        
        .btn-website {
            background: #667eea;
            color: white;
            padding: 8px 16px;
            border: none;
            border-radius: 6px;
            font-weight: 600;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
        }
        
        .btn-website:hover {
            background: #5a67d8;
        }
        
        /* Footer */
        .footer {
            background: #667eea;
            color: white;
            text-align: center;
            padding: 20px;
            font-size: 0.9rem;
        }
        
        /* Responsive Design */
        @media (max-width: 768px) {
            .header {
                flex-direction: column;
                gap: 15px;
                padding: 20px;
            }
            
            .search-form {
                flex-direction: column;
                align-items: stretch;
            }
            
            .property-details {
                flex-direction: column;
            }
            
            .professionals-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <!-- Header Navigation -->
    <header class="header">
        <a href="/" class="logo">
            🏠 BlueDwarf
        </a>
        
        <nav class="nav-center">
            <a href="/about" class="nav-link">About</a>
            <a href="/contact" class="nav-link">Contact</a>
        </nav>
        
        <div class="nav-right">
            <a href="/verify" class="btn btn-verify">🔒 Verify License</a>
            <a href="/login" class="btn btn-login">Login</a>
            <a href="/register" class="btn btn-primary">Get Started</a>
        </div>
    </header>
    
    <!-- Search Section -->
    <section class="search-section">
        <div class="search-card">
            <form action="/property-results" method="POST" class="search-form">
                <label class="form-label">Address</label>
                <input 
                    type="text" 
                    name="address" 
                    class="address-input"
                    value="{{ property_data.address }}"
                    placeholder="123 Pine Street, Any City, WA, 54321"
                >
                <button type="submit" class="btn-search">Search</button>
                <button type="button" class="btn-clear" onclick="clearForm()">Clear</button>
            </form>
        </div>
    </section>
    
    <!-- Results Content -->
    <main class="results-content">
        <div class="property-header">
            <h1 class="property-address">{{ property_data.address }}</h1>
        </div>
        
        <!-- Property Details -->
        <section class="property-details">
            <div class="property-info">
                <h3>Property Details</h3>
                <ul class="property-list">
                    <li>
                        <span class="property-label">Estimated Value:</span>
                        <span class="property-value">{{ property_data.estimated_value }}</span>
                    </li>
                    <li>
                        <span class="property-label">Bedrooms:</span>
                        <span class="property-value">{{ property_data.bedrooms }}</span>
                    </li>
                    <li>
                        <span class="property-label">Bathrooms:</span>
                        <span class="property-value">{{ property_data.bathrooms }}</span>
                    </li>
                    <li>
                        <span class="property-label">Square Feet:</span>
                        <span class="property-value">{{ property_data.square_feet }}</span>
                    </li>
                    <li>
                        <span class="property-label">Year Built:</span>
                        <span class="property-value">{{ property_data.year_built }}</span>
                    </li>
                    <li>
                        <span class="property-label">Monthly Rent Est:</span>
                        <span class="property-value">{{ property_data.monthly_rent }}</span>
                    </li>
                </ul>
            </div>
            
            <div class="property-visuals">
                <div class="visual-section">
                    <div class="visual-title">Street View</div>
                    <div class="visual-placeholder">Street View Image</div>
                </div>
                
                <div class="visual-section">
                    <div class="visual-title">Aerial View (2 blocks)</div>
                    <div class="visual-placeholder">Aerial Map View</div>
                </div>
                
                <button class="btn-view-details">View Details</button>
            </div>
        </section>
        
        <!-- Local Professionals -->
        <section class="professionals-section">
            <h2 class="professionals-title">Local Professionals in {{ city_state }}</h2>
            
            <div class="professionals-grid">
                {% for professional in professionals %}
                <div class="professional-card">
                    <div class="professional-header">
                        <h3 class="professional-title">{{ professional.title }}</h3>
                        {% if professional.verified %}
                        <span class="verified-badge">✅ Verified</span>
                        {% endif %}
                    </div>
                    <div class="professional-location">{{ professional.location }}</div>
                    <p class="professional-description">{{ professional.description }}</p>
                    <a href="#" class="btn-website">Website</a>
                </div>
                {% endfor %}
            </div>
        </section>
    </main>
    
    <!-- Footer -->
    <footer class="footer">
        © 2024 Elite Marketing Lab LLC. All rights reserved.<br>
        support@bluedwarf.io
    </footer>
    
    <script>
        function clearForm() {
            document.querySelector('.address-input').value = '';
        }
    </script>
</body>
</html>
    ''', property_data=property_data, professionals=professionals, city_state=city_state)

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
        }
        
        /* Header Navigation */
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px 30px;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
        }
        
        .logo {
            display: flex;
            align-items: center;
            gap: 8px;
            color: white;
            text-decoration: none;
            font-size: 1.2rem;
            font-weight: 600;
        }
        
        .nav-center {
            display: flex;
            gap: 20px;
        }
        
        .nav-link {
            color: white;
            text-decoration: none;
            padding: 8px 16px;
            border-radius: 20px;
            transition: all 0.3s ease;
            font-weight: 500;
        }
        
        .nav-link:hover {
            background: rgba(255, 255, 255, 0.2);
        }
        
        .nav-right {
            display: flex;
            gap: 10px;
        }
        
        .btn {
            padding: 8px 16px;
            border-radius: 20px;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.3s ease;
            border: none;
            cursor: pointer;
        }
        
        .btn-login {
            background: rgba(139, 92, 246, 0.9);
            color: white;
        }
        
        .btn-primary {
            background: rgba(79, 70, 229, 0.9);
            color: white;
        }
        
        /* Main Content */
        .main-content {
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: calc(100vh - 140px);
            padding: 40px 20px;
        }
        
        .verification-card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
            max-width: 600px;
            width: 100%;
        }
        
        .header-section {
            text-align: center;
            margin-bottom: 40px;
        }
        
        .verification-title {
            color: #333;
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }
        
        .verification-subtitle {
            color: #666;
            font-size: 1.1rem;
            line-height: 1.5;
        }
        
        /* Security Notice */
        .security-notice {
            background: #f0f9ff;
            border: 1px solid #0ea5e9;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 30px;
        }
        
        .security-title {
            color: #0ea5e9;
            font-weight: 600;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .security-text {
            color: #374151;
            line-height: 1.5;
            font-size: 0.95rem;
        }
        
        /* Process Steps */
        .process-steps {
            margin-bottom: 40px;
        }
        
        .step {
            display: flex;
            align-items: flex-start;
            gap: 15px;
            margin-bottom: 20px;
            padding: 15px;
            border-radius: 10px;
            background: #f9fafb;
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
            font-weight: 600;
            flex-shrink: 0;
        }
        
        .step-content h3 {
            color: #333;
            font-size: 1.1rem;
            margin-bottom: 5px;
        }
        
        .step-content p {
            color: #666;
            font-size: 0.95rem;
        }
        
        /* Form */
        .verification-form {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        
        .form-group {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }
        
        .form-label {
            font-weight: 600;
            color: #333;
        }
        
        .form-input, .form-select {
            padding: 12px 15px;
            border: 2px solid #e5e7eb;
            border-radius: 8px;
            font-size: 1rem;
            transition: border-color 0.3s ease;
        }
        
        .form-input:focus, .form-select:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .btn-start {
            background: #667eea;
            color: white;
            padding: 15px 30px;
            border: none;
            border-radius: 10px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-top: 10px;
        }
        
        .btn-start:hover {
            background: #5a67d8;
            transform: translateY(-2px);
        }
        
        .back-link {
            text-align: center;
            margin-top: 20px;
        }
        
        .back-link a {
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
        }
        
        .back-link a:hover {
            text-decoration: underline;
        }
        
        /* Footer */
        .footer {
            text-align: center;
            padding: 20px;
            color: rgba(255, 255, 255, 0.8);
            font-size: 0.9rem;
        }
        
        /* Responsive Design */
        @media (max-width: 768px) {
            .header {
                flex-direction: column;
                gap: 15px;
                padding: 20px;
            }
            
            .verification-card {
                margin: 0 20px;
                padding: 30px 20px;
            }
            
            .verification-title {
                font-size: 1.5rem;
                flex-direction: column;
                gap: 5px;
            }
        }
    </style>
</head>
<body>
    <!-- Header Navigation -->
    <header class="header">
        <a href="/" class="logo">
            🏠 BlueDwarf
        </a>
        
        <nav class="nav-center">
            <a href="/about" class="nav-link">About</a>
            <a href="/contact" class="nav-link">Contact</a>
        </nav>
        
        <div class="nav-right">
            <a href="/login" class="btn btn-login">Login</a>
            <a href="/register" class="btn btn-primary">Get Started</a>
        </div>
    </header>
    
    <!-- Main Content -->
    <main class="main-content">
        <div class="verification-card">
            <div class="header-section">
                <h1 class="verification-title">
                    🔒 License Verification
                </h1>
                <p class="verification-subtitle">
                    Verify your professional license to join our trusted network of verified contractors and service providers.
                </p>
            </div>
            
            <!-- Security Notice -->
            <div class="security-notice">
                <div class="security-title">
                    🛡️ Secure & Private
                </div>
                <p class="security-text">
                    Your documents are processed securely using enterprise-grade encryption. We use OCR technology and facial recognition to verify your identity and prevent fraud.
                </p>
            </div>
            
            <!-- Process Steps -->
            <div class="process-steps">
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
            
            <!-- Verification Form -->
            <form class="verification-form" action="/start-verification" method="POST">
                <div class="form-group">
                    <label class="form-label">First Name *</label>
                    <input type="text" name="first_name" class="form-input" required>
                </div>
                
                <div class="form-group">
                    <label class="form-label">Last Name *</label>
                    <input type="text" name="last_name" class="form-input" required>
                </div>
                
                <div class="form-group">
                    <label class="form-label">Email Address *</label>
                    <input type="email" name="email" class="form-input" required>
                </div>
                
                <div class="form-group">
                    <label class="form-label">Profession *</label>
                    <select name="profession" class="form-select" required>
                        <option value="">Select your profession</option>
                        <option value="general_contractor">General Contractor</option>
                        <option value="electrician">Electrician</option>
                        <option value="plumber">Plumber</option>
                        <option value="hvac_technician">HVAC Technician</option>
                        <option value="roofer">Roofer</option>
                        <option value="flooring_contractor">Flooring Contractor</option>
                        <option value="painter">Painter</option>
                        <option value="landscaper">Landscaper</option>
                        <option value="real_estate_agent">Real Estate Agent</option>
                        <option value="property_inspector">Property Inspector</option>
                        <option value="property_appraiser">Property Appraiser</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label class="form-label">State *</label>
                    <select name="state" class="form-select" required>
                        <option value="">Select your state</option>
                        <option value="california">California</option>
                        <option value="texas">Texas</option>
                        <option value="florida">Florida</option>
                        <option value="new_york">New York</option>
                        <option value="pennsylvania">Pennsylvania</option>
                        <option value="illinois">Illinois</option>
                        <option value="ohio">Ohio</option>
                        <option value="georgia">Georgia</option>
                        <option value="north_carolina">North Carolina</option>
                        <option value="michigan">Michigan</option>
                    </select>
                </div>
                
                <button type="submit" class="btn-start">
                    🚀 Start Verification Process
                </button>
            </form>
            
            <div class="back-link">
                <a href="/">← Back to Home</a>
            </div>
        </div>
    </main>
    
    <!-- Footer -->
    <footer class="footer">
        © 2024 Elite Marketing Lab LLC. All rights reserved.<br>
        support@bluedwarf.io
    </footer>
</body>
</html>
    ''')

# Additional routes for other pages
@app.route('/about')
def about():
    return render_template_string('<h1>About BlueDwarf</h1><p>Coming soon...</p>')

@app.route('/contact')
def contact():
    return render_template_string('<h1>Contact Us</h1><p>Coming soon...</p>')

@app.route('/login')
def login():
    return render_template_string('<h1>Login</h1><p>Coming soon...</p>')

@app.route('/register')
def register():
    return render_template_string('<h1>Professional Registration</h1><p>Coming soon...</p>')

@app.route('/start-verification', methods=['POST'])
def start_verification():
    # Handle verification form submission
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    email = request.form.get('email')
    profession = request.form.get('profession')
    state = request.form.get('state')
    
    # Create Sumsub applicant
    external_user_id = str(uuid.uuid4())
    applicant = sumsub.create_applicant(
        external_user_id=external_user_id,
        first_name=first_name,
        last_name=last_name,
        email=email
    )
    
    if applicant:
        # Get access token for WebSDK
        access_token = sumsub.get_access_token(applicant['id'])
        if access_token:
            # Store verification data in session
            session['verification_data'] = {
                'applicant_id': applicant['id'],
                'access_token': access_token['token'],
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'profession': profession,
                'state': state
            }
            return redirect(url_for('verification_sdk'))
    
    return jsonify({'error': 'Failed to start verification process'}), 500

@app.route('/verification-sdk')
def verification_sdk():
    verification_data = session.get('verification_data')
    if not verification_data:
        return redirect(url_for('verify_license'))
    
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>Professional Verification - BlueDwarf</title>
    <script src="https://cdn.sumsub.com/websdk/2.0.0/websdk.js"></script>
</head>
<body>
    <div id="sumsub-websdk-container"></div>
    
    <script>
        const accessToken = "{{ verification_data.access_token }}";
        
        const websdk = snsWebSdk.init(accessToken, () => accessToken)
            .withConf({
                lang: 'en',
                email: "{{ verification_data.email }}",
                theme: 'dark'
            })
            .withOptions({
                addViewportTag: false,
                adaptIframeHeight: true
            })
            .on('idCheck.onStepCompleted', (payload) => {
                console.log('Step completed:', payload);
            })
            .on('idCheck.onApplicantSubmitted', (payload) => {
                console.log('Verification submitted:', payload);
                window.location.href = '/verification-complete';
            })
            .build();
        
        websdk.render('#sumsub-websdk-container');
    </script>
</body>
</html>
    ''', verification_data=verification_data)

@app.route('/verification-complete')
def verification_complete():
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>Verification Complete - BlueDwarf</title>
</head>
<body>
    <h1>🎉 Verification Submitted!</h1>
    <p>Your professional license verification has been submitted successfully.</p>
    <p>You will receive an email notification once the verification is complete.</p>
    <a href="/">Return to Home</a>
</body>
</html>
    ''')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

