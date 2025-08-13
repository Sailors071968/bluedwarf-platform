from flask import Flask, render_template_string, request, jsonify, redirect, url_for, session
import os
from datetime import datetime
import json

app = Flask(__name__)
app.secret_key = 'bluedwarf_secret_key_2025'

# Homepage with enhanced design
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
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
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
            z-index: 100;
        }
        
        .nav {
            display: flex;
            justify-content: space-between;
            align-items: center;
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .logo {
            font-size: 1.5rem;
            font-weight: bold;
            color: #667eea;
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .nav-buttons {
            display: flex;
            gap: 1rem;
        }
        
        .btn {
            padding: 0.75rem 1.5rem;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            text-decoration: none;
            cursor: pointer;
            transition: all 0.3s ease;
            display: inline-block;
            text-align: center;
        }
        
        .btn-outline {
            background: transparent;
            color: #667eea;
            border: 2px solid #667eea;
        }
        
        .btn-outline:hover {
            background: #667eea;
            color: white;
            transform: translateY(-2px);
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
        }
        
        .main-content {
            max-width: 1200px;
            margin: 0 auto;
            padding: 4rem 2rem;
            text-align: center;
        }
        
        .hero-section {
            margin-bottom: 4rem;
        }
        
        .hero-title {
            font-size: 3.5rem;
            font-weight: bold;
            color: white;
            margin-bottom: 1rem;
            text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 1rem;
        }
        
        .hero-subtitle {
            font-size: 1.25rem;
            color: rgba(255, 255, 255, 0.9);
            margin-bottom: 3rem;
            font-weight: 300;
        }
        
        .search-card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 3rem;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
            max-width: 600px;
            margin: 0 auto 4rem;
        }
        
        .search-form {
            display: flex;
            flex-direction: column;
            gap: 1.5rem;
        }
        
        .search-input {
            padding: 1rem 1.5rem;
            border: 2px solid #e1e5e9;
            border-radius: 12px;
            font-size: 1.1rem;
            transition: all 0.3s ease;
            background: white;
        }
        
        .search-input:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        .search-buttons {
            display: flex;
            gap: 1rem;
            justify-content: center;
        }
        
        .search-btn {
            padding: 1rem 2rem;
            font-size: 1.1rem;
            border-radius: 12px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            border: none;
        }
        
        .search-btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .search-btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
        }
        
        .search-btn-secondary {
            background: #f8f9fa;
            color: #6c757d;
            border: 2px solid #e9ecef;
        }
        
        .search-btn-secondary:hover {
            background: #e9ecef;
            transform: translateY(-2px);
        }
        
        .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 2rem;
            margin-bottom: 4rem;
        }
        
        .feature-card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 2rem;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
        }
        
        .feature-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
        }
        
        .feature-icon {
            font-size: 3rem;
            margin-bottom: 1rem;
        }
        
        .feature-title {
            font-size: 1.25rem;
            font-weight: bold;
            margin-bottom: 1rem;
            color: #333;
        }
        
        .feature-description {
            color: #666;
            line-height: 1.6;
        }
        
        .footer {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            padding: 2rem;
            text-align: center;
            color: rgba(255, 255, 255, 0.8);
            margin-top: 4rem;
        }
        
        .footer a {
            color: rgba(255, 255, 255, 0.9);
            text-decoration: none;
        }
        
        .footer a:hover {
            color: white;
        }
        
        @media (max-width: 768px) {
            .hero-title {
                font-size: 2.5rem;
                flex-direction: column;
                gap: 0.5rem;
            }
            
            .search-card {
                margin: 0 1rem 3rem;
                padding: 2rem;
            }
            
            .search-buttons {
                flex-direction: column;
            }
            
            .nav-buttons {
                gap: 0.5rem;
            }
            
            .btn {
                padding: 0.5rem 1rem;
                font-size: 0.9rem;
            }
        }
    </style>
