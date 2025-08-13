from flask import Flask, render_template_string, request, redirect, url_for, session, jsonify
import os

app = Flask(__name__)
app.secret_key = 'bluedwarf-secret-key-2025'

# Homepage template with cleaned up design
HOME_TEMPLATE = '''
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
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: white;
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
            font-size: 1.5rem;
            font-weight: bold;
            text-decoration: none;
            color: white;
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
            border-radius: 8px;
            text-decoration: none;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        
        .login-btn {
            background: rgba(255, 255, 255, 0.2);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }
        
        .signup-btn {
            background: rgba(255, 255, 255, 0.9);
            color: #667eea;
        }
        
        .nav-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        }
        
        .main-content {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: calc(100vh - 200px);
            padding: 2rem;
            text-align: center;
        }
        
        .title {
            font-size: 3.5rem;
            font-weight: bold;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 1rem;
        }
        
        .subtitle {
            font-size: 1.25rem;
            margin-bottom: 3rem;
            opacity: 0.9;
        }
        
        .search-card {
            background: rgba(255, 255, 255, 0.95);
            padding: 2.5rem;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
            max-width: 600px;
            width: 100%;
        }
        
        .search-input {
            width: 100%;
            padding: 1rem 1.5rem;
            border: 2px solid #e1e5e9;
            border-radius: 12px;
            font-size: 1.1rem;
            margin-bottom: 1.5rem;
            outline: none;
            transition: border-color 0.3s ease;
        }
        
        .search-input:focus {
            border-color: #667eea;
        }
        
        .button-group {
            display: flex;
            gap: 1rem;
            justify-content: center;
        }
        
        .search-btn, .clear-btn {
            padding: 1rem 3rem;
            border-radius: 12px;
            font-size: 1.1rem;
            font-weight: 600;
            border: none;
            cursor: pointer;
            transition: all 0.3s ease;
            min-width: 150px;
        }
        
        .search-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .clear-btn {
            background: rgba(255, 255, 255, 0.1);
            color: #667eea;
            border: 2px solid #667eea;
        }
        
        .search-btn:hover, .clear-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
        }
        
        .footer {
            text-align: center;
            padding: 2rem;
            background: rgba(0, 0, 0, 0.1);
            margin-top: auto;
        }
        
        .footer a {
            color: white;
            text-decoration: none;
        }
        
        .footer a:hover {
            text-decoration: underline;
        }
        
        @media (max-width: 768px) {
            .title {
                font-size: 2.5rem;
            }
            
            .search-card {
                margin: 0 1rem;
                padding: 2rem;
            }
            
            .button-group {
                flex-direction: column;
            }
            
            .search-btn, .clear-btn {
                width: 100%;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <a href="/" class="logo">
            🏠 BlueDwarf
        </a>
        <div class="nav-buttons">
            <a href="/login" class="nav-btn login-btn">Login</a>
            <a href="/signup" class="nav-btn signup-btn">Get Started</a>
        </div>
    </div>
    
    <div class="main-content">
        <h1 class="title">
            🏠 Property Analysis
        </h1>
        <p class="subtitle">Instant Data • Full US Coverage</p>
        
        <div class="search-card">
            <form action="/search" method="POST">
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
    </div>
    
    <div class="footer">
        <p>&copy; 2025 Elite Marketing Lab LLC. All rights reserved. | <a href="mailto:support@bluedwarf.io">support@bluedwarf.io</a></p>
    </div>
</body>
</html>
'''

