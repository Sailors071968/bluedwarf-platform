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
            <a href="/register" class="btn btn-primary">Get Started</a>
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
    
    <script>
        function clearForm() {
            document.querySelector('.address-input').value = '';
        }
        
        function openModal(modalId) {
            document.getElementById(modalId).style.display = 'block';
        }
        
        function closeModal(modalId) {
            document.getElementById(modalId).style.display = 'none';
        }
        
        // Close modal when clicking outside
        window.onclick = function(event) {
            if (event.target.classList.contains('modal')) {
                event.target.style.display = 'none';
            }
        }
        
        // Close modal with Escape key
        document.addEventListener('keydown', function(event) {
            if (event.key === 'Escape') {
                const modals = document.querySelectorAll('.modal');
                modals.forEach(modal => {
                    if (modal.style.display === 'block') {
                        modal.style.display = 'none';
                    }
                });
            }
        });
        
        function submitContact(event) {
            event.preventDefault();
            alert('Thank you for your message! We will get back to you soon.');
            closeModal('contactModal');
            event.target.reset();
        }
    </script>
</body>
</html>
    ''')

@app.route('/clear-results')
def clear_results():
    """Route to clear all results and return to homepage"""
    return redirect(url_for('home'))

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
        
        /* Search Section */
        .search-section {
            padding: 20px 40px;
        }
        
        .search-card {
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
            margin: 0 auto;
            max-width: 800px;
        }
        
        .search-form {
            display: flex;
            align-items: center;
            gap: 15px;
            flex-wrap: wrap;
        }
        
        .form-label {
            font-weight: 600;
            color: #333;
        }
        
        .address-input {
            flex: 1;
            padding: 12px;
            border: 2px solid #e1e5e9;
            border-radius: 6px;
            font-size: 1rem;
            min-width: 300px;
        }
        
        .address-input:focus {
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
        
        /* Results Content */
        .results-content {
            padding: 20px 40px;
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .property-header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .property-address {
            font-size: 2.5rem;
            color: white;
            font-weight: 300;
            margin-bottom: 10px;
        }
        
        /* Property Details Section */
        .property-details {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 40px;
        }
        
        .property-info, .property-visuals {
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
        }
        
        .property-info h3, .property-visuals h3 {
            color: #333;
            margin-bottom: 20px;
            font-size: 1.3rem;
        }
        
        .property-list {
            list-style: none;
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        
        .property-list li {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 0;
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
            font-weight: 500;
            color: #333;
        }
        
        .visual-section {
            margin-bottom: 25px;
        }
        
        .visual-section h4 {
            color: #667eea;
            margin-bottom: 10px;
            font-size: 1.1rem;
        }
        
        .visual-placeholder {
            background: #f8f9fa;
            border: 2px dashed #dee2e6;
            border-radius: 8px;
            padding: 40px;
            text-align: center;
            color: #6c757d;
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
            transition: all 0.3s;
            width: 100%;
            font-size: 1rem;
        }
        
        .btn-view-details:hover {
            background: #5a67d8;
            transform: translateY(-2px);
        }
        
        /* Professionals Section */
        .professionals-section {
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
            margin-bottom: 30px;
        }
        
        .professionals-section h2 {
            color: #333;
            margin-bottom: 25px;
            font-size: 1.5rem;
        }
        
        .professionals-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
        }
        
        .professional-card {
            border: 1px solid #e1e5e9;
            border-radius: 8px;
            padding: 20px;
            transition: all 0.3s;
        }
        
        .professional-card:hover {
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            transform: translateY(-2px);
        }
        
        .professional-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .professional-title {
            font-weight: 600;
            color: #333;
            font-size: 1.1rem;
        }
        
        .verification-badge {
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        
        .verified {
            background: #d4edda;
            color: #155724;
        }
        
        .unverified {
            background: #f8d7da;
            color: #721c24;
        }
        
        .professional-location {
            color: #6c757d;
            font-size: 0.9rem;
            margin-bottom: 10px;
        }
        
        .professional-description {
            color: #555;
            line-height: 1.5;
            margin-bottom: 15px;
        }
        
        .btn-website {
            background: #667eea;
            color: white;
            padding: 8px 16px;
            border: none;
            border-radius: 4px;
            text-decoration: none;
            font-size: 0.9rem;
            font-weight: 500;
            transition: background 0.3s;
        }
        
        .btn-website:hover {
            background: #5a67d8;
        }
        
        /* Clear Results Section */
        .clear-section {
            text-align: center;
            padding: 30px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            margin-bottom: 30px;
        }
        
        .clear-section h3 {
            color: white;
            margin-bottom: 15px;
            font-size: 1.2rem;
        }
        
        .clear-section p {
            color: rgba(255, 255, 255, 0.8);
            margin-bottom: 20px;
        }
        
        .btn-clear-all {
            background: #dc3545;
            color: white;
            padding: 15px 40px;
            border: none;
            border-radius: 8px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .btn-clear-all:hover {
            background: #c82333;
            transform: translateY(-2px);
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
                grid-template-columns: 1fr;
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
                <button type="button" class="btn-clear" onclick="clearAllResults()">Clear</button>
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
                    <h4>Street View</h4>
                    <img src="https://maps.googleapis.com/maps/api/streetview?size=400x300&location={{ property_data.address }}&key=YOUR_GOOGLE_MAPS_API_KEY" 
                         alt="Street View" style="width: 100%; border-radius: 8px;" 
                         onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">
                    <div class="visual-placeholder" style="display: none;">Street View Image</div>
                </div>
                
                <div class="visual-section">
                    <h4>Aerial View (2 blocks)</h4>
                    <div id="map" style="width: 100%; height: 200px; border-radius: 8px;"></div>
                </div>
                
                <button class="btn-view-details" onclick="viewDetails('{{ property_data.address }}')">View Details</button>
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
                        <span class="verification-badge {{ 'verified' if professional.verified else 'unverified' }}">
                            {{ '✅ Verified' if professional.verified else '❌ Unverified' }}
                        </span>
                    </div>
                    <div class="professional-location">{{ professional.location }}</div>
                    <div class="professional-description">{{ professional.description }}</div>
                    <a href="#" class="btn-website">Website</a>
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
    
    <!-- Footer -->
    <footer class="footer">
        © 2024 Elite Marketing Lab LLC. All rights reserved.<br>
        support@bluedwarf.io
    </footer>
    
    <script>
        function clearAllResults() {
            // Redirect to clear results route which will take user back to homepage
            window.location.href = '/clear-results';
        }
        
        function viewDetails(address) {
            window.location.href = '/property-details?address=' + encodeURIComponent(address);
        }
        
        // Initialize Google Map
        function initMap() {
            const address = "{{ property_data.address }}";
            const geocoder = new google.maps.Geocoder();
            
            geocoder.geocode({ address: address }, function(results, status) {
                if (status === 'OK') {
                    const map = new google.maps.Map(document.getElementById('map'), {
                        zoom: 16,
                        center: results[0].geometry.location,
                        mapTypeId: 'satellite'
                    });
                    
                    new google.maps.Marker({
                        position: results[0].geometry.location,
                        map: map,
                        title: address
                    });
                    
                    // Add map type controls
                    const mapTypeControl = document.createElement('div');
                    mapTypeControl.style.margin = '10px';
                    
                    const mapButton = document.createElement('button');
                    mapButton.textContent = 'Map';
                    mapButton.style.marginRight = '5px';
                    mapButton.onclick = () => map.setMapTypeId('roadmap');
                    
                    const satelliteButton = document.createElement('button');
                    satelliteButton.textContent = 'Satellite';
                    satelliteButton.onclick = () => map.setMapTypeId('satellite');
                    
                    mapTypeControl.appendChild(mapButton);
                    mapTypeControl.appendChild(satelliteButton);
                    map.controls[google.maps.ControlPosition.TOP_RIGHT].push(mapTypeControl);
                }
            });
        }
    </script>
    <script async defer src="https://maps.googleapis.com/maps/api/js?key=YOUR_GOOGLE_MAPS_API_KEY&callback=initMap"></script>
</body>
</html>
    ''', property_data=property_data, professionals=professionals, city_state=city_state)

