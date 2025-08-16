from flask import Flask, render_template_string, request, redirect, url_for, jsonify
from flask_cors import CORS
import os
import requests
import hashlib
import hmac
import time
import json

app = Flask(__name__)
CORS(app)

# Google Maps API configuration
GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY', 'YOUR_GOOGLE_MAPS_API_KEY')

# Sumsub configuration
SUMSUB_APP_TOKEN = "sbx:Mfd6l7oxKRRbjzwBRfD5JewCe7xcUL7pIlOvPHGNSqp5zy..."
SUMSUB_SECRET_KEY = "GwFgol7U0miDMuUTbq3bluvRlF9M2oEv"
SUMSUB_BASE_URL = "https://api.sumsub.com"

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
            font-size: 1.5rem;
            font-weight: bold;
            color: white;
            text-decoration: none;
        }

        .nav-center {
            display: flex;
            gap: 2rem;
        }

        .nav-center a {
            color: white;
            text-decoration: none;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            transition: background-color 0.3s;
        }

        .nav-center a:hover {
            background-color: rgba(255, 255, 255, 0.2);
        }

        .nav-right {
            display: flex;
            gap: 1rem;
        }

        .btn {
            padding: 0.5rem 1rem;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            transition: all 0.3s;
            font-weight: 500;
        }

        .btn-login {
            background-color: rgba(255, 255, 255, 0.2);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }

        .btn-login:hover {
            background-color: rgba(255, 255, 255, 0.3);
        }

        .btn-get-started {
            background-color: #ff6b6b;
            color: white;
        }

        .btn-get-started:hover {
            background-color: #ff5252;
            transform: translateY(-2px);
        }

        .main-content {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: calc(100vh - 200px);
            text-align: center;
            padding: 2rem;
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

        .search-card {
            background: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            max-width: 500px;
            width: 100%;
        }

        .form-group {
            margin-bottom: 1.5rem;
        }

        .form-group label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 600;
            color: #333;
        }

        .form-group input {
            width: 100%;
            padding: 1rem;
            border: 2px solid #e1e5e9;
            border-radius: 8px;
            font-size: 1rem;
            transition: border-color 0.3s;
        }

        .form-group input:focus {
            outline: none;
            border-color: #667eea;
        }

        .btn-group {
            display: flex;
            gap: 1rem;
            justify-content: center;
        }

        .btn-search {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem 2rem;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            cursor: pointer;
            transition: transform 0.3s;
        }

        .btn-search:hover {
            transform: translateY(-2px);
        }

        .btn-clear {
            background-color: #6c757d;
            color: white;
            padding: 1rem 2rem;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            cursor: pointer;
            transition: background-color 0.3s;
        }

        .btn-clear:hover {
            background-color: #5a6268;
        }

        .footer {
            text-align: center;
            padding: 2rem;
            color: rgba(255, 255, 255, 0.8);
            font-size: 0.9rem;
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
            border-radius: 15px;
            width: 90%;
            max-width: 600px;
            max-height: 80vh;
            overflow-y: auto;
            position: relative;
        }

        .close {
            color: #aaa;
            float: right;
            font-size: 28px;
            font-weight: bold;
            position: absolute;
            right: 20px;
            top: 15px;
            cursor: pointer;
        }

        .close:hover {
            color: #000;
        }

        .modal h2 {
            margin-bottom: 1.5rem;
            color: #333;
        }

        .form-row {
            display: flex;
            gap: 1rem;
            margin-bottom: 1rem;
        }

        .form-row .form-group {
            flex: 1;
        }

        select {
            width: 100%;
            padding: 1rem;
            border: 2px solid #e1e5e9;
            border-radius: 8px;
            font-size: 1rem;
            background-color: white;
        }

        .btn-continue {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem 2rem;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            cursor: pointer;
            width: 100%;
            margin-top: 1rem;
        }

        .btn-continue:hover {
            transform: translateY(-2px);
        }

        @media (max-width: 768px) {
            .header {
                flex-direction: column;
                gap: 1rem;
                padding: 1rem;
            }

            .nav-center {
                order: 3;
            }

            .hero-title {
                font-size: 2rem;
            }

            .search-card {
                margin: 1rem;
                padding: 1.5rem;
            }

            .btn-group {
                flex-direction: column;
            }

            .form-row {
                flex-direction: column;
            }
        }
    </style>
