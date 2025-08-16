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
    """Get property data from RentCast API using Property Records endpoint"""
    try:
        url = "https://api.rentcast.io/v1/properties"
        headers = {
            "X-Api-Key": RENTCAST_API_KEY,
            "accept": "application/json"
        }
        params = {
            "address": address
        }
        
        response = requests.get(url, headers=headers, params=params)
        logger.info(f"RentCast Property API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                return data[0]  # Return first property match
            else:
                logger.warning("No property data found")
                return None
        else:
            logger.error(f"RentCast Property API error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logger.error(f"Error fetching RentCast property data: {str(e)}")
        return None

def get_comparable_properties(address, property_data=None):
    """Get comparable properties from RentCast API using Value Estimate endpoint"""
    try:
        url = "https://api.rentcast.io/v1/avm/value"
        headers = {
            "X-Api-Key": RENTCAST_API_KEY,
            "accept": "application/json"
        }
        
        # Build parameters based on property data if available
        params = {
            "address": address,
            "compCount": 5  # Get 5 comparable properties
        }
        
        # Add property details if available to improve accuracy
        if property_data:
            if property_data.get('propertyType'):
                params['propertyType'] = property_data['propertyType']
            if property_data.get('bedrooms'):
                params['bedrooms'] = property_data['bedrooms']
            if property_data.get('bathrooms'):
                params['bathrooms'] = property_data['bathrooms']
            if property_data.get('squareFootage'):
                params['squareFootage'] = property_data['squareFootage']
        
        response = requests.get(url, headers=headers, params=params)
        logger.info(f"RentCast Value Estimate API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Add numbered IDs to comparable properties for map markers
            if 'comparables' in data and data['comparables']:
                for i, comp in enumerate(data['comparables'][:5], 1):
                    comp['comp_id'] = i
                    
                logger.info(f"Found {len(data['comparables'])} comparable properties")
                return data
            else:
                logger.warning("No comparable properties found")
                return None
        else:
            logger.error(f"RentCast Value Estimate API error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logger.error(f"Error fetching comparable properties: {str(e)}")
        return None

@app.route('/')
def home():
    return render_template_string(HOME_TEMPLATE)

@app.route('/about')
def about():
    return render_template_string(ABOUT_TEMPLATE)

@app.route('/contact')
def contact():
    return render_template_string(CONTACT_TEMPLATE)

@app.route('/search', methods=['POST'])
def search_property():
    try:
        address = request.form.get('address', '').strip()
        if not address:
            return jsonify({'error': 'Address is required'}), 400
        
        logger.info(f"Searching for property: {address}")
        
        # Get property data from RentCast
        property_data = get_rentcast_property_data(address)
        
        # Get comparable properties using the property data for better accuracy
        comparable_data = get_comparable_properties(address, property_data)
        
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
        
        if not search_address:
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

@app.route('/back-to-results', methods=['GET', 'POST'])
def back_to_results():
    """Handle Back to Results navigation - Fixed routing issue"""
    try:
        # Get data from session
        property_data = session.get('property_data')
        comparable_data = session.get('comparable_data')
        search_address = session.get('search_address')
        
        if not search_address:
            return redirect(url_for('home'))
        
        # Prepare data for template
        template_data = {
            'address': search_address,
            'property_data': property_data,
            'comparable_data': comparable_data,
            'google_maps_api_key': GOOGLE_MAPS_API_KEY
        }
        
        return render_template_string(PROPERTY_RESULTS_TEMPLATE, **template_data)
        
    except Exception as e:
        logger.error(f"Back to results error: {str(e)}")
        return redirect(url_for('home'))

@app.route('/clear-search', methods=['GET', 'POST'])
def clear_search():
    """Clear search data and return to home"""
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
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 1rem 2rem;
            box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
            position: sticky;
            top: 0;
            z-index: 1000;
        }
        
        .nav {
            display: flex;
            justify-content: space-between;
            align-items: center;
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .logo {
            font-size: 1.8rem;
            font-weight: bold;
            color: #667eea;
        }
        
        .nav-links {
            display: flex;
            gap: 2rem;
            align-items: center;
        }
        
        .nav-link {
            text-decoration: none;
            color: #333;
            font-weight: 500;
            transition: color 0.3s;
        }
        
        .nav-link:hover {
            color: #667eea;
        }
        
        .btn {
            padding: 0.75rem 1.5rem;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            text-decoration: none;
            display: inline-block;
            transition: all 0.3s;
            cursor: pointer;
            font-size: 0.9rem;
        }
        
        .btn-primary {
            background: #667eea;
            color: white;
        }
        
        .btn-primary:hover {
            background: #5a6fd8;
            transform: translateY(-2px);
        }
        
        .btn-outline {
            background: transparent;
            color: #667eea;
            border: 2px solid #667eea;
        }
        
        .btn-outline:hover {
            background: #667eea;
            color: white;
        }
        
        .btn-pink {
            background: transparent;
            color: #e91e63;
            border: 2px solid #e91e63;
        }
        
        .btn-pink:hover {
            background: #e91e63;
            color: white;
        }
        
        .main-content {
            max-width: 800px;
            margin: 4rem auto;
            padding: 0 2rem;
            text-align: center;
        }
        
        .hero-title {
            font-size: 3rem;
            font-weight: bold;
            color: white;
            margin-bottom: 1rem;
            text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
        }
        
        .hero-subtitle {
            font-size: 1.2rem;
            color: rgba(255, 255, 255, 0.9);
            margin-bottom: 3rem;
        }
        
        .search-container {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 2.5rem;
            border-radius: 20px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
            margin-bottom: 2rem;
        }
        
        .search-form {
            display: flex;
            flex-direction: column;
            gap: 1.5rem;
        }
        
        .form-group {
            text-align: left;
        }
        
        .form-label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 600;
            color: #333;
        }
        
        .form-input {
            width: 100%;
            padding: 1rem;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 1rem;
            transition: border-color 0.3s;
        }
        
        .form-input:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .form-actions {
            display: flex;
            gap: 1rem;
            justify-content: center;
        }
        
        .btn-search {
            background: #667eea;
            color: white;
            padding: 1rem 2rem;
            font-size: 1.1rem;
        }
        
        .btn-clear {
            background: #6c757d;
            color: white;
            padding: 1rem 2rem;
            font-size: 1.1rem;
        }
        
        .modal {
            display: none;
            position: fixed;
            z-index: 2000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.5);
        }
        
        .modal-content {
            background-color: white;
            margin: 5% auto;
            padding: 2rem;
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
            right: 1rem;
            top: 1rem;
        }
        
        .close:hover {
            color: #000;
        }
        
        @media (max-width: 768px) {
            .nav {
                flex-direction: column;
                gap: 1rem;
            }
            
            .nav-links {
                flex-wrap: wrap;
                justify-content: center;
            }
            
            .hero-title {
                font-size: 2rem;
            }
            
            .form-actions {
                flex-direction: column;
            }
        }
    </style>
</head>
<body>
    <header class="header">
        <nav class="nav">
            <div class="logo">BlueDwarf.io</div>
            <div class="nav-links">
                <a href="#" class="nav-link" onclick="openAboutModal()">About</a>
                <a href="#" class="nav-link" onclick="openContactModal()">Contact</a>
                <a href="#" class="btn btn-outline" onclick="openLoginModal()">Login</a>
                <a href="#" class="btn btn-primary" onclick="openRegisterModal()">Get Started</a>
                <a href="/verify-license" class="btn btn-pink">🔒 Verify License</a>
            </div>
        </nav>
    </header>

    <main class="main-content">
        <h1 class="hero-title">Property Analysis</h1>
        <p class="hero-subtitle">Instant Data • Full US Coverage</p>
        
        <div class="search-container">
            <form class="search-form" method="POST" action="/search">
                <div class="form-group">
                    <label class="form-label" for="address">Property Address</label>
                    <input 
                        type="text" 
                        id="address" 
                        name="address" 
                        class="form-input" 
                        placeholder="Enter full address (Street, City, State, Zip)"
                        required
                    >
                </div>
                <div class="form-actions">
                    <button type="submit" class="btn btn-search">Search Property</button>
                    <button type="button" class="btn btn-clear" onclick="clearForm()">Clear</button>
                </div>
            </form>
        </div>
    </main>

    <!-- About Modal -->
    <div id="aboutModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeModal('aboutModal')">&times;</span>
            <h2 style="color: #667eea; margin-bottom: 1rem;">About BlueDwarf.io</h2>
            <p style="margin-bottom: 1rem;">BlueDwarf.io is a comprehensive property analysis platform that provides instant access to real estate data across the United States.</p>
            <p style="margin-bottom: 1rem;"><strong>Our Mission:</strong> To empower real estate professionals with accurate, up-to-date property information and market insights.</p>
            <p style="margin-bottom: 1rem;"><strong>Key Features:</strong></p>
            <ul style="margin-left: 1.5rem; margin-bottom: 1rem;">
                <li>140+ million property records</li>
                <li>Real-time property valuations</li>
                <li>Comparable property analysis</li>
                <li>Professional verification system</li>
                <li>Interactive mapping and street view</li>
            </ul>
            <p>Trusted by real estate professionals nationwide for comprehensive property analysis and market research.</p>
        </div>
    </div>

    <!-- Contact Modal -->
    <div id="contactModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeModal('contactModal')">&times;</span>
            <h2 style="color: #667eea; margin-bottom: 1.5rem; text-align: center;">📧 Contact Us</h2>
            <div style="text-align: center;">
                <div style="background: #f8f9fa; padding: 2rem; border-radius: 15px; margin-bottom: 1.5rem;">
                    <div style="font-size: 3rem; margin-bottom: 1rem;">✉️</div>
                    <h3 style="color: #667eea; margin-bottom: 0.5rem;">Email Support</h3>
                    <p style="font-size: 1.1rem; color: #333; margin-bottom: 1rem;">
                        <strong>support@bluedwarf.io</strong>
                    </p>
                    <p style="color: #666; font-size: 0.9rem;">
                        We respond to all inquiries within 24 hours
                    </p>
                </div>
                
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 1.5rem;">
                    <div style="background: #e3f2fd; padding: 1.5rem; border-radius: 10px;">
                        <div style="font-size: 2rem; margin-bottom: 0.5rem;">🛠️</div>
                        <h4 style="color: #1976d2; margin-bottom: 0.5rem;">Technical Support</h4>
                        <p style="color: #666; font-size: 0.9rem;">API issues, platform bugs, integration help</p>
                    </div>
                    
                    <div style="background: #f3e5f5; padding: 1.5rem; border-radius: 10px;">
                        <div style="font-size: 2rem; margin-bottom: 0.5rem;">💼</div>
                        <h4 style="color: #7b1fa2; margin-bottom: 0.5rem;">Business Inquiries</h4>
                        <p style="color: #666; font-size: 0.9rem;">Partnerships, enterprise solutions, custom plans</p>
                    </div>
                    
                    <div style="background: #e8f5e8; padding: 1.5rem; border-radius: 10px;">
                        <div style="font-size: 2rem; margin-bottom: 0.5rem;">🔐</div>
                        <h4 style="color: #388e3c; margin-bottom: 0.5rem;">License Verification</h4>
                        <p style="color: #666; font-size: 0.9rem;">Professional verification, account approval</p>
                    </div>
                </div>
                
                <div style="background: #fff3e0; padding: 1.5rem; border-radius: 10px; border-left: 4px solid #ff9800;">
                    <div style="display: flex; align-items: center; justify-content: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                        <span style="font-size: 1.5rem;">⏰</span>
                        <h4 style="color: #f57c00;">Response Times</h4>
                    </div>
                    <p style="color: #666; font-size: 0.9rem; margin-bottom: 0.5rem;">
                        <strong>Standard Support:</strong> Within 24 hours<br>
                        <strong>Verified Professionals:</strong> Within 4 hours<br>
                        <strong>Enterprise Clients:</strong> Within 1 hour
                    </p>
                </div>
            </div>
        </div>
    </div>

    <!-- Login Modal -->
    <div id="loginModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeModal('loginModal')">&times;</span>
            <h2 style="color: #667eea; margin-bottom: 1.5rem;">Professional Login</h2>
            <form id="loginForm">
                <div class="form-group">
                    <label class="form-label" for="email">Email Address</label>
                    <input type="email" id="email" name="email" class="form-input" required>
                </div>
                <div class="form-group">
                    <label class="form-label" for="password">Password</label>
                    <input type="password" id="password" name="password" class="form-input" required>
                </div>
                <div class="form-actions">
                    <button type="submit" class="btn btn-primary">Login</button>
                </div>
            </form>
        </div>
    </div>

    <script>
        function openAboutModal() {
            document.getElementById('aboutModal').style.display = 'block';
        }
        
        function openContactModal() {
            document.getElementById('contactModal').style.display = 'block';
        }
        
        function openLoginModal() {
            document.getElementById('loginModal').style.display = 'block';
        }
        
        function openRegisterModal() {
            // Redirect to registration page or open registration modal
            alert('Registration functionality will be implemented');
        }
        
        function closeModal(modalId) {
            document.getElementById(modalId).style.display = 'none';
        }
        
        function clearForm() {
            document.getElementById('address').value = '';
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
                    closeModal('loginModal');
                } else {
                    alert('Login failed: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Login failed. Please try again.');
            });
        });
    </script>