</head>
<body>
    <header class="header">
        <nav class="nav">
            <a href="/" class="logo">🏠 BlueDwarf</a>
            <div class="nav-buttons">
                <a href="/login" class="btn btn-outline">Login</a>
                <a href="/signup" class="btn btn-primary">Get Started</a>
            </div>
        </nav>
    </header>
    
    <main class="main-content">
        <section class="hero-section">
            <h1 class="hero-title">
                🏠 Property Analysis
            </h1>
            <p class="hero-subtitle">Instant Data • Full US Coverage</p>
        </section>
        
        <div class="search-card">
            <form class="search-form" action="/search" method="POST">
                <input 
                    type="text" 
                    name="address" 
                    class="search-input" 
                    placeholder="123 Pine Street, Any City, WA, 54321"
                    required
                >
                <div class="search-buttons">
                    <button type="submit" class="search-btn search-btn-primary">Search</button>
                    <button type="button" class="search-btn search-btn-secondary" onclick="clearForm()">Clear</button>
                </div>
            </form>
        </div>
        
        <div class="features-grid">
            <div class="feature-card">
                <div class="feature-icon">📄</div>
                <h3 class="feature-title">Document Verification</h3>
                <p class="feature-description">Advanced document analysis and validation with AI-powered accuracy</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">👤</div>
                <h3 class="feature-title">Identity Verification</h3>
                <p class="feature-description">Secure identity confirmation services for trusted transactions</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">📋</div>
                <h3 class="feature-title">License Validation</h3>
                <p class="feature-description">Professional license verification and compliance checking</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🏠</div>
                <h3 class="feature-title">Property Analysis</h3>
                <p class="feature-description">Comprehensive property evaluation with market insights</p>
            </div>
        </div>
    </main>
    
    <footer class="footer">
        <p>&copy; 2025 Elite Marketing Lab LLC. All rights reserved. | <a href="mailto:support@bluedwarf.io">support@bluedwarf.io</a></p>
    </footer>
    
    <script>
        function clearForm() {
            document.querySelector('input[name="address"]').value = '';
        }
        
        // Add smooth scrolling and animations
        document.addEventListener('DOMContentLoaded', function() {
            const cards = document.querySelectorAll('.feature-card');
            cards.forEach((card, index) => {
                card.style.animationDelay = `${index * 0.1}s`;
            });
        });
    </script>
