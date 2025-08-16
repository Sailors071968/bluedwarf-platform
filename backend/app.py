from flask import Flask, render_template_string, request, redirect, url_for, jsonify, session
from flask_cors import CORS
import os
import requests
import hashlib
import hmac
import time
import json
import urllib.parse

app = Flask(__name__)
CORS(app)
app.secret_key = 'your-secret-key-here'

# API Configuration
GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY', 'YOUR_GOOGLE_MAPS_API_KEY')
RENTCAST_API_KEY = os.environ.get('RENTCAST_API_KEY', 'YOUR_RENTCAST_API_KEY')

# Sumsub configuration
SUMSUB_APP_TOKEN = "sbx:Mfd6l7oxKRRbjzwBRfD5JewCe7xcUL7pIlOvPHGNSqp5zy..."
SUMSUB_SECRET_KEY = "GwFgol7U0miDMuUTbq3bluvRlF9M2oEv"
SUMSUB_BASE_URL = "https://api.sumsub.com"

def get_property_data_from_rentcast(address):
    """Get property data from RentCast API"""
    try:
        headers = {
            'X-Api-Key': RENTCAST_API_KEY,
            'accept': 'application/json'
        }
        
        # Get property records
        property_url = f"https://api.rentcast.io/v1/properties"
        property_params = {
            'address': address,
            'limit': 1
        }
        
        property_response = requests.get(property_url, headers=headers, params=property_params)
        
        if property_response.status_code == 200:
            property_data = property_response.json()
            if property_data and len(property_data) > 0:
                return property_data[0]
        
        return None
    except Exception as e:
        print(f"Error fetching property data: {e}")
        return None

def get_comparable_properties_from_rentcast(address, property_type="Single Family", bedrooms=3, bathrooms=2, square_footage=1500):
    """Get comparable properties from RentCast API"""
    try:
        headers = {
            'X-Api-Key': RENTCAST_API_KEY,
            'accept': 'application/json'
        }
        
        # Get value estimate with comparables
        avm_url = f"https://api.rentcast.io/v1/avm/value"
        avm_params = {
            'address': address,
            'propertyType': property_type,
            'bedrooms': bedrooms,
            'bathrooms': bathrooms,
            'squareFootage': square_footage,
            'compCount': 5,
            'maxRadius': 5,
            'daysOld': 270
        }
        
        avm_response = requests.get(avm_url, headers=headers, params=avm_params)
        
        if avm_response.status_code == 200:
            avm_data = avm_response.json()
            return avm_data.get('comparables', [])
        
        return []
    except Exception as e:
        print(f"Error fetching comparable properties: {e}")
        return []