</head>
<body>
    <header class="header">
        <a href="/" class="logo">🏠 BlueDwarf</a>
        <nav class="nav-center">
            <a href="#" onclick="openModal('aboutModal')">About</a>
            <a href="#" onclick="openModal('contactModal')">Contact</a>
        </nav>
        <div class="nav-right">
            <a href="#" class="btn btn-login">Login</a>
            <a href="#" class="btn btn-get-started" onclick="openModal('registrationModal')">Get Started</a>
        </div>
    </header>

    <main class="main-content">
        <h1 class="hero-title">🏠 Property Analysis</h1>
        <p class="hero-subtitle">Instant Data • Full US Coverage</p>
        
        <div class="search-card">
            <form action="/property-results" method="POST">
                <div class="form-group">
                    <label for="address">Address</label>
                    <input type="text" id="address" name="address" placeholder="123 Pine Street, Any City, WA, 54321" required>
                </div>
                <div class="btn-group">
                    <button type="submit" class="btn-search">Search</button>
                    <button type="button" class="btn-clear" onclick="clearForm()">Clear</button>
                </div>
            </form>
        </div>
    </main>

    <footer class="footer">
        © 2024 Elite Marketing Lab LLC. All rights reserved.<br>
        support@bluedwarf.io
    </footer>

    <!-- About Modal -->
    <div id="aboutModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeModal('aboutModal')">&times;</span>
            <h2>About BlueDwarf</h2>
            <p>BlueDwarf is a comprehensive property analysis platform that provides instant access to property data across the United States. Our platform combines cutting-edge technology with verified professional networks to deliver accurate, reliable property information.</p>
            
            <h3>Our Mission:</h3>
            <p>To democratize access to property information and connect property owners with verified, licensed professionals in their area.</p>
            
            <h3>Key Features:</h3>
            <ul>
                <li>Instant property analysis and valuation</li>
                <li>Street View and aerial mapping integration</li>
                <li>Comparable property analysis</li>
                <li>Verified professional network</li>
                <li>Professional license verification system</li>
                <li>Comprehensive property reports</li>
            </ul>
            
            <h3>Professional Verification:</h3>
            <p>We use advanced OCR technology and facial recognition to verify professional licenses, ensuring you only work with legitimate, licensed contractors and service providers.</p>
        </div>
    </div>

    <!-- Contact Modal -->
    <div id="contactModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeModal('contactModal')">&times;</span>
            <h2>Contact Us</h2>
            <form>
                <div class="form-group">
                    <label for="contact-name">Name</label>
                    <input type="text" id="contact-name" name="name" required>
                </div>
                <div class="form-group">
                    <label for="contact-email">Email</label>
                    <input type="email" id="contact-email" name="email" required>
                </div>
                <div class="form-group">
                    <label for="contact-subject">Subject</label>
                    <input type="text" id="contact-subject" name="subject" required>
                </div>
                <div class="form-group">
                    <label for="contact-message">Message</label>
                    <textarea id="contact-message" name="message" rows="5" style="width: 100%; padding: 1rem; border: 2px solid #e1e5e9; border-radius: 8px; font-size: 1rem; resize: vertical;" required></textarea>
                </div>
                <button type="submit" class="btn-continue">Send Message</button>
            </form>
        </div>
    </div>

    <!-- Registration Modal -->
    <div id="registrationModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeModal('registrationModal')">&times;</span>
            <h2>Professional Registration</h2>
            <form id="registrationForm" action="/continue-verification" method="POST">
                <div class="form-row">
                    <div class="form-group">
                        <label for="full-name">Full Name</label>
                        <input type="text" id="full-name" name="full_name" required>
                    </div>
                    <div class="form-group">
                        <label for="phone">Phone</label>
                        <input type="tel" id="phone" name="phone" required>
                    </div>
                </div>
                
                <div class="form-group">
                    <label for="email">Email</label>
                    <input type="email" id="email" name="email" required>
                </div>
                
                <div class="form-group">
                    <label for="business-address">Business Address</label>
                    <input type="text" id="business-address" name="business_address" required>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="license-number">License Number</label>
                        <input type="text" id="license-number" name="license_number" required>
                    </div>
                    <div class="form-group">
                        <label for="website">Website</label>
                        <input type="text" id="website" name="website" placeholder="example.com" pattern="[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}" title="Please enter a valid domain name (e.g., example.com)">
                    </div>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="profession">Profession</label>
                        <select id="profession" name="profession" required>
                            <option value="">Select Profession</option>
                            <option value="real_estate_agent">Real Estate Agent</option>
                            <option value="mortgage_lender">Mortgage Lender</option>
                            <option value="real_estate_attorney">Real Estate Attorney</option>
                            <option value="property_inspector">Property Inspector</option>
                            <option value="insurance_agent">Insurance Agent</option>
                            <option value="general_contractor">General Contractor</option>
                            <option value="electrician">Electrician</option>
                            <option value="plumber">Plumber</option>
                            <option value="roofer">Roofer</option>
                            <option value="hvac_technician">HVAC Technician</option>
                            <option value="property_appraiser">Property Appraiser</option>
                            <option value="painter">Painter</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="service-zip-codes">Service ZIP Codes</label>
                        <input type="text" id="service-zip-codes" name="service_zip_codes" placeholder="95814, 95815, 95816" required>
                    </div>
                </div>
                
                <div class="form-group">
                    <label for="password">Password</label>
                    <input type="password" id="password" name="password" required>
                </div>
                
                <button type="submit" class="btn-continue">Continue to License Verification</button>
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
            document.getElementById('address').value = '';
        }

        // Close modal when clicking outside of it
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