</body>
</html>
    ''')

# Enhanced search results page
@app.route('/search', methods=['POST'])
def search():
    address = request.form.get('address', '')
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
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
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
            z-index: 100;
        }
        
        .nav {
            display: flex;
            justify-content: space-between;
            align-items: center;
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .logo {
            font-size: 1.5rem;
            font-weight: bold;
            color: #667eea;
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .main-content {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        .results-header {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        
        .property-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
            margin-bottom: 2rem;
        }
        
        .property-card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 2rem;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        
        .property-image {
            width: 100%;
            height: 200px;
            background: linear-gradient(45deg, #f0f0f0, #e0e0e0);
            border-radius: 12px;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 3rem;
        }
        
        .property-details {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1rem;
            margin-top: 1rem;
        }
        
        .detail-item {
            display: flex;
            justify-content: space-between;
            padding: 0.5rem 0;
            border-bottom: 1px solid #eee;
        }
        
        .map-container {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 2rem;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            margin-bottom: 2rem;
        }
        
        .map-placeholder {
            width: 100%;
            height: 400px;
            background: linear-gradient(45deg, #f0f0f0, #e0e0e0);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2rem;
            color: #666;
        }
        
        .back-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem 2rem;
            border: none;
            border-radius: 12px;
            font-weight: 600;
            text-decoration: none;
            display: inline-block;
            margin-bottom: 2rem;
            transition: all 0.3s ease;
        }
        
        .back-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
        }
        
        @media (max-width: 768px) {
            .property-grid {
                grid-template-columns: 1fr;
            }
            
            .property-details {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <header class="header">
        <nav class="nav">
            <a href="/" class="logo">🏠 BlueDwarf</a>
        </nav>
    </header>
    
    <main class="main-content">
        <a href="/" class="back-btn">← Back to Search</a>
        
        <div class="results-header">
            <h1>Property Analysis Results</h1>
            <p><strong>Address:</strong> {{ address }}</p>
            <p><strong>Analysis Date:</strong> {{ current_date }}</p>
        </div>
        
        <div class="property-grid">
            <div class="property-card">
                <div class="property-image">🏠</div>
                <h3>Property Overview</h3>
                <div class="property-details">
                    <div class="detail-item">
                        <span>Estimated Value:</span>
                        <strong>$485,000</strong>
                    </div>
                    <div class="detail-item">
                        <span>Property Type:</span>
                        <span>Single Family</span>
                    </div>
                    <div class="detail-item">
                        <span>Year Built:</span>
                        <span>1995</span>
                    </div>
                    <div class="detail-item">
                        <span>Square Feet:</span>
                        <span>2,150 sq ft</span>
                    </div>
                    <div class="detail-item">
                        <span>Bedrooms:</span>
                        <span>3</span>
                    </div>
                    <div class="detail-item">
                        <span>Bathrooms:</span>
                        <span>2.5</span>
                    </div>
                </div>
            </div>
            
            <div class="property-card">
                <div class="property-image">📊</div>
                <h3>Market Analysis</h3>
                <div class="property-details">
                    <div class="detail-item">
                        <span>Market Trend:</span>
                        <strong style="color: green;">↗ Rising</strong>
                    </div>
                    <div class="detail-item">
                        <span>Neighborhood Avg:</span>
                        <span>$465,000</span>
                    </div>
                    <div class="detail-item">
                        <span>Price per Sq Ft:</span>
                        <span>$226</span>
                    </div>
                    <div class="detail-item">
                        <span>Days on Market:</span>
                        <span>28 days</span>
                    </div>
                    <div class="detail-item">
                        <span>Property Tax:</span>
                        <span>$5,820/year</span>
                    </div>
                    <div class="detail-item">
                        <span>HOA Fees:</span>
                        <span>$0/month</span>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="map-container">
            <h3>Property Location</h3>
            <div class="map-placeholder">
                🗺️ Interactive Map View
                <br>
                <small>{{ address }}</small>
            </div>
        </div>
    </main>
</body>
</html>
    ''', address=address, current_date=datetime.now().strftime('%B %d, %Y'))

# Enhanced login page
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
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 2rem;
        }
        
        .login-container {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 3rem;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
            width: 100%;
            max-width: 400px;
        }
        
        .logo {
            text-align: center;
            margin-bottom: 2rem;
        }
        
        .logo a {
            font-size: 2rem;
            font-weight: bold;
            color: #667eea;
            text-decoration: none;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
        }
        
        .login-title {
            text-align: center;
            margin-bottom: 2rem;
            color: #333;
            font-size: 1.5rem;
        }
        
        .form-group {
            margin-bottom: 1.5rem;
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
            border: 2px solid #e1e5e9;
            border-radius: 12px;
            font-size: 1rem;
            transition: all 0.3s ease;
            background: white;
        }
        
        .form-input:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        .login-btn {
            width: 100%;
            padding: 1rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-bottom: 1.5rem;
        }
        
        .login-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
        }
        
        .back-link {
            text-align: center;
        }
        
        .back-link a {
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
        }
        
        .back-link a:hover {
            text-decoration: underline;
        }
        
        .forgot-password {
            text-align: center;
            margin-bottom: 1rem;
        }
        
        .forgot-password a {
            color: #667eea;
            text-decoration: none;
            font-size: 0.9rem;
        }
        
        .forgot-password a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="logo">
            <a href="/">🏠 BlueDwarf</a>
        </div>
        
        <h2 class="login-title">Welcome Back</h2>
        
        <form action="/login" method="POST">
            <div class="form-group">
                <label for="email" class="form-label">Email</label>
                <input type="email" id="email" name="email" class="form-input" required>
            </div>
            
            <div class="form-group">
                <label for="password" class="form-label">Password</label>
                <input type="password" id="password" name="password" class="form-input" required>
            </div>
            
            <button type="submit" class="login-btn">Sign In</button>
            
            <div class="forgot-password">
                <a href="/forgot-password">Forgot your password?</a>
            </div>
        </form>
        
        <div class="back-link">
            <a href="/">← Back to Home</a>
        </div>
    </div>