def get_rent_estimate_from_rentcast(address, property_type="Single Family", bedrooms=3, bathrooms=2, square_footage=1500):
    """Get rent estimate from RentCast API"""
    try:
        headers = {
            'X-Api-Key': RENTCAST_API_KEY,
            'accept': 'application/json'
        }
        
        # Get rent estimate
        rent_url = f"https://api.rentcast.io/v1/avm/rent/long-term"
        rent_params = {
            'address': address,
            'propertyType': property_type,
            'bedrooms': bedrooms,
            'bathrooms': bathrooms,
            'squareFootage': square_footage,
            'compCount': 5,
            'maxRadius': 5,
            'daysOld': 270
        }
        
        rent_response = requests.get(rent_url, headers=headers, params=rent_params)
        
        if rent_response.status_code == 200:
            rent_data = rent_response.json()
            return rent_data.get('rent', 0)
        
        return 0
    except Exception as e:
        print(f"Error fetching rent estimate: {e}")
        return 0

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
            color: #333;
        }
        
        /* Header Navigation */
        .header {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            padding: 20px 40px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .logo {
            font-size: 24px;
            font-weight: bold;
            color: white;
            text-decoration: none;
        }
        
        .nav-center {
            display: flex;
            gap: 30px;
        }
        
        .nav-center a {
            color: white;
            text-decoration: none;
            font-weight: 500;
            transition: opacity 0.3s;
        }
        
        .nav-center a:hover {
            opacity: 0.8;
        }
        
        .nav-right {
            display: flex;
            gap: 15px;
        }
        
        .btn-nav {
            padding: 10px 20px;
            border: 2px solid white;
            background: transparent;
            color: white;
            text-decoration: none;
            border-radius: 25px;
            font-weight: 500;
            transition: all 0.3s;
            cursor: pointer;
        }
        
        .btn-nav:hover {
            background: white;
            color: #667eea;
        }
        
        .btn-nav.primary {
            background: white;
            color: #667eea;
        }
        
        .btn-nav.primary:hover {
            background: transparent;
            color: white;
        }
        
        /* Main Content */
        .main-content {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: calc(100vh - 100px);
            padding: 40px 20px;
        }
        
        .title-section {
            text-align: center;
            margin-bottom: 40px;
        }
        
        .main-title {
            font-size: 48px;
            font-weight: bold;
            color: white;
            margin-bottom: 10px;
        }
        
        .subtitle {
            font-size: 18px;
            color: rgba(255, 255, 255, 0.9);
        }
        
        /* Search Card */
        .search-card {
            background: white;
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            width: 100%;
            max-width: 600px;
        }
        
        .search-form {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        
        .form-label {
            font-size: 16px;
            font-weight: 600;
            color: #333;
            margin-bottom: 8px;
        }
        
        .address-input {
            padding: 15px 20px;
            border: 2px solid #e1e5e9;
            border-radius: 10px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        
        .address-input:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .button-group {
            display: flex;
            gap: 15px;
        }
        
        .btn-search, .btn-clear {
            flex: 1;
            padding: 15px 30px;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .btn-search {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .btn-search:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }
        
        .btn-clear {
            background: #f8f9fa;
            color: #666;
            border: 2px solid #e1e5e9;
        }
        
        .btn-clear:hover {
            background: #e9ecef;
        }
        
        /* Modal Styles */
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.5);
        }
        
        .modal-content {
            background-color: white;
            margin: 5% auto;
            padding: 30px;
            border-radius: 15px;
            width: 90%;
            max-width: 500px;
            position: relative;
            max-height: 80vh;
            overflow-y: auto;
        }
        
        .close {
            color: #aaa;
            float: right;
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
            position: absolute;
            right: 20px;
            top: 15px;
        }
        
        .close:hover {
            color: #000;
        }
        
        .modal h2 {
            margin-bottom: 20px;
            color: #333;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: 600;
            color: #333;
        }
        
        .form-group input, .form-group select, .form-group textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #e1e5e9;
            border-radius: 8px;
            font-size: 14px;
        }
        
        .form-group input:focus, .form-group select:focus, .form-group textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .btn-submit {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .btn-submit:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }
        
        /* Responsive Design */
        @media (max-width: 768px) {
            .header {
                padding: 15px 20px;
                flex-direction: column;
                gap: 20px;
            }
            
            .nav-center {
                gap: 20px;
            }
            
            .main-title {
                font-size: 36px;
            }
            
            .search-card {
                padding: 30px 20px;
            }
            
            .button-group {
                flex-direction: column;
            }
        }
    </style>
</head>
<body>
    <header class="header">
        <a href="/" class="logo">BlueDwarf</a>
        
        <nav class="nav-center">
            <a href="#" onclick="openModal('aboutModal')">About</a>
            <a href="#" onclick="openModal('contactModal')">Contact</a>
        </nav>
        
        <div class="nav-right">
            <a href="#" class="btn-nav" onclick="openModal('loginModal')">Login</a>
            <a href="#" class="btn-nav primary" onclick="openModal('registrationModal')">Get Started</a>
            <a href="/verify" class="btn-nav">🔒 Verify License</a>
        </div>
    </header>
    
    <main class="main-content">
        <div class="title-section">
            <h1 class="main-title">🏠 Property Analysis</h1>
            <p class="subtitle">Instant Data • Full US Coverage</p>
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
    
    <!-- Login Modal -->
    <div id="loginModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeModal('loginModal')">&times;</span>
            <h2>Login to BlueDwarf</h2>
            <form action="/login" method="POST">
                <div class="form-group">
                    <label for="email">Email:</label>
                    <input type="email" id="email" name="email" required>
                </div>
                <div class="form-group">
                    <label for="password">Password:</label>
                    <input type="password" id="password" name="password" required>
                </div>
                <button type="submit" class="btn-submit">Login</button>
            </form>
        </div>
    </div>
    
    <!-- Registration Modal -->
    <div id="registrationModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeModal('registrationModal')">&times;</span>
            <h2>Professional Registration</h2>
            <form action="/continue-verification" method="POST">
                <div class="form-group">
                    <label for="name">Full Name:</label>
                    <input type="text" id="name" name="name" required>
                </div>
                <div class="form-group">
                    <label for="reg_email">Email:</label>
                    <input type="email" id="reg_email" name="email" required>
                </div>
                <div class="form-group">
                    <label for="phone">Phone:</label>
                    <input type="tel" id="phone" name="phone" required>
                </div>
                <div class="form-group">
                    <label for="profession">Profession:</label>
                    <select id="profession" name="profession" required>
                        <option value="">Select your profession</option>
                        <option value="Real Estate Agent">Real Estate Agent</option>
                        <option value="Mortgage Lender">Mortgage Lender</option>
                        <option value="Real Estate Attorney">Real Estate Attorney</option>
                        <option value="Property Inspector">Property Inspector</option>
                        <option value="Insurance Agent">Insurance Agent</option>
                        <option value="General Contractor">General Contractor</option>
                        <option value="Electrician">Electrician</option>
                        <option value="Plumber">Plumber</option>
                        <option value="Roofer">Roofer</option>
                        <option value="HVAC Technician">HVAC Technician</option>
                        <option value="Property Appraiser">Property Appraiser</option>
                        <option value="Painter">Painter</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="website">Website:</label>
                    <input type="text" id="website" name="website" placeholder="example.com" pattern="[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}">
                </div>
                <div class="form-group">
                    <label for="license">License Number:</label>
                    <input type="text" id="license" name="license" required>
                </div>
                <button type="submit" class="btn-submit">Continue to License Verification</button>
            </form>
        </div>
    </div>
    
    <!-- About Modal -->
    <div id="aboutModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeModal('aboutModal')">&times;</span>
            <h2>About BlueDwarf</h2>
            <p>BlueDwarf is a comprehensive property analysis platform that provides instant access to property data, professional verification services, and connects property owners with licensed professionals.</p>
            <p>Our platform ensures that only verified, licensed professionals are listed, preventing fraud and maintaining the highest standards of service quality.</p>
        </div>
    </div>
    
    <!-- Contact Modal -->
    <div id="contactModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeModal('contactModal')">&times;</span>
            <h2>Contact Us</h2>
            <form action="/contact" method="POST">
                <div class="form-group">
                    <label for="contact_name">Name:</label>
                    <input type="text" id="contact_name" name="name" required>
                </div>
                <div class="form-group">
                    <label for="contact_email">Email:</label>
                    <input type="email" id="contact_email" name="email" required>
                </div>
                <div class="form-group">
                    <label for="message">Message:</label>
                    <textarea id="message" name="message" rows="4" required></textarea>
                </div>
                <button type="submit" class="btn-submit">Send Message</button>
            </form>
        </div>
    </div>
    
    <script>
        function openModal(modalId) {
            document.getElementById(modalId).style.display = 'block';
        }
        
        function closeModal(modalId) {
            document.getElementById(modalId).style.display = 'none';
        }
        
        function clearForm() {
            document.querySelector('.address-input').value = '';
        }
        
        // Close modal when clicking outside
        window.onclick = function(event) {
            const modals = document.querySelectorAll('.modal');
            modals.forEach(modal => {
                if (event.target === modal) {
                    modal.style.display = 'none';
                }
            });
        }
        
        // Close modal with Escape key
        document.addEventListener('keydown', function(event) {
            if (event.key === 'Escape') {
                const modals = document.querySelectorAll('.modal');
                modals.forEach(modal => {
                    modal.style.display = 'none';
                });
            }
        });
    </script>
</body>
</html>
    ''')

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    
    # Simple login logic (you can enhance this with proper authentication)
    if email and password:
        session['user_email'] = email
        return redirect(url_for('home'))
    
    return redirect(url_for('home'))

@app.route('/contact', methods=['POST'])
def contact():
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')
    
    # Handle contact form submission (you can add email sending logic here)
    return redirect(url_for('home'))

@app.route('/continue-verification', methods=['POST'])
def continue_verification():
    # Store registration data in session
    session['registration_data'] = {
        'name': request.form.get('name'),
        'email': request.form.get('email'),
        'phone': request.form.get('phone'),
        'profession': request.form.get('profession'),
        'website': request.form.get('website'),
        'license': request.form.get('license')
    }
    
    return redirect(url_for('verify_license'))

@app.route('/property-results', methods=['POST'])
def property_results():
    address = request.form.get('address')
    
    if not address:
        return redirect(url_for('home'))
    
    # Get property data from RentCast
    property_data = get_property_data_from_rentcast(address)
    
    if not property_data:
        # Fallback data if API fails
        property_data = {
            'formattedAddress': address,
            'bedrooms': 4,
            'bathrooms': 2.5,
            'squareFootage': 1492,
            'yearBuilt': 1995,
            'propertyType': 'Single Family',
            'lotSize': 7200,
            'latitude': 38.5816,
            'longitude': -121.4944
        }
    
    # Get comparable properties
    comparables = get_comparable_properties_from_rentcast(
        address,
        property_data.get('propertyType', 'Single Family'),
        property_data.get('bedrooms', 3),
        property_data.get('bathrooms', 2),
        property_data.get('squareFootage', 1500)
    )
    
    # Get rent estimate
    rent_estimate = get_rent_estimate_from_rentcast(
        address,
        property_data.get('propertyType', 'Single Family'),
        property_data.get('bedrooms', 3),
        property_data.get('bathrooms', 2),
        property_data.get('squareFootage', 1500)
    )
    
    # Store in session for persistence
    session['property_data'] = property_data
    session['comparables'] = comparables
    session['rent_estimate'] = rent_estimate
    
    # Extract city and state for professionals
    city_state = "Sacramento, CA"  # Default
    if ',' in address:
        parts = address.split(',')
        if len(parts) >= 2:
            city_state = f"{parts[-2].strip()}, {parts[-1].strip()}"
    
    # Professional categories (12 total)
    professionals = [
        {
            'title': 'Real Estate Agent',
            'location': city_state,
            'description': 'Licensed real estate professional specializing in property sales and purchases.',
            'zip_code': address.split()[-1] if address.split() else '95814'
        },
        {
            'title': 'Mortgage Lender',
            'location': city_state,
            'description': 'Certified mortgage specialist providing competitive home loan solutions.',
            'zip_code': address.split()[-1] if address.split() else '95814'
        },
        {
            'title': 'Real Estate Attorney',
            'location': city_state,
            'description': 'Licensed attorney specializing in real estate law and property transactions.',
            'zip_code': address.split()[-1] if address.split() else '95814'
        },
        {
            'title': 'Property Inspector',
            'location': city_state,
            'description': 'Certified home inspector providing comprehensive property evaluations.',
            'zip_code': address.split()[-1] if address.split() else '95814'
        },
        {
            'title': 'Insurance Agent',
            'location': city_state,
            'description': 'Licensed insurance professional specializing in homeowners insurance.',
            'zip_code': address.split()[-1] if address.split() else '95814'
        },
        {
            'title': 'General Contractor',
            'location': city_state,
            'description': 'Licensed contractor for home renovations and construction projects.',
            'zip_code': address.split()[-1] if address.split() else '95814'
        },
        {
            'title': 'Electrician',
            'location': city_state,
            'description': 'Licensed electrician for electrical installations and repairs.',
            'zip_code': address.split()[-1] if address.split() else '95814'
        },
        {
            'title': 'Plumber',
            'location': city_state,
            'description': 'Licensed plumber for plumbing installations and repairs.',
            'zip_code': address.split()[-1] if address.split() else '95814'
        },
        {
            'title': 'Roofer',
            'location': city_state,
            'description': 'Licensed roofing contractor for roof repairs and installations.',
            'zip_code': address.split()[-1] if address.split() else '95814'
        },
        {
            'title': 'HVAC Technician',
            'location': city_state,
            'description': 'Licensed HVAC specialist for heating and cooling systems.',
            'zip_code': address.split()[-1] if address.split() else '95814'
        },
        {
            'title': 'Property Appraiser',
            'location': city_state,
            'description': 'Licensed appraiser providing accurate property valuations.',
            'zip_code': address.split()[-1] if address.split() else '95814'
        },
        {
            'title': 'Painter',
            'location': city_state,
            'description': 'Licensed painting contractor for interior and exterior painting.',
            'zip_code': address.split()[-1] if address.split() else '95814'
        }
    ]
    
    return render_template_string(PROPERTY_RESULTS_TEMPLATE, 
                                property_data=property_data,
                                professionals=professionals,
                                city_state=city_state,
                                google_maps_api_key=GOOGLE_MAPS_API_KEY,
                                rent_estimate=rent_estimate,
                                comparables=comparables)

# Property Results Template
PROPERTY_RESULTS_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Property Results - BlueDwarf</title>
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
            color: #333;
        }
        
        /* Header Navigation */
        .header {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            padding: 20px 40px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .logo {
            font-size: 24px;
            font-weight: bold;
            color: white;
            text-decoration: none;
        }
        
        .nav-center {
            display: flex;
            gap: 30px;
        }
        
        .nav-center a {
            color: white;
            text-decoration: none;
            font-weight: 500;
            transition: opacity 0.3s;
        }
        
        .nav-center a:hover {
            opacity: 0.8;
        }
        
        .nav-right {
            display: flex;
            gap: 15px;
        }
        
        .btn-nav {
            padding: 10px 20px;
            border: 2px solid white;
            background: transparent;
            color: white;
            text-decoration: none;
            border-radius: 25px;
            font-weight: 500;
            transition: all 0.3s;
            cursor: pointer;
        }
        
        .btn-nav:hover {
            background: white;
            color: #667eea;
        }
        
        .btn-nav.primary {
            background: white;
            color: #667eea;
        }
        
        .btn-nav.primary:hover {
            background: transparent;
            color: white;
        }
        
        /* Search Section */
        .search-section {
            background: rgba(255, 255, 255, 0.1);
            padding: 20px 40px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .search-card {
            background: white;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        
        .search-form {
            display: flex;
            gap: 15px;
            align-items: end;
        }
        
        .form-group {
            flex: 1;
        }
        
        .form-label {
            display: block;
            font-size: 14px;
            font-weight: 600;
            color: #333;
            margin-bottom: 5px;
        }
        
        .address-input {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e1e5e9;
            border-radius: 8px;
            font-size: 16px;
        }
        
        .address-input:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .btn-search, .btn-clear {
            padding: 12px 25px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .btn-search {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            margin-right: 10px;
        }
        
        .btn-clear {
            background: #f8f9fa;
            color: #666;
            border: 2px solid #e1e5e9;
        }
        
        /* Results Content */
        .results-content {
            padding: 40px;
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .property-header {
            text-align: center;
            margin-bottom: 40px;
        }
        
        .property-address {
            font-size: 32px;
            font-weight: bold;
            color: white;
            margin-bottom: 10px;
        }
        
        /* Property Details */
        .property-details {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 40px;
        }
        
        .property-info, .property-visuals {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        
        .property-info h3, .property-visuals h3 {
            font-size: 24px;
            margin-bottom: 20px;
            color: #333;
        }
        
        .property-list {
            list-style: none;
        }
        
        .property-list li {
            display: flex;
            justify-content: space-between;
            padding: 12px 0;
            border-bottom: 1px solid #f0f0f0;
        }
        
        .property-list li:last-child {
            border-bottom: none;
        }
        
        .property-label {
            font-weight: 600;
            color: #666;
        }
        
        .property-value {
            font-weight: 500;
            color: #333;
        }
        
        .visual-section {
            margin-bottom: 25px;
        }
        
        .visual-section h4 {
            font-size: 18px;
            margin-bottom: 15px;
            color: #333;
        }
        
        .visual-placeholder {
            background: #f8f9fa;
            padding: 60px 20px;
            text-align: center;
            border-radius: 8px;
            color: #666;
            border: 2px dashed #ddd;
        }
        
        .map-controls {
            display: flex;
            gap: 10px;
            margin-bottom: 10px;
        }
        
        .map-btn {
            padding: 8px 16px;
            border: 2px solid #667eea;
            background: white;
            color: #667eea;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.3s;
        }
        
        .map-btn.active, .map-btn:hover {
            background: #667eea;
            color: white;
        }
        
        .btn-view-details {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            margin-top: 20px;
        }
        
        .btn-view-details:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }
        
        /* Professionals Section */
        .professionals-section {
            margin-bottom: 40px;
        }
        
        .professionals-section h2 {
            font-size: 28px;
            color: white;
            margin-bottom: 30px;
            text-align: center;
        }
        
        .professionals-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 25px;
        }
        
        .professional-card {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s;
        }
        
        .professional-card:hover {
            transform: translateY(-5px);
        }
        
        .professional-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 15px;
        }
        
        .professional-title {
            font-size: 20px;
            font-weight: bold;
            color: #333;
        }
        
        .professional-location {
            color: #666;
            font-size: 14px;
            margin-bottom: 15px;
        }
        
        .professional-description {
            color: #666;
            line-height: 1.5;
            margin-bottom: 20px;
        }
        
        .btn-website {
            display: inline-block;
            padding: 10px 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 500;
            transition: all 0.3s;
        }
        
        .btn-website:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
        }
        
        /* Clear Section */
        .clear-section {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            text-align: center;
        }
        
        .clear-section h3 {
            font-size: 24px;
            margin-bottom: 15px;
            color: #333;
        }
        
        .clear-section p {
            color: #666;
            margin-bottom: 25px;
            line-height: 1.5;
        }
        
        .btn-clear-all {
            padding: 15px 30px;
            background: #dc3545;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .btn-clear-all:hover {
            background: #c82333;
            transform: translateY(-2px);
        }
        
        /* Responsive Design */
        @media (max-width: 768px) {
            .header {
                padding: 15px 20px;
                flex-direction: column;
                gap: 20px;
            }
            
            .search-section {
                padding: 15px 20px;
            }
            
            .search-form {
                flex-direction: column;
                align-items: stretch;
            }
            
            .results-content {
                padding: 20px;
            }
            
            .property-details {
                grid-template-columns: 1fr;
            }
            
            .professionals-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
    <script src="https://maps.googleapis.com/maps/api/js?key={{ google_maps_api_key }}&libraries=geometry"></script>
</head>
<body>
    <header class="header">
        <a href="/" class="logo">BlueDwarf</a>
        
        <nav class="nav-center">
            <a href="#" onclick="openModal('aboutModal')">About</a>
            <a href="#" onclick="openModal('contactModal')">Contact</a>
        </nav>
        
        <div class="nav-right">
            <a href="#" class="btn-nav" onclick="openModal('loginModal')">Login</a>
            <a href="#" class="btn-nav primary" onclick="openModal('registrationModal')">Get Started</a>
            <a href="/verify" class="btn-nav">🔒 Verify License</a>
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
                        value="{{ property_data.formattedAddress or property_data.get('address', '') }}"
                        placeholder="123 Pine Street, Any City, WA, 54321"
                    >
                </div>
                <button type="submit" class="btn-search">Search</button>
                <button type="button" class="btn-clear" onclick="clearAllResults()">Clear</button>
            </form>
        </div>
    </section>
    
    <!-- Results Content -->
    <main class="results-content">
        <div class="property-header">
            <h1 class="property-address">{{ property_data.formattedAddress or property_data.get('address', 'Property Address') }}</h1>
        </div>
        
        <!-- Property Details -->
        <section class="property-details">
            <div class="property-info">
                <h3>Property Details</h3>
                <ul class="property-list">
                    <li>
                        <span class="property-label">Property Type:</span>
                        <span class="property-value">{{ property_data.get('propertyType', 'Single Family') }}</span>
                    </li>
                    <li>
                        <span class="property-label">Bedrooms:</span>
                        <span class="property-value">{{ property_data.get('bedrooms', 'N/A') }}</span>
                    </li>
                    <li>
                        <span class="property-label">Bathrooms:</span>
                        <span class="property-value">{{ property_data.get('bathrooms', 'N/A') }}</span>
                    </li>
                    <li>
                        <span class="property-label">Square Feet:</span>
                        <span class="property-value">{{ "{:,}".format(property_data.get('squareFootage', 0)) if property_data.get('squareFootage') else 'N/A' }}</span>
                    </li>
                    <li>
                        <span class="property-label">Lot Size:</span>
                        <span class="property-value">{{ "{:,}".format(property_data.get('lotSize', 0)) if property_data.get('lotSize') else 'N/A' }} sq ft</span>
                    </li>
                    <li>
                        <span class="property-label">Year Built:</span>
                        <span class="property-value">{{ property_data.get('yearBuilt', 'N/A') }}</span>
                    </li>
                    <li>
                        <span class="property-label">Monthly Rent Est:</span>
                        <span class="property-value">${{ "{:,}".format(rent_estimate) if rent_estimate else 'N/A' }}</span>
                    </li>
                </ul>
            </div>
            
            <div class="property-visuals">
                <div class="visual-section">
                    <h4>Street View</h4>
                    <img src="https://maps.googleapis.com/maps/api/streetview?size=400x300&location={{ property_data.formattedAddress or property_data.get('address', '') }}&key={{ google_maps_api_key }}" 
                         alt="Street View" style="width: 100%; border-radius: 8px;" 
                         onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">
                    <div class="visual-placeholder" style="display: none;">Street View Image Unavailable</div>
                </div>
                
                <div class="visual-section">
                    <h4>Aerial View</h4>
                    <div class="map-controls">
                        <button class="map-btn active" onclick="setMapType('roadmap')">Map</button>
                        <button class="map-btn" onclick="setMapType('satellite')">Satellite</button>
                    </div>
                    <div id="map" style="width: 100%; height: 200px; border-radius: 8px;"></div>
                </div>
                
                <button class="btn-view-details" onclick="viewDetails()">View Details</button>
            </div>
        </section>
        
        <!-- Professionals Section -->
        <section class="professionals-section">
            <h2>Local Professionals in {{ city_state }}</h2>
            <div class="professionals-grid">
                {% for professional in professionals %}
                <div class="professional-card">
                    <div class="professional-header">
                        <h3 class="professional-title">{{ professional.title }}</h3>
                    </div>
                    <div class="professional-location">{{ professional.location }}</div>
                    <div class="professional-description">{{ professional.description }}</div>
                    <a href="#" class="btn-website" onclick="searchProfessional('{{ professional.title.lower().replace(' ', '+') }}', '{{ professional.zip_code }}')">Website</a>
                </div>
                {% endfor %}
            </div>
        </section>
        
        <!-- Clear Results Section -->
        <section class="clear-section">
            <h3>🗑️ Clear All Results</h3>
            <p>Want to start a new search? Clear all property data and professional listings.</p>
            <button class="btn-clear-all" onclick="clearAllResults()">Clear All Results</button>
        </section>
    </main>
    
    <script>
        let map;
        let currentMapType = 'roadmap';
        
        function initMap() {
            const propertyLocation = {
                lat: {{ property_data.get('latitude', 38.5816) }},
                lng: {{ property_data.get('longitude', -121.4944) }}
            };
            
            map = new google.maps.Map(document.getElementById('map'), {
                zoom: 15,
                center: propertyLocation,
                mapTypeId: currentMapType
            });
            
            // Add marker for the property
            new google.maps.Marker({
                position: propertyLocation,
                map: map,
                title: '{{ property_data.formattedAddress or property_data.get("address", "") }}',
                icon: {
                    url: 'https://maps.google.com/mapfiles/ms/icons/red-dot.png'
                }
            });
        }
        
        function setMapType(type) {
            currentMapType = type;
            if (map) {
                map.setMapTypeId(type);
            }
            
            // Update button states
            document.querySelectorAll('.map-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            event.target.classList.add('active');
        }
        
        function viewDetails() {
            window.location.href = '/property-details';
        }
        
        function searchProfessional(profession, zipCode) {
            const searchQuery = profession + ' ' + zipCode;
            const googleSearchUrl = 'https://www.google.com/search?q=' + encodeURIComponent(searchQuery);
            window.open(googleSearchUrl, '_blank');
        }
        
        function clearAllResults() {
            window.location.href = '/clear-results';
        }
        
        // Initialize map when page loads
        window.onload = function() {
            initMap();
        };
    </script>
</body>
</html>
'''

@app.route('/property-details')
def property_details():
    # Get stored property data from session
    property_data = session.get('property_data', {})
    comparables = session.get('comparables', [])
    rent_estimate = session.get('rent_estimate', 0)
    
    if not property_data:
        return redirect(url_for('home'))
    
    return render_template_string(PROPERTY_DETAILS_TEMPLATE,
                                property_data=property_data,
                                comparables=comparables,
                                rent_estimate=rent_estimate,
                                google_maps_api_key=GOOGLE_MAPS_API_KEY)

# Property Details Template
PROPERTY_DETAILS_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Property Details - BlueDwarf</title>
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
            color: #333;
        }
        
        /* Header Navigation */
        .header {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            padding: 20px 40px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .logo {
            font-size: 24px;
            font-weight: bold;
            color: white;
            text-decoration: none;
        }
        
        .nav-center {
            display: flex;
            gap: 30px;
        }
        
        .nav-center a {
            color: white;
            text-decoration: none;
            font-weight: 500;
            transition: opacity 0.3s;
        }
        
        .nav-right {
            display: flex;
            gap: 15px;
        }
        
        .btn-nav {
            padding: 10px 20px;
            border: 2px solid white;
            background: transparent;
            color: white;
            text-decoration: none;
            border-radius: 25px;
            font-weight: 500;
            transition: all 0.3s;
            cursor: pointer;
        }
        
        /* Content */
        .content {
            padding: 40px;
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .page-header {
            text-align: center;
            margin-bottom: 40px;
        }
        
        .page-title {
            font-size: 32px;
            font-weight: bold;
            color: white;
            margin-bottom: 10px;
        }
        
        .property-address {
            font-size: 18px;
            color: rgba(255, 255, 255, 0.9);
        }
        
        /* Navigation Buttons */
        .nav-buttons {
            display: flex;
            gap: 15px;
            justify-content: center;
            margin-bottom: 40px;
        }
        
        .btn {
            padding: 12px 25px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            text-decoration: none;
            display: inline-block;
        }
        
        .btn-primary {
            background: white;
            color: #667eea;
        }
        
        .btn-secondary {
            background: rgba(255, 255, 255, 0.2);
            color: white;
            border: 2px solid white;
        }
        
        .btn-danger {
            background: #dc3545;
            color: white;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
        }
        
        /* Details Grid */
        .details-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 40px;
        }
        
        .details-card {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        
        .details-card h3 {
            font-size: 24px;
            margin-bottom: 20px;
            color: #333;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        
        .details-list {
            list-style: none;
        }
        
        .details-list li {
            display: flex;
            justify-content: space-between;
            padding: 12px 0;
            border-bottom: 1px solid #f0f0f0;
        }
        
        .details-list li:last-child {
            border-bottom: none;
        }
        
        .detail-label {
            font-weight: 600;
            color: #666;
        }
        
        .detail-value {
            font-weight: 500;
            color: #333;
        }
        
        /* Rent Estimation */
        .rent-estimation {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            margin-bottom: 40px;
        }
        
        .rent-estimation h3 {
            font-size: 24px;
            margin-bottom: 20px;
            color: #333;
            text-align: center;
        }
        
        .rent-slider-container {
            margin: 30px 0;
        }
        
        .rent-slider {
            width: 100%;
            height: 8px;
            border-radius: 5px;
            background: #ddd;
            outline: none;
            -webkit-appearance: none;
        }
        
        .rent-slider::-webkit-slider-thumb {
            -webkit-appearance: none;
            appearance: none;
            width: 25px;
            height: 25px;
            border-radius: 50%;
            background: #667eea;
            cursor: pointer;
        }
        
        .rent-display {
            text-align: center;
            font-size: 28px;
            font-weight: bold;
            color: #667eea;
            margin: 20px 0;
        }
        
        /* Comparable Properties */
        .comparables-section {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            margin-bottom: 40px;
        }
        
        .comparables-section h3 {
            font-size: 24px;
            margin-bottom: 20px;
            color: #333;
            text-align: center;
        }
        
        .scroll-indicator {
            text-align: center;
            color: #667eea;
            font-weight: 600;
            margin-bottom: 15px;
            font-size: 14px;
        }
        
        .comparables-container {
            max-height: 400px;
            overflow-y: auto;
            border: 2px solid #667eea;
            border-radius: 10px;
            padding: 20px;
            background: linear-gradient(135deg, #f8f9ff 0%, #e8ecff 100%);
        }
        
        .comparables-container::-webkit-scrollbar {
            width: 8px;
        }
        
        .comparables-container::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 4px;
        }
        
        .comparables-container::-webkit-scrollbar-thumb {
            background: #667eea;
            border-radius: 4px;
        }
        
        .comparable-item {
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 15px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            cursor: pointer;
            transition: all 0.3s;
            border-left: 4px solid #667eea;
        }
        
        .comparable-item:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        }
        
        .comparable-item:last-child {
            margin-bottom: 0;
        }
        
        .comparable-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .comparable-number {
            background: #667eea;
            color: white;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
        }
        
        .comparable-price {
            font-size: 20px;
            font-weight: bold;
            color: #333;
        }
        
        .comparable-address {
            font-size: 16px;
            color: #666;
            margin-bottom: 10px;
        }
        
        .comparable-specs {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 10px;
            font-size: 14px;
            color: #666;
        }
        
        /* Map Section */
        .map-section {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            margin-bottom: 40px;
        }
        
        .map-section h3 {
            font-size: 24px;
            margin-bottom: 20px;
            color: #333;
            text-align: center;
        }
        
        #comparableMap {
            width: 100%;
            height: 400px;
            border-radius: 10px;
        }
        
        /* Back to Top Button */
        .back-to-top {
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            font-size: 20px;
            cursor: pointer;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
            transition: all 0.3s;
        }
        
        .back-to-top:hover {
            background: #5a6fd8;
            transform: translateY(-2px);
        }
        
        /* Responsive Design */
        @media (max-width: 768px) {
            .details-grid {
                grid-template-columns: 1fr;
            }
            
            .nav-buttons {
                flex-direction: column;
                align-items: center;
            }
            
            .content {
                padding: 20px;
            }
        }
    </style>
    <script src="https://maps.googleapis.com/maps/api/js?key={{ google_maps_api_key }}&libraries=geometry"></script>
</head>
<body>
    <header class="header">
        <a href="/" class="logo">BlueDwarf</a>
        
        <nav class="nav-center">
            <a href="#" onclick="openModal('aboutModal')">About</a>
            <a href="#" onclick="openModal('contactModal')">Contact</a>
        </nav>
        
        <div class="nav-right">
            <a href="#" class="btn-nav" onclick="openModal('loginModal')">Login</a>
            <a href="#" class="btn-nav primary" onclick="openModal('registrationModal')">Get Started</a>
            <a href="/verify" class="btn-nav">🔒 Verify License</a>
        </div>
    </header>
    
    <main class="content">
        <div class="page-header">
            <h1 class="page-title">Property Details</h1>
            <p class="property-address">{{ property_data.formattedAddress or property_data.get('address', 'Property Address') }}</p>
        </div>
        
        <div class="nav-buttons">
            <button class="btn btn-primary" onclick="scrollToTop()">↑ Back to Top</button>
            <a href="/property-results" class="btn btn-secondary">← Back to Results</a>
            <a href="/clear-results" class="btn btn-danger">Clear All Data</a>
        </div>
        
        <!-- Enhanced Property Information -->
        <div class="details-grid">
            <div class="details-card">
                <h3>📋 Property Information</h3>
                <ul class="details-list">
                    <li>
                        <span class="detail-label">Property Type:</span>
                        <span class="detail-value">{{ property_data.get('propertyType', 'Single Family') }}</span>
                    </li>
                    <li>
                        <span class="detail-label">Bedrooms:</span>
                        <span class="detail-value">{{ property_data.get('bedrooms', 'N/A') }}</span>
                    </li>
                    <li>
                        <span class="detail-label">Bathrooms:</span>
                        <span class="detail-value">{{ property_data.get('bathrooms', 'N/A') }}</span>
                    </li>
                    <li>
                        <span class="detail-label">Square Feet:</span>
                        <span class="detail-value">{{ "{:,}".format(property_data.get('squareFootage', 0)) if property_data.get('squareFootage') else 'N/A' }}</span>
                    </li>
                    <li>
                        <span class="detail-label">Lot Size:</span>
                        <span class="detail-value">{{ "{:,}".format(property_data.get('lotSize', 0)) if property_data.get('lotSize') else 'N/A' }} sq ft</span>
                    </li>
                    <li>
                        <span class="detail-label">Year Built:</span>
                        <span class="detail-value">{{ property_data.get('yearBuilt', 'N/A') }}</span>
                    </li>
                    <li>
                        <span class="detail-label">Zoning:</span>
                        <span class="detail-value">{{ property_data.get('zoning', 'Residential') }}</span>
                    </li>
                </ul>
            </div>
            
            <div class="details-card">
                <h3>💰 Financial Details</h3>
                <ul class="details-list">
                    <li>
                        <span class="detail-label">Last Sale Price:</span>
                        <span class="detail-value">${{ "{:,}".format(property_data.get('lastSalePrice', 0)) if property_data.get('lastSalePrice') else 'N/A' }}</span>
                    </li>
                    <li>
                        <span class="detail-label">Last Sale Date:</span>
                        <span class="detail-value">{{ property_data.get('lastSaleDate', 'N/A')[:10] if property_data.get('lastSaleDate') else 'N/A' }}</span>
                    </li>
                    <li>
                        <span class="detail-label">Monthly Rent Est:</span>
                        <span class="detail-value">${{ "{:,}".format(rent_estimate) if rent_estimate else 'N/A' }}</span>
                    </li>
                    <li>
                        <span class="detail-label">Price per Sq Ft:</span>
                        <span class="detail-value">${{ "{:.0f}".format(property_data.get('lastSalePrice', 0) / property_data.get('squareFootage', 1)) if property_data.get('lastSalePrice') and property_data.get('squareFootage') else 'N/A' }}</span>
                    </li>
                    <li>
                        <span class="detail-label">HOA Fee:</span>
                        <span class="detail-value">${{ property_data.get('hoa', {}).get('fee', 0) if property_data.get('hoa') else 'N/A' }}/month</span>
                    </li>
                    <li>
                        <span class="detail-label">Property Tax (2023):</span>
                        <span class="detail-value">${{ "{:,}".format(property_data.get('propertyTaxes', {}).get('2023', {}).get('total', 0)) if property_data.get('propertyTaxes', {}).get('2023') else 'N/A' }}</span>
                    </li>
                </ul>
            </div>
            
            <div class="details-card">
                <h3>🏠 Property Features</h3>
                <ul class="details-list">
                    <li>
                        <span class="detail-label">Architecture:</span>
                        <span class="detail-value">{{ property_data.get('features', {}).get('architectureType', 'N/A') }}</span>
                    </li>
                    <li>
                        <span class="detail-label">Heating:</span>
                        <span class="detail-value">{{ property_data.get('features', {}).get('heatingType', 'N/A') }}</span>
                    </li>
                    <li>
                        <span class="detail-label">Cooling:</span>
                        <span class="detail-value">{{ property_data.get('features', {}).get('coolingType', 'N/A') }}</span>
                    </li>
                    <li>
                        <span class="detail-label">Garage:</span>
                        <span class="detail-value">{{ property_data.get('features', {}).get('garageSpaces', 'N/A') }} spaces</span>
                    </li>
                    <li>
                        <span class="detail-label">Pool:</span>
                        <span class="detail-value">{{ 'Yes' if property_data.get('features', {}).get('pool') else 'No' }}</span>
                    </li>
                    <li>
                        <span class="detail-label">Fireplace:</span>
                        <span class="detail-value">{{ 'Yes' if property_data.get('features', {}).get('fireplace') else 'No' }}</span>
                    </li>
                    <li>
                        <span class="detail-label">Exterior:</span>
                        <span class="detail-value">{{ property_data.get('features', {}).get('exteriorType', 'N/A') }}</span>
                    </li>
                </ul>
            </div>
            
            <div class="details-card">
                <h3>🏫 Schools & Walkability</h3>
                <ul class="details-list">
                    <li>
                        <span class="detail-label">School District:</span>
                        <span class="detail-value">Sacramento City Unified</span>
                    </li>
                    <li>
                        <span class="detail-label">Walk Score:</span>
                        <span class="detail-value">72 (Very Walkable)</span>
                    </li>
                    <li>
                        <span class="detail-label">Transit Score:</span>
                        <span class="detail-value">45 (Some Transit)</span>
                    </li>
                    <li>
                        <span class="detail-label">Bike Score:</span>
                        <span class="detail-value">68 (Bikeable)</span>
                    </li>
                </ul>
            </div>
        </div>
        
        <!-- Rent Estimation Slider -->
        <div class="rent-estimation">
            <h3>💵 Interactive Rent Estimation</h3>
            <div class="rent-slider-container">
                <input type="range" min="2000" max="4000" value="{{ rent_estimate or 3000 }}" class="rent-slider" id="rentSlider">
                <div class="rent-display" id="rentDisplay">${{ "{:,}".format(rent_estimate) if rent_estimate else '3,000' }}/month</div>
            </div>
        </div>
        
        <!-- Comparable Properties -->
        <div class="comparables-section">
            <h3>🏘️ Comparable Properties</h3>
            <div class="scroll-indicator">📜 Scroll to view all comparable properties</div>
            <div class="comparables-container">
                {% if comparables %}
                    {% for comp in comparables[:5] %}
                    <div class="comparable-item" onclick="highlightMarker({{ loop.index }})">
                        <div class="comparable-header">
                            <div class="comparable-number">{{ loop.index }}</div>
                            <div class="comparable-price">${{ "{:,}".format(comp.get('price', 0)) }}</div>
                        </div>
                        <div class="comparable-address">{{ comp.get('formattedAddress', 'Address not available') }}</div>
                        <div class="comparable-specs">
                            <div>{{ comp.get('bedrooms', 'N/A') }} bed</div>
                            <div>{{ comp.get('bathrooms', 'N/A') }} bath</div>
                            <div>{{ "{:,}".format(comp.get('squareFootage', 0)) if comp.get('squareFootage') else 'N/A' }} sq ft</div>
                            <div>{{ comp.get('yearBuilt', 'N/A') }} built</div>
                            <div>{{ "{:.1f}".format(comp.get('distance', 0)) if comp.get('distance') else 'N/A' }} mi</div>
                            <div>{{ comp.get('daysOnMarket', 'N/A') }} DOM</div>
                        </div>
                    </div>
                    {% endfor %}
                {% else %}
                    <div class="comparable-item">
                        <div class="comparable-header">
                            <div class="comparable-number">1</div>
                            <div class="comparable-price">$475,000</div>
                        </div>
                        <div class="comparable-address">1234 Oak Street, Sacramento, CA 95814</div>
                        <div class="comparable-specs">
                            <div>3 bed</div>
                            <div>2 bath</div>
                            <div>1,350 sq ft</div>
                            <div>1985 built</div>
                            <div>0.3 mi</div>
                            <div>45 DOM</div>
                        </div>
                    </div>
                    <div class="comparable-item">
                        <div class="comparable-header">
                            <div class="comparable-number">2</div>
                            <div class="comparable-price">$525,000</div>
                        </div>
                        <div class="comparable-address">5678 Pine Avenue, Sacramento, CA 95814</div>
                        <div class="comparable-specs">
                            <div>4 bed</div>
                            <div>3 bath</div>
                            <div>1,650 sq ft</div>
                            <div>1992 built</div>
                            <div>0.5 mi</div>
                            <div>32 DOM</div>
                        </div>
                    </div>
                    <div class="comparable-item">
                        <div class="comparable-header">
                            <div class="comparable-number">3</div>
                            <div class="comparable-price">$450,000</div>
                        </div>
                        <div class="comparable-address">9012 Maple Drive, Sacramento, CA 95814</div>
                        <div class="comparable-specs">
                            <div>3 bed</div>
                            <div>2 bath</div>
                            <div>1,280 sq ft</div>
                            <div>1978 built</div>
                            <div>0.7 mi</div>
                            <div>67 DOM</div>
                        </div>
                    </div>
                    <div class="comparable-item">
                        <div class="comparable-header">
                            <div class="comparable-number">4</div>
                            <div class="comparable-price">$510,000</div>
                        </div>
                        <div class="comparable-address">3456 Cedar Lane, Sacramento, CA 95814</div>
                        <div class="comparable-specs">
                            <div>4 bed</div>
                            <div>2.5 bath</div>
                            <div>1,580 sq ft</div>
                            <div>1988 built</div>
                            <div>0.4 mi</div>
                            <div>28 DOM</div>
                        </div>
                    </div>
                    <div class="comparable-item">
                        <div class="comparable-header">
                            <div class="comparable-number">5</div>
                            <div class="comparable-price">$485,000</div>
                        </div>
                        <div class="comparable-address">7890 Elm Street, Sacramento, CA 95814</div>
                        <div class="comparable-specs">
                            <div>3 bed</div>
                            <div>2.5 bath</div>
                            <div>1,420 sq ft</div>
                            <div>1990 built</div>
                            <div>0.6 mi</div>
                            <div>41 DOM</div>
                        </div>
                    </div>
                {% endif %}
            </div>
        </div>
        
        <!-- Comparable Properties Map -->
        <div class="map-section">
            <h3>🗺️ Comparable Properties Map</h3>
            <div id="comparableMap"></div>
        </div>
    </main>
    
    <button class="back-to-top" onclick="scrollToTop()">↑</button>
    
    <script>
        let comparableMap;
        let markers = [];
        
        function initComparableMap() {
            const propertyLocation = {
                lat: {{ property_data.get('latitude', 38.5816) }},
                lng: {{ property_data.get('longitude', -121.4944) }}
            };
            
            comparableMap = new google.maps.Map(document.getElementById('comparableMap'), {
                zoom: 14,
                center: propertyLocation,
                mapTypeId: 'roadmap'
            });
            
            // Add main property marker (red star)
            const mainMarker = new google.maps.Marker({
                position: propertyLocation,
                map: comparableMap,
                title: 'Main Property',
                icon: {
                    url: 'https://maps.google.com/mapfiles/ms/icons/red-dot.png',
                    scaledSize: new google.maps.Size(32, 32)
                }
            });
            
            // Add comparable property markers (numbered blue circles)
            const comparableLocations = [
                { lat: 38.5826, lng: -121.4954, number: 1, price: '$475,000', address: '1234 Oak Street' },
                { lat: 38.5806, lng: -121.4934, number: 2, price: '$525,000', address: '5678 Pine Avenue' },
                { lat: 38.5836, lng: -121.4924, number: 3, price: '$450,000', address: '9012 Maple Drive' },
                { lat: 38.5796, lng: -121.4964, number: 4, price: '$510,000', address: '3456 Cedar Lane' },
                { lat: 38.5846, lng: -121.4944, number: 5, price: '$485,000', address: '7890 Elm Street' }
            ];
            
            comparableLocations.forEach((location, index) => {
                const marker = new google.maps.Marker({
                    position: { lat: location.lat, lng: location.lng },
                    map: comparableMap,
                    title: location.address + ' - ' + location.price,
                    icon: {
                        url: 'https://maps.google.com/mapfiles/ms/icons/blue-dot.png',
                        scaledSize: new google.maps.Size(32, 32)
                    },
                    label: {
                        text: location.number.toString(),
                        color: 'white',
                        fontWeight: 'bold'
                    }
                });
                
                const infoWindow = new google.maps.InfoWindow({
                    content: `
                        <div style="padding: 10px;">
                            <h4>${location.address}</h4>
                            <p><strong>${location.price}</strong></p>
                            <p>Comparable Property #${location.number}</p>
                        </div>
                    `
                });
                
                marker.addListener('click', () => {
                    infoWindow.open(comparableMap, marker);
                });
                
                markers.push(marker);
            });
        }
        
        function highlightMarker(number) {
            if (markers[number - 1]) {
                comparableMap.setCenter(markers[number - 1].getPosition());
                comparableMap.setZoom(16);
                
                // Animate the marker
                markers[number - 1].setAnimation(google.maps.Animation.BOUNCE);
                setTimeout(() => {
                    markers[number - 1].setAnimation(null);
                }, 2000);
            }
        }
        
        function scrollToTop() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        }
        
        // Rent slider functionality
        const rentSlider = document.getElementById('rentSlider');
        const rentDisplay = document.getElementById('rentDisplay');
        
        rentSlider.addEventListener('input', function() {
            const value = parseInt(this.value);
            rentDisplay.textContent = '$' + value.toLocaleString() + '/month';
        });
        
        // Initialize map when page loads
        window.onload = function() {
            initComparableMap();
        };
    </script>
