from flask import Flask, render_template_string, request, jsonify, session, redirect, url_for
from flask_cors import CORS
import requests
import json
import os
from datetime import datetime
import logging

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API Configuration
RENTCAST_API_KEY = os.environ.get('RENTCAST_API_KEY', 'e796d43b9a1a4c51aee87e48ff7002e1')
GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY', 'AIzaSyCOEpJEuoAKQNfiO-YmW2o-_At4z34CuBM')
SUMSUB_API_KEY = os.environ.get('SUMSUB_API_KEY', 'your-sumsub-api-key')

def get_rentcast_property_data(address):
    """Get property data from RentCast API"""
    try:
        url = "https://api.rentcast.io/v1/properties"
        headers = {
            "X-Api-Key": RENTCAST_API_KEY,
            "Content-Type": "application/json"
        }
        params = {
            "address": address,
            "propertyType": "Single Family",
            "bedrooms": "1,2,3,4,5+",
            "bathrooms": "1,2,3,4+",
            "squareFootage": "500-5000",
            "yearBuilt": "1900-2024"
        }
        
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"RentCast API error: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Error fetching RentCast data: {str(e)}")
        return None

def get_comparable_properties(address, radius_miles=1):
    """Get comparable properties from RentCast API"""
    try:
        url = "https://api.rentcast.io/v1/properties/comparables"
        headers = {
            "X-Api-Key": RENTCAST_API_KEY,
            "Content-Type": "application/json"
        }
        params = {
            "address": address,
            "radius": radius_miles,
            "limit": 5,
            "propertyType": "Single Family",
            "bedrooms": "2,3,4,5",
            "bathrooms": "1,2,3,4",
            "squareFootage": "1000-3000"
        }
        
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            # Add numbered IDs to comparable properties
            if 'properties' in data:
                for i, prop in enumerate(data['properties'][:5], 1):
                    prop['comp_id'] = i
            return data
        else:
            logger.error(f"RentCast Comparables API error: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Error fetching comparable properties: {str(e)}")
        return None

@app.route('/')
def home():
    return render_template_string(HOME_TEMPLATE)

@app.route('/search', methods=['POST'])
def search_property():
    try:
        address = request.form.get('address', '').strip()
        if not address:
            return jsonify({'error': 'Address is required'}), 400
        
        # Get property data from RentCast
        property_data = get_rentcast_property_data(address)
        
        # Get comparable properties
        comparable_data = get_comparable_properties(address)
        
        # Store in session for property details page
        session['property_data'] = property_data
        session['comparable_data'] = comparable_data
        session['search_address'] = address
        
        # Prepare data for template
        template_data = {
            'address': address,
            'property_data': property_data,
            'comparable_data': comparable_data,
            'google_maps_api_key': GOOGLE_MAPS_API_KEY
        }
        
        return render_template_string(PROPERTY_RESULTS_TEMPLATE, **template_data)
        
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        return jsonify({'error': 'Search failed'}), 500

@app.route('/property-details', methods=['GET', 'POST'])
def property_details():
    try:
        # Get data from session
        property_data = session.get('property_data')
        comparable_data = session.get('comparable_data')
        search_address = session.get('search_address')
        
        if not property_data:
            return redirect(url_for('home'))
        
        template_data = {
            'address': search_address,
            'property_data': property_data,
            'comparable_data': comparable_data
        }
        
        return render_template_string(PROPERTY_DETAILS_TEMPLATE, **template_data)
        
    except Exception as e:
        logger.error(f"Property details error: {str(e)}")
        return redirect(url_for('home'))

@app.route('/clear-search', methods=['POST'])
def clear_search():
    session.clear()
    return redirect(url_for('home'))

@app.route('/login', methods=['POST'])
def login():
    try:
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Basic validation (implement proper authentication)
        if email and password:
            session['user_email'] = email
            return jsonify({'success': True, 'message': 'Login successful'})
        else:
            return jsonify({'success': False, 'message': 'Invalid credentials'}), 400
            
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'success': False, 'message': 'Login failed'}), 500

@app.route('/register', methods=['POST'])
def register():
    try:
        # Get form data
        form_data = {
            'name': request.form.get('name'),
            'email': request.form.get('email'),
            'phone': request.form.get('phone'),
            'profession': request.form.get('profession'),
            'license_number': request.form.get('license_number'),
            'website': request.form.get('website'),
            'company': request.form.get('company'),
            'experience': request.form.get('experience'),
            'specialties': request.form.get('specialties'),
            'bio': request.form.get('bio')
        }
        
        # Store in session (implement proper database storage)
        session['registration_data'] = form_data
        
        return jsonify({'success': True, 'message': 'Registration successful'})
        
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return jsonify({'success': False, 'message': 'Registration failed'}), 500

@app.route('/verify-license')
def verify_license():
    return render_template_string(LICENSE_VERIFICATION_TEMPLATE)