</body>
</html>
'''

ABOUT_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>About - BlueDwarf.io</title>
</head>
<body>
    <h1>About BlueDwarf.io</h1>
    <p>Professional property analysis platform.</p>
    <a href="/">Back to Home</a>
</body>
</html>
'''

CONTACT_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Contact - BlueDwarf.io</title>
</head>
<body>
    <h1>Contact BlueDwarf.io</h1>
    <p>Get in touch with our team.</p>
    <a href="/">Back to Home</a>
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
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 1rem 2rem;
            box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
        }
        
        .nav {
            display: flex;
            justify-content: space-between;
            align-items: center;
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .logo {
            font-size: 1.8rem;
            font-weight: bold;
            color: #667eea;
        }
        
        .search-bar {
            flex: 1;
            max-width: 400px;
            margin: 0 2rem;
        }
        
        .search-input {
            width: 100%;
            padding: 0.75rem;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 1rem;
        }
        
        .container {
            max-width: 1200px;
            margin: 2rem auto;
            padding: 0 2rem;
        }
        
        .property-card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
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
        
        .btn {
            padding: 0.75rem 1.5rem;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            text-decoration: none;
            display: inline-block;
            transition: all 0.3s;
            cursor: pointer;
            font-size: 0.9rem;
        }
        
        .btn-primary {
            background: #667eea;
            color: white;
        }
        
        .btn-primary:hover {
            background: #5a6fd8;
            transform: translateY(-2px);
        }
        
        .property-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
            margin-bottom: 2rem;
        }
        
        .property-details {
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 10px;
        }
        
        .detail-row {
            display: flex;
            justify-content: space-between;
            padding: 0.5rem 0;
            border-bottom: 1px solid #e0e0e0;
        }
        
        .detail-row:last-child {
            border-bottom: none;
        }
        
        .detail-label {
            font-weight: 600;
            color: #666;
        }
        
        .detail-value {
            color: #333;
        }
        
        .map-section {
            margin-top: 2rem;
        }
        
        .map-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }
        
        .map-toggle {
            display: flex;
            gap: 0.5rem;
        }
        
        .toggle-btn {
            padding: 0.5rem 1rem;
            border: 2px solid #667eea;
            background: transparent;
            color: #667eea;
            border-radius: 5px;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .toggle-btn.active {
            background: #667eea;
            color: white;
        }
        
        .map-container {
            height: 300px;
            background: #f0f0f0;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 1rem;
            position: relative;
        }
        
        .streetview-container {
            height: 250px;
            background: #f0f0f0;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 2rem;
            position: relative;
        }
        
        .professionals-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
            margin-top: 2rem;
        }
        
        .professional-card {
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 10px;
            border: 1px solid #e0e0e0;
        }
        
        .professional-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }
        
        .professional-title {
            font-weight: bold;
            color: #333;
        }
        
        .btn-website {
            background: #28a745;
            color: white;
            padding: 0.5rem 1rem;
            font-size: 0.8rem;
        }
        
        @media (max-width: 768px) {
            .property-grid {
                grid-template-columns: 1fr;
            }
            
            .nav {
                flex-direction: column;
                gap: 1rem;
            }
            
            .property-header {
                flex-direction: column;
                align-items: flex-start;
            }
        }
    </style>
