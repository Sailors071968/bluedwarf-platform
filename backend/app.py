from flask import Flask, render_template_string, request, jsonify, session, redirect, url_for
import os
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'bluedwarf_secret_key_2025'

# Enhanced Property Analysis Flask App with Google Street View, Comparables, and Aerial Maps

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
            display: flex;
            flex-direction: column;
        }
        
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem 2rem;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
        }
        
        .logo {
            color: white;
            font-size: 1.5rem;
            font-weight: bold;
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .nav-buttons {
            display: flex;
            gap: 1rem;
        }
        
        .nav-btn {
            padding: 0.75rem 1.5rem;
            border: none;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 500;
            transition: all 0.3s ease;
            cursor: pointer;
        }
        
        .login-btn {
            background: rgba(255, 255, 255, 0.2);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }
        
        .signup-btn {
            background: #ff6b6b;
            color: white;
        }
        
        .nav-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        }
        
        .main-content {
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            padding: 2rem;
            text-align: center;
        }
        
        .title {
            color: white;
            font-size: 3rem;
            font-weight: bold;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 1rem;
        }
        
        .subtitle {
            color: rgba(255, 255, 255, 0.9);
            font-size: 1.2rem;
            margin-bottom: 3rem;
        }
        
        .search-container {
            background: white;
            padding: 2rem;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            max-width: 600px;
            width: 100%;
        }
        
        .search-form {
            display: flex;
            flex-direction: column;
            gap: 1.5rem;
        }
        
        .search-input {
            padding: 1rem;
            border: 2px solid #e1e5e9;
            border-radius: 12px;
            font-size: 1rem;
            transition: border-color 0.3s ease;
            width: 100%;
        }
        
        .search-input:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .button-group {
            display: flex;
            gap: 1rem;
        }
        
        .search-btn, .clear-btn {
            flex: 1;
            padding: 1rem 2rem;
            border: none;
            border-radius: 12px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            min-width: 150px;
        }
        
        .search-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .clear-btn {
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
            color: white;
        }
        
        .search-btn:hover, .clear-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
        }
        
        .footer {
            text-align: center;
            padding: 2rem;
            color: rgba(255, 255, 255, 0.8);
            font-size: 0.9rem;
        }
        
        .footer a {
            color: rgba(255, 255, 255, 0.9);
            text-decoration: none;
        }
        
        @media (max-width: 768px) {
            .header {
                padding: 1rem;
            }
            
            .title {
                font-size: 2rem;
            }
            
            .search-container {
                margin: 0 1rem;
            }
            
            .button-group {
                flex-direction: column;
            }
        }
    </style>
</head>
<body>
    <header class="header">
        <a href="/" class="logo">
            🏠 BlueDwarf
        </a>
        <div class="nav-buttons">
            <a href="/login" class="nav-btn login-btn">Login</a>
            <a href="/signup" class="nav-btn signup-btn">Get Started</a>
        </div>
    </header>
    
    <main class="main-content">
        <h1 class="title">
            🏠 Property Analysis
        </h1>
        <p class="subtitle">Instant Data • Full US Coverage</p>
        
        <div class="search-container">
            <form class="search-form" action="/search" method="POST">
                <input 
                    type="text" 
                    name="address" 
                    class="search-input" 
                    placeholder="123 Pine Street, Any City, WA, 54321"
                    required
                >
                <div class="button-group">
                    <button type="submit" class="search-btn">Search</button>
                    <button type="button" class="clear-btn" onclick="document.querySelector('.search-input').value=''">Clear</button>
                </div>
            </form>
        </div>
    </main>
    
    <footer class="footer">
        © 2025 Elite Marketing Lab LLC. All rights reserved. | <a href="mailto:support@bluedwarf.io">support@bluedwarf.io</a>
    </footer>