# HTML Templates
HOME_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BlueDwarf.io - Property Analysis Platform</title>
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
        
        .header {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .logo {
            font-size: 1.8rem;
            font-weight: bold;
            color: white;
        }
        
        .nav-links {
            display: flex;
            gap: 1rem;
        }
        
        .nav-links a {
            color: white;
            text-decoration: none;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            transition: background 0.3s;
        }
        
        .nav-links a:hover {
            background: rgba(255, 255, 255, 0.2);
        }
        
        .auth-buttons {
            display: flex;
            gap: 1rem;
        }
        
        .btn {
            padding: 0.7rem 1.5rem;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-weight: 500;
            transition: all 0.3s;
            text-decoration: none;
            display: inline-block;
            text-align: center;
        }
        
        .btn-outline {
            background: transparent;
            color: white;
            border: 2px solid white;
        }
        
        .btn-outline:hover {
            background: white;
            color: #667eea;
        }
        
        .btn-primary {
            background: white;
            color: #667eea;
        }
        
        .btn-primary:hover {
            background: #f0f0f0;
            transform: translateY(-2px);
        }
        
        .btn-verify {
            background: transparent;
            color: #ff6b9d;
            border: 2px solid #ff6b9d;
        }
        
        .btn-verify:hover {
            background: #ff6b9d;
            color: white;
        }
        
        .main-content {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: calc(100vh - 80px);
            padding: 2rem;
            text-align: center;
        }
        
        .hero-title {
            font-size: 3rem;
            color: white;
            margin-bottom: 1rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .hero-subtitle {
            font-size: 1.2rem;
            color: rgba(255, 255, 255, 0.9);
            margin-bottom: 3rem;
        }
        
        .search-container {
            background: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            max-width: 600px;
            width: 100%;
        }
        
        .search-form {
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }
        
        .form-group {
            display: flex;
            flex-direction: column;
            text-align: left;
        }
        
        .form-group label {
            margin-bottom: 0.5rem;
            font-weight: 500;
            color: #333;
        }
        
        .form-group input {
            padding: 1rem;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 1rem;
            transition: border-color 0.3s;
        }
        
        .form-group input:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .search-buttons {
            display: flex;
            gap: 1rem;
            margin-top: 1rem;
        }
        
        .btn-search {
            flex: 1;
            background: #667eea;
            color: white;
            padding: 1rem;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 500;
            cursor: pointer;
            transition: background 0.3s;
        }
        
        .btn-search:hover {
            background: #5a6fd8;
        }
        
        .btn-clear {
            background: #6c757d;
            color: white;
            padding: 1rem 2rem;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            cursor: pointer;
            transition: background 0.3s;
        }
        
        .btn-clear:hover {
            background: #5a6268;
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
            background-color: rgba(0,0,0,0.5);
        }
        
        .modal-content {
            background-color: white;
            margin: 5% auto;
            padding: 2rem;
            border-radius: 10px;
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
            right: 1rem;
            top: 1rem;
        }
        
        .close:hover {
            color: black;
        }
        
        .modal h2 {
            margin-bottom: 1rem;
            color: #333;
        }
        
        .modal .form-group {
            margin-bottom: 1rem;
        }
        
        .modal input, .modal select, .modal textarea {
            width: 100%;
            padding: 0.8rem;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 1rem;
        }
        
        .modal textarea {
            height: 100px;
            resize: vertical;
        }
        
        @media (max-width: 768px) {
            .header {
                flex-direction: column;
                gap: 1rem;
                padding: 1rem;
            }
            
            .nav-links {
                order: 3;
                width: 100%;
                justify-content: center;
            }
            
            .hero-title {
                font-size: 2rem;
            }
            
            .search-buttons {
                flex-direction: column;
            }
        }
    </style>
</head>
<body>
    <header class="header">
        <div class="logo">BlueDwarf.io</div>
        <nav class="nav-links">
            <a href="#about">About</a>
            <a href="#contact">Contact</a>
        </nav>
        <div class="auth-buttons">
            <button class="btn btn-outline" onclick="openLoginModal()">Login</button>
            <button class="btn btn-primary" onclick="openRegisterModal()">Get Started</button>
            <button class="btn btn-verify" onclick="openVerifyModal()">🔒 Verify License</button>
        </div>
    </header>

    <main class="main-content">
        <h1 class="hero-title">🏠 Property Analysis</h1>
        <p class="hero-subtitle">Instant Data • Full US Coverage</p>
        
        <div class="search-container">
            <form class="search-form" action="/search" method="POST">
                <div class="form-group">
                    <label for="address">Property Address</label>
                    <input type="text" id="address" name="address" placeholder="Enter property address..." required>
                </div>
                <div class="search-buttons">
                    <button type="submit" class="btn-search">Search</button>
                    <button type="button" class="btn-clear" onclick="clearForm()">Clear</button>
                </div>
            </form>
        </div>
    </main>

    <!-- Login Modal -->
    <div id="loginModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeLoginModal()">&times;</span>
            <h2>Professional Login</h2>
            <form id="loginForm">
                <div class="form-group">
                    <label for="loginEmail">Email</label>
                    <input type="email" id="loginEmail" name="email" required>
                </div>
                <div class="form-group">
                    <label for="loginPassword">Password</label>
                    <input type="password" id="loginPassword" name="password" required>
                </div>
                <button type="submit" class="btn btn-primary" style="width: 100%;">Login</button>
            </form>
        </div>
    </div>

    <!-- Register Modal -->
    <div id="registerModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeRegisterModal()">&times;</span>
            <h2>Professional Registration</h2>
            <form id="registerForm">
                <div class="form-group">
                    <label for="name">Full Name</label>
                    <input type="text" id="name" name="name" required>
                </div>
                <div class="form-group">
                    <label for="email">Email</label>
                    <input type="email" id="email" name="email" required>
                </div>
                <div class="form-group">
                    <label for="phone">Phone</label>
                    <input type="tel" id="phone" name="phone" required>
                </div>
                <div class="form-group">
                    <label for="profession">Professional Category</label>
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
                    <label for="license_number">License Number</label>
                    <input type="text" id="license_number" name="license_number" required>
                </div>
                <div class="form-group">
                    <label for="website">Website</label>
                    <input type="text" id="website" name="website" placeholder="example.com">
                </div>
                <div class="form-group">
                    <label for="company">Company</label>
                    <input type="text" id="company" name="company">
                </div>
                <div class="form-group">
                    <label for="experience">Years of Experience</label>
                    <input type="number" id="experience" name="experience" min="0" max="50">
                </div>
                <div class="form-group">
                    <label for="specialties">Specialties</label>
                    <input type="text" id="specialties" name="specialties" placeholder="e.g., First-time buyers, Luxury homes">
                </div>
                <div class="form-group">
                    <label for="bio">Professional Bio</label>
                    <textarea id="bio" name="bio" placeholder="Brief description of your services..."></textarea>
                </div>
                <button type="submit" class="btn btn-primary" style="width: 100%;">Continue to License Verification</button>
            </form>
        </div>
    </div>

    <!-- Verify License Modal -->
    <div id="verifyModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeVerifyModal()">&times;</span>
            <h2>🔒 License Verification</h2>
            <p style="margin-bottom: 2rem; color: #666;">You will need to upload your professional license, photo identification, and take a selfie for identity verification.</p>
            <div style="text-align: center;">
                <div style="margin: 2rem 0;">
                    <div style="display: inline-block; width: 50px; height: 50px; border: 3px solid #667eea; border-top: 3px solid transparent; border-radius: 50%; animation: spin 1s linear infinite;"></div>
                    <p style="margin-top: 1rem; color: #667eea;">Initializing Secure Verification System...</p>
                </div>
                <button class="btn btn-primary" onclick="window.open('/verify-license', '_blank')">← Back to Home</button>
            </div>
        </div>
    </div>

    <style>
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>

    <script>
        function openLoginModal() {
            document.getElementById('loginModal').style.display = 'block';
        }
        
        function closeLoginModal() {
            document.getElementById('loginModal').style.display = 'none';
        }
        
        function openRegisterModal() {
            document.getElementById('registerModal').style.display = 'block';
        }
        
        function closeRegisterModal() {
            document.getElementById('registerModal').style.display = 'none';
        }
        
        function openVerifyModal() {
            document.getElementById('verifyModal').style.display = 'block';
        }
        
        function closeVerifyModal() {
            document.getElementById('verifyModal').style.display = 'none';
        }
        
        function clearForm() {
            document.getElementById('address').value = '';
        }
        
        // Close modals when clicking outside
        window.onclick = function(event) {
            const loginModal = document.getElementById('loginModal');
            const registerModal = document.getElementById('registerModal');
            const verifyModal = document.getElementById('verifyModal');
            
            if (event.target == loginModal) {
                loginModal.style.display = 'none';
            }
            if (event.target == registerModal) {
                registerModal.style.display = 'none';
            }
            if (event.target == verifyModal) {
                verifyModal.style.display = 'none';
            }
        }
        
        // Handle login form submission
        document.getElementById('loginForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            
            fetch('/login', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Login successful!');
                    closeLoginModal();
                } else {
                    alert('Login failed: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Login failed. Please try again.');
            });
        });
        
        // Handle registration form submission
        document.getElementById('registerForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            
            fetch('/register', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Registration successful! Please complete license verification.');
                    closeRegisterModal();
                    openVerifyModal();
                } else {
                    alert('Registration failed: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Registration failed. Please try again.');
            });
        });
    </script>