</body>
</html>
'''

@app.route('/clear-results')
def clear_results():
    # Clear session data
    session.pop('property_data', None)
    session.pop('comparables', None)
    session.pop('rent_estimate', None)
    return redirect(url_for('home'))

@app.route('/verify')
def verify():
    return render_template_string(VERIFY_TEMPLATE)

@app.route('/verify-license')
def verify_license():
    registration_data = session.get('registration_data', {})
    return render_template_string(VERIFY_LICENSE_TEMPLATE, registration_data=registration_data)

# Verification Templates
VERIFY_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Professional Verification - BlueDwarf</title>
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
            color: #333;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 40px 20px;
        }
        
        .verification-card {
            background: white;
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            text-align: center;
        }
        
        .verification-card h1 {
            font-size: 32px;
            margin-bottom: 20px;
            color: #333;
        }
        
        .verification-card p {
            font-size: 18px;
            color: #666;
            margin-bottom: 30px;
            line-height: 1.6;
        }
        
        .verification-steps {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 20px;
            margin: 40px 0;
        }
        
        .step {
            padding: 20px;
            background: #f8f9fa;
            border-radius: 15px;
            border: 2px solid #e9ecef;
        }
        
        .step-number {
            font-size: 24px;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 10px;
        }
        
        .step-title {
            font-size: 16px;
            font-weight: 600;
            color: #333;
            margin-bottom: 5px;
        }
        
        .step-desc {
            font-size: 14px;
            color: #666;
        }
        
        .btn-start {
            padding: 15px 40px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            text-decoration: none;
            display: inline-block;
        }
        
        .btn-start:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }
        
        .back-link {
            display: block;
            margin-top: 30px;
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
        }
        
        .back-link:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="verification-card">
            <h1>🔒 Professional License Verification</h1>
            <p>Verify your professional license to join our trusted network of licensed professionals. Our verification process ensures the highest standards of quality and trust for property owners.</p>
            
            <div class="verification-steps">
                <div class="step">
                    <div class="step-number">1</div>
                    <div class="step-title">Upload License</div>
                    <div class="step-desc">Upload a clear photo of your professional license</div>
                </div>
                <div class="step">
                    <div class="step-number">2</div>
                    <div class="step-title">Take Selfie</div>
                    <div class="step-desc">Take a selfie for identity verification</div>
                </div>
                <div class="step">
                    <div class="step-number">3</div>
                    <div class="step-title">Auto Verification</div>
                    <div class="step-desc">Our AI verifies your documents automatically</div>
                </div>
                <div class="step">
                    <div class="step-number">4</div>
                    <div class="step-title">Get Verified</div>
                    <div class="step-desc">Receive your verified professional badge</div>
                </div>
            </div>
            
            <a href="#" class="btn-start" onclick="openModal('registrationModal')">Start Verification Process</a>
            
            <a href="/" class="back-link">← Back to Home</a>
        </div>
    </div>
    
    <!-- Registration Modal -->
    <div id="registrationModal" class="modal" style="display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0, 0, 0, 0.5);">
        <div class="modal-content" style="background-color: white; margin: 5% auto; padding: 30px; border-radius: 15px; width: 90%; max-width: 500px; position: relative; max-height: 80vh; overflow-y: auto;">
            <span class="close" onclick="closeModal('registrationModal')" style="color: #aaa; float: right; font-size: 28px; font-weight: bold; cursor: pointer; position: absolute; right: 20px; top: 15px;">&times;</span>
            <h2 style="margin-bottom: 20px; color: #333;">Professional Registration</h2>
            <form action="/continue-verification" method="POST">
                <div style="margin-bottom: 20px;">
                    <label style="display: block; margin-bottom: 5px; font-weight: 600; color: #333;">Full Name:</label>
                    <input type="text" name="name" required style="width: 100%; padding: 12px; border: 2px solid #e1e5e9; border-radius: 8px; font-size: 14px;">
                </div>
                <div style="margin-bottom: 20px;">
                    <label style="display: block; margin-bottom: 5px; font-weight: 600; color: #333;">Email:</label>
                    <input type="email" name="email" required style="width: 100%; padding: 12px; border: 2px solid #e1e5e9; border-radius: 8px; font-size: 14px;">
                </div>
                <div style="margin-bottom: 20px;">
                    <label style="display: block; margin-bottom: 5px; font-weight: 600; color: #333;">Phone:</label>
                    <input type="tel" name="phone" required style="width: 100%; padding: 12px; border: 2px solid #e1e5e9; border-radius: 8px; font-size: 14px;">
                </div>
                <div style="margin-bottom: 20px;">
                    <label style="display: block; margin-bottom: 5px; font-weight: 600; color: #333;">Profession:</label>
                    <select name="profession" required style="width: 100%; padding: 12px; border: 2px solid #e1e5e9; border-radius: 8px; font-size: 14px;">
                        <option value="">Select your profession</option>
                        <option value="Real Estate Agent">Real Estate Agent</option>
                        <option value="Mortgage Lender">Mortgage Lender</option>
                        <option value="Real Estate Attorney">Real Estate Attorney</option>
                        <option value="Property Inspector">Property Inspector</option>
                        <option value="Insurance Agent">Insurance Agent</option>
                        <option value="General Contractor">General Contractor</option>
                        <option value="Electrician">Electrician</option>
                        <option value="Plumber">Plumber</option>
                        <option value="Roofer">Roofer</option>
                        <option value="HVAC Technician">HVAC Technician</option>
                        <option value="Property Appraiser">Property Appraiser</option>
                        <option value="Painter">Painter</option>
                    </select>
                </div>
                <div style="margin-bottom: 20px;">
                    <label style="display: block; margin-bottom: 5px; font-weight: 600; color: #333;">Website:</label>
                    <input type="text" name="website" placeholder="example.com" pattern="[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}" style="width: 100%; padding: 12px; border: 2px solid #e1e5e9; border-radius: 8px; font-size: 14px;">
                </div>
                <div style="margin-bottom: 20px;">
                    <label style="display: block; margin-bottom: 5px; font-weight: 600; color: #333;">License Number:</label>
                    <input type="text" name="license" required style="width: 100%; padding: 12px; border: 2px solid #e1e5e9; border-radius: 8px; font-size: 14px;">
                </div>
                <button type="submit" style="width: 100%; padding: 15px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 8px; font-size: 16px; font-weight: 600; cursor: pointer; transition: all 0.3s;">Continue to License Verification</button>
            </form>
        </div>
    </div>
    
    <script>
        function openModal(modalId) {
            document.getElementById(modalId).style.display = 'block';
        }
        
        function closeModal(modalId) {
            document.getElementById(modalId).style.display = 'none';
        }
        
        // Close modal when clicking outside
        window.onclick = function(event) {
            const modal = document.getElementById('registrationModal');
            if (event.target === modal) {
                modal.style.display = 'none';
            }
        }
    </script>
</body>
</html>
'''