# Enhanced Create Account template
SIGNUP_TEMPLATE = '''
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
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 2rem;
        }
        
        .signup-container {
            background: rgba(255, 255, 255, 0.95);
            padding: 3rem;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
            max-width: 600px;
            width: 100%;
            max-height: 90vh;
            overflow-y: auto;
        }
        
        .logo {
            text-align: center;
            margin-bottom: 2rem;
        }
        
        .logo a {
            font-size: 1.5rem;
            font-weight: bold;
            text-decoration: none;
            color: #667eea;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.5rem 1rem;
            border: 2px solid #667eea;
            border-radius: 8px;
        }
        
        .form-title {
            text-align: center;
            color: #333;
            margin-bottom: 2rem;
            font-size: 1.8rem;
        }
        
        .form-row {
            display: flex;
            gap: 1rem;
            margin-bottom: 1.5rem;
        }
        
        .form-group {
            flex: 1;
            margin-bottom: 1.5rem;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 0.5rem;
            color: #333;
            font-weight: 500;
        }
        
        .form-group input,
        .form-group select {
            width: 100%;
            padding: 1rem;
            border: 2px solid #e1e5e9;
            border-radius: 8px;
            font-size: 1rem;
            transition: border-color 0.3s ease;
            background: white;
        }
        
        .form-group input:focus,
        .form-group select:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .form-group select {
            cursor: pointer;
        }
        
        .zip-codes-input {
            font-family: monospace;
            font-size: 0.9rem;
        }
        
        .zip-codes-help {
            font-size: 0.8rem;
            color: #666;
            margin-top: 0.25rem;
        }
        
        .terms-section {
            margin: 1.5rem 0;
            text-align: center;
            font-size: 0.9rem;
            color: #666;
        }
        
        .terms-section a {
            color: #667eea;
            text-decoration: none;
        }
        
        .terms-section a:hover {
            text-decoration: underline;
        }
        
        .submit-btn {
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
            margin-bottom: 1rem;
        }
        
        .submit-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
        }
        
        .back-link {
            display: block;
            text-align: center;
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
        }
        
        .back-link:hover {
            text-decoration: underline;
        }
        
        @media (max-width: 768px) {
            .signup-container {
                padding: 2rem;
                margin: 1rem;
            }
            
            .form-row {
                flex-direction: column;
                gap: 0;
            }
        }
    </style>
</head>
<body>
    <div class="signup-container">
        <div class="logo">
            <a href="/">🏠 BlueDwarf</a>
        </div>
        
        <h2 class="form-title">Create Account</h2>
        
        <form action="/signup" method="POST">
            <div class="form-row">
                <div class="form-group">
                    <label for="first_name">First Name</label>
                    <input type="text" id="first_name" name="first_name" required>
                </div>
                <div class="form-group">
                    <label for="last_name">Last Name</label>
                    <input type="text" id="last_name" name="last_name" required>
                </div>
            </div>
            
            <div class="form-group">
                <label for="email">Email</label>
                <input type="email" id="email" name="email" required>
            </div>
            
            <div class="form-group">
                <label for="business_address">Business Address</label>
                <input type="text" id="business_address" name="business_address" placeholder="123 Main St, City, State, ZIP" required>
            </div>
            
            <div class="form-row">
                <div class="form-group">
                    <label for="license_number">License Number</label>
                    <input type="text" id="license_number" name="license_number" required>
                </div>
                <div class="form-group">
                    <label for="website">Website</label>
                    <input type="url" id="website" name="website" placeholder="https://yourwebsite.com">
                </div>
            </div>
            
            <div class="form-group">
                <label for="profession">Profession</label>
                <select id="profession" name="profession" required>
                    <option value="">Select your profession</option>
                    <option value="real_estate_agent">Real Estate Agent</option>
                    <option value="real_estate_broker">Real Estate Broker</option>
                    <option value="mortgage_lender">Mortgage Lender</option>
                    <option value="real_estate_attorney">Real Estate Attorney</option>
                    <option value="property_inspector">Property Inspector</option>
                    <option value="insurance_agent">Insurance Agent</option>
                    <option value="general_contractor">General Contractor</option>
                    <option value="property_appraiser">Property Appraiser</option>
                    <option value="structural_engineer">Structural Engineer</option>
                    <option value="escrow_officer">Escrow Officer</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="service_zip_codes">Service Zip Codes</label>
                <input 
                    type="text" 
                    id="service_zip_codes" 
                    name="service_zip_codes" 
                    class="zip-codes-input"
                    placeholder="95628, 95814, 95630" 
                    required
                >
                <div class="zip-codes-help">Enter zip codes separated by commas (e.g., 95628, 95814, 95630)</div>
            </div>
            
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required>
            </div>
            
            <div class="terms-section">
                By creating an account, you agree to our 
                <a href="/terms">Terms of Service</a> and 
                <a href="/privacy">Privacy Policy</a>
            </div>
            
            <button type="submit" class="submit-btn">Create Account</button>
            
            <a href="/" class="back-link">← Back to Home</a>
        </form>
    </div>
</body>
</html>
'''