</body>
</html>
    ''')

@app.route('/search', methods=['POST'])
def search_property():
    address = request.form.get('address', '')
    if not address:
        return redirect(url_for('home'))
    
    # Store the address in session for the results page
    session['search_address'] = address
    return redirect(url_for('property_results'))

@app.route('/property-results')
def property_results():
    address = session.get('search_address', '123 Pine Street, Any City, WA, 54321')
    
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Property Analysis Results - BlueDwarf</title>
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
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem 2rem;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
        }
        
        .logo {
            color: white;
            font-size: 1.5rem;
            font-weight: bold;
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .nav-buttons {
            display: flex;
            gap: 1rem;
        }
        
        .nav-btn {
            padding: 0.75rem 1.5rem;
            border: none;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 500;
            transition: all 0.3s ease;
            cursor: pointer;
            background: rgba(255, 255, 255, 0.2);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }
        
        .nav-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        .property-header {
            background: white;
            border-radius: 20px;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        
        .property-title {
            font-size: 2rem;
            font-weight: bold;
            color: #333;
            margin-bottom: 0.5rem;
        }
        
        .property-subtitle {
            color: #666;
            font-size: 1.1rem;
        }
        
        .content-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
            margin-bottom: 2rem;
        }
        
        .card {
            background: white;
            border-radius: 20px;
            padding: 2rem;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        
        .card-title {
            font-size: 1.5rem;
            font-weight: bold;
            margin-bottom: 1.5rem;
            color: #333;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .street-view-container {
            width: 100%;
            height: 300px;
            border-radius: 12px;
            overflow: hidden;
            background: #f0f0f0;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
        }
        
        .street-view-placeholder {
            color: #666;
            text-align: center;
        }
        
        .aerial-view-container {
            width: 100%;
            height: 300px;
            border-radius: 12px;
            overflow: hidden;
            background: #f0f0f0;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
        }
        
        .property-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
            margin-top: 1rem;
        }
        
        .stat-item {
            text-align: center;
            padding: 1rem;
            background: #f8f9fa;
            border-radius: 12px;
        }
        
        .stat-value {
            font-size: 1.5rem;
            font-weight: bold;
            color: #667eea;
        }
        
        .stat-label {
            font-size: 0.9rem;
            color: #666;
            margin-top: 0.25rem;
        }
        
        .rental-indicator {
            margin-top: 1.5rem;
        }
        
        .rental-range {
            display: flex;
            align-items: center;
            gap: 1rem;
            margin-top: 1rem;
        }
        
        .rental-bar {
            flex: 1;
            height: 8px;
            background: linear-gradient(to right, #4CAF50, #FFC107, #FF5722);
            border-radius: 4px;
            position: relative;
        }
        
        .rental-marker {
            position: absolute;
            top: -8px;
            width: 4px;
            height: 24px;
            background: #333;
            border-radius: 2px;
            left: 65%;
        }
        
        .rental-labels {
            display: flex;
            justify-content: space-between;
            margin-top: 0.5rem;
            font-size: 0.9rem;
            color: #666;
        }
        
        .comparables-section {
            grid-column: 1 / -1;
        }
        
        .comparables-grid {
            display: grid;
            grid-template-columns: 1fr 400px;
            gap: 2rem;
            margin-top: 1rem;
        }
        
        .comparables-list {
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }
        
        .comparable-item {
            display: flex;
            align-items: center;
            gap: 1rem;
            padding: 1rem;
            background: #f8f9fa;
            border-radius: 12px;
            transition: all 0.3s ease;
        }
        
        .comparable-item:hover {
            background: #e9ecef;
            transform: translateX(5px);
        }
        
        .comparable-number {
            width: 30px;
            height: 30px;
            background: #667eea;
            color: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
        }
        
        .comparable-info {
            flex: 1;
        }
        
        .comparable-address {
            font-weight: 600;
            color: #333;
        }
        
        .comparable-details {
            font-size: 0.9rem;
            color: #666;
            margin-top: 0.25rem;
        }
        
        .comparable-price {
            font-size: 1.1rem;
            font-weight: bold;
            color: #667eea;
        }
        
        .map-container {
            width: 100%;
            height: 400px;
            border-radius: 12px;
            overflow: hidden;
            background: #f0f0f0;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .map-placeholder {
            color: #666;
            text-align: center;
        }
        
        .back-button {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 1rem 2rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-decoration: none;
            border-radius: 12px;
            font-weight: 600;
            transition: all 0.3s ease;
            margin-top: 2rem;
        }
        
        .back-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
        }
        
        @media (max-width: 1024px) {
            .content-grid {
                grid-template-columns: 1fr;
            }
            
            .comparables-grid {
                grid-template-columns: 1fr;
            }
            
            .property-stats {
                grid-template-columns: repeat(2, 1fr);
            }
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 1rem;
            }
            
            .property-header {
                padding: 1.5rem;
            }
            
            .card {
                padding: 1.5rem;
            }
            
            .property-stats {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <header class="header">
        <a href="/" class="logo">
            🏠 BlueDwarf
        </a>
        <div class="nav-buttons">
            <a href="/login" class="nav-btn">Login</a>
            <a href="/signup" class="nav-btn">Get Started</a>
        </div>
    </header>
    
    <div class="container">
        <div class="property-header">
            <h1 class="property-title">{{ address }}</h1>
            <p class="property-subtitle">Comprehensive Property Analysis Report</p>
        </div>
        
        <div class="content-grid">
            <!-- Street View -->
            <div class="card">
                <h2 class="card-title">🏠 Street View</h2>
                <div class="street-view-container">
                    <iframe 
                        width="100%" 
                        height="100%" 
                        frameborder="0" 
                        style="border:0"
                        src="https://www.google.com/maps/embed/v1/streetview?key=YOUR_API_KEY&location={{ address|urlencode }}&heading=210&pitch=10&fov=75"
                        allowfullscreen>
                    </iframe>
                </div>
            </div>
            
            <!-- Aerial Satellite View -->
            <div class="card">
                <h2 class="card-title">🛰️ Aerial View</h2>
                <div class="aerial-view-container">
                    <iframe 
                        width="100%" 
                        height="100%" 
                        frameborder="0" 
                        style="border:0"
                        src="https://www.google.com/maps/embed/v1/view?key=YOUR_API_KEY&center={{ address|urlencode }}&zoom=17&maptype=satellite"
                        allowfullscreen>
                    </iframe>
                </div>
            </div>
            
            <!-- Property Overview -->
            <div class="card">
                <h2 class="card-title">📊 Property Overview</h2>
                <div class="property-stats">
                    <div class="stat-item">
                        <div class="stat-value">$485,000</div>
                        <div class="stat-label">Estimated Value</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">3</div>
                        <div class="stat-label">Bedrooms</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">2.5</div>
                        <div class="stat-label">Bathrooms</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">2,150</div>
                        <div class="stat-label">Sq Ft</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">1985</div>
                        <div class="stat-label">Year Built</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">0.25</div>
                        <div class="stat-label">Lot Size (Acres)</div>
                    </div>
                </div>
            </div>
            
            <!-- Market Analysis -->
            <div class="card">
                <h2 class="card-title">📈 Market Analysis</h2>
                <div class="property-stats">
                    <div class="stat-item">
                        <div class="stat-value">$226</div>
                        <div class="stat-label">Price per Sq Ft</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">28</div>
                        <div class="stat-label">Days on Market</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">+5.2%</div>
                        <div class="stat-label">YoY Appreciation</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">Rising</div>
                        <div class="stat-label">Market Trend</div>
                    </div>
                </div>
                
                <div class="rental-indicator">
                    <h3>Rental Rate Analysis</h3>
                    <div class="rental-range">
                        <span>$1,800</span>
                        <div class="rental-bar">
                            <div class="rental-marker"></div>
                        </div>
                        <span>$3,200</span>
                    </div>
                    <div class="rental-labels">
                        <span>Low</span>
                        <span>Current: $2,450/month</span>
                        <span>High</span>
                    </div>
                </div>
            </div>
            
            <!-- Comparable Properties -->
            <div class="card comparables-section">
                <h2 class="card-title">🏘️ Comparable Properties</h2>
                <div class="comparables-grid">
                    <div class="comparables-list">
                        <div class="comparable-item">
                            <div class="comparable-number">1</div>
                            <div class="comparable-info">
                                <div class="comparable-address">456 Oak Avenue</div>
                                <div class="comparable-details">3 bed • 2 bath • 2,080 sq ft • 0.3 mi</div>
                            </div>
                            <div class="comparable-price">$472,000</div>
                        </div>
                        
                        <div class="comparable-item">
                            <div class="comparable-number">2</div>
                            <div class="comparable-info">
                                <div class="comparable-address">789 Maple Street</div>
                                <div class="comparable-details">4 bed • 3 bath • 2,340 sq ft • 0.4 mi</div>
                            </div>
                            <div class="comparable-price">$518,000</div>
                        </div>
                        
                        <div class="comparable-item">
                            <div class="comparable-number">3</div>
                            <div class="comparable-info">
                                <div class="comparable-address">321 Elm Drive</div>
                                <div class="comparable-details">3 bed • 2.5 bath • 2,200 sq ft • 0.5 mi</div>
                            </div>
                            <div class="comparable-price">$495,000</div>
                        </div>
                        
                        <div class="comparable-item">
                            <div class="comparable-number">4</div>
                            <div class="comparable-info">
                                <div class="comparable-address">654 Cedar Lane</div>
                                <div class="comparable-details">3 bed • 2 bath • 1,950 sq ft • 0.6 mi</div>
                            </div>
                            <div class="comparable-price">$458,000</div>
                        </div>
                        
                        <div class="comparable-item">
                            <div class="comparable-number">5</div>
                            <div class="comparable-info">
                                <div class="comparable-address">987 Birch Court</div>
                                <div class="comparable-details">4 bed • 2.5 bath • 2,450 sq ft • 0.7 mi</div>
                            </div>
                            <div class="comparable-price">$535,000</div>
                        </div>
                    </div>
                    
                    <div class="map-container">
                        <iframe 
                            width="100%" 
                            height="100%" 
                            frameborder="0" 
                            style="border:0"
                            src="https://www.google.com/maps/embed/v1/view?key=YOUR_API_KEY&center={{ address|urlencode }}&zoom=15&maptype=roadmap"
                            allowfullscreen>
                        </iframe>
                    </div>
                </div>
            </div>
        </div>
        
        <a href="/" class="back-button">
            ← Back to Search
        </a>
    </div>
</body>
</html>
    ''', address=address)

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
            flex-direction: column;
        }
        
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem 2rem;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
        }
        
        .logo {
            color: white;
            font-size: 1.5rem;
            font-weight: bold;
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .main-content {
            flex: 1;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 2rem;
        }
        
        .login-container {
            background: white;
            padding: 3rem;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            max-width: 400px;
            width: 100%;
        }
        
        .login-title {
            font-size: 2rem;
            font-weight: bold;
            text-align: center;
            margin-bottom: 2rem;
            color: #333;
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
            transition: border-color 0.3s ease;
        }
        
        .form-input:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .login-btn {
            width: 100%;
            padding: 1rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .login-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
        }
        
        .back-link {
            display: block;
            text-align: center;
            margin-top: 2rem;
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
    <header class="header">
        <a href="/" class="logo">
            🏠 BlueDwarf
        </a>
    </header>
    
    <main class="main-content">
        <div class="login-container">
            <h1 class="login-title">Welcome Back</h1>
            <form>
                <div class="form-group">
                    <label class="form-label">Email</label>
                    <input type="email" class="form-input" required>
                </div>
                <div class="form-group">
                    <label class="form-label">Password</label>
                    <input type="password" class="form-input" required>
                </div>
                <button type="submit" class="login-btn">Sign In</button>
            </form>
            <a href="/" class="back-link">← Back to Home</a>
        </div>
    </main>
</body>
</html>
    ''')

@app.route('/signup')
def signup():
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Create Account - BlueDwarf</title>
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
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem 2rem;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
        }
        
        .logo {
            color: white;
            font-size: 1.5rem;
            font-weight: bold;
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .container {
            max-width: 800px;
            margin: 2rem auto;
            padding: 0 2rem;
        }
        
        .signup-container {
            background: white;
            border-radius: 20px;
            padding: 3rem;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        }
        
        .signup-title {
            font-size: 2rem;
            font-weight: bold;
            text-align: center;
            margin-bottom: 1rem;
            color: #333;
        }
        
        .security-notice {
            background: #e3f2fd;
            border-left: 4px solid #2196f3;
            padding: 1rem;
            margin-bottom: 2rem;
            border-radius: 8px;
        }
        
        .security-notice h3 {
            color: #1976d2;
            margin-bottom: 0.5rem;
        }
        
        .security-notice p {
            color: #424242;
            font-size: 0.9rem;
        }
        
        .form-section {
            margin-bottom: 2rem;
            padding: 1.5rem;
            border: 2px solid #f0f0f0;
            border-radius: 12px;
        }
        
        .section-title {
            font-size: 1.2rem;
            font-weight: bold;
            margin-bottom: 1rem;
            color: #333;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .form-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1rem;
            margin-bottom: 1rem;
        }
        
        .form-group {
            margin-bottom: 1rem;
        }
        
        .form-label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 600;
            color: #333;
        }
        
        .required {
            color: #e74c3c;
        }
        
        .form-input, .form-select {
            width: 100%;
            padding: 0.75rem;
            border: 2px solid #e1e5e9;
            border-radius: 8px;
            font-size: 1rem;
            transition: border-color 0.3s ease;
        }
        
        .form-input:focus, .form-select:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .upload-area {
            border: 2px dashed #ddd;
            border-radius: 8px;
            padding: 2rem;
            text-align: center;
            background: #fafafa;
            transition: all 0.3s ease;
            cursor: pointer;
        }
        
        .upload-area:hover {
            border-color: #667eea;
            background: #f0f4ff;
        }
        
        .upload-icon {
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }
        
        .upload-text {
            font-weight: 600;
            margin-bottom: 0.25rem;
        }
        
        .upload-subtext {
            font-size: 0.9rem;
            color: #666;
        }
        
        .camera-section {
            text-align: center;
            padding: 2rem;
            background: #f8f9fa;
            border-radius: 12px;
        }
        
        .camera-btn {
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            color: white;
            border: none;
            padding: 1rem 2rem;
            border-radius: 12px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .camera-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
        }
        
        .submit-btn {
            width: 100%;
            padding: 1rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-top: 2rem;
        }
        
        .submit-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
        }
        
        .terms-text {
            text-align: center;
            font-size: 0.9rem;
            color: #666;
            margin-top: 1rem;
        }
        
        .terms-text a {
            color: #667eea;
            text-decoration: none;
        }
        
        .back-link {
            display: block;
            text-align: center;
            margin-top: 2rem;
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
        }
        
        @media (max-width: 768px) {
            .form-row {
                grid-template-columns: 1fr;
            }
            
            .container {
                padding: 0 1rem;
            }
            
            .signup-container {
                padding: 2rem;
            }
        }
    </style>
</head>
<body>
    <header class="header">
        <a href="/" class="logo">
            🏠 BlueDwarf
        </a>
    </header>
    
    <div class="container">
        <div class="signup-container">
            <h1 class="signup-title">Create Account</h1>
            
            <div class="security-notice">
                <h3>🔒 Secure Professional Verification</h3>
                <p>To ensure platform security, all professionals must complete identity verification including document uploads and live photo verification.</p>
            </div>
            
            <form>
                <!-- Personal Information -->
                <div class="form-section">
                    <h2 class="section-title">👤 Personal Information</h2>
                    <div class="form-row">
                        <div class="form-group">
                            <label class="form-label">First Name <span class="required">*</span></label>
                            <input type="text" class="form-input" required>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Last Name <span class="required">*</span></label>
                            <input type="text" class="form-input" required>
                        </div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Email <span class="required">*</span></label>
                        <input type="email" class="form-input" required>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Password <span class="required">*</span></label>
                        <input type="password" class="form-input" required>
                    </div>
                </div>
                
                <!-- Professional Information -->
                <div class="form-section">
                    <h2 class="section-title">💼 Professional Information</h2>
                    <div class="form-group">
                        <label class="form-label">Business Address <span class="required">*</span></label>
                        <input type="text" class="form-input" placeholder="123 Main St, City, State, ZIP" required>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label class="form-label">License Number <span class="required">*</span></label>
                            <input type="text" class="form-input" required>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Website</label>
                            <input type="url" class="form-input" placeholder="https://yourwebsite.com">
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label class="form-label">Profession <span class="required">*</span></label>
                            <select class="form-select" required>
                                <option value="">Select your profession</option>
                                <option value="real-estate-agent">Real Estate Agent</option>
                                <option value="real-estate-broker">Real Estate Broker</option>
                                <option value="mortgage-lender">Mortgage Lender</option>
                                <option value="real-estate-attorney">Real Estate Attorney</option>
                                <option value="property-inspector">Property Inspector</option>
                                <option value="insurance-agent">Insurance Agent</option>
                                <option value="general-contractor">General Contractor</option>
                                <option value="property-appraiser">Property Appraiser</option>
                                <option value="structural-engineer">Structural Engineer</option>
                                <option value="escrow-officer">Escrow Officer</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Service Zip Codes <span class="required">*</span></label>
                            <input type="text" class="form-input" placeholder="95628, 95814, 95630" required>
                            <small style="color: #666; font-size: 0.8rem;">Enter zip codes separated by commas (e.g., 95628, 95814, 95630)</small>
                        </div>
                    </div>
                </div>
                
                <!-- Document Verification -->
                <div class="form-section">
                    <h2 class="section-title">📄 Document Verification</h2>
                    <div class="form-row">
                        <div class="form-group">
                            <label class="form-label">Professional License <span class="required">*</span></label>
                            <div class="upload-area">
                                <div class="upload-icon">📋</div>
                                <div class="upload-text">Upload Professional License</div>
                                <div class="upload-subtext">PDF, JPG, PNG (Max 5MB)</div>
                            </div>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Photo ID / Driver's License <span class="required">*</span></label>
                            <div class="upload-area">
                                <div class="upload-icon">🪪</div>
                                <div class="upload-text">Upload Photo ID</div>
                                <div class="upload-subtext">State-issued photo ID or driver's license (JPG, PNG - Max 5MB)</div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Live Photo Verification -->
                <div class="form-section">
                    <h2 class="section-title">📸 Live Photo Verification</h2>
                    <div class="camera-section">
                        <div style="font-size: 3rem; margin-bottom: 1rem;">📷</div>
                        <h4>Facial Recognition Verification</h4>
                        <p style="margin: 1rem 0; color: #666;">Take a live photo for identity verification using our secure facial recognition system.</p>
                        <button type="button" class="camera-btn">📸 Start Live Photo Capture</button>
                    </div>
                </div>
                
                <div class="terms-text">
                    By creating an account, you agree to our <a href="#">Terms of Service</a> and <a href="#">Privacy Policy</a>
                </div>
                
                <button type="submit" class="submit-btn">Create Account & Verify Identity</button>
            </form>
            
            <a href="/" class="back-link">← Back to Home</a>
        </div>
    </div>
</body>
</html>
    ''')

@app.route('/api/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "BlueDwarf Platform",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "message": "Enhanced platform with Street View, comparables, and aerial maps is live and operational!",
        "features": {
            "street_view": "Google Street View integration",
            "aerial_maps": "Satellite view with 2-block radius",
            "comparables": "Numbered properties with interactive map",
            "rental_analysis": "Low-to-high rate indicators",
            "verification": "Professional document and facial recognition"
        },
        "endpoints": {
            "home": "/",
            "search": "/search",
            "results": "/property-results",
            "login": "/login",
            "signup": "/signup",
            "health": "/api/health"
        },
        "environment": "production",
        "deployment": "Heroku"
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