@app.route('/property-details')
def property_details():
    address = request.args.get('address', '')
    
    # Mock property data
    property_data = {
        'address': address,
        'estimated_value': '$500,000',
        'bedrooms': '4',
        'bathrooms': '2',
        'square_feet': '1,492',
        'year_built': '1964',
        'monthly_rent': '$3,000'
    }
    
    # Mock comparable properties data
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
            'lat': 38.5825,
            'lng': -121.4935
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
        
        .btn-back {
            background: rgba(255, 255, 255, 0.2);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }
        
        .btn-back:hover {
            background: rgba(255, 255, 255, 0.3);
        }
        
        /* Main Content */
        .main-content {
            padding: 20px 40px;
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .page-header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .page-title {
            font-size: 2.5rem;
            color: white;
            font-weight: 300;
            margin-bottom: 10px;
        }
        
        .back-button {
            background: rgba(255, 255, 255, 0.2);
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 1rem;
            margin-bottom: 20px;
            transition: background 0.3s;
        }
        
        .back-button:hover {
            background: rgba(255, 255, 255, 0.3);
        }
        
        /* Rent Estimation Section */
        .rent-section {
            background: white;
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
        }
        
        .rent-section h2 {
            color: #333;
            margin-bottom: 20px;
            font-size: 1.5rem;
        }
        
        .rent-controls {
            display: flex;
            align-items: center;
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .rent-slider {
            flex: 1;
            height: 6px;
            border-radius: 3px;
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
        
        .rent-display {
            font-size: 1.2rem;
            font-weight: 600;
            color: #667eea;
            min-width: 120px;
        }
        
        /* Comparable Properties Section */
        .comparables-section {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
        }
        
        .comparables-map {
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
        }
        
        .comparables-list {
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
        }
        
        .section-title {
            color: #333;
            margin-bottom: 20px;
            font-size: 1.3rem;
        }
        
        #comparables-map {
            width: 100%;
            height: 400px;
            border-radius: 8px;
        }
        
        .comparable-card {
            border: 1px solid #e1e5e9;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 15px;
            transition: all 0.3s;
            position: relative;
        }
        
        .comparable-card:hover {
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            transform: translateY(-2px);
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
            font-size: 0.9rem;
        }
        
        .comparable-address {
            font-weight: 600;
            color: #333;
            margin-bottom: 10px;
            margin-top: 10px;
        }
        
        .comparable-value {
            font-size: 1.2rem;
            font-weight: 600;
            color: #667eea;
            margin-bottom: 10px;
        }
        
        .comparable-specs {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 8px;
            font-size: 0.9rem;
            color: #666;
        }
        
        .comparable-distance {
            color: #28a745;
            font-weight: 500;
            margin-top: 10px;
        }
        
        /* Footer */
        .footer {
            background: #667eea;
            color: white;
            text-align: center;
            padding: 20px;
            font-size: 0.9rem;
            margin-top: 40px;
        }
        
        /* Responsive Design */
        @media (max-width: 768px) {
            .header {
                flex-direction: column;
                gap: 15px;
                padding: 20px;
            }
            
            .comparables-section {
                grid-template-columns: 1fr;
            }
            
            .rent-controls {
                flex-direction: column;
                align-items: stretch;
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
            <button onclick="goBack()" class="btn btn-back">← Back</button>
        </div>
    </header>
    
    <!-- Main Content -->
    <main class="main-content">
        <div class="page-header">
            <h1 class="page-title">{{ property_data.address }}</h1>
        </div>
        
        <!-- Rent Estimation Section -->
        <section class="rent-section">
            <h2>💰 Rent Estimation</h2>
            <div class="rent-controls">
                <label>Monthly Rent Range:</label>
                <input type="range" class="rent-slider" id="rentSlider" min="2000" max="4000" value="3000" oninput="updateRent(this.value)">
                <div class="rent-display" id="rentDisplay">$3,000</div>
            </div>
            <p style="color: #666; font-size: 0.9rem;">Adjust the slider to see different rent estimates based on market conditions and property features.</p>
        </section>
        
        <!-- Comparable Properties Section -->
        <section class="comparables-section">
            <div class="comparables-map">
                <h3 class="section-title">📍 Comparable Properties Map</h3>
                <div id="comparables-map"></div>
            </div>
            
            <div class="comparables-list">
                <h3 class="section-title">🏘️ Comparable Properties (1.5 mile radius)</h3>
                {% for comp in comparable_properties %}
                <div class="comparable-card" id="card-{{ comp.id }}">
                    <div class="comparable-number">{{ comp.id }}</div>
                    <div class="comparable-address">{{ comp.address }}</div>
                    <div class="comparable-value">{{ comp.estimated_value }}</div>
                    <div class="comparable-specs">
                        <div>🛏️ {{ comp.bedrooms }} beds</div>
                        <div>🚿 {{ comp.bathrooms }} baths</div>
                        <div>📐 {{ comp.square_feet }} sq ft</div>
                        <div>📅 Built {{ comp.year_built }}</div>
                        <div>📊 {{ comp.days_on_market }} days on market</div>
                        <div class="comparable-distance">📍 {{ comp.distance }}</div>
                    </div>
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
        function goBack() {
            window.history.back();
        }
        
        function updateRent(value) {
            document.getElementById('rentDisplay').textContent = '$' + parseInt(value).toLocaleString();
        }
        
        // Initialize Google Map with comparable properties
        function initMap() {
            const mainProperty = {
                lat: 38.5815,
                lng: -121.4944
            };
            
            const map = new google.maps.Map(document.getElementById('comparables-map'), {
                zoom: 15,
                center: mainProperty,
                mapTypeId: 'roadmap'
            });
            
            // Main property marker
            new google.maps.Marker({
                position: mainProperty,
                map: map,
                title: '{{ property_data.address }}',
                icon: {
                    url: 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 40 40"><circle cx="20" cy="20" r="15" fill="#ff6b6b" stroke="white" stroke-width="3"/><text x="20" y="25" text-anchor="middle" fill="white" font-size="12" font-weight="bold">🏠</text></svg>'),
                    scaledSize: new google.maps.Size(40, 40)
                }
            });
            
            // Comparable properties markers
            const comparables = {{ comparable_properties | tojsonfilter }};
            
            comparables.forEach(function(comp) {
                const marker = new google.maps.Marker({
                    position: { lat: comp.lat, lng: comp.lng },
                    map: map,
                    title: comp.address,
                    icon: {
                        url: 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" width="35" height="35" viewBox="0 0 35 35"><circle cx="17.5" cy="17.5" r="12" fill="#667eea" stroke="white" stroke-width="2"/><text x="17.5" y="22" text-anchor="middle" fill="white" font-size="14" font-weight="bold">' + comp.id + '</text></svg>'),
                        scaledSize: new google.maps.Size(35, 35)
                    }
                });
                
                // Info window for each marker
                const infoWindow = new google.maps.InfoWindow({
                    content: '<div style="padding: 10px;"><strong>' + comp.address + '</strong><br>' +
                            '<span style="color: #667eea; font-weight: 600;">' + comp.estimated_value + '</span><br>' +
                            comp.bedrooms + ' beds • ' + comp.bathrooms + ' baths • ' + comp.square_feet + ' sq ft<br>' +
                            '<span style="color: #28a745;">' + comp.distance + ' away</span></div>'
                });
                
                marker.addListener('click', function() {
                    infoWindow.open(map, marker);
                    
                    // Highlight corresponding card
                    document.querySelectorAll('.comparable-card').forEach(card => {
                        card.style.border = '1px solid #e1e5e9';
                    });
                    document.getElementById('card-' + comp.id).style.border = '2px solid #667eea';
                });
            });
        }
        
        // Highlight map marker when card is clicked
        document.querySelectorAll('.comparable-card').forEach(function(card) {
            card.addEventListener('click', function() {
                const cardId = this.id.split('-')[1];
                // You could trigger the corresponding marker click here
                document.querySelectorAll('.comparable-card').forEach(c => {
                    c.style.border = '1px solid #e1e5e9';
                });
                this.style.border = '2px solid #667eea';
            });
        });
    </script>
    <script async defer src="https://maps.googleapis.com/maps/api/js?key=YOUR_GOOGLE_MAPS_API_KEY&callback=initMap"></script>
</body>
</html>
    ''', property_data=property_data, comparable_properties=comparable_properties)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get form data
        form_data = {
            'full_name': request.form.get('full_name'),
            'phone': request.form.get('phone'),
            'email': request.form.get('email'),
            'business_address': request.form.get('business_address'),
            'license_number': request.form.get('license_number'),
            'domain': request.form.get('domain'),
            'profession': request.form.get('profession'),
            'service_zip_codes': request.form.get('service_zip_codes'),
            'password': request.form.get('password')
        }
        
        # Store in session or database (for demo, we'll redirect to verification)
        return redirect(url_for('verify_license', email=form_data['email']))
    
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
        
        /* Main Content */
        .main-content {
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: calc(100vh - 200px);
            padding: 40px 20px;
        }
        
        .registration-card {
            background: white;
            border-radius: 12px;
            padding: 40px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            width: 100%;
            max-width: 600px;
        }
        
        .card-header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .card-title {
            font-size: 2rem;
            color: #333;
            margin-bottom: 10px;
        }
        
        .card-subtitle {
            color: #666;
            font-size: 1rem;
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
        
        .form-label {
            font-weight: 600;
            color: #333;
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
        
        /* Footer */
        .footer {
            background: rgba(255, 255, 255, 0.1);
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
            
            .registration-card {
                padding: 30px 20px;
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
        </div>
    </header>
    
    <!-- Main Content -->
    <main class="main-content">
        <div class="registration-card">
            <div class="card-header">
                <h1 class="card-title">Professional Registration</h1>
                <p class="card-subtitle">Join our network of verified professionals</p>
            </div>
            
            <form class="registration-form" method="POST">
                <div class="form-row">
                    <div class="form-group">
                        <label class="form-label">Full Name *</label>
                        <input type="text" name="full_name" class="form-input" required>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Phone Number *</label>
                        <input type="tel" name="phone" class="form-input" required>
                    </div>
                </div>
                
                <div class="form-group">
                    <label class="form-label">Email Address *</label>
                    <input type="email" name="email" class="form-input" required>
                </div>
                
                <div class="form-group">
                    <label class="form-label">Business Address *</label>
                    <input type="text" name="business_address" class="form-input" required>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label class="form-label">License Number *</label>
                        <input type="text" name="license_number" class="form-input" required>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Website Domain</label>
                        <input type="url" name="domain" class="form-input" placeholder="https://yourwebsite.com">
                    </div>
                </div>
                
                <div class="form-group">
                    <label class="form-label">Profession *</label>
                    <select name="profession" class="form-select" required>
                        <option value="">Select your profession</option>
                        <option value="real_estate_agent">Real Estate Agent</option>
                        <option value="mortgage_lender">Mortgage Lender</option>
                        <option value="real_estate_attorney">Real Estate Attorney</option>
                        <option value="property_inspector">Property Inspector</option>
                        <option value="insurance_agent">Insurance Agent</option>
                        <option value="property_manager">Property Manager</option>
                        <option value="contractor">General Contractor</option>
                        <option value="electrician">Electrician</option>
                        <option value="plumber">Plumber</option>
                        <option value="hvac_technician">HVAC Technician</option>
                        <option value="other">Other</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label class="form-label">Service ZIP Codes *</label>
                    <input type="text" name="service_zip_codes" class="form-input" 
                           placeholder="95814, 95815, 95816" 
                           title="Enter ZIP codes separated by commas" required>
                </div>
                
                <div class="form-group">
                    <label class="form-label">Password *</label>
                    <input type="password" name="password" class="form-input" required>
                </div>
                
                <button type="submit" class="btn-submit">
                    Continue to License Verification →
                </button>
            </form>
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

@app.route('/verify-license')
def verify_license():
    email = request.args.get('email', 'professional@example.com')
    
    # Generate Sumsub access token
    verification_data = create_sumsub_applicant(email)
    
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
            justify-content: center;
            align-items: center;
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
        }
        
        .card-header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .card-title {
            font-size: 2rem;
            color: #333;
            margin-bottom: 10px;
        }
        
        .card-subtitle {
            color: #666;
            font-size: 1rem;
            margin-bottom: 20px;
        }
        
        .verification-steps {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .step {
            text-align: center;
            padding: 20px;
            border: 2px solid #e1e5e9;
            border-radius: 8px;
            transition: all 0.3s;
        }
        
        .step.active {
            border-color: #667eea;
            background: #f8f9ff;
        }
        
        .step-icon {
            font-size: 2rem;
            margin-bottom: 10px;
        }
        
        .step-title {
            font-weight: 600;
            color: #333;
            margin-bottom: 5px;
        }
        
        .step-description {
            font-size: 0.9rem;
            color: #666;
        }
        
        #sumsub-websdk-container {
            min-height: 400px;
            border-radius: 8px;
            overflow: hidden;
        }
        
        /* Footer */
        .footer {
            background: rgba(255, 255, 255, 0.1);
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
            
            .verification-card {
                padding: 30px 20px;
            }
            
            .verification-steps {
                grid-template-columns: repeat(2, 1fr);
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
    </header>
    
    <!-- Main Content -->
    <main class="main-content">
        <div class="verification-card">
            <div class="card-header">
                <h1 class="card-title">🔒 Professional License Verification</h1>
                <p class="card-subtitle">Complete your professional verification to join our trusted network</p>
            </div>
            
            <div class="verification-steps">
                <div class="step active">
                    <div class="step-icon">📄</div>
                    <div class="step-title">Upload License</div>
                    <div class="step-description">Upload your professional license document</div>
                </div>
                <div class="step">
                    <div class="step-icon">📸</div>
                    <div class="step-title">Take Selfie</div>
                    <div class="step-description">Facial recognition with liveness detection</div>
                </div>
                <div class="step">
                    <div class="step-icon">⚡</div>
                    <div class="step-title">Auto Verification</div>
                    <div class="step-description">AI-powered document and identity verification</div>
                </div>
                <div class="step">
                    <div class="step-icon">✅</div>
                    <div class="step-title">Get Verified</div>
                    <div class="step-description">Receive your verified professional badge</div>
                </div>
            </div>
            
            <div id="sumsub-websdk-container"></div>
        </div>
    </main>
    
    <!-- Footer -->
    <footer class="footer">
        © 2024 Elite Marketing Lab LLC. All rights reserved.<br>
        support@bluedwarf.io
    </footer>
    
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

def create_sumsub_applicant(email):
    """Create a Sumsub applicant and return access token"""
    try:
        # This is a mock implementation
        # In production, you would make actual API calls to Sumsub
        return {
            'access_token': 'mock_access_token_' + email.replace('@', '_'),
            'email': email
        }
    except Exception as e:
        print(f"Error creating Sumsub applicant: {e}")
        return {
            'access_token': 'mock_access_token',
            'email': email
        }

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