</body>
</html>
    ''')

# Enhanced signup page
@app.route('/signup')
def signup():
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
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 2rem;
        }
        
        .signup-container {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 3rem;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
            width: 100%;
            max-width: 450px;
        }
        
        .logo {
            text-align: center;
            margin-bottom: 2rem;
        }
        
        .logo a {
            font-size: 2rem;
            font-weight: bold;
            color: #667eea;
            text-decoration: none;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
        }
        
        .signup-title {
            text-align: center;
            margin-bottom: 2rem;
            color: #333;
            font-size: 1.5rem;
        }
        
        .form-group {
            margin-bottom: 1.5rem;
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
            border: 2px solid #e1e5e9;
            border-radius: 12px;
            font-size: 1rem;
            transition: all 0.3s ease;
            background: white;
        }
        
        .form-input:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        .signup-btn {
            width: 100%;
            padding: 1rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-bottom: 1.5rem;
        }
        
        .signup-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
        }
        
        .back-link {
            text-align: center;
        }
        
        .back-link a {
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
        }
        
        .back-link a:hover {
            text-decoration: underline;
        }
        
        .terms {
            font-size: 0.9rem;
            color: #666;
            text-align: center;
            margin-bottom: 1rem;
            line-height: 1.4;
        }
        
        .terms a {
            color: #667eea;
            text-decoration: none;
        }
        
        .terms a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="signup-container">
        <div class="logo">
            <a href="/">🏠 BlueDwarf</a>
        </div>
        
        <h2 class="signup-title">Create Your Account</h2>
        
        <form action="/signup" method="POST">
            <div class="form-group">
                <label for="fullname" class="form-label">Full Name</label>
                <input type="text" id="fullname" name="fullname" class="form-input" required>
            </div>
            
            <div class="form-group">
                <label for="email" class="form-label">Email</label>
                <input type="email" id="email" name="email" class="form-input" required>
            </div>
            
            <div class="form-group">
                <label for="company" class="form-label">Company (Optional)</label>
                <input type="text" id="company" name="company" class="form-input">
            </div>
            
            <div class="form-group">
                <label for="password" class="form-label">Password</label>
                <input type="password" id="password" name="password" class="form-input" required>
            </div>
            
            <div class="terms">
                By creating an account, you agree to our <a href="/terms">Terms of Service</a> and <a href="/privacy">Privacy Policy</a>.
            </div>
            
            <button type="submit" class="signup-btn">Create Account</button>
        </form>
        
        <div class="back-link">
            <a href="/">← Back to Home</a>
        </div>
    </div>
</body>
</html>
    ''')