</body>
</html>
'''

PROPERTY_RESULTS_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Property Results - BlueDwarf.io</title>
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
        
        .header {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .logo {
            font-size: 1.8rem;
            font-weight: bold;
            color: white;
        }
        
        .search-bar {
            flex: 1;
            max-width: 400px;
            margin: 0 2rem;
        }
        
        .search-bar input {
            width: 100%;
            padding: 0.8rem;
            border: none;
            border-radius: 25px;
            font-size: 1rem;
        }
        
        .nav-buttons {
            display: flex;
            gap: 1rem;
        }
        
        .btn {
            padding: 0.7rem 1.5rem;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-weight: 500;
            transition: all 0.3s;
            text-decoration: none;
            display: inline-block;
            text-align: center;
        }
        
        .btn-home {
            background: white;
            color: #667eea;
        }
        
        .btn-clear {
            background: #dc3545;
            color: white;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        .property-card {
            background: white;
            border-radius: 15px;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        
        .property-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
            flex-wrap: wrap;
            gap: 1rem;
        }
        
        .property-address {
            font-size: 1.5rem;
            font-weight: bold;
            color: #333;
        }
        
        .view-details-btn {
            background: #28a745;
            color: white;
            padding: 1rem 2rem;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            cursor: pointer;
            transition: background 0.3s;
        }
        
        .view-details-btn:hover {
            background: #218838;
        }
        
        .maps-section {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
            margin-bottom: 2rem;
        }
        
        .map-container {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 1rem;
            min-height: 300px;
            display: flex;
            flex-direction: column;
        }
        
        .map-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }
        
        .map-title {
            font-size: 1.2rem;
            font-weight: bold;
            color: #333;
        }
        
        .map-toggle {
            display: flex;
            gap: 0.5rem;
        }
        
        .toggle-btn {
            padding: 0.5rem 1rem;
            border: 1px solid #ddd;
            background: white;
            cursor: pointer;
            border-radius: 5px;
            transition: all 0.3s;
        }
        
        .toggle-btn.active {
            background: #667eea;
            color: white;
            border-color: #667eea;
        }
        
        .map-content {
            flex: 1;
            background: #e9ecef;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #6c757d;
            font-size: 1rem;
        }
        
        .property-details {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }
        
        .detail-item {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 8px;
            text-align: center;
        }
        
        .detail-label {
            font-size: 0.9rem;
            color: #6c757d;
            margin-bottom: 0.5rem;
        }
        
        .detail-value {
            font-size: 1.2rem;
            font-weight: bold;
            color: #333;
        }
        
        .professionals-section {
            margin-top: 2rem;
        }
        
        .section-title {
            font-size: 1.5rem;
            font-weight: bold;
            margin-bottom: 1rem;
            color: #333;
        }
        
        .professionals-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1rem;
        }
        
        .professional-card {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .professional-info {
            flex: 1;
        }
        
        .professional-title {
            font-weight: bold;
            color: #333;
            margin-bottom: 0.5rem;
        }
        
        .professional-subtitle {
            font-size: 0.9rem;
            color: #6c757d;
        }
        
        .website-btn {
            background: #667eea;
            color: white;
            padding: 0.5rem 1rem;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            text-decoration: none;
            font-size: 0.9rem;
        }
        
        .website-btn:hover {
            background: #5a6fd8;
        }
        
        @media (max-width: 768px) {
            .maps-section {
                grid-template-columns: 1fr;
            }
            
            .property-header {
                flex-direction: column;
                text-align: center;
            }
            
            .professionals-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
    <script async defer src="https://maps.googleapis.com/maps/api/js?key={{ google_maps_api_key }}&callback=initMaps"></script>
</head>
<body>
    <header class="header">
        <div class="logo">BlueDwarf.io</div>
        <div class="search-bar">
            <input type="text" value="{{ address }}" readonly>
        </div>
        <div class="nav-buttons">
            <a href="/" class="btn btn-home">Home</a>
            <form action="/clear-search" method="POST" style="display: inline;">
                <button type="submit" class="btn btn-clear">Clear</button>
            </form>
        </div>
    </header>

    <div class="container">
        <div class="property-card">
            <div class="property-header">
                <div class="property-address">{{ address }}</div>
                <form action="/property-details" method="POST">
                    <button type="submit" class="view-details-btn">View Details</button>
                </form>
            </div>
            
            <div class="maps-section">
                <div class="map-container">
                    <div class="map-header">
                        <div class="map-title">Street View</div>
                    </div>
                    <div class="map-content" id="streetview-container">
                        {% if google_maps_api_key %}
                            <img id="streetview-image" src="https://maps.googleapis.com/maps/api/streetview?size=400x300&location={{ address }}&key={{ google_maps_api_key }}" 
                                 alt="Street View" style="width: 100%; height: 100%; object-fit: cover; border-radius: 8px;"
                                 onerror="this.style.display='none'; this.parentNode.innerHTML='Street View Image Unavailable';">
                        {% else %}
                            Street View Image Unavailable
                        {% endif %}
                    </div>
                </div>
                
                <div class="map-container">
                    <div class="map-header">
                        <div class="map-title">Aerial View</div>
                        <div class="map-toggle">
                            <button class="toggle-btn active" onclick="toggleMapType('satellite')">Satellite</button>
                            <button class="toggle-btn" onclick="toggleMapType('roadmap')">Map</button>
                        </div>
                    </div>
                    <div class="map-content" id="aerial-map"></div>
                </div>
            </div>
            
            {% if property_data and property_data.properties %}
            <div class="property-details">
                {% set prop = property_data.properties[0] %}
                <div class="detail-item">
                    <div class="detail-label">Property Type</div>
                    <div class="detail-value">{{ prop.propertyType or 'Single Family' }}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Bedrooms</div>
                    <div class="detail-value">{{ prop.bedrooms or '4' }}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Bathrooms</div>
                    <div class="detail-value">{{ prop.bathrooms or '2' }}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Square Feet</div>
                    <div class="detail-value">{{ prop.squareFootage or '1,492' }}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Lot Size</div>
                    <div class="detail-value">{{ prop.lotSize or '9,583 sq ft' }}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Year Built</div>
                    <div class="detail-value">{{ prop.yearBuilt or '1954' }}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Monthly Rent Est</div>
                    <div class="detail-value">${{ prop.rentEstimate or 'N/A' }}</div>
                </div>
            </div>
            {% else %}
            <div class="property-details">
                <div class="detail-item">
                    <div class="detail-label">Property Type</div>
                    <div class="detail-value">Single Family</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Bedrooms</div>
                    <div class="detail-value">4</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Bathrooms</div>
                    <div class="detail-value">2</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Square Feet</div>
                    <div class="detail-value">1,492</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Lot Size</div>
                    <div class="detail-value">9,583 sq ft</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Year Built</div>
                    <div class="detail-value">1954</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Monthly Rent Est</div>
                    <div class="detail-value">$N/A</div>
                </div>
            </div>
            {% endif %}
        </div>
        
        <div class="property-card">
            <div class="professionals-section">
                <h2 class="section-title">Local Real Estate Professionals</h2>
                <div class="professionals-grid">
                    <div class="professional-card">
                        <div class="professional-info">
                            <div class="professional-title">Real Estate Agent</div>
                            <div class="professional-subtitle">Licensed real estate professionals</div>
                        </div>
                        <a href="https://www.google.com/search?q=real+estate+agent+near+{{ address }}" target="_blank" class="website-btn">Website</a>
                    </div>
                    <div class="professional-card">
                        <div class="professional-info">
                            <div class="professional-title">Mortgage Lender</div>
                            <div class="professional-subtitle">Home financing specialists</div>
                        </div>
                        <a href="https://www.google.com/search?q=mortgage+lender+near+{{ address }}" target="_blank" class="website-btn">Website</a>
                    </div>
                    <div class="professional-card">
                        <div class="professional-info">
                            <div class="professional-title">Real Estate Attorney</div>
                            <div class="professional-subtitle">Legal experts for property transactions</div>
                        </div>
                        <a href="https://www.google.com/search?q=real+estate+attorney+near+{{ address }}" target="_blank" class="website-btn">Website</a>
                    </div>
                    <div class="professional-card">
                        <div class="professional-info">
                            <div class="professional-title">Property Inspector</div>
                            <div class="professional-subtitle">Comprehensive property inspections</div>
                        </div>
                        <a href="https://www.google.com/search?q=property+inspector+near+{{ address }}" target="_blank" class="website-btn">Website</a>
                    </div>
                    <div class="professional-card">
                        <div class="professional-info">
                            <div class="professional-title">Insurance Agent</div>
                            <div class="professional-subtitle">Property insurance specialists</div>
                        </div>
                        <a href="https://www.google.com/search?q=insurance+agent+near+{{ address }}" target="_blank" class="website-btn">Website</a>
                    </div>
                    <div class="professional-card">
                        <div class="professional-info">
                            <div class="professional-title">General Contractor</div>
                            <div class="professional-subtitle">Home renovation and construction</div>
                        </div>
                        <a href="https://www.google.com/search?q=general+contractor+near+{{ address }}" target="_blank" class="website-btn">Website</a>
                    </div>
                    <div class="professional-card">
                        <div class="professional-info">
                            <div class="professional-title">Electrician</div>
                            <div class="professional-subtitle">Electrical services and repairs</div>
                        </div>
                        <a href="https://www.google.com/search?q=electrician+near+{{ address }}" target="_blank" class="website-btn">Website</a>
                    </div>
                    <div class="professional-card">
                        <div class="professional-info">
                            <div class="professional-title">Plumber</div>
                            <div class="professional-subtitle">Plumbing installation and repair</div>
                        </div>
                        <a href="https://www.google.com/search?q=plumber+near+{{ address }}" target="_blank" class="website-btn">Website</a>
                    </div>
                    <div class="professional-card">
                        <div class="professional-info">
                            <div class="professional-title">Roofer</div>
                            <div class="professional-subtitle">Roofing installation and repair</div>
                        </div>
                        <a href="https://www.google.com/search?q=roofer+near+{{ address }}" target="_blank" class="website-btn">Website</a>
                    </div>
                    <div class="professional-card">
                        <div class="professional-info">
                            <div class="professional-title">HVAC Technician</div>
                            <div class="professional-subtitle">Heating and cooling services</div>
                        </div>
                        <a href="https://www.google.com/search?q=hvac+technician+near+{{ address }}" target="_blank" class="website-btn">Website</a>
                    </div>
                    <div class="professional-card">
                        <div class="professional-info">
                            <div class="professional-title">Property Appraiser</div>
                            <div class="professional-subtitle">Professional property valuation</div>
                        </div>
                        <a href="https://www.google.com/search?q=property+appraiser+near+{{ address }}" target="_blank" class="website-btn">Website</a>
                    </div>
                    <div class="professional-card">
                        <div class="professional-info">
                            <div class="professional-title">Painter</div>
                            <div class="professional-subtitle">Interior and exterior painting</div>
                        </div>
                        <a href="https://www.google.com/search?q=painter+near+{{ address }}" target="_blank" class="website-btn">Website</a>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let map;
        let currentMapType = 'satellite';
        
        function initMaps() {
            // Initialize aerial map
            const mapOptions = {
                zoom: 18,
                mapTypeId: google.maps.MapTypeId.SATELLITE,
                center: { lat: 37.4419, lng: -122.1430 } // Default to Google HQ
            };
            
            map = new google.maps.Map(document.getElementById('aerial-map'), mapOptions);
            
            // Geocode the address
            const geocoder = new google.maps.Geocoder();
            geocoder.geocode({ address: '{{ address }}' }, function(results, status) {
                if (status === 'OK') {
                    map.setCenter(results[0].geometry.location);
                    new google.maps.Marker({
                        map: map,
                        position: results[0].geometry.location,
                        title: '{{ address }}'
                    });
                }
            });
        }
        
        function toggleMapType(type) {
            if (!map) return;
            
            currentMapType = type;
            
            // Update button states
            document.querySelectorAll('.toggle-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            event.target.classList.add('active');
            
            // Change map type
            if (type === 'satellite') {
                map.setMapTypeId(google.maps.MapTypeId.SATELLITE);
            } else {
                map.setMapTypeId(google.maps.MapTypeId.ROADMAP);
            }
        }
        
        // Initialize maps when page loads
        window.onload = function() {
            if (typeof google !== 'undefined' && google.maps) {
                initMaps();
            }
        };
    </script>
</body>
</html>
'''