# Login template
LOGIN_TEMPLATE = '''
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
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 2rem;
        }
        
        .login-container {
            background: rgba(255, 255, 255, 0.95);
            padding: 3rem;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
            max-width: 400px;
            width: 100%;
        }
        
        .logo {
            text-align: center;
            margin-bottom: 2rem;
        }
        
        .logo a {
            font-size: 1.5rem;
            font-weight: bold;
            text-decoration: none;
            color: #667eea;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.5rem 1rem;
            border: 2px solid #667eea;
            border-radius: 8px;
        }
        
        .form-title {
            text-align: center;
            color: #333;
            margin-bottom: 2rem;
            font-size: 1.8rem;
        }
        
        .form-group {
            margin-bottom: 1.5rem;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 0.5rem;
            color: #333;
            font-weight: 500;
        }
        
        .form-group input {
            width: 100%;
            padding: 1rem;
            border: 2px solid #e1e5e9;
            border-radius: 8px;
            font-size: 1rem;
            transition: border-color 0.3s ease;
        }
        
        .form-group input:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .submit-btn {
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
            margin-bottom: 1rem;
        }
        
        .submit-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
        }
        
        .forgot-link {
            display: block;
            text-align: center;
            color: #667eea;
            text-decoration: none;
            margin-bottom: 1rem;
        }
        
        .forgot-link:hover {
            text-decoration: underline;
        }
        
        .back-link {
            display: block;
            text-align: center;
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
    <div class="login-container">
        <div class="logo">
            <a href="/">🏠 BlueDwarf</a>
        </div>
        
        <h2 class="form-title">Welcome Back</h2>
        
        <form action="/login" method="POST">
            <div class="form-group">
                <label for="email">Email</label>
                <input type="email" id="email" name="email" required>
            </div>
            
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required>
            </div>
            
            <button type="submit" class="submit-btn">Sign In</button>
            
            <a href="/forgot-password" class="forgot-link">Forgot your password?</a>
            
            <a href="/" class="back-link">← Back to Home</a>
        </form>
    </div>
</body>
</html>
'''