@app.route('/property-results', methods=['POST'])
def property_results():
    address = request.form.get('address', '')
    
    # Extract city and state from address for professional search
    address_parts = address.split(',')
    city_state = ', '.join(address_parts[-2:]).strip() if len(address_parts) >= 2 else 'Sacramento, CA'
    
    # Extract ZIP code for website button functionality
    zip_code = '95814'  # Default ZIP code
    if len(address_parts) >= 3:
        last_part = address_parts[-1].strip()
        # Extract ZIP code from last part (assuming format like "CA 95814")
        zip_parts = last_part.split()
        if len(zip_parts) >= 2:
            zip_code = zip_parts[-1]
    
    # Mock property data with enhanced details
    property_data = {
        'address': address,
        'estimated_value': '$500,000',
        'property_type': 'Single Family Home',
        'bedrooms': '4',
        'bathrooms': '2.5',
        'square_feet': '1,492',
        'lot_size': '0.18 acres',
        'year_built': '1964',
        'parking': '2-car garage',
        'heating_cooling': 'Central Air/Heat',
        'monthly_rent': '$3,000',
        'price_per_sqft': '$335',
        'property_tax': '$6,250/year',
        'zip_code': zip_code
    }
    
    # 12 Professional categories as specified
    professionals = [
        {
            'title': 'Real Estate Agent',
            'location': city_state,
            'description': 'Experienced agent specializing in residential properties and first-time buyers',
            'category': 'real estate agent'
        },
        {
            'title': 'Mortgage Lender',
            'location': city_state,
            'description': 'Specialized in home loans and refinancing with competitive rates',
            'category': 'mortgage lender'
        },
        {
            'title': 'Real Estate Attorney',
            'location': city_state,
            'description': 'Expert in real estate transactions and contract negotiations',
            'category': 'real estate attorney'
        },
        {
            'title': 'Property Inspector',
            'location': city_state,
            'description': 'Certified home inspector with comprehensive inspection services',
            'category': 'property inspector'
        },
        {
            'title': 'Insurance Agent',
            'location': city_state,
            'description': 'Home and auto insurance specialist with competitive coverage options',
            'category': 'insurance agent'
        },
        {
            'title': 'General Contractor',
            'location': city_state,
            'description': 'Licensed general contractor for home renovations and construction projects',
            'category': 'general contractor'
        },
        {
            'title': 'Electrician',
            'location': city_state,
            'description': 'Licensed electrician for residential and commercial electrical work',
            'category': 'electrician'
        },
        {
            'title': 'Plumber',
            'location': city_state,
            'description': 'Professional plumbing services for repairs, installations, and maintenance',
            'category': 'plumber'
        },
        {
            'title': 'Roofer',
            'location': city_state,
            'description': 'Expert roofing contractor for repairs, replacements, and installations',
            'category': 'roofer'
        },
        {
            'title': 'HVAC Technician',
            'location': city_state,
            'description': 'Heating, ventilation, and air conditioning installation and repair services',
            'category': 'hvac technician'
        },
        {
            'title': 'Property Appraiser',
            'location': city_state,
            'description': 'Certified property appraiser for accurate property valuations',
            'category': 'property appraiser'
        },
        {
            'title': 'Painter',
            'location': city_state,
            'description': 'Professional painting contractor for interior and exterior projects',
            'category': 'painter'
        }
    ]
    
    return render_template_string('''
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
            font-size: 1.5rem;
            font-weight: bold;
            color: white;
            text-decoration: none;
        }

        .nav-center {
            display: flex;
            gap: 2rem;
        }

        .nav-center a {
            color: white;
            text-decoration: none;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            transition: background-color 0.3s;
        }

        .nav-center a:hover {
            background-color: rgba(255, 255, 255, 0.2);
        }

        .nav-right {
            display: flex;
            gap: 1rem;
        }

        .btn {
            padding: 0.5rem 1rem;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            transition: all 0.3s;
            font-weight: 500;
        }

        .btn-login {
            background-color: rgba(255, 255, 255, 0.2);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }

        .btn-get-started {
            background-color: #ff6b6b;
            color: white;
        }

        .search-bar {
            background: white;
            padding: 1rem 2rem;
            display: flex;
            align-items: center;
            gap: 1rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        .search-bar label {
            font-weight: 600;
            color: #333;
        }

        .search-bar input {
            flex: 1;
            padding: 0.75rem;
            border: 2px solid #e1e5e9;
            border-radius: 5px;
            font-size: 1rem;
        }

        .search-bar button {
            padding: 0.75rem 1.5rem;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-weight: 500;
            transition: all 0.3s;
        }

        .btn-search {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }

        .btn-clear {
            background-color: #6c757d;
            color: white;
        }

        .content {
            padding: 2rem;
            max-width: 1200px;
            margin: 0 auto;
        }

        .property-title {
            text-align: center;
            color: white;
            font-size: 2rem;
            margin-bottom: 2rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }

        .property-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
            margin-bottom: 3rem;
        }

        .property-details, .property-visuals {
            background: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }

        .property-details h3 {
            margin-bottom: 1.5rem;
            color: #333;
            font-size: 1.5rem;
        }

        .property-list {
            list-style: none;
        }

        .property-list li {
            display: flex;
            justify-content: space-between;
            padding: 0.75rem 0;
            border-bottom: 1px solid #f0f0f0;
        }

        .property-list li:last-child {
            border-bottom: none;
        }

        .property-label {
            font-weight: 600;
            color: #555;
        }

        .property-value {
            color: #333;
            font-weight: 500;
        }

        .visual-section {
            margin-bottom: 2rem;
        }

        .visual-section:last-child {
            margin-bottom: 0;
        }

        .visual-section h4 {
            margin-bottom: 1rem;
            color: #667eea;
            font-size: 1.2rem;
        }

        .map-controls {
            display: flex;
            gap: 0.5rem;
            margin-bottom: 1rem;
        }

        .map-control-btn {
            padding: 0.5rem 1rem;
            border: 1px solid #ddd;
            background: white;
            cursor: pointer;
            border-radius: 5px;
            transition: all 0.3s;
        }

        .map-control-btn.active {
            background: #667eea;
            color: white;
            border-color: #667eea;
        }

        .btn-view-details {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem 2rem;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            cursor: pointer;
            width: 100%;
            margin-top: 1rem;
            transition: transform 0.3s;
        }

        .btn-view-details:hover {
            transform: translateY(-2px);
        }

        .professionals-section {
            background: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
        }

        .professionals-section h2 {
            text-align: center;
            margin-bottom: 2rem;
            color: #333;
            font-size: 2rem;
        }

        .professionals-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 2rem;
        }

        .professional-card {
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 10px;
            border: 1px solid #e1e5e9;
            transition: transform 0.3s, box-shadow 0.3s;
        }

        .professional-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        }

        .professional-card h3 {
            color: #333;
            margin-bottom: 0.5rem;
            font-size: 1.3rem;
        }

        .professional-location {
            color: #666;
            font-size: 0.9rem;
            margin-bottom: 1rem;
        }

        .professional-description {
            color: #555;
            margin-bottom: 1.5rem;
            line-height: 1.5;
        }

        .btn-website {
            background: #667eea;
            color: white;
            padding: 0.75rem 1.5rem;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            transition: background-color 0.3s;
            font-weight: 500;
        }

        .btn-website:hover {
            background: #5a67d8;
        }

        .clear-section {
            background: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            text-align: center;
        }

        .clear-section h3 {
            color: #333;
            margin-bottom: 1rem;
        }

        .clear-section p {
            color: #666;
            margin-bottom: 1.5rem;
        }

        .btn-clear-all {
            background: #dc3545;
            color: white;
            padding: 1rem 2rem;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            cursor: pointer;
            transition: background-color 0.3s;
        }

        .btn-clear-all:hover {
            background: #c82333;
        }

        @media (max-width: 768px) {
            .property-container {
                grid-template-columns: 1fr;
            }

            .professionals-grid {
                grid-template-columns: 1fr;
            }

            .search-bar {
                flex-direction: column;
                align-items: stretch;
            }

            .search-bar input {
                margin: 0.5rem 0;
            }
        }
    </style>
</head>
<body>
    <header class="header">
        <a href="/" class="logo">🏠 BlueDwarf</a>
        <nav class="nav-center">
            <a href="#" onclick="openModal('aboutModal')">About</a>
            <a href="#" onclick="openModal('contactModal')">Contact</a>
        </nav>
        <div class="nav-right">
            <a href="#" class="btn btn-login">Login</a>
            <a href="#" class="btn btn-get-started" onclick="openModal('registrationModal')">Get Started</a>
        </div>
    </header>

    <div class="search-bar">
        <label for="address">Address</label>
        <input type="text" id="address" value="{{ property_data.address }}" readonly>
        <button type="button" class="btn-search" onclick="searchProperty()">Search</button>
        <button type="button" class="btn-clear" onclick="clearResults()">Clear</button>
    </div>

    <div class="content">
        <h1 class="property-title">{{ property_data.address }}</h1>
        
        <div class="property-container">
            <div class="property-details">
                <h3>Property Details</h3>
                <ul class="property-list">
                    <li>
                        <span class="property-label">Estimated Value:</span>
                        <span class="property-value">{{ property_data.estimated_value }}</span>
                    </li>
                    <li>
                        <span class="property-label">Property Type:</span>
                        <span class="property-value">{{ property_data.property_type }}</span>
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
                        <span class="property-label">Lot Size:</span>
                        <span class="property-value">{{ property_data.lot_size }}</span>
                    </li>
                    <li>
                        <span class="property-label">Year Built:</span>
                        <span class="property-value">{{ property_data.year_built }}</span>
                    </li>
                    <li>
                        <span class="property-label">Parking:</span>
                        <span class="property-value">{{ property_data.parking }}</span>
                    </li>
                    <li>
                        <span class="property-label">Heating/Cooling:</span>
                        <span class="property-value">{{ property_data.heating_cooling }}</span>
                    </li>
                    <li>
                        <span class="property-label">Monthly Rent Est:</span>
                        <span class="property-value">{{ property_data.monthly_rent }}</span>
                    </li>
                    <li>
                        <span class="property-label">Price per Sq Ft:</span>
                        <span class="property-value">{{ property_data.price_per_sqft }}</span>
                    </li>
                    <li>
                        <span class="property-label">Property Tax:</span>
                        <span class="property-value">{{ property_data.property_tax }}</span>
                    </li>
                </ul>
            </div>
            
            <div class="property-visuals">
                <div class="visual-section">
                    <h4>Street View</h4>
                    <img src="https://maps.googleapis.com/maps/api/streetview?size=400x300&location={{ property_data.address }}&key={{ google_maps_api_key }}" 
                         alt="Street View" style="width: 100%; border-radius: 8px;" 
                         onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">
                    <div class="visual-placeholder" style="display: none;">Street View Image</div>
                </div>
                
                <div class="visual-section">
                    <h4>Aerial View (2 blocks)</h4>
                    <div class="map-controls">
                        <button class="map-control-btn active" onclick="toggleMapType('roadmap')">Map</button>
                        <button class="map-control-btn" onclick="toggleMapType('satellite')">Satellite</button>
                    </div>
                    <div id="map" style="width: 100%; height: 200px; border-radius: 8px;"></div>
                </div>
                
                <button class="btn-view-details" onclick="viewDetails('{{ property_data.address }}')">View Details</button>
            </div>
        </div>

        <div class="professionals-section">
            <h2>Local Professionals in {{ city_state }}</h2>
            <div class="professionals-grid">
                {% for professional in professionals %}
                <div class="professional-card">
                    <h3>{{ professional.title }}</h3>
                    <div class="professional-location">{{ professional.location }}</div>
                    <div class="professional-description">{{ professional.description }}</div>
                    <button class="btn-website" onclick="searchProfessional('{{ professional.category }}', '{{ property_data.zip_code }}')">Website</button>
                </div>
                {% endfor %}
            </div>
        </div>

        <div class="clear-section">
            <h3>🗑️ Clear All Results</h3>
            <p>Want to start a new search? Clear all property data and professional listings.</p>
            <button class="btn-clear-all" onclick="clearResults()">Clear All Results</button>
        </div>
    </div>

    <script>
        let map;
        let currentMapType = 'roadmap';

        function initMap() {
            const address = "{{ property_data.address }}";
            const geocoder = new google.maps.Geocoder();
            
            geocoder.geocode({ address: address }, function(results, status) {
                if (status === 'OK') {
                    const location = results[0].geometry.location;
                    
                    map = new google.maps.Map(document.getElementById('map'), {
                        zoom: 16,
                        center: location,
                        mapTypeId: currentMapType
                    });

                    new google.maps.Marker({
                        position: location,
                        map: map,
                        title: address
                    });
                } else {
                    document.getElementById('map').innerHTML = '<div style="padding: 2rem; text-align: center; color: #666;">Map could not be loaded</div>';
                }
            });
        }

        function toggleMapType(type) {
            currentMapType = type;
            if (map) {
                map.setMapTypeId(type);
            }
            
            // Update button states
            document.querySelectorAll('.map-control-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            event.target.classList.add('active');
        }

        function viewDetails(address) {
            window.location.href = '/property-details?address=' + encodeURIComponent(address);
        }

        function searchProfessional(category, zipCode) {
            const searchQuery = category + ' ' + zipCode;
            const googleSearchUrl = 'https://www.google.com/search?q=' + encodeURIComponent(searchQuery);
            window.open(googleSearchUrl, '_blank');
        }

        function clearResults() {
            window.location.href = '/clear-results';
        }

        function searchProperty() {
            const address = document.getElementById('address').value;
            if (address) {
                const form = document.createElement('form');
                form.method = 'POST';
                form.action = '/property-results';
                
                const input = document.createElement('input');
                input.type = 'hidden';
                input.name = 'address';
                input.value = address;
                
                form.appendChild(input);
                document.body.appendChild(form);
                form.submit();
            }
        }

        // Initialize map when page loads
        window.onload = function() {
            if (typeof google !== 'undefined' && google.maps) {
                initMap();
            }
        }
    </script>
    <script async defer src="https://maps.googleapis.com/maps/api/js?key={{ google_maps_api_key }}&callback=initMap"></script>
</body>
</html>
    ''', property_data=property_data, professionals=professionals, city_state=city_state, google_maps_api_key=GOOGLE_MAPS_API_KEY)