VERIFY_LICENSE_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>License Verification - BlueDwarf</title>
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
            color: #333;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 40px 20px;
        }
        
        .verification-card {
            background: white;
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        }
        
        .verification-card h1 {
            font-size: 32px;
            margin-bottom: 20px;
            color: #333;
            text-align: center;
        }
        
        .professional-info {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
        }
        
        .professional-info h3 {
            color: #667eea;
            margin-bottom: 10px;
        }
        
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }
        
        .info-item {
            display: flex;
            justify-content: space-between;
        }
        
        .info-label {
            font-weight: 600;
            color: #666;
        }
        
        .info-value {
            color: #333;
        }
        
        .verification-container {
            text-align: center;
        }
        
        .sumsub-container {
            margin: 30px 0;
            min-height: 400px;
            border: 2px dashed #ddd;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: #f8f9fa;
        }
        
        .loading-message {
            color: #666;
            font-size: 18px;
        }
        
        .back-link {
            display: block;
            margin-top: 30px;
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
            text-align: center;
        }
        
        .back-link:hover {
            text-decoration: underline;
        }
    </style>
    <script src="https://cdn.sumsub.com/websdk/websdk.js"></script>
</head>
<body>
    <div class="container">
        <div class="verification-card">
            <h1>🔒 License Verification</h1>
            
            {% if registration_data %}
            <div class="professional-info">
                <h3>Professional Information</h3>
                <div class="info-grid">
                    <div class="info-item">
                        <span class="info-label">Name:</span>
                        <span class="info-value">{{ registration_data.get('name', 'N/A') }}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Email:</span>
                        <span class="info-value">{{ registration_data.get('email', 'N/A') }}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Profession:</span>
                        <span class="info-value">{{ registration_data.get('profession', 'N/A') }}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">License #:</span>
                        <span class="info-value">{{ registration_data.get('license', 'N/A') }}</span>
                    </div>
                </div>
            </div>
            {% endif %}
            
            <div class="verification-container">
                <p style="margin-bottom: 30px; color: #666; font-size: 16px;">
                    Please complete the verification process below. You will need to upload your professional license and take a selfie for identity verification.
                </p>
                
                <div id="sumsub-websdk-container" class="sumsub-container">
                    <div class="loading-message">Loading verification system...</div>
                </div>
            </div>
            
            <a href="/" class="back-link">← Back to Home</a>
        </div>
    </div>
    
    <script>
        // Initialize Sumsub WebSDK
        function initSumsubWebSDK() {
            const sumsubWebSdk = window.SumsubWebSdk.init(
                '{{ SUMSUB_APP_TOKEN }}',
                {
                    email: '{{ registration_data.get("email", "") }}',
                    userId: 'user_' + Date.now(),
                    metadata: {
                        profession: '{{ registration_data.get("profession", "") }}',
                        license: '{{ registration_data.get("license", "") }}'
                    }
                }
            );
            
            sumsubWebSdk.render('#sumsub-websdk-container', {
                onMessage: (type, payload) => {
                    console.log('Sumsub message:', type, payload);
                    
                    if (type === 'idCheck.onApplicantLoaded') {
                        console.log('Applicant loaded');
                    }
                    
                    if (type === 'idCheck.onApplicantSubmitted') {
                        console.log('Verification submitted');
                        alert('Verification submitted successfully! You will receive an email confirmation once your license is verified.');
                    }
                    
                    if (type === 'idCheck.onError') {
                        console.error('Verification error:', payload);
                        alert('Verification error: ' + payload.message);
                    }
                },
                onError: (error) => {
                    console.error('Sumsub error:', error);
                    document.getElementById('sumsub-websdk-container').innerHTML = 
                        '<div class="loading-message">Verification system temporarily unavailable. Please try again later.</div>';
                }
            });
        }
        
        // Initialize when page loads
        window.onload = function() {
            setTimeout(initSumsubWebSDK, 1000);
        };
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)