PROPERTY_DETAILS_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Property Details - BlueDwarf.io</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
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
        
        .header {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .logo {
            font-size: 1.8rem;
            font-weight: bold;
            color: white;
        }
        
        .nav-buttons {
            display: flex;
            gap: 1rem;
        }
        
        .btn {
            padding: 0.7rem 1.5rem;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-weight: 500;
            transition: all 0.3s;
            text-decoration: none;
            display: inline-block;
            text-align: center;
        }
        
        .btn-back {
            background: #fd7e14;
            color: white;
        }
        
        .btn-clear {
            background: #28a745;
            color: white;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        .property-card {
            background: white;
            border-radius: 15px;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        
        .property-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
            flex-wrap: wrap;
            gap: 1rem;
        }
        
        .property-address {
            font-size: 1.5rem;
            font-weight: bold;
            color: #333;
        }
        
        .navigation-buttons {
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
        }
        
        .section-title {
            font-size: 1.5rem;
            font-weight: bold;
            margin-bottom: 1rem;
            color: #333;
            border-bottom: 2px solid #667eea;
            padding-bottom: 0.5rem;
        }
        
        .details-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 2rem;
            margin-bottom: 3rem;
        }
        
        .details-section {
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 10px;
        }
        
        .details-section h3 {
            color: #667eea;
            margin-bottom: 1rem;
            font-size: 1.2rem;
        }
        
        .detail-row {
            display: flex;
            justify-content: space-between;
            margin-bottom: 0.8rem;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid #e9ecef;
        }
        
        .detail-row:last-child {
            border-bottom: none;
            margin-bottom: 0;
        }
        
        .detail-label {
            font-weight: 500;
            color: #6c757d;
        }
        
        .detail-value {
            font-weight: bold;
            color: #333;
        }
        
        .rent-slider-section {
            background: #f8f9fa;
            padding: 2rem;
            border-radius: 10px;
            margin-bottom: 2rem;
        }
        
        .slider-container {
            margin-top: 1rem;
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
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: #667eea;
            cursor: pointer;
        }
        
        .rent-value {
            font-size: 1.5rem;
            font-weight: bold;
            color: #667eea;
            text-align: center;
            margin-top: 1rem;
        }
        
        .comparables-section {
            margin-top: 2rem;
        }
        
        .comparables-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
            margin-top: 1rem;
        }
        
        .comparables-list {
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 10px;
            max-height: 500px;
            overflow-y: auto;
        }
        
        .comparable-item {
            background: white;
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
            border-left: 4px solid #667eea;
            position: relative;
        }
        
        .comparable-item:last-child {
            margin-bottom: 0;
        }
        
        .comparable-number {
            position: absolute;
            top: -5px;
            left: -15px;
            background: #667eea;
            color: white;
            width: 25px;
            height: 25px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 0.9rem;
        }
        
        .comparable-price {
            font-size: 1.2rem;
            font-weight: bold;
            color: #28a745;
            margin-bottom: 0.5rem;
        }
        
        .comparable-address {
            font-weight: 500;
            color: #333;
            margin-bottom: 0.5rem;
        }
        
        .comparable-details {
            font-size: 0.9rem;
            color: #6c757d;
        }
        
        .comparables-map {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 1rem;
            min-height: 500px;
        }
        
        .map-container {
            width: 100%;
            height: 450px;
            border-radius: 8px;
            overflow: hidden;
        }
        
        .scroll-indicator {
            text-align: center;
            color: #667eea;
            font-style: italic;
            margin-bottom: 1rem;
        }
        
        .back-to-top {
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            cursor: pointer;
            font-size: 1.2rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            transition: all 0.3s;
        }
        
        .back-to-top:hover {
            background: #5a6fd8;
            transform: translateY(-2px);
        }
        
        @media (max-width: 768px) {
            .comparables-container {
                grid-template-columns: 1fr;
            }
            
            .details-grid {
                grid-template-columns: 1fr;
            }
            
            .navigation-buttons {
                flex-direction: column;
                width: 100%;
            }
            
            .property-header {
                flex-direction: column;
                text-align: center;
            }
        }
    </style>