@app.route('/property-details')
def property_details():
    address = request.args.get('address', '')
    
    # Mock property data
    property_data = {
        'address': address,
        'estimated_value': '$500,000',
        'bedrooms': '4',
        'bathrooms': '2.5',
        'square_feet': '1,492',
        'lot_size': '0.18 acres',
        'year_built': '1964',
        'parking': '2-car garage',
        'heating': 'Central Air/Heat',
        'cooling': 'Central Air',
        'monthly_rent': '$3,000',
        'price_per_sqft': '$335',
        'property_tax': '$6,250/year',
        'hoa_fees': 'None',
        'last_sold': 'March 2019',
        'last_sold_price': '$425,000',
        'flooring': 'Hardwood, Carpet',
        'roof': 'Composition Shingle',
        'exterior': 'Stucco',
        'zoning': 'Residential R-1',
        'school_district': 'Sacramento City Unified',
        'elementary_school': 'John Bidwell Elementary',
        'middle_school': 'Kit Carson Middle School',
        'high_school': 'McClatchy High School',
        'walk_score': '72 - Very Walkable',
        'transit_score': '45 - Some Transit',
        'bike_score': '68 - Bikeable'
    }
    
    # Mock comparable properties with numbered markers
    comparable_properties = [
        {
            'id': 1,
            'address': '125 Main Street, Sacramento, CA',
            'bedrooms': '3',
            'bathrooms': '2',
            'square_feet': '1,380',
            'year_built': '1962',
            'distance': '0.1 miles away',
            'days_on_market': '45 days on market',
            'price_per_sqft': '$344/sq ft',
            'estimated_value': '$475,000',
            'lat': 38.5816,
            'lng': -121.4944
        },
        {
            'id': 2,
            'address': '456 Oak Avenue, Sacramento, CA',
            'bedrooms': '4',
            'bathrooms': '3',
            'square_feet': '1,650',
            'year_built': '1968',
            'distance': '0.3 miles away',
            'days_on_market': '32 days on market',
            'price_per_sqft': '$318/sq ft',
            'estimated_value': '$525,000',
            'lat': 38.5826,
            'lng': -121.4954
        },
        {
            'id': 3,
            'address': '789 Pine Street, Sacramento, CA',
            'bedrooms': '3',
            'bathrooms': '2',
            'square_feet': '1,250',
            'year_built': '1960',
            'distance': '0.5 miles away',
            'days_on_market': '67 days on market',
            'price_per_sqft': '$360/sq ft',
            'estimated_value': '$450,000',
            'lat': 38.5836,
            'lng': -121.4964
        },
        {
            'id': 4,
            'address': '321 Elm Drive, Sacramento, CA',
            'bedrooms': '4',
            'bathrooms': '2.5',
            'square_feet': '1,580',
            'year_built': '1965',
            'distance': '0.7 miles away',
            'days_on_market': '28 days on market',
            'price_per_sqft': '$323/sq ft',
            'estimated_value': '$510,000',
            'lat': 38.5846,
            'lng': -121.4974
        },
        {
            'id': 5,
            'address': '654 Maple Court, Sacramento, CA',
            'bedrooms': '3',
            'bathrooms': '2.5',
            'square_feet': '1,420',
            'year_built': '1963',
            'distance': '0.9 miles away',
            'days_on_market': '51 days on market',
            'price_per_sqft': '$342/sq ft',
            'estimated_value': '$485,000',
            'lat': 38.5856,
            'lng': -121.4984
        }
    ]
    
    return render_template_string('''
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
            font-size: 1.5rem;
            font-weight: bold;
            color: white;
            text-decoration: none;
        }

        .nav-center {
            display: flex;
            gap: 2rem;
        }

        .nav-center a {
            color: white;
            text-decoration: none;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            transition: background-color 0.3s;
        }

        .nav-right {
            display: flex;
            gap: 1rem;
        }

        .btn {
            padding: 0.5rem 1rem;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            transition: all 0.3s;
            font-weight: 500;
        }

        .btn-back {
            background-color: #ff6b6b;
            color: white;
            margin: 1rem 2rem;
        }

        .btn-back:hover {
            background-color: #ff5252;
        }

        .content {
            padding: 2rem;
            max-width: 1200px;
            margin: 0 auto;
        }

        .property-title {
            text-align: center;
            color: white;
            font-size: 2rem;
            margin-bottom: 2rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }

        .details-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
            margin-bottom: 2rem;
        }

        .details-section {
            background: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }

        .details-section h3 {
            margin-bottom: 1.5rem;
            color: #333;
            font-size: 1.3rem;
            border-bottom: 2px solid #667eea;
            padding-bottom: 0.5rem;
        }

        .property-list {
            list-style: none;
        }

        .property-list li {
            display: flex;
            justify-content: space-between;
            padding: 0.75rem 0;
            border-bottom: 1px solid #f0f0f0;
        }

        .property-list li:last-child {
            border-bottom: none;
        }

        .property-label {
            font-weight: 600;
            color: #555;
        }

        .property-value {
            color: #333;
            font-weight: 500;
        }

        .rent-estimation {
            margin-top: 1.5rem;
        }

        .rent-slider {
            width: 100%;
            margin: 1rem 0;
        }

        .rent-display {
            text-align: center;
            font-size: 1.5rem;
            color: #667eea;
            font-weight: bold;
            margin: 1rem 0;
        }

        .rent-range {
            display: flex;
            justify-content: space-between;
            color: #666;
            font-size: 0.9rem;
        }

        .comparables-section {
            background: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
        }

        .comparables-section h3 {
            margin-bottom: 1.5rem;
            color: #333;
            font-size: 1.5rem;
            text-align: center;
        }

        .comparables-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
        }

        .comparables-map {
            height: 400px;
            border-radius: 10px;
            border: 1px solid #e1e5e9;
        }

        .comparables-list {
            max-height: 400px;
            overflow-y: auto;
            padding-right: 1rem;
            border: 2px solid #667eea;
            border-radius: 10px;
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        }

        /* Scrollbar styling to make it obvious */
        .comparables-list::-webkit-scrollbar {
            width: 12px;
        }

        .comparables-list::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 10px;
        }

        .comparables-list::-webkit-scrollbar-thumb {
            background: #667eea;
            border-radius: 10px;
        }

        .comparables-list::-webkit-scrollbar-thumb:hover {
            background: #5a67d8;
        }

        .scroll-indicator {
            text-align: center;
            color: #667eea;
            font-weight: bold;
            padding: 0.5rem;
            background: rgba(102, 126, 234, 0.1);
            border-radius: 5px;
            margin-bottom: 1rem;
            font-size: 0.9rem;
        }

        .comparable-card {
            background: white;
            margin: 1rem;
            padding: 1.5rem;
            border-radius: 10px;
            border: 1px solid #e1e5e9;
            cursor: pointer;
            transition: all 0.3s;
            position: relative;
        }

        .comparable-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            border-color: #667eea;
        }

        .comparable-number {
            position: absolute;
            top: -10px;
            left: 15px;
            background: #667eea;
            color: white;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 1.1rem;
        }

        .comparable-address {
            font-weight: bold;
            color: #333;
            margin-bottom: 0.5rem;
            margin-top: 0.5rem;
        }

        .comparable-specs {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 0.5rem;
            margin: 1rem 0;
            font-size: 0.9rem;
            color: #666;
        }

        .comparable-price {
            font-size: 1.2rem;
            font-weight: bold;
            color: #667eea;
            text-align: center;
            margin-top: 1rem;
            padding-top: 1rem;
            border-top: 1px solid #e1e5e9;
        }

        @media (max-width: 768px) {
            .details-grid {
                grid-template-columns: 1fr;
            }

            .comparables-container {
                grid-template-columns: 1fr;
            }

            .comparables-map {
                height: 300px;
            }
        }
    </style>
</head>
<body>
    <header class="header">
        <a href="/" class="logo">🏠 BlueDwarf</a>
        <nav class="nav-center">
            <a href="#" onclick="openModal('aboutModal')">About</a>
            <a href="#" onclick="openModal('contactModal')">Contact</a>
        </nav>
        <div class="nav-right">
            <a href="#" class="btn btn-login">Login</a>
            <a href="#" class="btn btn-get-started" onclick="openModal('registrationModal')">Get Started</a>
        </div>
    </header>

    <button class="btn btn-back" onclick="history.back()">← Back to Results</button>

    <div class="content">
        <h1 class="property-title">{{ property_data.address }}</h1>
        
        <div class="details-grid">
            <div class="details-section">
                <h3>Property Information</h3>
                <ul class="property-list">
                    <li>
                        <span class="property-label">Estimated Value:</span>
                        <span class="property-value">{{ property_data.estimated_value }}</span>
                    </li>
                    <li>
                        <span class="property-label">Property Type:</span>
                        <span class="property-value">Single Family Home</span>
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
                        <span class="property-label">Lot Size:</span>
                        <span class="property-value">{{ property_data.lot_size }}</span>
                    </li>
                    <li>
                        <span class="property-label">Year Built:</span>
                        <span class="property-value">{{ property_data.year_built }}</span>
                    </li>
                    <li>
                        <span class="property-label">Parking:</span>
                        <span class="property-value">{{ property_data.parking }}</span>
                    </li>
                    <li>
                        <span class="property-label">Heating:</span>
                        <span class="property-value">{{ property_data.heating }}</span>
                    </li>
                    <li>
                        <span class="property-label">Cooling:</span>
                        <span class="property-value">{{ property_data.cooling }}</span>
                    </li>
                </ul>
            </div>

            <div class="details-section">
                <h3>Financial Details</h3>
                <ul class="property-list">
                    <li>
                        <span class="property-label">Monthly Rent Est:</span>
                        <span class="property-value">{{ property_data.monthly_rent }}</span>
                    </li>
                    <li>
                        <span class="property-label">Price per Sq Ft:</span>
                        <span class="property-value">{{ property_data.price_per_sqft }}</span>
                    </li>
                    <li>
                        <span class="property-label">Property Tax:</span>
                        <span class="property-value">{{ property_data.property_tax }}</span>
                    </li>
                    <li>
                        <span class="property-label">HOA Fees:</span>
                        <span class="property-value">{{ property_data.hoa_fees }}</span>
                    </li>
                    <li>
                        <span class="property-label">Last Sold:</span>
                        <span class="property-value">{{ property_data.last_sold }}</span>
                    </li>
                    <li>
                        <span class="property-label">Last Sold Price:</span>
                        <span class="property-value">{{ property_data.last_sold_price }}</span>
                    </li>
                </ul>

                <div class="rent-estimation">
                    <h4 style="color: #667eea; margin-bottom: 1rem;">Rent Estimation</h4>
                    <div class="rent-display" id="rentDisplay">$3,000/month</div>
                    <input type="range" class="rent-slider" id="rentSlider" min="2000" max="4000" value="3000" step="50" oninput="updateRent(this.value)">
                    <div class="rent-range">
                        <span>$2,000</span>
                        <span>$4,000</span>
                    </div>
                </div>
            </div>
        </div>

        <div class="details-grid">
            <div class="details-section">
                <h3>Property Features</h3>
                <ul class="property-list">
                    <li>
                        <span class="property-label">Flooring:</span>
                        <span class="property-value">{{ property_data.flooring }}</span>
                    </li>
                    <li>
                        <span class="property-label">Roof:</span>
                        <span class="property-value">{{ property_data.roof }}</span>
                    </li>
                    <li>
                        <span class="property-label">Exterior:</span>
                        <span class="property-value">{{ property_data.exterior }}</span>
                    </li>
                    <li>
                        <span class="property-label">Zoning:</span>
                        <span class="property-value">{{ property_data.zoning }}</span>
                    </li>
                </ul>
            </div>

            <div class="details-section">
                <h3>Schools & Walkability</h3>
                <ul class="property-list">
                    <li>
                        <span class="property-label">School District:</span>
                        <span class="property-value">{{ property_data.school_district }}</span>
                    </li>
                    <li>
                        <span class="property-label">Elementary School:</span>
                        <span class="property-value">{{ property_data.elementary_school }}</span>
                    </li>
                    <li>
                        <span class="property-label">Middle School:</span>
                        <span class="property-value">{{ property_data.middle_school }}</span>
                    </li>
                    <li>
                        <span class="property-label">High School:</span>
                        <span class="property-value">{{ property_data.high_school }}</span>
                    </li>
                    <li>
                        <span class="property-label">Walk Score:</span>
                        <span class="property-value">{{ property_data.walk_score }}</span>
                    </li>
                    <li>
                        <span class="property-label">Transit Score:</span>
                        <span class="property-value">{{ property_data.transit_score }}</span>
                    </li>
                    <li>
                        <span class="property-label">Bike Score:</span>
                        <span class="property-value">{{ property_data.bike_score }}</span>
                    </li>
                </ul>
            </div>
        </div>

        <div class="comparables-section">
            <h3>Comparable Properties (1.5 mile radius)</h3>
            <div class="comparables-container">
                <div id="comparablesMap" class="comparables-map"></div>
                <div class="comparables-list">
                    <div class="scroll-indicator">
                        📜 Scroll to view all comparable properties
                    </div>
                    {% for comp in comparable_properties %}
                    <div class="comparable-card" id="card-{{ comp.id }}" onclick="focusMarker({{ comp.id }})">
                        <div class="comparable-number">{{ comp.id }}</div>
                        <div class="comparable-address">{{ comp.address }}</div>
                        <div class="comparable-specs">
                            <div>{{ comp.bedrooms }} bed, {{ comp.bathrooms }} bath</div>
                            <div>{{ comp.square_feet }} sq ft</div>
                            <div>Built: {{ comp.year_built }}</div>
                            <div>{{ comp.distance }}</div>
                            <div>{{ comp.days_on_market }}</div>
                            <div>{{ comp.price_per_sqft }}</div>
                        </div>
                        <div class="comparable-price">{{ comp.estimated_value }}</div>
                    </div>
                    {% endfor %}
                </div>
            </div>
        </div>
    </div>

    <script>
        let map;
        let markers = [];
        let infoWindows = [];

        function initMap() {
            // Center map on main property location (Sacramento, CA)
            const mainLocation = { lat: 38.5816, lng: -121.4944 };
            
            map = new google.maps.Map(document.getElementById('comparablesMap'), {
                zoom: 14,
                center: mainLocation,
                mapTypeId: 'roadmap'
            });

            // Add main property marker (red star)
            const mainMarker = new google.maps.Marker({
                position: mainLocation,
                map: map,
                title: "{{ property_data.address }}",
                icon: {
                    path: google.maps.SymbolPath.CIRCLE,
                    scale: 12,
                    fillColor: '#ff0000',
                    fillOpacity: 1,
                    strokeColor: '#ffffff',
                    strokeWeight: 2
                }
            });

            // Add comparable property markers with numbers
            const comparables = {{ comparable_properties | tojson }};
            
            comparables.forEach(function(comp) {
                const marker = new google.maps.Marker({
                    position: { lat: comp.lat, lng: comp.lng },
                    map: map,
                    title: comp.address,
                    label: {
                        text: comp.id.toString(),
                        color: 'white',
                        fontWeight: 'bold',
                        fontSize: '14px'
                    },
                    icon: {
                        path: google.maps.SymbolPath.CIRCLE,
                        scale: 15,
                        fillColor: '#667eea',
                        fillOpacity: 1,
                        strokeColor: '#ffffff',
                        strokeWeight: 2
                    }
                });

                const infoWindow = new google.maps.InfoWindow({
                    content: `
                        <div style="padding: 10px; max-width: 250px;">
                            <h4 style="margin: 0 0 10px 0; color: #333;">${comp.address}</h4>
                            <p style="margin: 5px 0;"><strong>${comp.bedrooms} bed, ${comp.bathrooms} bath</strong></p>
                            <p style="margin: 5px 0;">${comp.square_feet} sq ft • Built: ${comp.year_built}</p>
                            <p style="margin: 5px 0;">${comp.distance}</p>
                            <p style="margin: 5px 0;">${comp.days_on_market}</p>
                            <p style="margin: 10px 0 0 0; font-size: 18px; font-weight: bold; color: #667eea;">${comp.estimated_value}</p>
                        </div>
                    `
                });

                marker.addListener('click', function() {
                    // Close all other info windows
                    infoWindows.forEach(iw => iw.close());
                    infoWindow.open(map, marker);
                    
                    // Highlight corresponding card
                    document.querySelectorAll('.comparable-card').forEach(card => {
                        card.style.border = '1px solid #e1e5e9';
                    });
                    document.getElementById('card-' + comp.id).style.border = '2px solid #667eea';
                });

                markers.push(marker);
                infoWindows.push(infoWindow);
            });
        }

        function focusMarker(id) {
            const marker = markers[id - 1];
            const infoWindow = infoWindows[id - 1];
            
            // Close all info windows
            infoWindows.forEach(iw => iw.close());
            
            // Open the selected info window
            infoWindow.open(map, marker);
            
            // Center map on marker
            map.setCenter(marker.getPosition());
            map.setZoom(16);
            
            // Highlight the card
            document.querySelectorAll('.comparable-card').forEach(card => {
                card.style.border = '1px solid #e1e5e9';
            });
            document.getElementById('card-' + id).style.border = '2px solid #667eea';
        }

        function updateRent(value) {
            document.getElementById('rentDisplay').textContent = '$' + parseInt(value).toLocaleString() + '/month';
        }

        // Initialize map when page loads
        window.onload = function() {
            if (typeof google !== 'undefined' && google.maps) {
                initMap();
            }
        }
    </script>
    <script async defer src="https://maps.googleapis.com/maps/api/js?key={{ google_maps_api_key }}&callback=initMap"></script>
</body>
</html>
    ''', property_data=property_data, comparable_properties=comparable_properties, google_maps_api_key=GOOGLE_MAPS_API_KEY)