# Dashboard page
@app.route('/dashboard')
def dashboard():
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - BlueDwarf</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: #f8f9fa;
            min-height: 100vh;
        }
        
        .header {
            background: white;
            padding: 1rem 2rem;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            position: sticky;
            top: 0;
            z-index: 100;
        }
        
        .nav {
            display: flex;
            justify-content: space-between;
            align-items: center;
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .logo {
            font-size: 1.5rem;
            font-weight: bold;
            color: #667eea;
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .user-menu {
            display: flex;
            align-items: center;
            gap: 1rem;
        }
        
        .main-content {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        .dashboard-header {
            margin-bottom: 2rem;
        }
        
        .dashboard-title {
            font-size: 2rem;
            color: #333;
            margin-bottom: 0.5rem;
        }
        
        .dashboard-subtitle {
            color: #666;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }
        
        .stat-card {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }
        
        .stat-icon {
            font-size: 2rem;
            margin-bottom: 1rem;
        }
        
        .stat-value {
            font-size: 2rem;
            font-weight: bold;
            color: #333;
            margin-bottom: 0.5rem;
        }
        
        .stat-label {
            color: #666;
            font-size: 0.9rem;
        }
        
        .recent-searches {
            background: white;
            border-radius: 12px;
            padding: 2rem;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            margin-bottom: 2rem;
        }
        
        .section-title {
            font-size: 1.25rem;
            font-weight: bold;
            margin-bottom: 1rem;
            color: #333;
        }
        
        .search-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem 0;
            border-bottom: 1px solid #eee;
        }
        
        .search-item:last-child {
            border-bottom: none;
        }
        
        .search-address {
            font-weight: 500;
            color: #333;
        }
        
        .search-date {
            color: #666;
            font-size: 0.9rem;
        }
        
        .btn {
            padding: 0.75rem 1.5rem;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            text-decoration: none;
            cursor: pointer;
            transition: all 0.3s ease;
            display: inline-block;
            text-align: center;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
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
    </style>
</head>
<body>
    <header class="header">
        <nav class="nav">
            <a href="/" class="logo">🏠 BlueDwarf</a>
            <div class="user-menu">
                <a href="/settings" class="btn btn-outline">Settings</a>
                <a href="/logout" class="btn btn-primary">Logout</a>
            </div>
        </nav>
    </header>
    
    <main class="main-content">
        <div class="dashboard-header">
            <h1 class="dashboard-title">Welcome back!</h1>
            <p class="dashboard-subtitle">Here's your property analysis overview</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-icon">🔍</div>
                <div class="stat-value">24</div>
                <div class="stat-label">Total Searches</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">⭐</div>
                <div class="stat-value">8</div>
                <div class="stat-label">Saved Properties</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">📊</div>
                <div class="stat-value">12</div>
                <div class="stat-label">Reports Generated</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">🎯</div>
                <div class="stat-value">3</div>
                <div class="stat-label">Active Alerts</div>
            </div>
        </div>
        
        <div class="recent-searches">
            <h2 class="section-title">Recent Searches</h2>
            <div class="search-item">
                <div>
                    <div class="search-address">123 Pine Street, Seattle, WA</div>
                    <div class="search-date">Searched 2 hours ago</div>
                </div>
                <a href="/search-results/123-pine-street" class="btn btn-outline">View Report</a>
            </div>
            <div class="search-item">
                <div>
                    <div class="search-address">456 Oak Avenue, Portland, OR</div>
                    <div class="search-date">Searched yesterday</div>
                </div>
                <a href="/search-results/456-oak-avenue" class="btn btn-outline">View Report</a>
            </div>
            <div class="search-item">
                <div>
                    <div class="search-address">789 Maple Drive, San Francisco, CA</div>
                    <div class="search-date">Searched 3 days ago</div>
                </div>
                <a href="/search-results/789-maple-drive" class="btn btn-outline">View Report</a>
            </div>
        </div>
    </main>
</body>
</html>
    ''')

# API endpoints
@app.route('/api/health')
def api_health():
    return jsonify({
        'status': 'healthy',
        'service': 'BlueDwarf Platform',
        'version': '2.0.0',
        'timestamp': datetime.now().isoformat(),
        'environment': 'production',
        'deployment': 'Heroku',
        'message': 'Advanced platform is live and operational!',
        'endpoints': {
            'home': '/',
            'search': '/search',
            'login': '/login',
            'signup': '/signup',
            'dashboard': '/dashboard',
            'health': '/api/health'
        }
    })

@app.route('/api/property/<address>')
def api_property(address):
    return jsonify({
        'address': address,
        'estimated_value': 485000,
        'property_type': 'Single Family',
        'year_built': 1995,
        'square_feet': 2150,
        'bedrooms': 3,
        'bathrooms': 2.5,
        'market_trend': 'Rising',
        'neighborhood_avg': 465000,
        'price_per_sqft': 226,
        'days_on_market': 28,
        'property_tax': 5820,
        'hoa_fees': 0,
        'analysis_date': datetime.now().isoformat()
    })

# Handle form submissions
@app.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    # In a real app, you would validate credentials here
    session['user'] = email
    return redirect(url_for('dashboard'))

@app.route('/signup', methods=['POST'])
def signup_post():
    fullname = request.form.get('fullname')
    email = request.form.get('email')
    company = request.form.get('company')
    password = request.form.get('password')
    # In a real app, you would create the user account here
    session['user'] = email
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