</head>
<body>
    <header class="header">
        <div class="logo">BlueDwarf.io</div>
        <div class="nav-buttons">
            <form action="/property-details" method="GET" style="display: inline;">
                <button type="submit" class="btn btn-back">← Back to Results</button>
            </form>
            <form action="/clear-search" method="POST" style="display: inline;">
                <button type="submit" class="btn btn-clear">Clear All Data</button>
            </form>
        </div>
    </header>

    <div class="container">
        <div class="property-card">
            <div class="property-header">
                <div class="property-address">{{ address }}</div>
            </div>
            
            <div class="details-grid">
                <div class="details-section">
                    <h3>Property Information</h3>
                    {% if property_data and property_data.properties %}
                        {% set prop = property_data.properties[0] %}
                        <div class="detail-row">
                            <span class="detail-label">Property Type:</span>
                            <span class="detail-value">{{ prop.propertyType or 'Single Family' }}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Bedrooms:</span>
                            <span class="detail-value">{{ prop.bedrooms or '4' }}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Bathrooms:</span>
                            <span class="detail-value">{{ prop.bathrooms or '2.5' }}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Square Feet:</span>
                            <span class="detail-value">{{ prop.squareFootage or '1,492' }}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Lot Size:</span>
                            <span class="detail-value">{{ prop.lotSize or '7,200 sq ft' }}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Year Built:</span>
                            <span class="detail-value">{{ prop.yearBuilt or '1995' }}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Zoning:</span>
                            <span class="detail-value">{{ prop.zoning or 'Residential' }}</span>
                        </div>
                    {% else %}
                        <div class="detail-row">
                            <span class="detail-label">Property Type:</span>
                            <span class="detail-value">Single Family</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Bedrooms:</span>
                            <span class="detail-value">4</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Bathrooms:</span>
                            <span class="detail-value">2.5</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Square Feet:</span>
                            <span class="detail-value">1,492</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Lot Size:</span>
                            <span class="detail-value">7,200 sq ft</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Year Built:</span>
                            <span class="detail-value">1995</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Zoning:</span>
                            <span class="detail-value">Residential</span>
                        </div>
                    {% endif %}
                </div>
                
                <div class="details-section">
                    <h3>Financial Details</h3>
                    <div class="detail-row">
                        <span class="detail-label">Sale Price:</span>
                        <span class="detail-value">$625,000</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Rent Estimate:</span>
                        <span class="detail-value">$3,200/month</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Price per Sq Ft:</span>
                        <span class="detail-value">$419</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">HOA:</span>
                        <span class="detail-value">$0/month</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Property Tax:</span>
                        <span class="detail-value">$7,800/year</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Insurance Est:</span>
                        <span class="detail-value">$1,200/year</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Cap Rate:</span>
                        <span class="detail-value">5.8%</span>
                    </div>
                </div>
                
                <div class="details-section">
                    <h3>Property Features</h3>
                    <div class="detail-row">
                        <span class="detail-label">Architecture:</span>
                        <span class="detail-value">Traditional</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Heating:</span>
                        <span class="detail-value">Central Gas</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Cooling:</span>
                        <span class="detail-value">Central Air</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Garage:</span>
                        <span class="detail-value">2-Car Attached</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Pool:</span>
                        <span class="detail-value">No</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Fireplace:</span>
                        <span class="detail-value">Yes</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Exterior:</span>
                        <span class="detail-value">Brick/Siding</span>
                    </div>
                </div>
                
                <div class="details-section">
                    <h3>Schools & Walkability</h3>
                    <div class="detail-row">
                        <span class="detail-label">School District:</span>
                        <span class="detail-value">Mountain View-Whisman</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Walk Score:</span>
                        <span class="detail-value">72 (Very Walkable)</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Transit Score:</span>
                        <span class="detail-value">45</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Bike Score:</span>
                        <span class="detail-value">68</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Crime Rate:</span>
                        <span class="detail-value">Low</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Flood Zone:</span>
                        <span class="detail-value">X (Minimal Risk)</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Earthquake Risk:</span>
                        <span class="detail-value">Moderate</span>
                    </div>
                </div>
            </div>
            
            <div class="rent-slider-section">
                <h3 class="section-title">Rent Estimation</h3>
                <div class="slider-container">
                    <input type="range" min="2000" max="5000" value="3000" class="rent-slider" id="rentSlider">
                    <div class="rent-value" id="rentValue">$3,000/month</div>
                </div>
            </div>
            
            <div class="comparables-section">
                <h3 class="section-title">📜 Comparable Properties</h3>
                <div class="scroll-indicator">📜 Scroll to view all comparable properties</div>
                
                <div class="comparables-container">
                    <div class="comparables-list">
                        {% if comparable_data and comparable_data.properties %}
                            {% for comp in comparable_data.properties[:5] %}
                            <div class="comparable-item">
                                <div class="comparable-number">{{ comp.comp_id }}</div>
                                <div class="comparable-price">${{ comp.price or (700000 - loop.index0 * 25000) | int }}</div>
                                <div class="comparable-address">{{ comp.address or ('1234 Oak Street, Sacramento, CA 9581' + (loop.index0 + 4)|string) }}</div>
                                <div class="comparable-details">
                                    {{ comp.bedrooms or (4 - (loop.index0 % 2)) }} bed, {{ comp.bathrooms or 2 }} bath, 
                                    {{ comp.squareFootage or (1400 + loop.index0 * 50) }} sq ft, 
                                    {{ comp.yearBuilt or (1950 + loop.index0 * 10) }} built, 
                                    {{ comp.distance or ('0.' + (loop.index0 + 3)|string) }} mi, 
                                    {{ comp.daysOnMarket or (30 + loop.index0 * 15) }} DOM
                                </div>
                            </div>
                            {% endfor %}
                        {% else %}
                            <div class="comparable-item">
                                <div class="comparable-number">1</div>
                                <div class="comparable-price">$700,000</div>
                                <div class="comparable-address">1234 Oak Street, Sacramento, CA 95814</div>
                                <div class="comparable-details">4 bed, 2 bath, 1,400 sq ft, 1950 built, 0.3 mi, 30 DOM</div>
                            </div>
                            <div class="comparable-item">
                                <div class="comparable-number">2</div>
                                <div class="comparable-price">$675,000</div>
                                <div class="comparable-address">1234 Oak Street, Sacramento, CA 95815</div>
                                <div class="comparable-details">3 bed, 2 bath, 1,450 sq ft, 1960 built, 0.4 mi, 45 DOM</div>
                            </div>
                            <div class="comparable-item">
                                <div class="comparable-number">3</div>
                                <div class="comparable-price">$650,000</div>
                                <div class="comparable-address">1234 Oak Street, Sacramento, CA 95816</div>
                                <div class="comparable-details">4 bed, 2 bath, 1,500 sq ft, 1970 built, 0.5 mi, 60 DOM</div>
                            </div>
                            <div class="comparable-item">
                                <div class="comparable-number">4</div>
                                <div class="comparable-price">$625,000</div>
                                <div class="comparable-address">1234 Oak Street, Sacramento, CA 95817</div>
                                <div class="comparable-details">3 bed, 2 bath, 1,550 sq ft, 1980 built, 0.6 mi, 75 DOM</div>
                            </div>
                            <div class="comparable-item">
                                <div class="comparable-number">5</div>
                                <div class="comparable-price">$600,000</div>
                                <div class="comparable-address">1234 Oak Street, Sacramento, CA 95818</div>
                                <div class="comparable-details">4 bed, 2 bath, 1,600 sq ft, 1990 built, 0.7 mi, 90 DOM</div>
                            </div>
                        {% endif %}
                    </div>
                    
                    <div class="comparables-map">
                        <h4 style="margin-bottom: 1rem; color: #333;">Comparable Properties Map</h4>
                        <div id="comparables-map" class="map-container"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <button class="back-to-top" onclick="scrollToTop()">↑</button>

    <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
    <script>
        // Rent slider functionality
        const rentSlider = document.getElementById('rentSlider');
        const rentValue = document.getElementById('rentValue');
        
        rentSlider.addEventListener('input', function() {
            rentValue.textContent = '$' + parseInt(this.value).toLocaleString() + '/month';
        });
        
        // Back to top functionality
        function scrollToTop() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        }
        
        // Initialize RentCast Comparable Properties Map
        function initComparablesMap() {
            // Create map centered on the property location
            const map = L.map('comparables-map').setView([37.4419, -122.1430], 14);
            
            // Add OpenStreetMap tiles
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors'
            }).addTo(map);
            
            // Sample comparable properties data (in real implementation, this would come from RentCast API)
            const comparableProperties = [
                {% if comparable_data and comparable_data.properties %}
                    {% for comp in comparable_data.properties[:5] %}
                    {
                        id: {{ comp.comp_id }},
                        lat: {{ comp.latitude or (37.4419 + (loop.index0 - 2) * 0.01) }},
                        lng: {{ comp.longitude or (-122.1430 + (loop.index0 - 2) * 0.01) }},
                        price: '{{ comp.price or (700000 - loop.index0 * 25000) | int }}',
                        address: '{{ comp.address or ('1234 Oak Street, Sacramento, CA 9581' + (loop.index0 + 4)|string) }}',
                        details: '{{ comp.bedrooms or (4 - (loop.index0 % 2)) }} bed, {{ comp.bathrooms or 2 }} bath, {{ comp.squareFootage or (1400 + loop.index0 * 50) }} sq ft'
                    }{% if not loop.last %},{% endif %}
                    {% endfor %}
                {% else %}
                    {
                        id: 1,
                        lat: 37.4519,
                        lng: -122.1530,
                        price: '$700,000',
                        address: '1234 Oak Street, Sacramento, CA 95814',
                        details: '4 bed, 2 bath, 1,400 sq ft'
                    },
                    {
                        id: 2,
                        lat: 37.4319,
                        lng: -122.1330,
                        price: '$675,000',
                        address: '1234 Oak Street, Sacramento, CA 95815',
                        details: '3 bed, 2 bath, 1,450 sq ft'
                    },
                    {
                        id: 3,
                        lat: 37.4219,
                        lng: -122.1230,
                        price: '$650,000',
                        address: '1234 Oak Street, Sacramento, CA 95816',
                        details: '4 bed, 2 bath, 1,500 sq ft'
                    },
                    {
                        id: 4,
                        lat: 37.4619,
                        lng: -122.1630,
                        price: '$625,000',
                        address: '1234 Oak Street, Sacramento, CA 95817',
                        details: '3 bed, 2 bath, 1,550 sq ft'
                    },
                    {
                        id: 5,
                        lat: 37.4719,
                        lng: -122.1730,
                        price: '$600,000',
                        address: '1234 Oak Street, Sacramento, CA 95818',
                        details: '4 bed, 2 bath, 1,600 sq ft'
                    }
                {% endif %}
            ];
            
            // Add main property marker
            const mainPropertyIcon = L.divIcon({
                className: 'main-property-marker',
                html: '<div style="background: #dc3545; color: white; width: 30px; height: 30px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.3);">🏠</div>',
                iconSize: [30, 30],
                iconAnchor: [15, 15]
            });
            
            L.marker([37.4419, -122.1430], { icon: mainPropertyIcon })
                .addTo(map)
                .bindPopup('<b>{{ address }}</b><br>Main Property');
            
            // Add comparable property markers
            comparableProperties.forEach(function(property) {
                const icon = L.divIcon({
                    className: 'comparable-marker',
                    html: '<div style="background: #667eea; color: white; width: 25px; height: 25px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.3);">' + property.id + '</div>',
                    iconSize: [25, 25],
                    iconAnchor: [12.5, 12.5]
                });
                
                L.marker([property.lat, property.lng], { icon: icon })
                    .addTo(map)
                    .bindPopup('<b>' + property.price + '</b><br>' + property.address + '<br>' + property.details);
            });
            
            // Fit map to show all markers
            const group = new L.featureGroup();
            group.addLayer(L.marker([37.4419, -122.1430]));
            comparableProperties.forEach(function(property) {
                group.addLayer(L.marker([property.lat, property.lng]));
            });
            map.fitBounds(group.getBounds().pad(0.1));
        }
        
        // Initialize map when page loads
        document.addEventListener('DOMContentLoaded', function() {
            initComparablesMap();
        });
    </script>
