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
import random
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

def get_coordinates(address):
    """Get latitude and longitude for an address using Google Geocoding API"""
    try:
        encoded_address = urllib.parse.quote(address)
        url = f"https://maps.googleapis.com/maps/api/geocode/json?address={encoded_address}&key={GOOGLE_MAPS_API_KEY}"
        response = requests.get(url)
        data = response.json()
        
        if data['status'] == 'OK' and data['results']:
            location = data['results'][0]['geometry']['location']
            return location['lat'], location['lng']
    except Exception as e:
        print(f"Geocoding error: {e}")
    
    # Default coordinates for Sacramento, CA if geocoding fails
    return 38.5816, -121.4944

def generate_comparable_properties(address, lat, lng):
    """Generate mock comparable properties around the given location"""
    properties = []
    
    # Generate 3 comparable properties with realistic data
    property_types = [
        {"beds": 3, "baths": 2, "sqft": random.randint(1200, 1600), "year": random.randint(1990, 2020)},
        {"beds": 4, "baths": 2, "sqft": random.randint(1400, 1800), "year": random.randint(1985, 2015)},
        {"beds": 3, "baths": 3, "sqft": random.randint(1300, 1700), "year": random.randint(1995, 2010)}
    ]
    
    streets = ["Cedar Lane", "Pine Street", "Maple Drive", "Oak Avenue", "Elm Street", "Birch Way"]
    
    for i, prop_type in enumerate(property_types):
        # Generate nearby coordinates (within ~1.5 mile radius)
        lat_offset = random.uniform(-0.02, 0.02)  # ~1.4 miles
        lng_offset = random.uniform(-0.02, 0.02)
        
        street_num = random.randint(1000, 9999)
        street_name = random.choice(streets)
        
        properties.append({
            'id': i + 1,
            'address': f"{street_num} {street_name}",
            'city': "Sacramento, CA",
            'zip': f"958{random.randint(10, 99)}",
            'beds': prop_type['beds'],
            'baths': prop_type['baths'],
            'sqft': prop_type['sqft'],
            'year_built': prop_type['year'],
            'days_on_market': random.randint(5, 180),
            'lat': lat + lat_offset,
            'lng': lng + lng_offset,
            'estimated_value': random.randint(450000, 650000)
        })
    
    return properties

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
            <a href="/login" class="btn btn-login">Login</a>
            <a href="/get-started" class="btn btn-primary">Get Started</a>
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
    
    # Get coordinates for the address
    lat, lng = get_coordinates(address)
    
    # Generate comparable properties
    comparable_properties = generate_comparable_properties(address, lat, lng)
    
    # Mock property data (replace with real API calls)
    property_data = {
        'address': address,
        'estimated_value': '$500,000',
        'bedrooms': '4',
        'bathrooms': '2',
        'square_feet': '1,492',
        'year_built': '1964',
        'monthly_rent': '$3,000',
        'lat': lat,
        'lng': lng
    }
    
    # Extract city and state from address
    city_state = "Sacramento, CA"  # This should be parsed from the address
    
    # Mock professionals data with verification status
    professionals = [
        {
            'title': 'Real Estate Agent',
            'location': city_state,
            'description': 'Experienced agent specializing in residential properties and first-time buyers',
            'verified': True,
            'website': 'https://example.com'
        },
        {
            'title': 'Mortgage Lender',
            'location': city_state,
            'description': 'Specialized in home loans and refinancing with competitive rates',
            'verified': True,
            'website': 'https://example.com'
        },
        {
            'title': 'Real Estate Attorney',
            'location': city_state,
            'description': 'Expert in real estate transactions and contract negotiations',
            'verified': False,
            'website': 'https://example.com'
        },
        {
            'title': 'Property Inspector',
            'location': city_state,
            'description': 'Certified home inspector with comprehensive inspection services',
            'verified': True,
            'website': 'https://example.com'
        },
        {
            'title': 'Insurance Agent',
            'location': city_state,
            'description': 'Home and auto insurance specialist with competitive coverage options',
            'verified': False,
            'website': 'https://example.com'
        },
        {
            'title': 'Property Manager',
            'location': city_state,
            'description': 'Professional property management services for residential and commercial properties',
            'verified': True,
            'website': 'https://example.com'
        }
    ]
    
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BlueDwarf - Property Analysis Platform</title>
    <script src="https://maps.googleapis.com/maps/api/js?key={{ google_maps_api_key }}&libraries=geometry"></script>
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
            align-items: end;
        }
        
        .form-group {
            flex: 1;
        }
        
        .form-label {
            display: block;
            font-weight: 600;
            color: #333;
            margin-bottom: 5px;
        }
        
        .address-input {
            width: 100%;
            padding: 10px 15px;
            border: 2px solid #e5e7eb;
            border-radius: 10px;
            font-size: 1rem;
        }
        
        .btn-search, .btn-clear {
            padding: 10px 20px;
            border: none;
            border-radius: 10px;
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
        
        /* Results Section */
        .results-section {
            padding: 20px 30px;
        }
        
        .property-header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        
        .property-title {
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 10px;
        }
        
        .property-details-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .property-details {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 30px;
        }
        
        .details-title {
            color: #667eea;
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 20px;
        }
        
        .detail-row {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #e5e7eb;
        }
        
        .detail-label {
            font-weight: 600;
            color: #333;
        }
        
        .detail-value {
            color: #666;
        }
        
        /* Street View and Maps */
        .visual-section {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 30px;
        }
        
        .visual-title {
            color: #667eea;
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 15px;
            text-align: center;
        }
        
        .street-view-container, .map-container {
            margin-bottom: 30px;
        }
        
        .street-view-image {
            width: 100%;
            height: 200px;
            border-radius: 10px;
            object-fit: cover;
        }
        
        #map, #aerial-map {
            width: 100%;
            height: 200px;
            border-radius: 10px;
        }
        
        .view-details-btn {
            background: #667eea;
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 10px;
            font-weight: 600;
            cursor: pointer;
            display: block;
            margin: 20px auto 0;
            transition: all 0.3s ease;
        }
        
        .view-details-btn:hover {
            background: #5a67d8;
            transform: translateY(-2px);
        }
        
        /* Professionals Section */
        .professionals-section {
            padding: 40px 30px;
        }
        
        .professionals-title {
            text-align: center;
            color: white;
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 30px;
        }
        
        .professionals-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .professional-card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 25px;
            border-left: 5px solid #667eea;
            transition: transform 0.3s ease;
        }
        
        .professional-card:hover {
            transform: translateY(-5px);
        }
        
        .professional-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 10px;
        }
        
        .professional-title {
            font-size: 1.2rem;
            font-weight: 700;
            color: #333;
        }
        
        .verified-badge {
            background: #10b981;
            color: white;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        
        .unverified-badge {
            background: #ef4444;
            color: white;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        
        .professional-location {
            color: #666;
            font-size: 0.9rem;
            margin-bottom: 10px;
        }
        
        .professional-description {
            color: #555;
            line-height: 1.5;
            margin-bottom: 15px;
        }
        
        .website-btn {
            background: #667eea;
            color: white;
            padding: 8px 16px;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            transition: all 0.3s ease;
        }
        
        .website-btn:hover {
            background: #5a67d8;
        }
        
        /* Responsive Design */
        @media (max-width: 768px) {
            .property-details-container {
                grid-template-columns: 1fr;
            }
            
            .search-form {
                flex-direction: column;
                gap: 15px;
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
            <a href="/login" class="btn btn-login">Login</a>
            <a href="/get-started" class="btn btn-primary">Get Started</a>
        </div>
    </header>
    
    <!-- Search Section -->
    <section class="search-section">
        <div class="search-card">
            <form action="/property-results" method="POST" class="search-form">
                <div class="form-group">
                    <label class="form-label">Address</label>
                    <input 
                        type="text" 
                        name="address" 
                        class="address-input"
                        value="{{ property_data.address }}"
                        placeholder="123 Pine Street, Any City, WA, 54321"
                        required
                    >
                </div>
                <button type="submit" class="btn-search">Search</button>
                <button type="button" class="btn-clear" onclick="clearForm()">Clear</button>
            </form>
        </div>
    </section>
    
    <!-- Results Section -->
    <section class="results-section">
        <div class="property-header">
            <h1 class="property-title">{{ property_data.address }}</h1>
        </div>
        
        <div class="property-details-container">
            <div class="property-details">
                <h2 class="details-title">Property Details</h2>
                <div class="detail-row">
                    <span class="detail-label">Estimated Value:</span>
                    <span class="detail-value">{{ property_data.estimated_value }}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Bedrooms:</span>
                    <span class="detail-value">{{ property_data.bedrooms }}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Bathrooms:</span>
                    <span class="detail-value">{{ property_data.bathrooms }}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Square Feet:</span>
                    <span class="detail-value">{{ property_data.square_feet }}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Year Built:</span>
                    <span class="detail-value">{{ property_data.year_built }}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Monthly Rent Est:</span>
                    <span class="detail-value">{{ property_data.monthly_rent }}</span>
                </div>
            </div>
            
            <div class="visual-section">
                <div class="street-view-container">
                    <h3 class="visual-title">Street View</h3>
                    <img 
                        src="https://maps.googleapis.com/maps/api/streetview?size=400x200&location={{ property_data.lat }},{{ property_data.lng }}&key={{ google_maps_api_key }}"
                        alt="Street View"
                        class="street-view-image"
                    >
                </div>
                
                <div class="map-container">
                    <h3 class="visual-title">Aerial View (2 blocks)</h3>
                    <div id="aerial-map"></div>
                </div>
                
                <button class="view-details-btn" onclick="showDetails()">View Details</button>
            </div>
        </div>
    </section>
    
    <!-- Professionals Section -->
    <section class="professionals-section">
        <h2 class="professionals-title">Local Professionals in {{ city_state }}</h2>
        <div class="professionals-grid">
            {% for professional in professionals %}
            <div class="professional-card">
                <div class="professional-header">
                    <h3 class="professional-title">{{ professional.title }}</h3>
                    {% if professional.verified %}
                        <span class="verified-badge">✅ Verified</span>
                    {% else %}
                        <span class="unverified-badge">❌ Unverified</span>
                    {% endif %}
                </div>
                <div class="professional-location">{{ professional.location }}</div>
                <div class="professional-description">{{ professional.description }}</div>
                <a href="{{ professional.website }}" class="website-btn" target="_blank">Website</a>
            </div>
            {% endfor %}
        </div>
    </section>
    
    <script>
        function initMap() {
            const propertyLocation = { lat: {{ property_data.lat }}, lng: {{ property_data.lng }} };
            
            const map = new google.maps.Map(document.getElementById("aerial-map"), {
                zoom: 16,
                center: propertyLocation,
                mapTypeId: 'satellite'
            });
            
            new google.maps.Marker({
                position: propertyLocation,
                map: map,
                title: "{{ property_data.address }}"
            });
        }
        
        function showDetails() {
            window.location.href = '/property-details?address=' + encodeURIComponent('{{ property_data.address }}');
        }
        
        function clearForm() {
            document.querySelector('.address-input').value = '';
        }
        
        // Initialize map when page loads
        window.onload = initMap;
    </script>
</body>
</html>
    ''', 
    property_data=property_data, 
    professionals=professionals, 
    city_state=city_state,
    google_maps_api_key=GOOGLE_MAPS_API_KEY)

@app.route('/property-details')
def property_details():
    address = request.args.get('address', '')
    
    # Get coordinates for the address
    lat, lng = get_coordinates(address)
    
    # Generate comparable properties
    comparable_properties = generate_comparable_properties(address, lat, lng)
    
    # Mock property data
    property_data = {
        'address': address,
        'estimated_value': '$500,000',
        'bedrooms': '4',
        'bathrooms': '2',
        'square_feet': '1,492',
        'year_built': '1964',
        'monthly_rent': '$3,000',
        'rent_low': '$2,700',
        'rent_high': '$3,300',
        'lat': lat,
        'lng': lng
    }
    
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Property Details - BlueDwarf</title>
    <script src="https://maps.googleapis.com/maps/api/js?key={{ google_maps_api_key }}&libraries=geometry"></script>
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
        
        /* Content */
        .content {
            padding: 30px;
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .page-title {
            text-align: center;
            color: white;
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 30px;
        }
        
        /* Rent Estimation */
        .rent-section {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
        }
        
        .rent-title {
            color: #667eea;
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 20px;
        }
        
        .rent-estimate {
            font-size: 2rem;
            font-weight: 700;
            color: #333;
            text-align: center;
            margin-bottom: 20px;
        }
        
        .rent-range {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        
        .rent-range-slider {
            width: 100%;
            height: 20px;
            background: linear-gradient(to right, #10b981 0%, #3b82f6 100%);
            border-radius: 10px;
            position: relative;
        }
        
        .rent-labels {
            display: flex;
            justify-content: space-between;
            font-weight: 600;
            color: #666;
        }
        
        /* Comparable Properties Map */
        .map-section {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
        }
        
        .map-title {
            color: #333;
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 10px;
        }
        
        .map-description {
            color: #666;
            margin-bottom: 20px;
        }
        
        #comparable-map {
            width: 100%;
            height: 400px;
            border-radius: 10px;
        }
        
        /* Comparable Properties Cards */
        .comparables-section {
            background: rgba(255, 152, 0, 0.1);
            border-radius: 20px;
            padding: 30px;
        }
        
        .comparables-title {
            color: #d97706;
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 10px;
        }
        
        .comparables-subtitle {
            color: #666;
            margin-bottom: 20px;
        }
        
        .comparables-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
        
        .comparable-card {
            background: white;
            border-radius: 15px;
            padding: 20px;
            border-left: 5px solid #d97706;
            position: relative;
        }
        
        .comparable-number {
            position: absolute;
            top: -10px;
            left: -10px;
            background: #d97706;
            color: white;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
        }
        
        .comparable-address {
            font-weight: 700;
            color: #333;
            margin-bottom: 5px;
        }
        
        .comparable-location {
            color: #666;
            font-size: 0.9rem;
            margin-bottom: 10px;
        }
        
        .comparable-details {
            color: #555;
            margin-bottom: 10px;
        }
        
        .comparable-specs {
            font-size: 0.9rem;
            color: #666;
        }
        
        /* Back Button */
        .back-btn {
            background: #667eea;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 10px;
            font-weight: 600;
            cursor: pointer;
            margin-bottom: 20px;
            text-decoration: none;
            display: inline-block;
        }
        
        .back-btn:hover {
            background: #5a67d8;
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
            <a href="/get-started" class="btn btn-primary">Get Started</a>
        </div>
    </header>
    
    <div class="content">
        <a href="javascript:history.back()" class="back-btn">← Back to Results</a>
        
        <h1 class="page-title">{{ property_data.address }}</h1>
        
        <!-- Rent Estimation Section -->
        <div class="rent-section">
            <h2 class="rent-title">Estimated Monthly Rent: {{ property_data.monthly_rent }}</h2>
            
            <div class="rent-range">
                <div style="width: 100%;">
                    <div class="rent-range-slider"></div>
                    <div class="rent-labels">
                        <span>Low Estimate<br>{{ property_data.rent_low }}</span>
                        <span>High Estimate<br>{{ property_data.rent_high }}</span>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Comparable Properties Map -->
        <div class="map-section">
            <h2 class="map-title">Comparable Properties Map with Numbered Flags</h2>
            <p class="map-description">Interactive map showing numbered flags for each comparable property location.</p>
            <div id="comparable-map"></div>
        </div>
        
        <!-- Comparable Properties Cards -->
        <div class="comparables-section">
            <h2 class="comparables-title">Comparable Properties from Same Area</h2>
            <p class="comparables-subtitle">Comparable properties from {{ property_data.address.split(',')[-2] if ',' in property_data.address else 'Sacramento' }}, CA within 1.5 mile radius.</p>
            
            <div class="comparables-grid">
                {% for property in comparable_properties %}
                <div class="comparable-card">
                    <div class="comparable-number">{{ property.id }}</div>
                    <div class="comparable-address">{{ property.address }}</div>
                    <div class="comparable-location">{{ property.city }} {{ property.zip }}</div>
                    <div class="comparable-details">{{ property.beds }} bed, {{ property.baths }} bath</div>
                    <div class="comparable-specs">{{ property.sqft }} sq ft • Built {{ property.year_built }}<br>{{ property.days_on_market }} days on market</div>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>
    
    <script>
        function initComparableMap() {
            const propertyLocation = { lat: {{ property_data.lat }}, lng: {{ property_data.lng }} };
            const comparableProperties = {{ comparable_properties | tojsonfilter }};
            
            const map = new google.maps.Map(document.getElementById("comparable-map"), {
                zoom: 14,
                center: propertyLocation,
                mapTypeId: 'roadmap'
            });
            
            // Main property marker (red)
            new google.maps.Marker({
                position: propertyLocation,
                map: map,
                title: "{{ property_data.address }}",
                icon: {
                    url: 'https://maps.google.com/mapfiles/ms/icons/red-dot.png'
                }
            });
            
            // Comparable property markers (numbered)
            comparableProperties.forEach(function(property) {
                const marker = new google.maps.Marker({
                    position: { lat: property.lat, lng: property.lng },
                    map: map,
                    title: property.address,
                    label: {
                        text: property.id.toString(),
                        color: 'white',
                        fontWeight: 'bold'
                    },
                    icon: {
                        url: 'https://maps.google.com/mapfiles/ms/icons/blue-dot.png'
                    }
                });
                
                const infoWindow = new google.maps.InfoWindow({
                    content: `
                        <div style="padding: 10px;">
                            <h4>${property.address}</h4>
                            <p>${property.city} ${property.zip}</p>
                            <p>${property.beds} bed, ${property.baths} bath</p>
                            <p>${property.sqft} sq ft • Built ${property.year_built}</p>
                        </div>
                    `
                });
                
                marker.addListener('click', function() {
                    infoWindow.open(map, marker);
                });
            });
        }
        
        // Initialize map when page loads
        window.onload = initComparableMap;
    </script>
</body>
</html>
    ''', 
    property_data=property_data, 
    comparable_properties=comparable_properties,
    google_maps_api_key=GOOGLE_MAPS_API_KEY)

@app.route('/get-started')
def get_started():
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Get Started - BlueDwarf</title>
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
        
        /* Registration Form */
        .registration-container {
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: calc(100vh - 80px);
            padding: 20px;
        }
        
        .registration-card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 40px;
            max-width: 500px;
            width: 100%;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
        }
        
        .registration-title {
            text-align: center;
            color: #333;
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 30px;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-label {
            display: block;
            color: #333;
            font-weight: 600;
            margin-bottom: 8px;
        }
        
        .required {
            color: #ef4444;
        }
        
        .form-input, .form-select, .form-textarea {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e5e7eb;
            border-radius: 10px;
            font-size: 1rem;
            transition: border-color 0.3s ease;
        }
        
        .form-input:focus, .form-select:focus, .form-textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .form-textarea {
            resize: vertical;
            min-height: 80px;
        }
        
        .register-btn {
            width: 100%;
            background: #667eea;
            color: white;
            padding: 15px;
            border: none;
            border-radius: 10px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-top: 20px;
        }
        
        .register-btn:hover {
            background: #5a67d8;
            transform: translateY(-2px);
        }
        
        .login-link {
            text-align: center;
            margin-top: 20px;
            color: #666;
        }
        
        .login-link a {
            color: #667eea;
            text-decoration: none;
            font-weight: 600;
        }
        
        .login-link a:hover {
            text-decoration: underline;
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
        </div>
    </header>
    
    <!-- Registration Form -->
    <div class="registration-container">
        <div class="registration-card">
            <h1 class="registration-title">Professional Registration</h1>
            
            <form action="/register-step-2" method="POST">
                <div class="form-group">
                    <label class="form-label">Full Name <span class="required">*</span></label>
                    <input type="text" name="full_name" class="form-input" required>
                </div>
                
                <div class="form-group">
                    <label class="form-label">Phone <span class="required">*</span></label>
                    <input type="tel" name="phone" class="form-input" required>
                </div>
                
                <div class="form-group">
                    <label class="form-label">Email <span class="required">*</span></label>
                    <input type="email" name="email" class="form-input" required>
                </div>
                
                <div class="form-group">
                    <label class="form-label">Business Address <span class="required">*</span></label>
                    <input type="text" name="business_address" class="form-input" placeholder="123 Main St, City, State, ZIP" required>
                </div>
                
                <div class="form-group">
                    <label class="form-label">License Number</label>
                    <input type="text" name="license_number" class="form-input" placeholder="Optional">
                </div>
                
                <div class="form-group">
                    <label class="form-label">Domain Name</label>
                    <input type="text" name="domain_name" class="form-input" placeholder="yourcompany.com">
                </div>
                
                <div class="form-group">
                    <label class="form-label">Profession <span class="required">*</span></label>
                    <select name="profession" class="form-select" required>
                        <option value="">Select profession</option>
                        <option value="Real Estate Agent">Real Estate Agent</option>
                        <option value="Mortgage Lender">Mortgage Lender</option>
                        <option value="Real Estate Attorney">Real Estate Attorney</option>
                        <option value="Property Inspector">Property Inspector</option>
                        <option value="Insurance Agent">Insurance Agent</option>
                        <option value="Property Manager">Property Manager</option>
                        <option value="General Contractor">General Contractor</option>
                        <option value="Property Appraiser">Property Appraiser</option>
                        <option value="Title Company">Title Company</option>
                        <option value="Other">Other</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label class="form-label">Service ZIP Codes <span class="required">*</span></label>
                    <textarea name="service_zip_codes" class="form-textarea" placeholder="95628, 95814, 95630" required></textarea>
                </div>
                
                <div class="form-group">
                    <label class="form-label">Password <span class="required">*</span></label>
                    <input type="password" name="password" class="form-input" required>
                </div>
                
                <button type="submit" class="register-btn">Continue to License Verification</button>
            </form>
            
            <div class="login-link">
                Already have an account? <a href="/login">Login here</a>
            </div>
        </div>
    </div>
</body>
</html>
    ''')

@app.route('/register-step-2', methods=['POST'])
def register_step_2():
    # Store registration data in session
    session['registration_data'] = {
        'full_name': request.form.get('full_name'),
        'phone': request.form.get('phone'),
        'email': request.form.get('email'),
        'business_address': request.form.get('business_address'),
        'license_number': request.form.get('license_number'),
        'domain_name': request.form.get('domain_name'),
        'profession': request.form.get('profession'),
        'service_zip_codes': request.form.get('service_zip_codes'),
        'password': request.form.get('password')
    }
    
    # Redirect to verification page (step 2)
    return redirect(url_for('verify_license'))

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
        
        /* Verification Container */
        .verification-container {
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: calc(100vh - 80px);
            padding: 20px;
        }
        
        .verification-card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 40px;
            max-width: 600px;
            width: 100%;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
        }
        
        .verification-title {
            text-align: center;
            color: #333;
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 10px;
        }
        
        .verification-subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
        }
        
        /* Progress Steps */
        .progress-steps {
            display: flex;
            justify-content: space-between;
            margin-bottom: 40px;
            position: relative;
        }
        
        .progress-steps::before {
            content: '';
            position: absolute;
            top: 20px;
            left: 0;
            right: 0;
            height: 2px;
            background: #e5e7eb;
            z-index: 1;
        }
        
        .step {
            display: flex;
            flex-direction: column;
            align-items: center;
            position: relative;
            z-index: 2;
        }
        
        .step-circle {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: #e5e7eb;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            color: #666;
            margin-bottom: 8px;
        }
        
        .step.active .step-circle {
            background: #667eea;
            color: white;
        }
        
        .step.completed .step-circle {
            background: #10b981;
            color: white;
        }
        
        .step-label {
            font-size: 0.9rem;
            color: #666;
            text-align: center;
        }
        
        /* Verification Form */
        .verification-form {
            display: none;
        }
        
        .verification-form.active {
            display: block;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-label {
            display: block;
            color: #333;
            font-weight: 600;
            margin-bottom: 8px;
        }
        
        .required {
            color: #ef4444;
        }
        
        .form-input {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e5e7eb;
            border-radius: 10px;
            font-size: 1rem;
            transition: border-color 0.3s ease;
        }
        
        .form-input:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .file-upload {
            border: 2px dashed #667eea;
            border-radius: 10px;
            padding: 30px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .file-upload:hover {
            background: rgba(102, 126, 234, 0.05);
        }
        
        .file-upload-icon {
            font-size: 3rem;
            color: #667eea;
            margin-bottom: 10px;
        }
        
        .file-upload-text {
            color: #333;
            font-weight: 600;
            margin-bottom: 5px;
        }
        
        .file-upload-subtext {
            color: #666;
            font-size: 0.9rem;
        }
        
        .camera-section {
            text-align: center;
            padding: 30px;
            border: 2px solid #e5e7eb;
            border-radius: 10px;
        }
        
        .camera-icon {
            font-size: 4rem;
            color: #667eea;
            margin-bottom: 15px;
        }
        
        .camera-text {
            color: #333;
            font-weight: 600;
            margin-bottom: 10px;
        }
        
        .camera-subtext {
            color: #666;
            font-size: 0.9rem;
            margin-bottom: 20px;
        }
        
        .camera-btn {
            background: #667eea;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 10px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .camera-btn:hover {
            background: #5a67d8;
        }
        
        .next-btn, .back-btn {
            padding: 12px 24px;
            border: none;
            border-radius: 10px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            margin: 10px 5px;
        }
        
        .next-btn {
            background: #667eea;
            color: white;
        }
        
        .next-btn:hover {
            background: #5a67d8;
        }
        
        .back-btn {
            background: #6b7280;
            color: white;
        }
        
        .back-btn:hover {
            background: #4b5563;
        }
        
        .button-group {
            text-align: center;
            margin-top: 30px;
        }
        
        .success-message {
            text-align: center;
            padding: 40px;
        }
        
        .success-icon {
            font-size: 4rem;
            color: #10b981;
            margin-bottom: 20px;
        }
        
        .success-title {
            color: #333;
            font-size: 1.5rem;
            font-weight: 700;
            margin-bottom: 10px;
        }
        
        .success-text {
            color: #666;
            margin-bottom: 20px;
        }
        
        .dashboard-btn {
            background: #10b981;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 10px;
            font-weight: 600;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            transition: all 0.3s ease;
        }
        
        .dashboard-btn:hover {
            background: #059669;
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
            <a href="/get-started" class="btn btn-primary">Get Started</a>
        </div>
    </header>
    
    <!-- Verification Container -->
    <div class="verification-container">
        <div class="verification-card">
            <h1 class="verification-title">Professional License Verification</h1>
            <p class="verification-subtitle">Complete your professional verification in 4 simple steps</p>
            
            <!-- Progress Steps -->
            <div class="progress-steps">
                <div class="step active" id="step-1">
                    <div class="step-circle">1</div>
                    <div class="step-label">Personal Info</div>
                </div>
                <div class="step" id="step-2">
                    <div class="step-circle">2</div>
                    <div class="step-label">Upload License</div>
                </div>
                <div class="step" id="step-3">
                    <div class="step-circle">3</div>
                    <div class="step-label">Take Selfie</div>
                </div>
                <div class="step" id="step-4">
                    <div class="step-circle">4</div>
                    <div class="step-label">Verification</div>
                </div>
            </div>
            
            <!-- Step 1: Personal Information -->
            <div class="verification-form active" id="form-1">
                <div class="form-group">
                    <label class="form-label">First Name <span class="required">*</span></label>
                    <input type="text" class="form-input" required>
                </div>
                
                <div class="form-group">
                    <label class="form-label">Last Name <span class="required">*</span></label>
                    <input type="text" class="form-input" required>
                </div>
                
                <div class="form-group">
                    <label class="form-label">Email <span class="required">*</span></label>
                    <input type="email" class="form-input" required>
                </div>
                
                <div class="form-group">
                    <label class="form-label">Phone Number <span class="required">*</span></label>
                    <input type="tel" class="form-input" required>
                </div>
                
                <div class="button-group">
                    <button class="next-btn" onclick="nextStep(1)">Next Step</button>
                </div>
            </div>
            
            <!-- Step 2: Upload License -->
            <div class="verification-form" id="form-2">
                <div class="form-group">
                    <label class="form-label">Professional License Document <span class="required">*</span></label>
                    <div class="file-upload" onclick="document.getElementById('license-upload').click()">
                        <div class="file-upload-icon">📄</div>
                        <div class="file-upload-text">Upload License Document</div>
                        <div class="file-upload-subtext">PDF, JPG, PNG (Max 16MB)</div>
                    </div>
                    <input type="file" id="license-upload" style="display: none;" accept=".pdf,.jpg,.jpeg,.png">
                </div>
                
                <div class="button-group">
                    <button class="back-btn" onclick="prevStep(2)">Back</button>
                    <button class="next-btn" onclick="nextStep(2)">Next Step</button>
                </div>
            </div>
            
            <!-- Step 3: Take Selfie -->
            <div class="verification-form" id="form-3">
                <div class="camera-section">
                    <div class="camera-icon">📸</div>
                    <div class="camera-text">Take a Live Selfie</div>
                    <div class="camera-subtext">We'll use facial recognition to verify your identity</div>
                    <button class="camera-btn">Start Camera</button>
                </div>
                
                <div class="button-group">
                    <button class="back-btn" onclick="prevStep(3)">Back</button>
                    <button class="next-btn" onclick="nextStep(3)">Next Step</button>
                </div>
            </div>
            
            <!-- Step 4: Verification Complete -->
            <div class="verification-form" id="form-4">
                <div class="success-message">
                    <div class="success-icon">✅</div>
                    <div class="success-title">Verification Complete!</div>
                    <div class="success-text">Your professional license has been successfully verified. You can now access all professional features.</div>
                    <a href="/dashboard" class="dashboard-btn">Go to Dashboard</a>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let currentStep = 1;
        
        function nextStep(step) {
            if (step < 4) {
                // Hide current form
                document.getElementById(`form-${step}`).classList.remove('active');
                document.getElementById(`step-${step}`).classList.add('completed');
                document.getElementById(`step-${step}`).classList.remove('active');
                
                // Show next form
                currentStep = step + 1;
                document.getElementById(`form-${currentStep}`).classList.add('active');
                document.getElementById(`step-${currentStep}`).classList.add('active');
            }
        }
        
        function prevStep(step) {
            if (step > 1) {
                // Hide current form
                document.getElementById(`form-${step}`).classList.remove('active');
                document.getElementById(`step-${step}`).classList.remove('active');
                
                // Show previous form
                currentStep = step - 1;
                document.getElementById(`form-${currentStep}`).classList.add('active');
                document.getElementById(`step-${currentStep}`).classList.add('active');
                document.getElementById(`step-${currentStep}`).classList.remove('completed');
            }
        }
    </script>
</body>
</html>
    ''')

@app.route('/login')
def login():
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - BlueDwarf</title>
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
        }
        
        .login-card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 40px;
            max-width: 400px;
            width: 100%;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
        }
        
        .login-title {
            text-align: center;
            color: #333;
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 30px;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-label {
            display: block;
            color: #333;
            font-weight: 600;
            margin-bottom: 8px;
        }
        
        .form-input {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e5e7eb;
            border-radius: 10px;
            font-size: 1rem;
            transition: border-color 0.3s ease;
        }
        
        .form-input:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .login-btn {
            width: 100%;
            background: #667eea;
            color: white;
            padding: 15px;
            border: none;
            border-radius: 10px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-top: 20px;
        }
        
        .login-btn:hover {
            background: #5a67d8;
            transform: translateY(-2px);
        }
        
        .register-link {
            text-align: center;
            margin-top: 20px;
            color: #666;
        }
        
        .register-link a {
            color: #667eea;
            text-decoration: none;
            font-weight: 600;
        }
        
        .back-link {
            text-align: center;
            margin-bottom: 20px;
        }
        
        .back-link a {
            color: #667eea;
            text-decoration: none;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <div class="login-card">
        <div class="back-link">
            <a href="/">← Back to Home</a>
        </div>
        
        <h1 class="login-title">Login</h1>
        
        <form>
            <div class="form-group">
                <label class="form-label">Email</label>
                <input type="email" class="form-input" required>
            </div>
            
            <div class="form-group">
                <label class="form-label">Password</label>
                <input type="password" class="form-input" required>
            </div>
            
            <button type="submit" class="login-btn">Login</button>
        </form>
        
        <div class="register-link">
            Don't have an account? <a href="/get-started">Get Started</a>
        </div>
    </div>
</body>
</html>
    ''')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