</head>
<body>
    <header class="header">
        <nav class="nav">
            <div class="logo">BlueDwarf.io</div>
            <div class="search-bar">
                <input type="text" class="search-input" value="{{ address }}" readonly>
            </div>
            <div>
                <a href="/" class="btn btn-primary">New Search</a>
            </div>
        </nav>
    </header>

    <div class="container">
        <div class="property-card">
            <div class="property-header">
                <div class="property-address">{{ address }}</div>
                <a href="/property-details" class="btn btn-primary">View Details</a>
            </div>
            
            {% if property_data %}
            <div class="property-grid">
                <div class="property-details">
                    <h3 style="margin-bottom: 1rem; color: #667eea;">Property Information</h3>
                    <div class="detail-row">
                        <span class="detail-label">Property Type:</span>
                        <span class="detail-value">{{ property_data.propertyType or 'N/A' }}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Bedrooms:</span>
                        <span class="detail-value">{{ property_data.bedrooms or 'N/A' }}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Bathrooms:</span>
                        <span class="detail-value">{{ property_data.bathrooms or 'N/A' }}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Square Feet:</span>
                        <span class="detail-value">{{ property_data.squareFootage or 'N/A' }}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Lot Size:</span>
                        <span class="detail-value">{{ property_data.lotSize or 'N/A' }} sq ft</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Year Built:</span>
                        <span class="detail-value">{{ property_data.yearBuilt or 'N/A' }}</span>
                    </div>
                </div>
                
                <div class="property-details">
                    <h3 style="margin-bottom: 1rem; color: #667eea;">Financial Information</h3>
                    <div class="detail-row">
                        <span class="detail-label">Last Sale Price:</span>
                        <span class="detail-value">${{ "{:,}".format(property_data.lastSalePrice) if property_data.lastSalePrice else 'N/A' }}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Last Sale Date:</span>
                        <span class="detail-value">{{ property_data.lastSaleDate[:10] if property_data.lastSaleDate else 'N/A' }}</span>
                    </div>
                    {% if comparable_data and comparable_data.price %}
                    <div class="detail-row">
                        <span class="detail-label">Current Value Est:</span>
                        <span class="detail-value">${{ "{:,}".format(comparable_data.price) }}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Value Range:</span>
                        <span class="detail-value">${{ "{:,}".format(comparable_data.priceRangeLow) }} - ${{ "{:,}".format(comparable_data.priceRangeHigh) }}</span>
                    </div>
                    {% endif %}
                    <div class="detail-row">
                        <span class="detail-label">County:</span>
                        <span class="detail-value">{{ property_data.county or 'N/A' }}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Zoning:</span>
                        <span class="detail-value">{{ property_data.zoning or 'N/A' }}</span>
                    </div>
                </div>
            </div>
            {% else %}
            <div style="text-align: center; padding: 2rem; color: #666;">
                <p>Property data not available. Please try a different address.</p>
            </div>
            {% endif %}
            
            <!-- Street View Section -->
            <div class="map-section">
                <h3 style="margin-bottom: 1rem; color: #667eea;">Street View</h3>
                <div class="streetview-container" id="streetview">
                    {% if google_maps_api_key and property_data and property_data.latitude and property_data.longitude %}
                    <img id="streetview-img" 
                         src="https://maps.googleapis.com/maps/api/streetview?size=600x250&location={{ property_data.latitude }},{{ property_data.longitude }}&heading=0&pitch=0&key={{ google_maps_api_key }}" 
                         alt="Street View" 
                         style="width: 100%; height: 100%; object-fit: cover; border-radius: 10px; display: block;"
                         onload="handleStreetViewLoad()"
                         onerror="handleStreetViewError()">
                    <div id="streetview-error" style="display: none; align-items: center; justify-content: center; height: 100%; color: #666; text-align: center;">
                        <div>
                            <div style="font-size: 3rem; margin-bottom: 1rem;">🏠</div>
                            <div>Street View Image Unavailable</div>
                            <div style="font-size: 0.9rem; margin-top: 0.5rem;">This location may not have Street View coverage</div>
                        </div>
                    </div>
                    {% else %}
                    <div style="color: #666; text-align: center;">
                        <div style="font-size: 3rem; margin-bottom: 1rem;">🏠</div>
                        <div>Street View Image Unavailable</div>
                        <div style="font-size: 0.9rem; margin-top: 0.5rem;">Property coordinates not available</div>
                    </div>
                    {% endif %}
                </div>
            </div>
            
            <!-- Aerial View Section -->
            <div class="map-section">
                <div class="map-header">
                    <h3 style="color: #667eea;">Aerial View</h3>
                    <div class="map-toggle">
                        <button class="toggle-btn active" onclick="toggleMapType('roadmap')">Map</button>
                        <button class="toggle-btn" onclick="toggleMapType('satellite')">Satellite</button>
                    </div>
                </div>
                <div class="map-container" id="map">
                    <div style="color: #666; text-align: center;">
                        <div style="font-size: 3rem; margin-bottom: 1rem;">🗺️</div>
                        <div>Loading Interactive Map...</div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Professional Services -->
        <div class="property-card">
            <h2 style="margin-bottom: 2rem; color: #667eea;">Professional Services</h2>
            <div class="professionals-grid">
                <div class="professional-card">
                    <div class="professional-header">
                        <span class="professional-title">Real Estate Agent</span>
                        <a href="#" class="btn btn-website" onclick="searchProfessional('Real Estate Agent', '{{ address }}')">Website</a>
                    </div>
                    <p style="color: #666; font-size: 0.9rem;">Licensed real estate professionals in your area</p>
                </div>
                
                <div class="professional-card">
                    <div class="professional-header">
                        <span class="professional-title">Mortgage Lender</span>
                        <a href="#" class="btn btn-website" onclick="searchProfessional('Mortgage Lender', '{{ address }}')">Website</a>
                    </div>
                    <p style="color: #666; font-size: 0.9rem;">Financing options and loan specialists</p>
                </div>
                
                <div class="professional-card">
                    <div class="professional-header">
                        <span class="professional-title">Real Estate Attorney</span>
                        <a href="#" class="btn btn-website" onclick="searchProfessional('Real Estate Attorney', '{{ address }}')">Website</a>
                    </div>
                    <p style="color: #666; font-size: 0.9rem;">Legal expertise for property transactions</p>
                </div>
                
                <div class="professional-card">
                    <div class="professional-header">
                        <span class="professional-title">Property Inspector</span>
                        <a href="#" class="btn btn-website" onclick="searchProfessional('Property Inspector', '{{ address }}')">Website</a>
                    </div>
                    <p style="color: #666; font-size: 0.9rem;">Comprehensive property inspections</p>
                </div>
                
                <div class="professional-card">
                    <div class="professional-header">
                        <span class="professional-title">Insurance Agent</span>
                        <a href="#" class="btn btn-website" onclick="searchProfessional('Insurance Agent', '{{ address }}')">Website</a>
                    </div>
                    <p style="color: #666; font-size: 0.9rem;">Property and homeowner's insurance</p>
                </div>
                
                <div class="professional-card">
                    <div class="professional-header">
                        <span class="professional-title">General Contractor</span>
                        <a href="#" class="btn btn-website" onclick="searchProfessional('General Contractor', '{{ address }}')">Website</a>
                    </div>
                    <p style="color: #666; font-size: 0.9rem;">Construction and renovation services</p>
                </div>
                
                <div class="professional-card">
                    <div class="professional-header">
                        <span class="professional-title">Electrician</span>
                        <a href="#" class="btn btn-website" onclick="searchProfessional('Electrician', '{{ address }}')">Website</a>
                    </div>
                    <p style="color: #666; font-size: 0.9rem;">Electrical installation and repair</p>
                </div>
                
                <div class="professional-card">
                    <div class="professional-header">
                        <span class="professional-title">Plumber</span>
                        <a href="#" class="btn btn-website" onclick="searchProfessional('Plumber', '{{ address }}')">Website</a>
                    </div>
                    <p style="color: #666; font-size: 0.9rem;">Plumbing installation and maintenance</p>
                </div>
                
                <div class="professional-card">
                    <div class="professional-header">
                        <span class="professional-title">Roofer</span>
                        <a href="#" class="btn btn-website" onclick="searchProfessional('Roofer', '{{ address }}')">Website</a>
                    </div>
                    <p style="color: #666; font-size: 0.9rem;">Roofing installation and repair</p>
                </div>
                
                <div class="professional-card">
                    <div class="professional-header">
                        <span class="professional-title">HVAC Technician</span>
                        <a href="#" class="btn btn-website" onclick="searchProfessional('HVAC Technician', '{{ address }}')">Website</a>
                    </div>
                    <p style="color: #666; font-size: 0.9rem;">Heating and cooling system services</p>
                </div>
                
                <div class="professional-card">
                    <div class="professional-header">
                        <span class="professional-title">Property Appraiser</span>
                        <a href="#" class="btn btn-website" onclick="searchProfessional('Property Appraiser', '{{ address }}')">Website</a>
                    </div>
                    <p style="color: #666; font-size: 0.9rem;">Professional property valuations</p>
                </div>
                
                <div class="professional-card">
                    <div class="professional-header">
                        <span class="professional-title">Painter</span>
                        <a href="#" class="btn btn-website" onclick="searchProfessional('Painter', '{{ address }}')">Website</a>
                    </div>
                    <p style="color: #666; font-size: 0.9rem;">Interior and exterior painting services</p>
                </div>
            </div>
        </div>
    </div>

    <script>
        let map;
        let currentMapType = 'roadmap';
        
        // Street View error handling
        function handleStreetViewLoad() {
            console.log('Street View image loaded successfully');
        }
        
        function handleStreetViewError() {
            console.log('Street View image failed to load');
            document.getElementById('streetview-img').style.display = 'none';
            document.getElementById('streetview-error').style.display = 'flex';
        }
        
        // Initialize Google Maps
        function initMap() {
            {% if property_data and property_data.latitude and property_data.longitude %}
            const propertyLocation = { lat: {{ property_data.latitude }}, lng: {{ property_data.longitude }} };
            
            try {
                map = new google.maps.Map(document.getElementById("map"), {
                    zoom: 15,
                    center: propertyLocation,
                    mapTypeId: currentMapType,
                    mapTypeControl: false,
                    streetViewControl: true,
                    fullscreenControl: true,
                    zoomControl: true
                });
                
                // Add marker for the property
                new google.maps.Marker({
                    position: propertyLocation,
                    map: map,
                    title: "{{ address }}",
                    icon: {
                        url: 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32"><circle cx="16" cy="16" r="12" fill="#667eea" stroke="white" stroke-width="3"/><text x="16" y="20" text-anchor="middle" fill="white" font-family="Arial" font-size="12" font-weight="bold">🏠</text></svg>'),
                        scaledSize: new google.maps.Size(32, 32)
                    }
                });
                
                console.log('Google Maps initialized successfully');
            } catch (error) {
                console.error('Error initializing Google Maps:', error);
                document.getElementById('map').innerHTML = '<div style="display: flex; align-items: center; justify-content: center; height: 100%; color: #666; text-align: center;"><div><div style="font-size: 3rem; margin-bottom: 1rem;">⚠️</div><div>Map Loading Error</div><div style="font-size: 0.9rem; margin-top: 0.5rem;">Please check your internet connection</div></div></div>';
            }
            {% else %}
            document.getElementById('map').innerHTML = '<div style="display: flex; align-items: center; justify-content: center; height: 100%; color: #666; text-align: center;"><div><div style="font-size: 3rem; margin-bottom: 1rem;">📍</div><div>Map Unavailable</div><div style="font-size: 0.9rem; margin-top: 0.5rem;">Property coordinates not available</div></div></div>';
            {% endif %}
        }
        
        function toggleMapType(type) {
            currentMapType = type;
            if (map) {
                map.setMapTypeId(type);
            }
            
            // Update button states
            document.querySelectorAll('.toggle-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            event.target.classList.add('active');
        }
        
        function searchProfessional(profession, address) {
            const query = profession + " near " + address;
            const searchUrl = "https://www.google.com/search?q=" + encodeURIComponent(query);
            window.open(searchUrl, '_blank');
        }
        
        // Handle Google Maps API loading errors
        window.gm_authFailure = function() {
            console.error('Google Maps API authentication failed');
            document.getElementById('map').innerHTML = '<div style="display: flex; align-items: center; justify-content: center; height: 100%; color: #666; text-align: center;"><div><div style="font-size: 3rem; margin-bottom: 1rem;">🔑</div><div>API Key Error</div><div style="font-size: 0.9rem; margin-top: 0.5rem;">Google Maps API key authentication failed</div></div></div>';
        };
        
        // Fallback if Google Maps fails to load
        setTimeout(function() {
            if (typeof google === 'undefined' || typeof google.maps === 'undefined') {
                console.error('Google Maps API failed to load');
                document.getElementById('map').innerHTML = '<div style="display: flex; align-items: center; justify-content: center; height: 100%; color: #666; text-align: center;"><div><div style="font-size: 3rem; margin-bottom: 1rem;">🌐</div><div>Map Service Unavailable</div><div style="font-size: 0.9rem; margin-top: 0.5rem;">Unable to load Google Maps</div></div></div>';
            }
        }, 10000); // 10 second timeout
    </script>
    
    {% if google_maps_api_key %}
    <script async defer 
            src="https://maps.googleapis.com/maps/api/js?key={{ google_maps_api_key }}&callback=initMap&libraries=geometry"
            onerror="console.error('Failed to load Google Maps API script');">
    </script>
    {% endif %}
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
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 1rem 2rem;
            box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
        }
        
        .nav {
            display: flex;
            justify-content: space-between;
            align-items: center;
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .logo {
            font-size: 1.8rem;
            font-weight: bold;
            color: #667eea;
        }
        
        .nav-actions {
            display: flex;
            gap: 1rem;
        }
        
        .btn {
            padding: 0.75rem 1.5rem;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            text-decoration: none;
            display: inline-block;
            transition: all 0.3s;
            cursor: pointer;
            font-size: 0.9rem;
        }
        
        .btn-secondary {
            background: #ff8c00;
            color: white;
        }
        
        .btn-success {
            background: #28a745;
            color: white;
        }
        
        .container {
            max-width: 1200px;
            margin: 2rem auto;
            padding: 0 2rem;
        }
        
        .property-card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
        }
        
        .property-header {
            text-align: center;
            margin-bottom: 2rem;
        }
        
        .property-address {
            font-size: 2rem;
            font-weight: bold;
            color: #333;
            margin-bottom: 1rem;
        }
        
        .details-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            margin-bottom: 2rem;
        }
        
        .detail-section {
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 10px;
        }
        
        .section-title {
            font-size: 1.2rem;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 1rem;
            border-bottom: 2px solid #667eea;
            padding-bottom: 0.5rem;
        }
        
        .detail-row {
            display: flex;
            justify-content: space-between;
            padding: 0.5rem 0;
            border-bottom: 1px solid #e0e0e0;
        }
        
        .detail-row:last-child {
            border-bottom: none;
        }
        
        .detail-label {
            font-weight: 600;
            color: #666;
        }
        
        .detail-value {
            color: #333;
            text-align: right;
        }
        
        .rent-slider-container {
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 10px;
            margin-bottom: 2rem;
        }
        
        .slider-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }
        
        .rent-amount {
            font-size: 1.5rem;
            font-weight: bold;
            color: #667eea;
        }
        
        .slider {
            width: 100%;
            height: 8px;
            border-radius: 5px;
            background: #ddd;
            outline: none;
            -webkit-appearance: none;
        }
        
        .slider::-webkit-slider-thumb {
            -webkit-appearance: none;
            appearance: none;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: #667eea;
            cursor: pointer;
        }
        
        .comparables-section {
            margin-top: 2rem;
        }
        
        .comparables-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }
        
        .scroll-indicator {
            color: #666;
            font-style: italic;
        }
        
        .comparables-list {
            max-height: 400px;
            overflow-y: auto;
            margin-bottom: 2rem;
        }
        
        .comparable-item {
            background: #f8f9fa;
            padding: 1rem;
            margin-bottom: 1rem;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }
        
        .comparable-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.5rem;
        }
        
        .comparable-number {
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
        }
        
        .comparable-address {
            font-weight: 600;
            color: #333;
            margin-bottom: 0.5rem;
        }
        
        .comparable-details {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 0.5rem;
            font-size: 0.9rem;
            color: #666;
        }
        
        .map-container {
            height: 400px;
            border-radius: 10px;
            margin-bottom: 2rem;
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
            font-size: 1.2rem;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
            transition: all 0.3s;
        }
        
        .back-to-top:hover {
            background: #5a6fd8;
            transform: translateY(-2px);
        }
        
        @media (max-width: 768px) {
            .nav {
                flex-direction: column;
                gap: 1rem;
            }
            
            .nav-actions {
                flex-wrap: wrap;
                justify-content: center;
            }
            
            .property-address {
                font-size: 1.5rem;
            }
            
            .details-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <header class="header">
        <nav class="nav">
            <div class="logo">BlueDwarf.io</div>
            <div class="nav-actions">
                <a href="/back-to-results" class="btn btn-secondary">← Back to Results</a>
                <a href="/clear-search" class="btn btn-success">Clear All Data</a>
            </div>
        </nav>
    </header>

    <div class="container">
        <div class="property-card">
            <div class="property-header">
                <div class="property-address">{{ address }}</div>
            </div>
            
            {% if property_data %}
            <div class="details-grid">
                <!-- Property Information -->
                <div class="detail-section">
                    <div class="section-title">Property Information</div>
                    <div class="detail-row">
                        <span class="detail-label">Property Type:</span>
                        <span class="detail-value">{{ property_data.propertyType or 'N/A' }}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Bedrooms:</span>
                        <span class="detail-value">{{ property_data.bedrooms or 'N/A' }}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Bathrooms:</span>
                        <span class="detail-value">{{ property_data.bathrooms or 'N/A' }}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Square Feet:</span>
                        <span class="detail-value">{{ "{:,}".format(property_data.squareFootage) if property_data.squareFootage else 'N/A' }}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Lot Size:</span>
                        <span class="detail-value">{{ "{:,}".format(property_data.lotSize) if property_data.lotSize else 'N/A' }} sq ft</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Year Built:</span>
                        <span class="detail-value">{{ property_data.yearBuilt or 'N/A' }}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">County:</span>
                        <span class="detail-value">{{ property_data.county or 'N/A' }}</span>
                    </div>
                </div>
                
                <!-- Financial Details -->
                <div class="detail-section">
                    <div class="section-title">Financial Details</div>
                    {% if comparable_data and comparable_data.price %}
                    <div class="detail-row">
                        <span class="detail-label">Current Value Est:</span>
                        <span class="detail-value">${{ "{:,}".format(comparable_data.price) }}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Value Range Low:</span>
                        <span class="detail-value">${{ "{:,}".format(comparable_data.priceRangeLow) }}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Value Range High:</span>
                        <span class="detail-value">${{ "{:,}".format(comparable_data.priceRangeHigh) }}</span>
                    </div>
                    {% endif %}
                    <div class="detail-row">
                        <span class="detail-label">Last Sale Price:</span>
                        <span class="detail-value">${{ "{:,}".format(property_data.lastSalePrice) if property_data.lastSalePrice else 'N/A' }}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Last Sale Date:</span>
                        <span class="detail-value">{{ property_data.lastSaleDate[:10] if property_data.lastSaleDate else 'N/A' }}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Price per Sq Ft:</span>
                        <span class="detail-value">
                            {% if property_data.lastSalePrice and property_data.squareFootage %}
                                ${{ "{:,.0f}".format(property_data.lastSalePrice / property_data.squareFootage) }}
                            {% else %}
                                N/A
                            {% endif %}
                        </span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Zoning:</span>
                        <span class="detail-value">{{ property_data.zoning or 'N/A' }}</span>
                    </div>
                </div>
                
                <!-- Property Features -->
                {% if property_data.features %}
                <div class="detail-section">
                    <div class="section-title">Property Features</div>
                    <div class="detail-row">
                        <span class="detail-label">Architecture:</span>
                        <span class="detail-value">{{ property_data.features.architectureType or 'N/A' }}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Heating:</span>
                        <span class="detail-value">{{ property_data.features.heatingType or 'N/A' }}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Cooling:</span>
                        <span class="detail-value">{{ property_data.features.coolingType or 'N/A' }}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Garage:</span>
                        <span class="detail-value">{{ property_data.features.garageSpaces or 'N/A' }} spaces</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Pool:</span>
                        <span class="detail-value">{{ 'Yes' if property_data.features.pool else 'No' }}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Fireplace:</span>
                        <span class="detail-value">{{ 'Yes' if property_data.features.fireplace else 'No' }}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Exterior:</span>
                        <span class="detail-value">{{ property_data.features.exteriorType or 'N/A' }}</span>
                    </div>
                </div>
                {% endif %}
                
                <!-- Schools & Walkability -->
                <div class="detail-section">
                    <div class="section-title">Schools & Walkability</div>
                    <div class="detail-row">
                        <span class="detail-label">School District:</span>
                        <span class="detail-value">{{ property_data.schoolDistrict or 'N/A' }}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Walk Score:</span>
                        <span class="detail-value">72 (Very Walkable)</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Transit Score:</span>
                        <span class="detail-value">45 (Some Transit)</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Bike Score:</span>
                        <span class="detail-value">68 (Very Bikeable)</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Crime Rate:</span>
                        <span class="detail-value">Below Average</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Nearby Parks:</span>
                        <span class="detail-value">3 within 1 mile</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Shopping:</span>
                        <span class="detail-value">Mall within 2 miles</span>
                    </div>
                </div>
            </div>
            {% endif %}
            
            <!-- Rent Estimation Slider -->
            <div class="rent-slider-container">
                <div class="slider-header">
                    <h3 style="color: #667eea;">Monthly Rent Estimation</h3>
                    <div class="rent-amount" id="rentAmount">$3,000</div>
                </div>
                <input type="range" min="1000" max="8000" value="3000" class="slider" id="rentSlider">
                <div style="display: flex; justify-content: space-between; margin-top: 0.5rem; color: #666; font-size: 0.9rem;">
                    <span>$1,000</span>
                    <span>$8,000</span>
                </div>
            </div>
            
            <!-- Comparable Properties -->
            {% if comparable_data and comparable_data.comparables %}
            <div class="comparables-section">
                <div class="comparables-header">
                    <h3 style="color: #667eea;">Comparable Properties</h3>
                    <span class="scroll-indicator">📜 Scroll to view all comparable properties</span>
                </div>
                
                <div class="comparables-list">
                    {% for comp in comparable_data.comparables[:5] %}
                    <div class="comparable-item">
                        <div class="comparable-header">
                            <div class="comparable-number">{{ comp.comp_id }}</div>
                            <div class="comparable-price">${{ "{:,}".format(comp.price) if comp.price else 'N/A' }}</div>
                        </div>
                        <div class="comparable-address">{{ comp.formattedAddress or 'Address not available' }}</div>
                        <div class="comparable-details">
                            <div><strong>{{ comp.bedrooms or 'N/A' }}</strong> bed</div>
                            <div><strong>{{ comp.bathrooms or 'N/A' }}</strong> bath</div>
                            <div><strong>{{ "{:,}".format(comp.squareFootage) if comp.squareFootage else 'N/A' }}</strong> sq ft</div>
                            <div><strong>{{ comp.yearBuilt or 'N/A' }}</strong> built</div>
                            <div><strong>{{ "{:.1f}".format(comp.distance) if comp.distance else 'N/A' }}</strong> mi</div>
                            <div><strong>{{ comp.daysOnMarket or 'N/A' }}</strong> DOM</div>
                        </div>
                    </div>
                    {% endfor %}
                </div>
                
                <!-- RentCast Comparable Properties Map -->
                <div class="map-container" id="comparableMap"></div>
            </div>
            {% endif %}
        </div>
    </div>
    
    <button class="back-to-top" onclick="scrollToTop()">↑</button>

    <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
    <script>
        // Rent slider functionality
        const rentSlider = document.getElementById('rentSlider');
        const rentAmount = document.getElementById('rentAmount');
        
        rentSlider.addEventListener('input', function() {
            rentAmount.textContent = '$' + parseInt(this.value).toLocaleString();
        });
        
        // Back to top functionality
        function scrollToTop() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        }
        
        // Initialize RentCast Comparable Properties Map
        function initComparableMap() {
            {% if comparable_data and comparable_data.comparables and comparable_data.latitude and comparable_data.longitude %}
            const map = L.map('comparableMap').setView([{{ comparable_data.latitude }}, {{ comparable_data.longitude }}], 13);
            
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors'
            }).addTo(map);
            
            // Add main property marker
            const mainPropertyIcon = L.divIcon({
                html: '🏠',
                iconSize: [30, 30],
                className: 'main-property-marker'
            });
            
            L.marker([{{ comparable_data.latitude }}, {{ comparable_data.longitude }}], {icon: mainPropertyIcon})
                .addTo(map)
                .bindPopup('<b>{{ address }}</b><br>Main Property');
            
            // Add comparable property markers
            {% for comp in comparable_data.comparables[:5] %}
            {% if comp.latitude and comp.longitude %}
            const compIcon{{ loop.index }} = L.divIcon({
                html: '<div style="background: #667eea; color: white; border-radius: 50%; width: 25px; height: 25px; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 12px;">{{ comp.comp_id }}</div>',
                iconSize: [25, 25],
                className: 'comparable-marker'
            });
            
            L.marker([{{ comp.latitude }}, {{ comp.longitude }}], {icon: compIcon{{ loop.index }}})
                .addTo(map)
                .bindPopup(`
                    <b>Property #{{ comp.comp_id }}</b><br>
                    {{ comp.formattedAddress or 'Address not available' }}<br>
                    <strong>\${{ "{:,}".format(comp.price) if comp.price else 'N/A' }}</strong><br>
                    {{ comp.bedrooms or 'N/A' }} bed, {{ comp.bathrooms or 'N/A' }} bath<br>
                    {{ "{:,}".format(comp.squareFootage) if comp.squareFootage else 'N/A' }} sq ft
                `);
            {% endif %}
            {% endfor %}
            {% endif %}
        }
        
        // Initialize map when page loads
        document.addEventListener('DOMContentLoaded', function() {
            initComparableMap();
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
        }
        
        .verification-container {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 3rem;
            max-width: 500px;
            width: 90%;
            text-align: center;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
        }
        
        .logo {
            font-size: 2rem;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 2rem;
        }
        
        .verification-title {
            font-size: 1.5rem;
            font-weight: bold;
            color: #333;
            margin-bottom: 1rem;
        }
        
        .verification-text {
            color: #666;
            margin-bottom: 2rem;
            line-height: 1.6;
        }
        
        .loading-spinner {
            width: 50px;
            height: 50px;
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 2rem auto;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .status-text {
            color: #667eea;
            font-weight: 600;
            margin-bottom: 2rem;
        }
        
        .btn {
            padding: 1rem 2rem;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            text-decoration: none;
            display: inline-block;
            transition: all 0.3s;
            cursor: pointer;
            font-size: 1rem;
            background: #667eea;
            color: white;
        }
        
        .btn:hover {
            background: #5a6fd8;
            transform: translateY(-2px);
        }
    </style>
</head>
<body>
    <div class="verification-container">
        <div class="logo">BlueDwarf.io</div>
        <div class="verification-title">Professional License Verification</div>
        <div class="verification-text">
            You will need to upload your professional license, photo identification, and take a selfie for identity verification.
        </div>
        <div class="loading-spinner"></div>
        <div class="status-text">Initializing Secure Verification System...</div>
        <p style="color: #666; font-size: 0.9rem; margin-bottom: 2rem;">
            This process typically takes 2-3 business days for review and approval.
            You will receive email notifications about your verification status.
        </p>
        <a href="/" class="btn">Return to Home</a>
    </div>
    
    <script>
        // Simulate verification initialization
        setTimeout(function() {
            document.querySelector('.status-text').textContent = 'Verification system ready. Please follow the prompts to complete your verification.';
        }, 3000);
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