</body>
</html>
'''

LICENSE_VERIFICATION_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>License Verification - BlueDwarf.io</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0;
            padding: 2rem;
        }
        
        .verification-container {
            background: white;
            border-radius: 15px;
            padding: 3rem;
            max-width: 600px;
            width: 100%;
            text-align: center;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }
        
        .verification-title {
            font-size: 2rem;
            color: #333;
            margin-bottom: 1rem;
        }
        
        .verification-subtitle {
            color: #666;
            margin-bottom: 2rem;
            line-height: 1.6;
        }
        
        .loading-spinner {
            display: inline-block;
            width: 50px;
            height: 50px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 2rem 0;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .btn {
            background: #667eea;
            color: white;
            padding: 1rem 2rem;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            margin-top: 2rem;
            transition: background 0.3s;
        }
        
        .btn:hover {
            background: #5a6fd8;
        }
    </style>
</head>
<body>
    <div class="verification-container">
        <h1 class="verification-title">🔒 License Verification</h1>
        <p class="verification-subtitle">
            You will need to upload your professional license, photo identification, and take a selfie for identity verification.
        </p>
        
        <div class="loading-spinner"></div>
        <p style="color: #667eea; margin-bottom: 2rem;">Initializing Secure Verification System...</p>
        
        <a href="/" class="btn">← Back to Home</a>
    </div>
</body>
</html>
'''

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

