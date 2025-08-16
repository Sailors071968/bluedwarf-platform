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
            font-size: 1.5rem;
            font-weight: bold;
            color: white;
            text-decoration: none;
        }
        
        .nav-center {
            display: flex;
            gap: 30px;
        }
        
        .nav-link {
            color: white;
            text-decoration: none;
            padding: 8px 16px;
            border-radius: 6px;
            transition: background 0.3s;
        }
        
        .nav-link:hover {
            background: rgba(255, 255, 255, 0.1);
        }
        
        .nav-right {
            display: flex;
            gap: 15px;
        }
        
        .btn {
            padding: 10px 20px;
            border-radius: 6px;
            text-decoration: none;
            font-weight: 500;
            transition: all 0.3s;
            border: none;
            cursor: pointer;
        }
        
        .btn-login {
            background: rgba(255, 255, 255, 0.2);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }
        
        .btn-login:hover {
            background: rgba(255, 255, 255, 0.3);
        }
        
        .btn-primary {
            background: #ff6b6b;
            color: white;
        }
        
        .btn-primary:hover {
            background: #ff5252;
            transform: translateY(-2px);
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
            font-size: 3rem;
            color: white;
            margin-bottom: 10px;
            font-weight: 300;
        }
        
        .hero-subtitle {
            font-size: 1.2rem;
            color: rgba(255, 255, 255, 0.8);
            margin-bottom: 40px;
        }
        
        /* Search Card */
        .search-card {
            background: white;
            border-radius: 12px;
            padding: 40px;
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
            font-size: 1.1rem;
            font-weight: 600;
            color: #333;
            text-align: center;
        }
        
        .address-input {
            padding: 15px;
            border: 2px solid #e1e5e9;
            border-radius: 8px;
            font-size: 1rem;
            transition: border-color 0.3s;
        }
        
        .address-input:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .button-group {
            display: flex;
            gap: 15px;
            justify-content: center;
        }
        
        .btn-search {
            background: #667eea;
            color: white;
            padding: 15px 30px;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .btn-search:hover {
            background: #5a67d8;
            transform: translateY(-2px);
        }
        
        .btn-clear {
            background: #6c757d;
            color: white;
            padding: 15px 30px;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .btn-clear:hover {
            background: #5a6268;
        }
        
        /* Footer */
        .footer {
            background: rgba(255, 255, 255, 0.1);
            color: white;
            text-align: center;
            padding: 20px;
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
            background-color: rgba(0, 0, 0, 0.5);
        }
        
        .modal-content {
            background-color: white;
            margin: 5% auto;
            padding: 30px;
            border-radius: 12px;
            width: 90%;
            max-width: 600px;
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
            color: #333;
            margin-bottom: 20px;
        }
        
        .modal p {
            color: #666;
            line-height: 1.6;
            margin-bottom: 15px;
        }
        
        .contact-form {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        
        .contact-form label {
            font-weight: 600;
            color: #333;
        }
        
        .contact-form input,
        .contact-form textarea {
            padding: 12px;
            border: 2px solid #e1e5e9;
            border-radius: 6px;
            font-size: 1rem;
        }
        
        .contact-form input:focus,
        .contact-form textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .contact-form textarea {
            min-height: 120px;
            resize: vertical;
        }
        
        .contact-form button {
            background: #667eea;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 6px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.3s;
        }
        
        .contact-form button:hover {
            background: #5a67d8;
        }
        
        /* Registration Modal Styles */
        .registration-modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.5);
        }
        
        .registration-content {
            background-color: white;
            margin: 2% auto;
            padding: 40px;
            border-radius: 12px;
            width: 90%;
            max-width: 700px;
            position: relative;
            max-height: 90vh;
            overflow-y: auto;
        }
        
        .registration-form {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        
        .form-group {
            display: flex;
            flex-direction: column;
            gap: 5px;
        }
        
        .form-input, .form-select {
            padding: 12px;
            border: 2px solid #e1e5e9;
            border-radius: 6px;
            font-size: 1rem;
            transition: border-color 0.3s;
        }
        
        .form-input:focus, .form-select:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .form-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        
        .btn-submit {
            background: #667eea;
            color: white;
            padding: 15px 30px;
            border: none;
            border-radius: 8px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            margin-top: 10px;
        }
        
        .btn-submit:hover {
            background: #5a67d8;
            transform: translateY(-2px);
        }
        
        /* Responsive Design */
        @media (max-width: 768px) {
            .header {
                flex-direction: column;
                gap: 15px;
                padding: 20px;
            }
            
            .nav-center {
                order: 2;
            }
            
            .nav-right {
                order: 1;
            }
            
            .hero-title {
                font-size: 2rem;
            }
            
            .search-card {
                padding: 30px 20px;
            }
            
            .button-group {
                flex-direction: column;
            }
            
            .form-row {
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
            <a href="#" class="nav-link" onclick="openModal('aboutModal')">About</a>
            <a href="#" class="nav-link" onclick="openModal('contactModal')">Contact</a>
        </nav>
        
        <div class="nav-right">
            <a href="/login" class="btn btn-login">Login</a>
            <a href="#" class="btn btn-primary" onclick="openRegistrationModal()">Get Started</a>
        </div>
    </header>
    
    <!-- Main Content -->
    <main class="main-content">
        <div class="hero-section">
            <h1 class="hero-title">🏠 Property Analysis</h1>
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
    
    <!-- About Modal -->
    <div id="aboutModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeModal('aboutModal')">&times;</span>
            <h2>About BlueDwarf</h2>
            <p>BlueDwarf is a comprehensive property analysis platform that provides instant access to property data across the United States. Our platform combines cutting-edge technology with verified professional networks to deliver accurate, reliable property information.</p>
            
            <p><strong>Our Mission:</strong> To democratize access to property information and connect property owners with verified, licensed professionals in their area.</p>
            
            <p><strong>Key Features:</strong></p>
            <ul>
                <li>Instant property analysis and valuation</li>
                <li>Street View and aerial mapping integration</li>
                <li>Comparable property analysis</li>
                <li>Verified professional network</li>
                <li>Professional license verification system</li>
                <li>Comprehensive property reports</li>
            </ul>
            
            <p><strong>Professional Verification:</strong> We use advanced OCR technology and facial recognition to verify professional licenses, ensuring you only work with legitimate, licensed contractors and service providers.</p>
        </div>
    </div>
    
    <!-- Contact Modal -->
    <div id="contactModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeModal('contactModal')">&times;</span>
            <h2>Contact Us</h2>
            <p>Get in touch with our team. We're here to help with any questions about our property analysis platform or professional verification services.</p>
            
            <form class="contact-form" onsubmit="submitContact(event)">
                <label for="name">Name *</label>
                <input type="text" id="name" name="name" required>
                
                <label for="email">Email *</label>
                <input type="email" id="email" name="email" required>
                
                <label for="subject">Subject *</label>
                <input type="text" id="subject" name="subject" required>
                
                <label for="message">Message *</label>
                <textarea id="message" name="message" required></textarea>
                
                <button type="submit">Send Message</button>
            </form>
            
            <div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid #eee;">
                <strong>Direct Contact:</strong><br>
                📧 Email: support@bluedwarf.io
            </div>
        </div>
    </div>
    
    <!-- Registration Modal -->
    <div id="registrationModal" class="registration-modal">
        <div class="registration-content">
            <span class="close" onclick="closeRegistrationModal()">&times;</span>
            <div style="text-align: center; margin-bottom: 30px;">
                <h2 style="color: #333; margin-bottom: 10px;">Professional Registration</h2>
                <p style="color: #666;">Join our network of verified professionals</p>
            </div>
            
            <form class="registration-form" onsubmit="submitRegistration(event)">
                <div class="form-row">
                    <div class="form-group">
                        <label style="font-weight: 600; color: #333;">Full Name *</label>
                        <input type="text" name="full_name" class="form-input" required>
                    </div>
                    <div class="form-group">
                        <label style="font-weight: 600; color: #333;">Phone Number *</label>
                        <input type="tel" name="phone" class="form-input" required>
                    </div>
                </div>
                
                <div class="form-group">
                    <label style="font-weight: 600; color: #333;">Email Address *</label>
                    <input type="email" name="email" class="form-input" required>
                </div>
                
                <div class="form-group">
                    <label style="font-weight: 600; color: #333;">Business Address *</label>
                    <input type="text" name="business_address" class="form-input" required>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label style="font-weight: 600; color: #333;">License Number *</label>
                        <input type="text" name="license_number" class="form-input" required>
                    </div>
                    <div class="form-group">
                        <label style="font-weight: 600; color: #333;">Website Domain</label>
                        <input type="url" name="website" class="form-input" placeholder="https://yourwebsite.com">
                    </div>
                </div>
                
                <div class="form-group">
                    <label style="font-weight: 600; color: #333;">Profession *</label>
                    <select name="profession" class="form-select" required>
                        <option value="">Select your profession</option>
                        <option value="real_estate_agent">Real Estate Agent</option>
                        <option value="mortgage_lender">Mortgage Lender</option>
                        <option value="real_estate_attorney">Real Estate Attorney</option>
                        <option value="property_inspector">Property Inspector</option>
                        <option value="insurance_agent">Insurance Agent</option>
                        <option value="property_manager">Property Manager</option>
                        <option value="general_contractor">General Contractor</option>
                        <option value="electrician">Electrician</option>
                        <option value="plumber">Plumber</option>
                        <option value="hvac_technician">HVAC Technician</option>
                        <option value="landscaper">Landscaper</option>
                        <option value="roofer">Roofer</option>
                        <option value="painter">Painter</option>
                        <option value="flooring_specialist">Flooring Specialist</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label style="font-weight: 600; color: #333;">Service ZIP Codes *</label>
                    <input type="text" name="service_areas" class="form-input" placeholder="95814, 95815, 95816" required>
                </div>
                
                <div class="form-group">
                    <label style="font-weight: 600; color: #333;">Password *</label>
                    <input type="password" name="password" class="form-input" required>
                </div>
                
                <button type="submit" class="btn-submit">Continue to License Verification →</button>
            </form>
        </div>
    </div>
    
    <script>
        // Modal Functions
        function openModal(modalId) {
            document.getElementById(modalId).style.display = 'block';
        }
        
        function closeModal(modalId) {
            document.getElementById(modalId).style.display = 'none';
        }
        
        function openRegistrationModal() {
            document.getElementById('registrationModal').style.display = 'block';
        }
        
        function closeRegistrationModal() {
            document.getElementById('registrationModal').style.display = 'none';
        }
        
        // Close modals when clicking outside
        window.onclick = function(event) {
            const modals = document.querySelectorAll('.modal, .registration-modal');
            modals.forEach(modal => {
                if (event.target === modal) {
                    modal.style.display = 'none';
                }
            });
        }
        
        // Close modals with Escape key
        document.addEventListener('keydown', function(event) {
            if (event.key === 'Escape') {
                const modals = document.querySelectorAll('.modal, .registration-modal');
                modals.forEach(modal => {
                    modal.style.display = 'none';
                });
            }
        });
        
        // Form Functions
        function clearForm() {
            document.querySelector('.address-input').value = '';
        }
        
        function submitContact(event) {
            event.preventDefault();
            alert('Thank you for your message! We will get back to you soon.');
            closeModal('contactModal');
            event.target.reset();
        }
        
        function submitRegistration(event) {
            event.preventDefault();
            const formData = new FormData(event.target);
            const email = formData.get('email');
            
            // Redirect to license verification with email parameter
            window.location.href = '/verify-license?email=' + encodeURIComponent(email);
        }
    </script>
</body>
</html>
    ''')

@app.route('/property-results', methods=['GET', 'POST'])
def property_results():
    if request.method == 'POST':
        address = request.form.get('address', '')
    else:
        address = request.args.get('address', '')
    
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Property Results - BlueDwarf</title>
    <script src="https://maps.googleapis.com/maps/api/js?key=YOUR_GOOGLE_MAPS_API_KEY&libraries=places"></script>
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
            font-size: 1.5rem;
            font-weight: bold;
            color: white;
            text-decoration: none;
        }
        
        .nav-center {
            display: flex;
            gap: 30px;
        }
        
        .nav-link {
            color: white;
            text-decoration: none;
            padding: 8px 16px;
            border-radius: 6px;
            transition: background 0.3s;
        }
        
        .nav-link:hover {
            background: rgba(255, 255, 255, 0.1);
        }
        
        .nav-right {
            display: flex;
            gap: 15px;
        }
        
        .btn {
            padding: 10px 20px;
            border-radius: 6px;
            text-decoration: none;
            font-weight: 500;
            transition: all 0.3s;
            border: none;
            cursor: pointer;
        }
        
        .btn-login {
            background: rgba(255, 255, 255, 0.2);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }
        
        .btn-login:hover {
            background: rgba(255, 255, 255, 0.3);
        }
        
        .btn-primary {
            background: #ff6b6b;
            color: white;
        }
        
        .btn-primary:hover {
            background: #ff5252;
            transform: translateY(-2px);
        }
        
        /* Search Bar */
        .search-bar {
            background: white;
            margin: 20px;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .search-form {
            display: flex;
            gap: 15px;
            align-items: center;
        }
        
        .search-label {
            font-weight: 600;
            color: #333;
            min-width: 80px;
        }
        
        .search-input {
            flex: 1;
            padding: 12px;
            border: 2px solid #e1e5e9;
            border-radius: 6px;
            font-size: 1rem;
        }
        
        .search-input:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .btn-search, .btn-clear {
            padding: 12px 24px;
            border: none;
            border-radius: 6px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .btn-search {
            background: #667eea;
            color: white;
        }
        
        .btn-search:hover {
            background: #5a67d8;
        }
        
        .btn-clear {
            background: #6c757d;
            color: white;
        }
        
        .btn-clear:hover {
            background: #5a6268;
        }
        
        /* Main Content */
        .main-content {
            padding: 20px;
        }
        
        .property-header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        
        .property-title {
            font-size: 2.5rem;
            margin-bottom: 10px;
            font-weight: 300;
        }
        
        /* Property Section */
        .property-section {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 40px;
        }
        
        .property-details {
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        }
        
        .property-details h3 {
            color: #333;
            margin-bottom: 20px;
            font-size: 1.5rem;
        }
        
        .detail-item {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #f0f0f0;
        }
        
        .detail-item:last-child {
            border-bottom: none;
        }
        
        .detail-label {
            font-weight: 600;
            color: #666;
        }
        
        .detail-value {
            color: #333;
            font-weight: 500;
        }
        
        /* Street View and Maps */
        .visual-section {
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        }
        
        .visual-section h4 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.2rem;
        }
        
        .street-view-container {
            width: 100%;
            height: 200px;
            background: #f8f9fa;
            border-radius: 8px;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
            overflow: hidden;
        }
        
        .street-view-image {
            width: 100%;
            height: 100%;
            object-fit: cover;
            border-radius: 8px;
        }
        
        .street-view-placeholder {
            color: #666;
            font-style: italic;
        }
        
        .map-container {
            width: 100%;
            height: 250px;
            border-radius: 8px;
            overflow: hidden;
            position: relative;
        }
        
        .map-controls {
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
        }
        
        .map-btn {
            padding: 8px 16px;
            border: 2px solid #667eea;
            background: white;
            color: #667eea;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s;
        }
        
        .map-btn.active {
            background: #667eea;
            color: white;
        }
        
        .map-btn:hover {
            background: #667eea;
            color: white;
        }
        
        .view-details-btn {
            background: #667eea;
            color: white;
            padding: 15px 30px;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            width: 100%;
            margin-top: 20px;
        }
        
        .view-details-btn:hover {
            background: #5a67d8;
            transform: translateY(-2px);
        }
        
        /* Professionals Section */
        .professionals-section {
            margin-top: 40px;
        }
        
        .section-title {
            color: white;
            font-size: 2rem;
            text-align: center;
            margin-bottom: 30px;
            font-weight: 300;
        }
        
        .professionals-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        
        .professional-card {
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s;
        }
        
        .professional-card:hover {
            transform: translateY(-5px);
        }
        
        .professional-title {
            color: #333;
            font-size: 1.3rem;
            margin-bottom: 8px;
            font-weight: 600;
        }
        
        .professional-location {
            color: #666;
            margin-bottom: 15px;
            font-weight: 500;
        }
        
        .professional-description {
            color: #555;
            line-height: 1.6;
            margin-bottom: 20px;
        }
        
        .professional-website {
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 10px 20px;
            border-radius: 6px;
            text-decoration: none;
            font-weight: 600;
            transition: background 0.3s;
        }
        
        .professional-website:hover {
            background: #5a67d8;
        }
        
        /* Clear Results Section */
        .clear-section {
            background: white;
            border-radius: 12px;
            padding: 30px;
            text-align: center;
            margin-top: 40px;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        }
        
        .clear-section h3 {
            color: #333;
            margin-bottom: 15px;
            font-size: 1.5rem;
        }
        
        .clear-section p {
            color: #666;
            margin-bottom: 20px;
            line-height: 1.6;
        }
        
        .btn-clear-all {
            background: #dc3545;
            color: white;
            padding: 15px 30px;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
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
                flex-direction: column;
                gap: 15px;
                padding: 20px;
            }
            
            .search-form {
                flex-direction: column;
                align-items: stretch;
            }
            
            .property-section {
                grid-template-columns: 1fr;
            }
            
            .property-title {
                font-size: 2rem;
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
            <a href="#" class="nav-link" onclick="openModal('aboutModal')">About</a>
            <a href="#" class="nav-link" onclick="openModal('contactModal')">Contact</a>
        </nav>
        
        <div class="nav-right">
            <a href="/login" class="btn btn-login">Login</a>
            <a href="#" class="btn btn-primary" onclick="openRegistrationModal()">Get Started</a>
        </div>
    </header>
    
    <!-- Search Bar -->
    <div class="search-bar">
        <form action="/property-results" method="POST" class="search-form">
            <label class="search-label">Address</label>
            <input 
                type="text" 
                name="address" 
                class="search-input"
                value="{{ address }}"
                placeholder="123 Pine Street, Any City, WA, 54321"
            >
            <button type="submit" class="btn-search">Search</button>
            <button type="button" class="btn-clear" onclick="clearResults()">Clear</button>
        </form>
    </div>
    
    <!-- Main Content -->
    <main class="main-content">
        <div class="property-header">
            <h1 class="property-title">{{ address }}</h1>
        </div>
        
        <!-- Property Details Section -->
        <div class="property-section">
            <div class="property-details">
                <h3>Property Details</h3>
                <div class="detail-item">
                    <span class="detail-label">Estimated Value:</span>
                    <span class="detail-value">$500,000</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Property Type:</span>
                    <span class="detail-value">Single Family Home</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Bedrooms:</span>
                    <span class="detail-value">4</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Bathrooms:</span>
                    <span class="detail-value">2.5</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Square Feet:</span>
                    <span class="detail-value">1,492</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Lot Size:</span>
                    <span class="detail-value">0.18 acres</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Year Built:</span>
                    <span class="detail-value">1964</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Parking:</span>
                    <span class="detail-value">2-car garage</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Heating/Cooling:</span>
                    <span class="detail-value">Central Air/Heat</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Monthly Rent Est:</span>
                    <span class="detail-value">$3,000</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Price per Sq Ft:</span>
                    <span class="detail-value">$335</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Property Tax:</span>
                    <span class="detail-value">$6,250/year</span>
                </div>
            </div>
            
            <div class="visual-section">
                <h4>Street View</h4>
                <div class="street-view-container">
                    <img 
                        src="https://maps.googleapis.com/maps/api/streetview?size=400x200&location={{ address }}&key=YOUR_GOOGLE_MAPS_API_KEY"
                        alt="Street View of {{ address }}"
                        class="street-view-image"
                        onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';"
                    >
                    <div class="street-view-placeholder" style="display: none;">
                        Google Street View Image
                    </div>
                </div>
                
                <h4>Aerial View (2 blocks)</h4>
                <div class="map-controls">
                    <button class="map-btn active" onclick="switchMapType('roadmap')">Map</button>
                    <button class="map-btn" onclick="switchMapType('satellite')">Satellite</button>
                </div>
                <div id="map" class="map-container"></div>
                
                <button class="view-details-btn" onclick="viewDetails('{{ address }}')">View Details</button>
            </div>
        </div>
        
        <!-- Professionals Section -->
        <section class="professionals-section">
            <h2 class="section-title">Local Professionals in Sacramento, CA</h2>
            
            <div class="professionals-grid">
                <div class="professional-card">
                    <h3 class="professional-title">Real Estate Agent</h3>
                    <p class="professional-location">Sacramento, CA</p>
                    <p class="professional-description">Experienced agent specializing in residential properties and first-time buyers</p>
                    <a href="#" class="professional-website">Website</a>
                </div>
                
                <div class="professional-card">
                    <h3 class="professional-title">Mortgage Lender</h3>
                    <p class="professional-location">Sacramento, CA</p>
                    <p class="professional-description">Specialized in home loans and refinancing with competitive rates</p>
                    <a href="#" class="professional-website">Website</a>
                </div>
                
                <div class="professional-card">
                    <h3 class="professional-title">Real Estate Attorney</h3>
                    <p class="professional-location">Sacramento, CA</p>
                    <p class="professional-description">Expert in real estate transactions and contract negotiations</p>
                    <a href="#" class="professional-website">Website</a>
                </div>
                
                <div class="professional-card">
                    <h3 class="professional-title">Property Inspector</h3>
                    <p class="professional-location">Sacramento, CA</p>
                    <p class="professional-description">Certified home inspector with comprehensive inspection services</p>
                    <a href="#" class="professional-website">Website</a>
                </div>
                
                <div class="professional-card">
                    <h3 class="professional-title">Insurance Agent</h3>
                    <p class="professional-location">Sacramento, CA</p>
                    <p class="professional-description">Home and auto insurance specialist with competitive coverage options</p>
                    <a href="#" class="professional-website">Website</a>
                </div>
                
                <div class="professional-card">
                    <h3 class="professional-title">Property Manager</h3>
                    <p class="professional-location">Sacramento, CA</p>
                    <p class="professional-description">Professional property management services for residential and commercial properties</p>
                    <a href="#" class="professional-website">Website</a>
                </div>
                
                <div class="professional-card">
                    <h3 class="professional-title">General Contractor</h3>
                    <p class="professional-location">Sacramento, CA</p>
                    <p class="professional-description">Licensed general contractor for home renovations and construction projects</p>
                    <a href="#" class="professional-website">Website</a>
                </div>
                
                <div class="professional-card">
                    <h3 class="professional-title">HVAC Technician</h3>
                    <p class="professional-location">Sacramento, CA</p>
                    <p class="professional-description">Heating, ventilation, and air conditioning installation and repair services</p>
                    <a href="#" class="professional-website">Website</a>
                </div>
                
                <div class="professional-card">
                    <h3 class="professional-title">Electrician</h3>
                    <p class="professional-location">Sacramento, CA</p>
                    <p class="professional-description">Licensed electrician for residential and commercial electrical work</p>
                    <a href="#" class="professional-website">Website</a>
                </div>
                
                <div class="professional-card">
                    <h3 class="professional-title">Plumber</h3>
                    <p class="professional-location">Sacramento, CA</p>
                    <p class="professional-description">Professional plumbing services for repairs, installations, and maintenance</p>
                    <a href="#" class="professional-website">Website</a>
                </div>
            </div>
        </section>
        
        <!-- Clear Results Section -->
        <div class="clear-section">
            <h3>🗑️ Clear All Results</h3>
            <p>Want to start a new search? Clear all property data and professional listings.</p>
            <button class="btn-clear-all" onclick="clearResults()">Clear All Results</button>
        </div>
    </main>
    
    <script>
        let map;
        let currentMapType = 'roadmap';
        
        function initMap() {
            const address = "{{ address }}";
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
                    document.getElementById('map').innerHTML = '<div style="display: flex; align-items: center; justify-content: center; height: 100%; color: #666;">Map unavailable for this location</div>';
                }
            });
        }
        
        function switchMapType(type) {
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
        
        function viewDetails(address) {
            window.location.href = '/property-details?address=' + encodeURIComponent(address);
        }
        
        function clearResults() {
            window.location.href = '/clear-results';
        }
        
        // Initialize map when page loads
        window.onload = function() {
            if (typeof google !== 'undefined') {
                initMap();
            }
        };
    </script>
</body>
</html>
    ''', address=address)

@app.route('/property-details')
def property_details():
    address = request.args.get('address', '')
    
    # Enhanced property data with comprehensive details
    property_data = {
        'address': address,
        'estimated_value': '$500,000',
        'bedrooms': '4',
        'bathrooms': '2.5',
        'square_feet': '1,492',
        'year_built': '1964',
        'monthly_rent': '$3,000',
        'lot_size': '0.18 acres',
        'property_type': 'Single Family Home',
        'parking': '2-car garage',
        'heating': 'Central Air/Heat',
        'cooling': 'Central Air',
        'flooring': 'Hardwood, Carpet',
        'roof': 'Composition Shingle',
        'exterior': 'Stucco',
        'last_sold': 'March 2019',
        'last_sold_price': '$425,000',
        'price_per_sqft': '$335',
        'hoa_fees': 'None',
        'property_tax': '$6,250/year',
        'zoning': 'Residential R-1',
        'school_district': 'Sacramento City Unified',
        'elementary_school': 'John Bidwell Elementary',
        'middle_school': 'Kit Carson Middle School',
        'high_school': 'McClatchy High School',
        'walk_score': '72 - Very Walkable',
        'transit_score': '45 - Some Transit',
        'bike_score': '68 - Bikeable'
    }
    
    # Enhanced comparable properties data with more details
    comparable_properties = [
        {
            'id': 1,
            'address': '125 Main Street, Sacramento, CA',
            'estimated_value': '$475,000',
            'bedrooms': '3',
            'bathrooms': '2',
            'square_feet': '1,380',
            'year_built': '1962',
            'days_on_market': '45',
            'distance': '0.1 miles',
            'price_per_sqft': '$344',
            'lot_size': '0.15 acres',
            'last_sold': 'January 2024',
            'lat': 38.5816,
            'lng': -121.4944
        },
        {
            'id': 2,
            'address': '456 Oak Avenue, Sacramento, CA',
            'estimated_value': '$525,000',
            'bedrooms': '4',
            'bathrooms': '3',
            'square_feet': '1,650',
            'year_built': '1968',
            'days_on_market': '32',
            'distance': '0.3 miles',
            'price_per_sqft': '$318',
            'lot_size': '0.22 acres',
            'last_sold': 'November 2023',
            'lat': 38.5820,
            'lng': -121.4950
        },
        {
            'id': 3,
            'address': '789 Pine Street, Sacramento, CA',
            'estimated_value': '$450,000',
            'bedrooms': '3',
            'bathrooms': '2',
            'square_feet': '1,250',
            'year_built': '1960',
            'days_on_market': '67',
            'distance': '0.5 miles',
            'price_per_sqft': '$360',
            'lot_size': '0.12 acres',
            'last_sold': 'September 2023',
            'lat': 38.5825,
            'lng': -121.4935
        },
        {
            'id': 4,
            'address': '321 Elm Drive, Sacramento, CA',
            'estimated_value': '$510,000',
            'bedrooms': '4',
            'bathrooms': '2.5',
            'square_feet': '1,580',
            'year_built': '1965',
            'days_on_market': '28',
            'distance': '0.7 miles',
            'price_per_sqft': '$323',
            'lot_size': '0.19 acres',
            'last_sold': 'February 2024',
            'lat': 38.5810,
            'lng': -121.4940
        },
        {
            'id': 5,
            'address': '654 Maple Court, Sacramento, CA',
            'estimated_value': '$485,000',
            'bedrooms': '3',
            'bathrooms': '2.5',
            'square_feet': '1,420',
            'year_built': '1963',
            'days_on_market': '51',
            'distance': '0.9 miles',
            'price_per_sqft': '$342',
            'lot_size': '0.16 acres',
            'last_sold': 'December 2023',
            'lat': 38.5805,
            'lng': -121.4955
        }
    ]
    
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Property Details - BlueDwarf</title>
    <script src="https://maps.googleapis.com/maps/api/js?key=YOUR_GOOGLE_MAPS_API_KEY&libraries=places"></script>
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
            font-size: 1.5rem;
            font-weight: bold;
            color: white;
            text-decoration: none;
        }
        
        .nav-center {
            display: flex;
            gap: 30px;
        }
        
        .nav-link {
            color: white;
            text-decoration: none;
            padding: 8px 16px;
            border-radius: 6px;
            transition: background 0.3s;
        }
        
        .nav-link:hover {
            background: rgba(255, 255, 255, 0.1);
        }
        
        .nav-right {
            display: flex;
            gap: 15px;
        }
        
        .btn {
            padding: 10px 20px;
            border-radius: 6px;
            text-decoration: none;
            font-weight: 500;
            transition: all 0.3s;
            border: none;
            cursor: pointer;
        }
        
        .btn-login {
            background: rgba(255, 255, 255, 0.2);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }
        
        .btn-primary {
            background: #ff6b6b;
            color: white;
        }
        
        /* Main Content */
        .main-content {
            padding: 20px;
        }
        
        .back-button {
            background: rgba(255, 255, 255, 0.2);
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 6px;
            font-weight: 600;
            cursor: pointer;
            margin-bottom: 20px;
            transition: all 0.3s;
        }
        
        .back-button:hover {
            background: rgba(255, 255, 255, 0.3);
        }
        
        .property-header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        
        .property-title {
            font-size: 2.5rem;
            margin-bottom: 10px;
            font-weight: 300;
        }
        
        /* Content Sections */
        .content-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 40px;
        }
        
        .content-section {
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        }
        
        .section-title {
            color: #333;
            margin-bottom: 20px;
            font-size: 1.5rem;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        
        .detail-item {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #f0f0f0;
        }
        
        .detail-item:last-child {
            border-bottom: none;
        }
        
        .detail-label {
            font-weight: 600;
            color: #666;
        }
        
        .detail-value {
            color: #333;
            font-weight: 500;
        }
        
        /* Rent Estimation */
        .rent-estimation {
            margin-top: 20px;
        }
        
        .rent-slider-container {
            margin: 20px 0;
        }
        
        .rent-slider {
            width: 100%;
            margin: 10px 0;
        }
        
        .rent-display {
            text-align: center;
            font-size: 1.2rem;
            font-weight: 600;
            color: #667eea;
            margin: 10px 0;
        }
        
        /* Comparable Properties */
        .comparables-section {
            grid-column: 1 / -1;
        }
        
        .comparables-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-top: 20px;
        }
        
        .comparables-map {
            height: 400px;
            border-radius: 8px;
            overflow: hidden;
        }
        
        .comparables-list {
            max-height: 400px;
            overflow-y: auto;
        }
        
        .comparable-card {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 15px;
            border-left: 4px solid #667eea;
            transition: all 0.3s;
            cursor: pointer;
        }
        
        .comparable-card:hover {
            background: #e9ecef;
            transform: translateX(5px);
        }
        
        .comparable-card.active {
            background: #e3f2fd;
            border-left-color: #2196f3;
        }
        
        .comparable-number {
            background: #667eea;
            color: white;
            width: 25px;
            height: 25px;
            border-radius: 50%;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            margin-right: 10px;
        }
        
        .comparable-address {
            font-weight: 600;
            color: #333;
            margin-bottom: 10px;
        }
        
        .comparable-details {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            font-size: 0.9rem;
            color: #666;
        }
        
        .comparable-value {
            font-size: 1.1rem;
            font-weight: 600;
            color: #667eea;
            margin-top: 10px;
        }
        
        /* Responsive Design */
        @media (max-width: 768px) {
            .content-grid {
                grid-template-columns: 1fr;
            }
            
            .comparables-grid {
                grid-template-columns: 1fr;
            }
            
            .property-title {
                font-size: 2rem;
            }
        }
    </style>
</head>
<body>
    <!-- Header Navigation -->
    <header class="header">
        <a href="/" class="logo">🏠 BlueDwarf</a>
        <nav class="nav-center">
            <a href="#" class="nav-link">About</a>
            <a href="#" class="nav-link">Contact</a>
        </nav>
        <div class="nav-right">
            <a href="/login" class="btn btn-login">Login</a>
            <a href="#" class="btn btn-primary">Get Started</a>
        </div>
    </header>
    
    <!-- Main Content -->
    <main class="main-content">
        <button class="back-button" onclick="goBack()">← Back to Results</button>
        
        <div class="property-header">
            <h1 class="property-title">{{ property_data.address }}</h1>
        </div>
        
        <div class="content-grid">
            <!-- Enhanced Property Details -->
            <div class="content-section">
                <h3 class="section-title">Property Information</h3>
                <div class="detail-item">
                    <span class="detail-label">Estimated Value:</span>
                    <span class="detail-value">{{ property_data.estimated_value }}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Property Type:</span>
                    <span class="detail-value">{{ property_data.property_type }}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Bedrooms:</span>
                    <span class="detail-value">{{ property_data.bedrooms }}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Bathrooms:</span>
                    <span class="detail-value">{{ property_data.bathrooms }}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Square Feet:</span>
                    <span class="detail-value">{{ property_data.square_feet }}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Lot Size:</span>
                    <span class="detail-value">{{ property_data.lot_size }}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Year Built:</span>
                    <span class="detail-value">{{ property_data.year_built }}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Parking:</span>
                    <span class="detail-value">{{ property_data.parking }}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Heating:</span>
                    <span class="detail-value">{{ property_data.heating }}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Cooling:</span>
                    <span class="detail-value">{{ property_data.cooling }}</span>
                </div>
            </div>
            
            <!-- Financial Information -->
            <div class="content-section">
                <h3 class="section-title">Financial Details</h3>
                <div class="detail-item">
                    <span class="detail-label">Monthly Rent Est:</span>
                    <span class="detail-value">{{ property_data.monthly_rent }}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Price per Sq Ft:</span>
                    <span class="detail-value">{{ property_data.price_per_sqft }}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Property Tax:</span>
                    <span class="detail-value">{{ property_data.property_tax }}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">HOA Fees:</span>
                    <span class="detail-value">{{ property_data.hoa_fees }}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Last Sold:</span>
                    <span class="detail-value">{{ property_data.last_sold }}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Last Sold Price:</span>
                    <span class="detail-value">{{ property_data.last_sold_price }}</span>
                </div>
                
                <!-- Rent Estimation Slider -->
                <div class="rent-estimation">
                    <h4 style="color: #667eea; margin-bottom: 15px;">Rent Estimation</h4>
                    <div class="rent-slider-container">
                        <input type="range" min="2000" max="4000" value="3000" class="rent-slider" id="rentSlider">
                        <div class="rent-display" id="rentDisplay">$3,000/month</div>
                        <div style="display: flex; justify-content: space-between; font-size: 0.9rem; color: #666;">
                            <span>$2,000</span>
                            <span>$4,000</span>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Property Features -->
            <div class="content-section">
                <h3 class="section-title">Property Features</h3>
                <div class="detail-item">
                    <span class="detail-label">Flooring:</span>
                    <span class="detail-value">{{ property_data.flooring }}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Roof:</span>
                    <span class="detail-value">{{ property_data.roof }}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Exterior:</span>
                    <span class="detail-value">{{ property_data.exterior }}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Zoning:</span>
                    <span class="detail-value">{{ property_data.zoning }}</span>
                </div>
            </div>
            
            <!-- Schools & Walkability -->
            <div class="content-section">
                <h3 class="section-title">Schools & Walkability</h3>
                <div class="detail-item">
                    <span class="detail-label">School District:</span>
                    <span class="detail-value">{{ property_data.school_district }}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Elementary School:</span>
                    <span class="detail-value">{{ property_data.elementary_school }}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Middle School:</span>
                    <span class="detail-value">{{ property_data.middle_school }}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">High School:</span>
                    <span class="detail-value">{{ property_data.high_school }}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Walk Score:</span>
                    <span class="detail-value">{{ property_data.walk_score }}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Transit Score:</span>
                    <span class="detail-value">{{ property_data.transit_score }}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Bike Score:</span>
                    <span class="detail-value">{{ property_data.bike_score }}</span>
                </div>
            </div>
            
            <!-- Comparable Properties -->
            <div class="content-section comparables-section">
                <h3 class="section-title">Comparable Properties (1.5 mile radius)</h3>
                <div class="comparables-grid">
                    <div id="comparablesMap" class="comparables-map"></div>
                    <div class="comparables-list">
                        {% for comp in comparable_properties %}
                        <div class="comparable-card" onclick="selectComparable({{ comp.id }}, {{ comp.lat }}, {{ comp.lng }})">
                            <div style="display: flex; align-items: center; margin-bottom: 10px;">
                                <span class="comparable-number">{{ comp.id }}</span>
                                <span class="comparable-address">{{ comp.address }}</span>
                            </div>
                            <div class="comparable-details">
                                <div>{{ comp.bedrooms }} bed, {{ comp.bathrooms }} bath</div>
                                <div>{{ comp.square_feet }} sq ft</div>
                                <div>Built: {{ comp.year_built }}</div>
                                <div>{{ comp.distance }} away</div>
                                <div>{{ comp.days_on_market }} days on market</div>
                                <div>${{ comp.price_per_sqft }}/sq ft</div>
                            </div>
                            <div class="comparable-value">{{ comp.estimated_value }}</div>
                        </div>
                        {% endfor %}
                    </div>
                </div>
            </div>
        </div>
    </main>
    
    <script>
        let comparablesMap;
        let markers = [];
        let infoWindows = [];
        
        // Rent slider functionality
        const rentSlider = document.getElementById('rentSlider');
        const rentDisplay = document.getElementById('rentDisplay');
        
        rentSlider.addEventListener('input', function() {
            const value = parseInt(this.value);
            rentDisplay.textContent = '$' + value.toLocaleString() + '/month';
        });
        
        // Initialize comparables map
        function initComparablesMap() {
            const centerLat = 38.5816;
            const centerLng = -121.4944;
            
            comparablesMap = new google.maps.Map(document.getElementById('comparablesMap'), {
                zoom: 14,
                center: { lat: centerLat, lng: centerLng },
                mapTypeId: 'roadmap'
            });
            
            // Add main property marker
            new google.maps.Marker({
                position: { lat: centerLat, lng: centerLng },
                map: comparablesMap,
                title: '{{ property_data.address }}',
                icon: {
                    url: 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 40 40"><circle cx="20" cy="20" r="15" fill="#ff6b6b" stroke="white" stroke-width="3"/><text x="20" y="25" text-anchor="middle" fill="white" font-family="Arial" font-size="12" font-weight="bold">★</text></svg>'),
                    scaledSize: new google.maps.Size(40, 40)
                }
            });
            
            // Add comparable property markers
            const comparables = {{ comparable_properties | tojson }};
            comparables.forEach(function(comp, index) {
                const marker = new google.maps.Marker({
                    position: { lat: comp.lat, lng: comp.lng },
                    map: comparablesMap,
                    title: comp.address,
                    icon: {
                        url: 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" width="35" height="35" viewBox="0 0 35 35"><circle cx="17.5" cy="17.5" r="12" fill="#667eea" stroke="white" stroke-width="2"/><text x="17.5" y="22" text-anchor="middle" fill="white" font-family="Arial" font-size="12" font-weight="bold">' + comp.id + '</text></svg>'),
                        scaledSize: new google.maps.Size(35, 35)
                    }
                });
                
                const infoWindow = new google.maps.InfoWindow({
                    content: `
                        <div style="padding: 10px; max-width: 250px;">
                            <h4 style="margin: 0 0 10px 0; color: #333;">${comp.address}</h4>
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 5px; font-size: 0.9rem;">
                                <div><strong>Value:</strong> ${comp.estimated_value}</div>
                                <div><strong>Beds:</strong> ${comp.bedrooms}</div>
                                <div><strong>Baths:</strong> ${comp.bathrooms}</div>
                                <div><strong>Sq Ft:</strong> ${comp.square_feet}</div>
                                <div><strong>Built:</strong> ${comp.year_built}</div>
                                <div><strong>Distance:</strong> ${comp.distance}</div>
                            </div>
                        </div>
                    `
                });
                
                marker.addListener('click', function() {
                    // Close all other info windows
                    infoWindows.forEach(iw => iw.close());
                    infoWindow.open(comparablesMap, marker);
                    
                    // Highlight corresponding card
                    document.querySelectorAll('.comparable-card').forEach(card => {
                        card.classList.remove('active');
                    });
                    document.querySelectorAll('.comparable-card')[index].classList.add('active');
                });
                
                markers.push(marker);
                infoWindows.push(infoWindow);
            });
        }
        
        function selectComparable(id, lat, lng) {
            // Highlight selected card
            document.querySelectorAll('.comparable-card').forEach(card => {
                card.classList.remove('active');
            });
            event.currentTarget.classList.add('active');
            
            // Center map on selected property
            comparablesMap.setCenter({ lat: lat, lng: lng });
            comparablesMap.setZoom(16);
            
            // Close all info windows
            infoWindows.forEach(iw => iw.close());
            
            // Open info window for selected marker
            const markerIndex = id - 1;
            if (markers[markerIndex] && infoWindows[markerIndex]) {
                infoWindows[markerIndex].open(comparablesMap, markers[markerIndex]);
            }
        }
        
        function goBack() {
            window.history.back();
        }
        
        // Initialize map when page loads
        window.onload = function() {
            if (typeof google !== 'undefined') {
                initComparablesMap();
            }
        };
    </script>
</body>
</html>
    ''', property_data=property_data, comparable_properties=comparable_properties)

@app.route('/clear-results')
def clear_results():
    return redirect('/')

@app.route('/verify-license')
def verify_license():
    email = request.args.get('email', '')
    
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>License Verification - BlueDwarf</title>
    <script src="https://cdn.sumsub.com/websdk/2.0.0/websdk.js"></script>
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
            font-size: 1.5rem;
            font-weight: bold;
            color: white;
            text-decoration: none;
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
        
        .verification-card {
            background: white;
            border-radius: 12px;
            padding: 40px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            width: 100%;
            max-width: 800px;
            text-align: center;
        }
        
        .verification-title {
            font-size: 2.5rem;
            color: #333;
            margin-bottom: 20px;
            font-weight: 300;
        }
        
        .verification-subtitle {
            font-size: 1.2rem;
            color: #666;
            margin-bottom: 40px;
            line-height: 1.6;
        }
        
        .verification-steps {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 30px;
            margin-bottom: 40px;
        }
        
        .step {
            text-align: center;
        }
        
        .step-icon {
            font-size: 3rem;
            margin-bottom: 15px;
        }
        
        .step-title {
            font-size: 1.2rem;
            font-weight: 600;
            color: #333;
            margin-bottom: 10px;
        }
        
        .step-description {
            color: #666;
            line-height: 1.5;
        }
        
        .sumsub-container {
            margin: 30px 0;
            min-height: 400px;
        }
        
        .back-button {
            background: #6c757d;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 6px;
            font-weight: 600;
            cursor: pointer;
            margin-top: 20px;
            transition: all 0.3s;
        }
        
        .back-button:hover {
            background: #5a6268;
        }
        
        /* Responsive Design */
        @media (max-width: 768px) {
            .verification-card {
                padding: 30px 20px;
            }
            
            .verification-title {
                font-size: 2rem;
            }
            
            .verification-steps {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <!-- Header Navigation -->
    <header class="header">
        <a href="/" class="logo">🏠 BlueDwarf</a>
    </header>
    
    <!-- Main Content -->
    <main class="main-content">
        <div class="verification-card">
            <h1 class="verification-title">🔒 Professional License Verification</h1>
            <p class="verification-subtitle">
                Complete your professional verification to join our network of trusted, licensed professionals. 
                This process uses advanced OCR and facial recognition technology to verify your credentials.
            </p>
            
            <div class="verification-steps">
                <div class="step">
                    <div class="step-icon">📄</div>
                    <h3 class="step-title">1. Upload License</h3>
                    <p class="step-description">Upload a clear photo of your professional license document</p>
                </div>
                
                <div class="step">
                    <div class="step-icon">📸</div>
                    <h3 class="step-title">2. Take Selfie</h3>
                    <p class="step-description">Take a live selfie for facial recognition verification</p>
                </div>
                
                <div class="step">
                    <div class="step-icon">⚡</div>
                    <h3 class="step-title">3. Auto Verification</h3>
                    <p class="step-description">Our AI system processes and verifies your documents</p>
                </div>
                
                <div class="step">
                    <div class="step-icon">✅</div>
                    <h3 class="step-title">4. Get Verified</h3>
                    <p class="step-description">Receive your verified professional status</p>
                </div>
            </div>
            
            <!-- Sumsub Verification Widget -->
            <div id="sumsub-websdk-container" class="sumsub-container"></div>
            
            <button class="back-button" onclick="goBack()">← Back to Registration</button>
        </div>
    </main>
    
    <script>
        function goBack() {
            window.history.back();
        }
        
        // Initialize Sumsub WebSDK
        function initSumsubWebSDK() {
            const accessToken = generateAccessToken('{{ email }}');
            
            const snsWebSdk = snsWebSdkInit(accessToken, function (messageType, payload) {
                console.log('WebSDK message:', messageType, payload);
                
                if (messageType === 'idCheck.onReady') {
                    console.log('Sumsub WebSDK is ready');
                }
                
                if (messageType === 'idCheck.onStepCompleted') {
                    console.log('Step completed:', payload);
                }
                
                if (messageType === 'idCheck.onError') {
                    console.error('Sumsub error:', payload);
                }
                
                if (messageType === 'idCheck.applicantStatus') {
                    console.log('Applicant status:', payload);
                    if (payload.reviewStatus === 'completed') {
                        window.location.href = '/verification-complete?status=' + payload.reviewResult.reviewAnswer;
                    }
                }
            })
            .withConf({
                lang: 'en',
                email: '{{ email }}',
                theme: 'light'
            })
            .withOptions({
                addViewportTag: false,
                adaptIframeHeight: true
            })
            .on('idCheck.stepCompleted', (payload) => {
                console.log('Step completed:', payload);
            })
            .build();
            
            snsWebSdk.launch('#sumsub-websdk-container');
        }
        
        function generateAccessToken(email) {
            // In production, this should be generated server-side
            return 'sbx:Mfd6l7oxKRRbjzwBRfD5JewCe7xcUL7pIlOvPHGNSqp5zy...';
        }
        
        // Initialize when page loads
        window.onload = function() {
            if (typeof snsWebSdkInit !== 'undefined') {
                initSumsubWebSDK();
            } else {
                console.error('Sumsub WebSDK not loaded');
                document.getElementById('sumsub-websdk-container').innerHTML = 
                    '<div style="padding: 40px; text-align: center; color: #666;">Verification system loading...</div>';
            }
        };
    </script>
</body>
</html>
    ''', email=email)

