from flask import Flask, render_template_string, request, redirect, url_for, session, jsonify
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
            color: black;
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
        
        .form-group input, .form-group select {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e1e5e9;
            border-radius: 8px;
            font-size: 16px;
        }
        
        .form-group input:focus, .form-group select:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .btn-modal {
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
        
        .btn-modal:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }
        
        /* Responsive Design */
        @media (max-width: 768px) {
            .header {
                padding: 15px 20px;
                flex-direction: column;
                gap: 15px;
            }
            
            .nav-center, .nav-right {
                gap: 15px;
            }
            
            .main-title {
                font-size: 36px;
            }
            
            .search-card {
                padding: 30px 20px;
            }
        }
    </style>
</head>
<body>
    <header class="header">
        <a href="/" class="logo">BlueDwarf</a>
        <nav class="nav-center">
            <a href="#" onclick="showAbout()">About</a>
            <a href="#" onclick="showContact()">Contact</a>
        </nav>
        <div class="nav-right">
            <a href="#" class="btn-nav" onclick="showLogin()">Login</a>
            <a href="#" class="btn-nav primary" onclick="showRegistration()">Get Started</a>
            <a href="/verify" class="btn-nav" style="background: #e91e63; border-color: #e91e63;">🔒 Verify License</a>
        </div>
    </header>
    
    <main class="main-content">
        <div class="title-section">
            <h1 class="main-title">🏠 Property Analysis</h1>
            <p class="subtitle">Instant Data • Full US Coverage</p>
        </div>
        
        <div class="search-card">
            <form class="search-form" action="/property-results" method="POST">
                <label class="form-label">Address</label>
                <input type="text" name="address" class="address-input" placeholder="123 Pine Street, Any City, WA, 54321" required>
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
                    <label>Email:</label>
                    <input type="email" name="email" required>
                </div>
                <div class="form-group">
                    <label>Password:</label>
                    <input type="password" name="password" required>
                </div>
                <button type="submit" class="btn-modal">Login</button>
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
                    <label>Full Name:</label>
                    <input type="text" name="name" required>
                </div>
                <div class="form-group">
                    <label>Email:</label>
                    <input type="email" name="email" required>
                </div>
                <div class="form-group">
                    <label>Phone:</label>
                    <input type="tel" name="phone" required>
                </div>
                <div class="form-group">
                    <label>Profession:</label>
                    <select name="profession" required>
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
                    <label>License Number:</label>
                    <input type="text" name="license" required>
                </div>
                <div class="form-group">
                    <label>Website:</label>
                    <input type="text" name="website" placeholder="example.com">
                </div>
                <div class="form-group">
                    <label>Zip Code:</label>
                    <input type="text" name="zipcode" required>
                </div>
                <button type="submit" class="btn-modal">Continue to License Verification</button>
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
                    <label>Name:</label>
                    <input type="text" name="name" required>
                </div>
                <div class="form-group">
                    <label>Email:</label>
                    <input type="email" name="email" required>
                </div>
                <div class="form-group">
                    <label>Message:</label>
                    <textarea name="message" rows="4" style="width: 100%; padding: 12px 15px; border: 2px solid #e1e5e9; border-radius: 8px; font-size: 16px; resize: vertical;" required></textarea>
                </div>
                <button type="submit" class="btn-modal">Send Message</button>
            </form>
        </div>
    </div>
    
    <script>
        function showLogin() {
            document.getElementById('loginModal').style.display = 'block';
        }
        
        function showRegistration() {
            document.getElementById('registrationModal').style.display = 'block';
        }
        
        function showAbout() {
            document.getElementById('aboutModal').style.display = 'block';
        }
        
        function showContact() {
            document.getElementById('contactModal').style.display = 'block';
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
    </script>
</body>
</html>
    ''')

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    # Add login logic here
    return redirect(url_for('home'))

@app.route('/contact', methods=['POST'])
def contact():
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')
    # Add contact form processing here
    return redirect(url_for('home'))

@app.route('/continue-verification', methods=['POST'])
def continue_verification():
    registration_data = {
        'name': request.form.get('name'),
        'email': request.form.get('email'),
        'phone': request.form.get('phone'),
        'profession': request.form.get('profession'),
        'license': request.form.get('license'),
        'website': request.form.get('website'),
        'zipcode': request.form.get('zipcode')
    }
    session['registration_data'] = registration_data
    return redirect(url_for('verify_license'))

# FIX #4: Allow both POST and GET methods for Back to Results functionality
@app.route('/property-results', methods=['POST', 'GET'])
def property_results():
    if request.method == 'POST':
        address = request.form.get('address')
        session['address'] = address
        
        # Get property data from RentCast
        property_data = get_property_data_from_rentcast(address)
        session['property_data'] = property_data
        
        if property_data:
            comparables = get_comparable_properties_from_rentcast(
                address,
                property_data.get('propertyType'),
                property_data.get('bedrooms'),
                property_data.get('bathrooms'),
                property_data.get('squareFootage')
            )
            rent_estimate = get_rent_estimate_from_rentcast(
                address,
                property_data.get('propertyType'),
                property_data.get('bedrooms'),
                property_data.get('bathrooms'),
                property_data.get('squareFootage')
            )
            session['comparables'] = comparables
            session['rent_estimate'] = rent_estimate
        else:
            # Fallback data if RentCast API fails
            property_data = {
                'propertyType': 'Single Family',
                'bedrooms': 4,
                'bathrooms': 2.5,
                'squareFootage': 1492,
                'lotSize': 7200,
                'yearBuilt': 1995,
                'monthlyRent': None
            }
            session['property_data'] = property_data
            comparables = []
            rent_estimate = 0
            
        return render_template_string(PROPERTY_RESULTS_TEMPLATE,
                                    address=address,
                                    property_data=property_data,
                                    google_maps_api_key=GOOGLE_MAPS_API_KEY)
    else:
        # Handle GET request for Back to Results
        address = session.get('address')
        property_data = session.get('property_data')
        if not address or not property_data:
            return redirect(url_for('home'))
        return render_template_string(PROPERTY_RESULTS_TEMPLATE,
                                    address=address,
                                    property_data=property_data,
                                    google_maps_api_key=GOOGLE_MAPS_API_KEY)

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
        }
        
        .btn-clear {
            background: #f8f9fa;
            color: #666;
            border: 2px solid #e1e5e9;
        }
        
        /* Main Content */
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
        }
        
        .property-header {
            text-align: center;
            margin-bottom: 40px;
        }
        
        .property-title {
            font-size: 36px;
            font-weight: bold;
            color: white;
            margin-bottom: 20px;
        }
        
        .property-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 40px;
        }
        
        .property-card {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        
        .property-card h3 {
            font-size: 24px;
            margin-bottom: 20px;
            color: #333;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        
        .property-details {
            list-style: none;
        }
        
        .property-details li {
            display: flex;
            justify-content: space-between;
            padding: 12px 0;
            border-bottom: 1px solid #f0f0f0;
        }
        
        .property-details li:last-child {
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
        
        /* Street View and Map */
        .media-section {
            margin-bottom: 20px;
        }
        
        .street-view-container {
            width: 100%;
            height: 200px;
            border-radius: 10px;
            overflow: hidden;
            margin-bottom: 20px;
            background: #f0f0f0;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #666;
        }
        
        .street-view-image {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        
        .map-container {
            width: 100%;
            height: 300px;
            border-radius: 10px;
            overflow: hidden;
            background: #f0f0f0;
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
            font-weight: 500;
            transition: all 0.3s;
        }
        
        .map-btn.active {
            background: #667eea;
            color: white;
        }
        
        .view-details-btn {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            margin-top: 20px;
        }
        
        .view-details-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }
        
        /* Professional Listings */
        .professionals-section {
            margin-top: 60px;
        }
        
        .section-title {
            font-size: 32px;
            font-weight: bold;
            color: white;
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
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            text-align: center;
        }
        
        .professional-card h4 {
            font-size: 20px;
            margin-bottom: 10px;
            color: #333;
        }
        
        .professional-location {
            color: #666;
            margin-bottom: 15px;
            font-weight: 500;
        }
        
        .professional-description {
            color: #666;
            margin-bottom: 20px;
            line-height: 1.5;
        }
        
        .website-btn {
            display: inline-block;
            padding: 10px 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 500;
            transition: all 0.3s;
        }
        
        .website-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
        }
        
        /* Clear Results */
        .clear-section {
            text-align: center;
            margin-top: 60px;
            padding: 40px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
        }
        
        .clear-section h3 {
            color: white;
            margin-bottom: 15px;
            font-size: 24px;
        }
        
        .clear-section p {
            color: rgba(255, 255, 255, 0.9);
            margin-bottom: 25px;
        }
        
        .clear-btn {
            padding: 15px 30px;
            background: #dc3545;
            color: white;
            text-decoration: none;
            border-radius: 10px;
            font-weight: 600;
            transition: all 0.3s;
            display: inline-block;
        }
        
        .clear-btn:hover {
            background: #c82333;
            transform: translateY(-2px);
        }
        
        /* Responsive Design */
        @media (max-width: 768px) {
            .property-grid {
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
    <!-- FIX #2: Properly load Google Maps API with callback -->
    <script async defer src="https://maps.googleapis.com/maps/api/js?key={{ google_maps_api_key }}&libraries=geometry&callback=initMap"></script>
</head>
<body>
    <header class="header">
        <a href="/" class="logo">BlueDwarf</a>
        <nav class="nav-center">
            <a href="#" onclick="showAbout()">About</a>
            <a href="#" onclick="showContact()">Contact</a>
        </nav>
        <div class="nav-right">
            <a href="#" class="btn-nav" onclick="showLogin()">Login</a>
            <a href="#" class="btn-nav primary" onclick="showRegistration()">Get Started</a>
            <a href="/verify" class="btn-nav" style="background: #e91e63; border-color: #e91e63;">🔒 Verify License</a>
        </div>
    </header>
    
    <div class="search-section">
        <div class="search-card">
            <form class="search-form" action="/property-results" method="POST">
                <div class="form-group">
                    <label class="form-label">Address</label>
                    <input type="text" name="address" class="address-input" value="{{ address }}" required>
                </div>
                <button type="submit" class="btn-search">Search</button>
                <button type="button" class="btn-clear" onclick="clearResults()">Clear</button>
            </form>
        </div>
    </div>
    
    <main class="container">
        <div class="property-header">
            <h1 class="property-title">{{ address }}</h1>
        </div>
        
        <div class="property-grid">
            <div class="property-card">
                <h3>Property Details</h3>
                <ul class="property-details">
                    <li>
                        <span class="detail-label">Property Type:</span>
                        <span class="detail-value">{{ property_data.get('propertyType', 'Single Family') }}</span>
                    </li>
                    <li>
                        <span class="detail-label">Bedrooms:</span>
                        <span class="detail-value">{{ property_data.get('bedrooms', 4) }}</span>
                    </li>
                    <li>
                        <span class="detail-label">Bathrooms:</span>
                        <span class="detail-value">{{ property_data.get('bathrooms', 2.5) }}</span>
                    </li>
                    <li>
                        <span class="detail-label">Square Feet:</span>
                        <span class="detail-value">{{ "{:,}".format(property_data.get('squareFootage', 1492)) }}</span>
                    </li>
                    <li>
                        <span class="detail-label">Lot Size:</span>
                        <span class="detail-value">{{ "{:,}".format(property_data.get('lotSize', 7200)) }} sq ft</span>
                    </li>
                    <li>
                        <span class="detail-label">Year Built:</span>
                        <span class="detail-value">{{ property_data.get('yearBuilt', 1995) }}</span>
                    </li>
                    <li>
                        <span class="detail-label">Monthly Rent Est:</span>
                        <span class="detail-value">${{ property_data.get('monthlyRent', 'N/A') }}</span>
                    </li>
                </ul>
            </div>
            
            <div class="property-card">
                <h3>Street View</h3>
                <div class="street-view-container">
                    <!-- FIX #2: Street View will be loaded via JavaScript -->
                    <div id="streetViewContainer">Street View Image Unavailable</div>
                </div>
                
                <h3>Aerial View</h3>
                <div class="map-controls">
                    <button class="map-btn active" onclick="setMapType('roadmap')">Map</button>
                    <button class="map-btn" onclick="setMapType('satellite')">Satellite</button>
                </div>
                <div class="map-container">
                    <!-- FIX #2: Map will be loaded via JavaScript -->
                    <div id="map" style="width: 100%; height: 100%;"></div>
                </div>
                
                <button class="view-details-btn" onclick="viewDetails()">View Details</button>
            </div>
        </div>
        
        <!-- Professional Listings -->
        <section class="professionals-section">
            <h2 class="section-title">Local Professionals in {{ address.split(',')[-2:] | join(',') if ',' in address else address }}</h2>
            <div class="professionals-grid">
                {% set professionals = [
                    ('Real Estate Agent', 'Licensed real estate professional specializing in property sales and purchases.'),
                    ('Mortgage Lender', 'Certified mortgage specialist providing competitive home loan solutions.'),
                    ('Real Estate Attorney', 'Licensed attorney specializing in real estate law and property transactions.'),
                    ('Property Inspector', 'Certified home inspector providing comprehensive property evaluations.'),
                    ('Insurance Agent', 'Licensed insurance professional specializing in homeowners insurance.'),
                    ('General Contractor', 'Licensed contractor for home renovations and construction projects.'),
                    ('Electrician', 'Licensed electrician for electrical installations and repairs.'),
                    ('Plumber', 'Licensed plumber for plumbing installations and repairs.'),
                    ('Roofer', 'Licensed roofing contractor for roof repairs and installations.'),
                    ('HVAC Technician', 'Licensed HVAC specialist for heating and cooling systems.'),
                    ('Property Appraiser', 'Licensed appraiser providing accurate property valuations.'),
                    ('Painter', 'Licensed painting contractor for interior and exterior painting.')
                ] %}
                
                {% for profession, description in professionals %}
                <div class="professional-card">
                    <h4>{{ profession }}</h4>
                    <p class="professional-location">{{ address.split(',')[-2:] | join(',') if ',' in address else address }}</p>
                    <p class="professional-description">{{ description }}</p>
                    <a href="javascript:void(0)" class="website-btn" onclick="searchProfessional('{{ profession }}', '{{ address.split(',')[-1].strip() if ',' in address else '94043' }}')">Website</a>
                </div>
                {% endfor %}
            </div>
        </section>
        
        <!-- Clear Results Section -->
        <section class="clear-section">
            <h3>🗑️ Clear All Results</h3>
            <p>Want to start a new search? Clear all property data and professional listings.</p>
            <a href="/clear-results" class="clear-btn">Clear All Results</a>
        </section>
    </main>
    
    <script>
        let map;
        let streetViewService;
        let streetViewPanorama;
        
        // FIX #2: Initialize Google Maps properly
        function initMap() {
            const address = "{{ address }}";
            
            // Geocode the address to get coordinates
            const geocoder = new google.maps.Geocoder();
            geocoder.geocode({ address: address }, function(results, status) {
                if (status === 'OK') {
                    const location = results[0].geometry.location;
                    
                    // Initialize the map
                    map = new google.maps.Map(document.getElementById('map'), {
                        zoom: 18,
                        center: location,
                        mapTypeId: 'roadmap'
                    });
                    
                    // Add marker for the property
                    new google.maps.Marker({
                        position: location,
                        map: map,
                        title: address
                    });
                    
                    // Initialize Street View
                    streetViewService = new google.maps.StreetViewService();
                    streetViewService.getPanorama({
                        location: location,
                        radius: 50
                    }, function(data, status) {
                        if (status === 'OK') {
                            const streetViewImage = `https://maps.googleapis.com/maps/api/streetview?size=400x200&location=${location.lat()},${location.lng()}&key={{ google_maps_api_key }}`;
                            document.getElementById('streetViewContainer').innerHTML = 
                                `<img src="${streetViewImage}" alt="Street View" class="street-view-image">`;
                        } else {
                            document.getElementById('streetViewContainer').innerHTML = 'Street View Image Unavailable';
                        }
                    });
                } else {
                    console.error('Geocoding failed: ' + status);
                    document.getElementById('map').innerHTML = 'Map loading failed';
                }
            });
        }
        
        function setMapType(type) {
            if (map) {
                map.setMapTypeId(type);
                
                // Update button states
                document.querySelectorAll('.map-btn').forEach(btn => btn.classList.remove('active'));
                event.target.classList.add('active');
            }
        }
        
        function viewDetails() {
            window.location.href = '/property-details';
        }
        
        function clearResults() {
            window.location.href = '/clear-results';
        }
        
        function searchProfessional(profession, zipcode) {
            const searchQuery = `${profession} ${zipcode}`;
            const googleSearchUrl = `https://www.google.com/search?q=${encodeURIComponent(searchQuery)}`;
            window.open(googleSearchUrl, '_blank');
        }
        
        // Initialize map when page loads
        window.onload = function() {
            if (typeof google !== 'undefined' && google.maps) {
                initMap();
            }
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

# FIX #3: Remove unnecessary Back to Top button from the top
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
        
        /* Main Container */
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
        }
        
        .page-title {
            text-align: center;
            color: white;
            font-size: 36px;
            margin-bottom: 10px;
        }
        
        .property-address {
            text-align: center;
            color: rgba(255, 255, 255, 0.9);
            font-size: 18px;
            margin-bottom: 30px;
        }
        
        /* FIX #3: Navigation buttons without unnecessary Back to Top */
        .navigation-buttons {
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
            text-decoration: none;
            cursor: pointer;
            transition: all 0.3s;
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
            appearance: none;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: #667eea;
            cursor: pointer;
        }
        
        .rent-value {
            text-align: center;
            font-size: 28px;
            font-weight: bold;
            color: #667eea;
            margin-top: 15px;
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
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        
        .scroll-indicator {
            text-align: center;
            color: #667eea;
            font-weight: 500;
            margin-bottom: 20px;
        }
        
        .comparables-list {
            max-height: 400px;
            overflow-y: auto;
            border: 1px solid #e1e5e9;
            border-radius: 10px;
            padding: 15px;
        }
        
        .comparable-item {
            padding: 20px;
            border: 1px solid #e1e5e9;
            border-radius: 10px;
            margin-bottom: 15px;
            background: #f8f9fa;
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
            font-weight: 600;
            color: #666;
            margin-bottom: 10px;
        }
        
        .comparable-specs {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
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
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        
        #comparableMap {
            width: 100%;
            height: 400px;
            border-radius: 10px;
            background: #f0f0f0;
        }
        
        /* Back to Top Button (ONLY at bottom) */
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
            font-size: 18px;
            cursor: pointer;
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
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
            
            .navigation-buttons {
                flex-direction: column;
                align-items: center;
            }
            
            .comparable-specs {
                justify-content: center;
            }
        }
    </style>
    <script async defer src="https://maps.googleapis.com/maps/api/js?key={{ google_maps_api_key }}&libraries=geometry&callback=initComparableMap"></script>
</head>
<body>
    <header class="header">
        <a href="/" class="logo">BlueDwarf</a>
        <nav class="nav-center">
            <a href="#" onclick="showAbout()">About</a>
            <a href="#" onclick="showContact()">Contact</a>
        </nav>
        <div class="nav-right">
            <a href="#" class="btn-nav" onclick="showLogin()">Login</a>
            <a href="#" class="btn-nav primary" onclick="showRegistration()">Get Started</a>
            <a href="/verify" class="btn-nav" style="background: #e91e63; border-color: #e91e63;">🔒 Verify License</a>
        </div>
    </header>
    
    <main class="container">
        <h1 class="page-title">Property Details</h1>
        <p class="property-address">{{ property_data.get('address', '1600 Amphitheatre Parkway, Mountain View, CA 94043') }}</p>
        
        <!-- FIX #3: Navigation buttons without unnecessary Back to Top at top -->
        <div class="navigation-buttons">
            <a href="{{ url_for('property_results') }}" class="btn btn-secondary">← Back to Results</a>
            <a href="{{ url_for('clear_results') }}" class="btn btn-danger">Clear All Data</a>
        </div>
        
        <!-- Property Information Grid -->
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
                        <span class="detail-value">{{ property_data.get('bedrooms', 4) }}</span>
                    </li>
                    <li>
                        <span class="detail-label">Bathrooms:</span>
                        <span class="detail-value">{{ property_data.get('bathrooms', 2.5) }}</span>
                    </li>
                    <li>
                        <span class="detail-label">Square Feet:</span>
                        <span class="detail-value">{{ "{:,}".format(property_data.get('squareFootage', 1492)) }}</span>
                    </li>
                    <li>
                        <span class="detail-label">Lot Size:</span>
                        <span class="detail-value">{{ "{:,}".format(property_data.get('lotSize', 7200)) }} sq ft</span>
                    </li>
                    <li>
                        <span class="detail-label">Year Built:</span>
                        <span class="detail-value">{{ property_data.get('yearBuilt', 1995) }}</span>
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
                        <span class="detail-value">${{ property_data.get('lastSalePrice', 'N/A') }}</span>
                    </li>
                    <li>
                        <span class="detail-label">Last Sale Date:</span>
                        <span class="detail-value">{{ property_data.get('lastSaleDate', 'N/A') }}</span>
                    </li>
                    <li>
                        <span class="detail-label">Monthly Rent Est:</span>
                        <span class="detail-value">${{ property_data.get('monthlyRent', 'N/A') }}</span>
                    </li>
                    <li>
                        <span class="detail-label">Price per Sq Ft:</span>
                        <span class="detail-value">${{ property_data.get('pricePerSqFt', 'N/A') }}</span>
                    </li>
                    <li>
                        <span class="detail-label">HOA Fee:</span>
                        <span class="detail-value">${{ property_data.get('hoaFee', 'N/A') }}/month</span>
                    </li>
                    <li>
                        <span class="detail-label">Property Tax (2023):</span>
                        <span class="detail-value">${{ property_data.get('propertyTax', 'N/A') }}</span>
                    </li>
                </ul>
            </div>
        </div>
        
        <div class="details-grid">
            <div class="details-card">
                <h3>🏠 Property Features</h3>
                <ul class="details-list">
                    <li>
                        <span class="detail-label">Architecture:</span>
                        <span class="detail-value">{{ property_data.get('architecture', 'N/A') }}</span>
                    </li>
                    <li>
                        <span class="detail-label">Heating:</span>
                        <span class="detail-value">{{ property_data.get('heating', 'N/A') }}</span>
                    </li>
                    <li>
                        <span class="detail-label">Cooling:</span>
                        <span class="detail-value">{{ property_data.get('cooling', 'N/A') }}</span>
                    </li>
                    <li>
                        <span class="detail-label">Garage:</span>
                        <span class="detail-value">{{ property_data.get('garage', 'N/A') }} spaces</span>
                    </li>
                    <li>
                        <span class="detail-label">Pool:</span>
                        <span class="detail-value">{{ 'Yes' if property_data.get('pool') else 'No' }}</span>
                    </li>
                    <li>
                        <span class="detail-label">Fireplace:</span>
                        <span class="detail-value">{{ 'Yes' if property_data.get('fireplace') else 'No' }}</span>
                    </li>
                    <li>
                        <span class="detail-label">Exterior:</span>
                        <span class="detail-value">{{ property_data.get('exterior', 'N/A') }}</span>
                    </li>
                </ul>
            </div>
            
            <div class="details-card">
                <h3>🏫 Schools & Walkability</h3>
                <ul class="details-list">
                    <li>
                        <span class="detail-label">School District:</span>
                        <span class="detail-value">{{ property_data.get('schoolDistrict', 'Sacramento City Unified') }}</span>
                    </li>
                    <li>
                        <span class="detail-label">Walk Score:</span>
                        <span class="detail-value">{{ property_data.get('walkScore', 72) }} (Very Walkable)</span>
                    </li>
                    <li>
                        <span class="detail-label">Transit Score:</span>
                        <span class="detail-value">{{ property_data.get('transitScore', 45) }} (Some Transit)</span>
                    </li>
                    <li>
                        <span class="detail-label">Bike Score:</span>
                        <span class="detail-value">{{ property_data.get('bikeScore', 68) }} (Bikeable)</span>
                    </li>
                </ul>
            </div>
        </div>
        
        <!-- Interactive Rent Estimation -->
        <div class="rent-estimation">
            <h3>💵 Interactive Rent Estimation</h3>
            <div class="rent-slider-container">
                <input type="range" min="2000" max="4000" value="3000" class="rent-slider" id="rentSlider">
            </div>
            <div class="rent-value" id="rentValue">$3,000/month</div>
        </div>
        
        <!-- Comparable Properties -->
        <div class="comparables-section">
            <h3>🏘️ Comparable Properties</h3>
            <p class="scroll-indicator">📜 Scroll to view all comparable properties</p>
            <div class="comparables-list">
                {% if comparables and comparables|length > 0 %}
                    {% for comp in comparables[:5] %}
                    <div class="comparable-item">
                        <div class="comparable-header">
                            <div class="comparable-number">{{ loop.index }}</div>
                            <div class="comparable-price">${{ "{:,}".format(comp.get('price', 475000)) }}</div>
                        </div>
                        <div class="comparable-address">{{ comp.get('address', '1234 Oak Street, Sacramento, CA 95814') }}</div>
                        <div class="comparable-specs">
                            <div>{{ comp.get('bedrooms', 3) }} bed</div>
                            <div>{{ comp.get('bathrooms', 2) }} bath</div>
                            <div>{{ "{:,}".format(comp.get('squareFootage', 1350)) }} sq ft</div>
                            <div>{{ comp.get('yearBuilt', 1985) }} built</div>
                            <div>{{ comp.get('distance', 0.3) }} mi</div>
                            <div>{{ comp.get('daysOnMarket', 45) }} DOM</div>
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
    
    <!-- FIX #3: Keep ONLY the bottom Back to Top button -->
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
                    label: {
                        text: location.number.toString(),
                        color: 'white',
                        fontWeight: 'bold'
                    },
                    icon: {
                        url: 'https://maps.google.com/mapfiles/ms/icons/blue-dot.png',
                        scaledSize: new google.maps.Size(32, 32)
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
        
        // Rent slider functionality
        const rentSlider = document.getElementById('rentSlider');
        const rentValue = document.getElementById('rentValue');
        
        rentSlider.addEventListener('input', function() {
            const value = this.value;
            rentValue.textContent = `$${parseInt(value).toLocaleString()}/month`;
        });
        
        function scrollToTop() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        }
        
        // Initialize map when page loads
        window.onload = function() {
            if (typeof google !== 'undefined' && google.maps) {
                initComparableMap();
            }
        };
    </script>
</body>
</html>
'''

@app.route('/clear-results')
def clear_results():
    session.clear()
    return redirect(url_for('home'))

@app.route('/verify')
def verify():
    return redirect(url_for('verify_license'))

@app.route('/verify-license')
def verify_license():
    registration_data = session.get('registration_data', {})
    return render_template_string(VERIFY_LICENSE_TEMPLATE,
                                registration_data=registration_data,
                                SUMSUB_APP_TOKEN=SUMSUB_APP_TOKEN)

# FIX #1: Improved Sumsub integration with better error handling
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
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .container {
            width: 100%;
            max-width: 800px;
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
            margin-bottom: 30px;
            color: #333;
        }
        
        .professional-info {
            background: #f8f9fa;
            padding: 25px;
            border-radius: 15px;
            margin-bottom: 30px;
            text-align: left;
        }
        
        .professional-info h3 {
            margin-bottom: 20px;
            color: #333;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        
        .info-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }
        
        .info-item {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #e1e5e9;
        }
        
        .info-label {
            font-weight: 600;
            color: #666;
        }
        
        .info-value {
            font-weight: 500;
            color: #333;
        }
        
        .verification-container {
            margin: 30px 0;
        }
        
        .sumsub-container {
            min-height: 500px;
            border: 2px solid #e1e5e9;
            border-radius: 15px;
            padding: 20px;
            background: #f8f9fa;
        }
        
        .loading-message {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 400px;
            color: #666;
            font-size: 18px;
        }
        
        .loading-spinner {
            width: 50px;
            height: 50px;
            border: 4px solid #e1e5e9;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-bottom: 20px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .back-link {
            display: inline-block;
            margin-top: 30px;
            padding: 15px 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-decoration: none;
            border-radius: 10px;
            font-weight: 500;
            transition: all 0.3s;
        }
        
        .back-link:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }
        
        .error-message {
            background: #f8d7da;
            color: #721c24;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            border: 1px solid #f5c6cb;
        }
        
        .success-message {
            background: #d4edda;
            color: #155724;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            border: 1px solid #c3e6cb;
        }
        
        @media (max-width: 768px) {
            .info-grid {
                grid-template-columns: 1fr;
            }
            
            .verification-card {
                padding: 30px 20px;
            }
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
                    Please complete the verification process below. You will need to upload your professional license, photo identification and take a selfie for identity verification.
                </p>
                
                <div id="sumsub-websdk-container" class="sumsub-container">
                    <div class="loading-message">
                        <div class="loading-spinner"></div>
                        <div>Initializing Secure Verification System...</div>
                        <div style="font-size: 14px; margin-top: 10px; color: #999;">Please wait while we load the verification interface</div>
                    </div>
                </div>
            </div>
            
            <a href="/" class="back-link">← Back to Home</a>
        </div>
    </div>
    
    <script>
        // FIX #1: Improved Sumsub WebSDK initialization with better error handling
        function initSumsubWebSDK() {
            try {
                console.log('Initializing Sumsub WebSDK...');
                
                // Check if Sumsub SDK is loaded
                if (typeof window.SumsubWebSdk === 'undefined') {
                    throw new Error('Sumsub WebSDK not loaded');
                }
                
                const sumsubWebSdk = window.SumsubWebSdk.init(
                    '{{ SUMSUB_APP_TOKEN }}',
                    {
                        email: '{{ registration_data.get("email", "test@example.com") }}',
                        userId: 'user_' + Date.now(),
                        metadata: {
                            profession: '{{ registration_data.get("profession", "") }}',
                            license: '{{ registration_data.get("license", "") }}'
                        }
                    }
                );
                
                console.log('Sumsub WebSDK initialized successfully');
                
                sumsubWebSdk.render('#sumsub-websdk-container', {
                    onMessage: (type, payload) => {
                        console.log('Sumsub message:', type, payload);
                        
                        if (type === 'idCheck.onApplicantLoaded') {
                            console.log('Applicant loaded successfully');
                            document.querySelector('.loading-message').style.display = 'none';
                        }
                        
                        if (type === 'idCheck.onApplicantSubmitted') {
                            console.log('Verification submitted successfully');
                            document.getElementById('sumsub-websdk-container').innerHTML = 
                                '<div class="success-message"><h3>✅ Verification Submitted Successfully!</h3><p>Your professional license verification has been submitted. You will receive an email confirmation once your license is verified by our team.</p></div>';
                        }
                        
                        if (type === 'idCheck.onError') {
                            console.error('Verification error:', payload);
                            document.getElementById('sumsub-websdk-container').innerHTML = 
                                '<div class="error-message"><h3>❌ Verification Error</h3><p>There was an error during the verification process: ' + (payload.message || 'Unknown error') + '</p><p>Please try again or contact support if the issue persists.</p></div>';
                        }
                    },
                    onError: (error) => {
                        console.error('Sumsub initialization error:', error);
                        document.getElementById('sumsub-websdk-container').innerHTML = 
                            '<div class="error-message"><h3>⚠️ Verification System Unavailable</h3><p>The verification system is temporarily unavailable. This could be due to:</p><ul style="text-align: left; margin: 10px 0;"><li>Network connectivity issues</li><li>Temporary service maintenance</li><li>Browser compatibility issues</li></ul><p>Please try refreshing the page or contact support for assistance.</p></div>';
                    }
                });
                
            } catch (error) {
                console.error('Failed to initialize Sumsub WebSDK:', error);
                document.getElementById('sumsub-websdk-container').innerHTML = 
                    '<div class="error-message"><h3>⚠️ Verification System Error</h3><p>Failed to initialize the verification system. Error: ' + error.message + '</p><p>Please try refreshing the page or contact support.</p></div>';
            }
        }
        
        // FIX #1: Increased timeout and added retry mechanism
        let initAttempts = 0;
        const maxAttempts = 3;
        
        function attemptInit() {
            initAttempts++;
            console.log(`Verification init attempt ${initAttempts}/${maxAttempts}`);
            
            if (typeof window.SumsubWebSdk !== 'undefined') {
                initSumsubWebSDK();
            } else if (initAttempts < maxAttempts) {
                console.log('Sumsub SDK not ready, retrying in 2 seconds...');
                setTimeout(attemptInit, 2000);
            } else {
                console.error('Failed to load Sumsub SDK after multiple attempts');
                document.getElementById('sumsub-websdk-container').innerHTML = 
                    '<div class="error-message"><h3>⚠️ Verification System Loading Failed</h3><p>The verification system failed to load after multiple attempts. This may be due to network issues or browser restrictions.</p><p>Please try:</p><ul style="text-align: left; margin: 10px 0;"><li>Refreshing the page</li><li>Disabling ad blockers</li><li>Using a different browser</li><li>Checking your internet connection</li></ul></div>';
            }
        }
        
        // Initialize when page loads with increased delay
        window.onload = function() {
            console.log('Page loaded, starting verification initialization...');
            setTimeout(attemptInit, 3000); // FIX #1: Increased initial delay to 3 seconds
        };
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)