# Property search results template
SEARCH_RESULTS_TEMPLATE = '''
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
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: white;
            padding: 2rem;
        }
        
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
        }
        
        .logo {
            font-size: 1.5rem;
            font-weight: bold;
            text-decoration: none;
            color: white;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .back-btn {
            background: rgba(255, 255, 255, 0.2);
            color: white;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        
        .back-btn:hover {
            background: rgba(255, 255, 255, 0.3);
        }
        
        .results-header {
            background: rgba(255, 255, 255, 0.95);
            color: #333;
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
        }
        
        .results-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
            margin-bottom: 2rem;
        }
        
        .result-card {
            background: rgba(255, 255, 255, 0.95);
            color: #333;
            padding: 2rem;
            border-radius: 15px;
        }
        
        .card-header {
            display: flex;
            align-items: center;
            gap: 1rem;
            margin-bottom: 1.5rem;
        }
        
        .card-icon {
            width: 60px;
            height: 60px;
            background: #f0f0f0;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
        }
        
        .card-title {
            font-size: 1.3rem;
            font-weight: bold;
        }
        
        .property-details {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1rem;
        }
        
        .detail-item {
            display: flex;
            justify-content: space-between;
            padding: 0.5rem 0;
            border-bottom: 1px solid #eee;
        }
        
        .detail-label {
            font-weight: 500;
        }
        
        .detail-value {
            font-weight: bold;
        }
        
        .rising {
            color: #22c55e;
        }
        
        .map-section {
            background: rgba(255, 255, 255, 0.95);
            color: #333;
            padding: 2rem;
            border-radius: 15px;
        }
        
        .map-placeholder {
            background: #f0f0f0;
            height: 300px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.1rem;
            color: #666;
        }
        
        @media (max-width: 768px) {
            .results-grid {
                grid-template-columns: 1fr;
            }
            
            .property-details {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <a href="/" class="logo">🏠 BlueDwarf</a>
        <a href="/" class="back-btn">← Back to Search</a>
    </div>
    
    <div class="results-header">
        <h1>Property Analysis Results</h1>
        <p><strong>Address:</strong> {{ address }}</p>
        <p><strong>Analysis Date:</strong> {{ analysis_date }}</p>
    </div>
    
    <div class="results-grid">
        <div class="result-card">
            <div class="card-header">
                <div class="card-icon">🏠</div>
                <h2 class="card-title">Property Overview</h2>
            </div>
            <div class="property-details">
                <div class="detail-item">
                    <span class="detail-label">Estimated Value:</span>
                    <span class="detail-value">$485,000</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Property Type:</span>
                    <span class="detail-value">Single Family</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Year Built:</span>
                    <span class="detail-value">1995</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Square Feet:</span>
                    <span class="detail-value">2,150 sq ft</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Bedrooms:</span>
                    <span class="detail-value">3</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Bathrooms:</span>
                    <span class="detail-value">2.5</span>
                </div>
            </div>
        </div>
        
        <div class="result-card">
            <div class="card-header">
                <div class="card-icon">📊</div>
                <h2 class="card-title">Market Analysis</h2>
            </div>
            <div class="property-details">
                <div class="detail-item">
                    <span class="detail-label">Market Trend:</span>
                    <span class="detail-value rising">↗ Rising</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Neighborhood Avg:</span>
                    <span class="detail-value">$465,000</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Price per Sq Ft:</span>
                    <span class="detail-value">$226</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Days on Market:</span>
                    <span class="detail-value">28 days</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Property Tax:</span>
                    <span class="detail-value">$5,820/year</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">HOA Fees:</span>
                    <span class="detail-value">$0/month</span>
                </div>
            </div>
        </div>
    </div>
    
    <div class="map-section">
        <h2>Property Location</h2>
        <div class="map-placeholder">
            🗺️ Interactive Map View<br>{{ address }}
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HOME_TEMPLATE)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        # Here you would typically validate credentials
        session['user_email'] = email
        return redirect(url_for('dashboard'))
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Get all the form data
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        business_address = request.form.get('business_address')
        license_number = request.form.get('license_number')
        website = request.form.get('website')
        profession = request.form.get('profession')
        service_zip_codes = request.form.get('service_zip_codes')
        password = request.form.get('password')
        
        # Here you would typically save to database
        session['user_email'] = email
        session['user_name'] = f"{first_name} {last_name}"
        return redirect(url_for('dashboard'))
    
    return render_template_string(SIGNUP_TEMPLATE)

@app.route('/search', methods=['POST'])
def search():
    address = request.form.get('address', '')
    from datetime import datetime
    analysis_date = datetime.now().strftime('%B %d, %Y')
    
    return render_template_string(SEARCH_RESULTS_TEMPLATE, 
                                address=address, 
                                analysis_date=analysis_date)

@app.route('/dashboard')
def dashboard():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    # Simple dashboard template
    dashboard_template = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dashboard - BlueDwarf</title>
        <style>
            body { font-family: Arial, sans-serif; padding: 2rem; }
            .header { background: #667eea; color: white; padding: 1rem; border-radius: 8px; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Welcome to your Dashboard</h1>
            <p>Email: {{ session.user_email }}</p>
            <a href="/logout" style="color: white;">Logout</a>
        </div>
        <p><a href="/">← Back to Home</a></p>
    </body>
    </html>
    '''
    return render_template_string(dashboard_template, session=session)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'BlueDwarf Platform',
        'version': '1.0.0',
        'message': 'Platform is live and operational!',
        'timestamp': '2025-08-13T18:00:00Z',
        'environment': 'production',
        'deployment': 'Heroku',
        'endpoints': {
            'home': '/',
            'login': '/login',
            'signup': '/signup',
            'search': '/search',
            'health': '/api/health'
        }
    })

@app.route('/terms')
def terms():
    return '<h1>Terms of Service</h1><p>Terms of service content would go here.</p><a href="/">← Back to Home</a>'

@app.route('/privacy')
def privacy():
    return '<h1>Privacy Policy</h1><p>Privacy policy content would go here.</p><a href="/">← Back to Home</a>'

@app.route('/forgot-password')
def forgot_password():
    return '<h1>Forgot Password</h1><p>Password reset functionality would go here.</p><a href="/login">← Back to Login</a>'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