@app.route('/verification-complete')
def verification_complete():
    status = request.args.get('status', 'pending')
    
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>Verification Complete - BlueDwarf</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0;
            padding: 20px;
        }
        
        .completion-card {
            background: white;
            border-radius: 12px;
            padding: 40px;
            text-align: center;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            max-width: 500px;
            width: 100%;
        }
        
        .success-icon {
            font-size: 4rem;
            margin-bottom: 20px;
        }
        
        .completion-title {
            font-size: 2rem;
            color: #333;
            margin-bottom: 20px;
        }
        
        .completion-message {
            color: #666;
            line-height: 1.6;
            margin-bottom: 30px;
        }
        
        .btn-home {
            background: #667eea;
            color: white;
            padding: 15px 30px;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            transition: all 0.3s;
        }
        
        .btn-home:hover {
            background: #5a67d8;
            transform: translateY(-2px);
        }
    </style>
</head>
<body>
    <div class="completion-card">
        {% if status == 'GREEN' %}
            <div class="success-icon">✅</div>
            <h1 class="completion-title">Verification Successful!</h1>
            <p class="completion-message">
                Congratulations! Your professional license has been successfully verified. 
                You are now part of our trusted network of licensed professionals.
            </p>
        {% elif status == 'RED' %}
            <div class="success-icon">❌</div>
            <h1 class="completion-title">Verification Failed</h1>
            <p class="completion-message">
                We were unable to verify your professional license. Please contact our support team 
                at support@bluedwarf.io for assistance.
            </p>
        {% else %}
            <div class="success-icon">⏳</div>
            <h1 class="completion-title">Verification Pending</h1>
            <p class="completion-message">
                Thank you for submitting your verification documents. Our team is reviewing your 
                application and will notify you once the process is complete.
            </p>
        {% endif %}
        
        <a href="/" class="btn-home">Return to Homepage</a>
    </div>
</body>
</html>
    ''', status=status)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