@app.route('/continue-verification', methods=['POST'])
def continue_verification():
    # Get form data
    email = request.form.get('email', '')
    full_name = request.form.get('full_name', '')
    
    return redirect(url_for('verify_license', email=email, name=full_name))

@app.route('/verify-license')
def verify_license():
    email = request.args.get('email', '')
    name = request.args.get('name', '')
    
    return render_template_string('''
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
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 2rem;
        }

        .verification-container {
            background: white;
            padding: 3rem;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            max-width: 600px;
            width: 100%;
            text-align: center;
        }

        .verification-container h1 {
            color: #333;
            margin-bottom: 1rem;
            font-size: 2rem;
        }

        .verification-container p {
            color: #666;
            margin-bottom: 2rem;
            line-height: 1.6;
        }

        .verification-steps {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 1rem;
            margin: 2rem 0;
        }

        .step {
            padding: 1rem;
            background: #f8f9fa;
            border-radius: 10px;
            border: 2px solid #e1e5e9;
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
            margin: 0 auto 0.5rem;
            font-weight: bold;
        }

        .step-title {
            font-weight: 600;
            color: #333;
            margin-bottom: 0.5rem;
        }

        .step-description {
            font-size: 0.9rem;
            color: #666;
        }

        .sumsub-container {
            margin: 2rem 0;
            padding: 2rem;
            border: 2px dashed #667eea;
            border-radius: 15px;
            background: rgba(102, 126, 234, 0.05);
        }

        .btn-back {
            background: #6c757d;
            color: white;
            padding: 1rem 2rem;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            margin-top: 2rem;
        }

        .btn-back:hover {
            background: #5a6268;
        }
    </style>
    <script src="https://cdn.sumsub.com/websdk/2.0.0/websdk.js"></script>
</head>
<body>
    <div class="verification-container">
        <h1>🔒 Professional License Verification</h1>
        <p>Welcome {{ name }}! Complete your professional verification to join our trusted network of licensed professionals.</p>
        
        <div class="verification-steps">
            <div class="step">
                <div class="step-number">1</div>
                <div class="step-title">Upload License</div>
                <div class="step-description">Take a photo of your professional license</div>
            </div>
            <div class="step">
                <div class="step-number">2</div>
                <div class="step-title">Take Selfie</div>
                <div class="step-description">Facial recognition with liveness detection</div>
            </div>
            <div class="step">
                <div class="step-number">3</div>
                <div class="step-title">Auto Verification</div>
                <div class="step-description">AI-powered document and identity verification</div>
            </div>
            <div class="step">
                <div class="step-number">4</div>
                <div class="step-title">Get Verified</div>
                <div class="step-description">Receive your verified professional badge</div>
            </div>
        </div>

        <div class="sumsub-container">
            <div id="sumsub-websdk-container"></div>
        </div>

        <a href="/" class="btn-back">← Back to Home</a>
    </div>

    <script>
        // Initialize Sumsub WebSDK
        const snsWebSdk = snsWebSdkInit(
            '{{ sumsub_token }}',
            function (messageType, payload) {
                console.log('WebSDK message:', messageType, payload);
                
                if (messageType === 'idCheck.onReady') {
                    console.log('Verification ready');
                } else if (messageType === 'idCheck.onStepCompleted') {
                    console.log('Step completed:', payload);
                } else if (messageType === 'idCheck.onError') {
                    console.error('Verification error:', payload);
                }
            }
        )
        .withConf({
            lang: 'en',
            email: '{{ email }}',
            theme: 'light'
        })
        .withOptions({
            addViewportTag: false,
            adaptIframeHeight: true
        })
        .on('idCheck.onInitialized', function () {
            console.log('Verification initialized');
        })
        .build();

        // Mount the WebSDK
        snsWebSdk.mount('#sumsub-websdk-container');
    </script>
</body>
</html>
    ''', email=email, name=name, sumsub_token=SUMSUB_APP_TOKEN)

@app.route('/clear-results')
def clear_results():
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

