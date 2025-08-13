from flask import Flask, render_template_string, jsonify, request
import os
from datetime import datetime

app = Flask(__name__)

# Homepage template matching the desired design
HOME_TEMPLATE = """
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
            padding: 20px 30px;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
        }
        
        .logo {
            display: flex;
            align-items: center;
            font-size: 24px;
            font-weight: 600;
            color: white;
            text-decoration: none;
        }
        
        .logo .house-icon {
            margin-right: 10px;
            font-size: 28px;
        }
        
        .header-buttons {
            display: flex;
            gap: 15px;
        }
        
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 500;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            text-align: center;
            transition: all 0.3s ease;
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
            background: #5a67d8;
            color: white;
        }
        
        .btn-primary:hover {
            background: #4c51bf;
            transform: translateY(-2px);
        }
        
        .main-content {
            text-align: center;
            padding: 60px 30px;
            max-width: 800px;
            margin: 0 auto;
        }
        
        .main-title {
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 48px;
            font-weight: 700;
            margin-bottom: 20px;
            color: white;
        }
        
        .main-title .house-icon {
            margin-right: 15px;
            font-size: 52px;
        }
        
        .subtitle {
            font-size: 20px;
            margin-bottom: 50px;
            opacity: 0.9;
            font-weight: 300;
        }
        
        .search-card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
            max-width: 500px;
            margin: 0 auto;
        }
        
        .search-title {
            color: #2d3748;
            font-size: 24px;
            font-weight: 600;
            margin-bottom: 30px;
        }
        
        .form-group {
            margin-bottom: 25px;
        }
        
        .form-input {
            width: 100%;
            padding: 16px 20px;
            border: 2px solid #e2e8f0;
            border-radius: 12px;
            font-size: 16px;
            color: #2d3748;
            background: white;
            transition: all 0.3s ease;
        }
        
        .form-input:focus {
            outline: none;
            border-color: #5a67d8;
            box-shadow: 0 0 0 3px rgba(90, 103, 216, 0.1);
        }
        
        .form-input::placeholder {
            color: #a0aec0;
        }
        
        .btn-search {
            width: 100%;
            padding: 16px;
            background: #5a67d8;
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-bottom: 15px;
        }
        
        .btn-search:hover {
            background: #4c51bf;
            transform: translateY(-2px);
        }
        
        .btn-clear {
            width: 100%;
            padding: 16px;
            background: #718096;
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .btn-clear:hover {
            background: #4a5568;
        }
        
        .footer {
            text-align: center;
            padding: 40px 30px;
            color: rgba(255, 255, 255, 0.8);
            font-size: 14px;
        }
        
        .footer a {
            color: rgba(255, 255, 255, 0.9);
            text-decoration: none;
        }
        
        .footer a:hover {
            text-decoration: underline;
        }
        
        @media (max-width: 768px) {
            .header {
                padding: 15px 20px;
            }
            
            .logo {
                font-size: 20px;
            }
            
            .btn {
                padding: 10px 18px;
                font-size: 14px;
            }
            
            .main-title {
                font-size: 36px;
            }
            
            .subtitle {
                font-size: 18px;
            }
            
            .search-card {
                padding: 30px 20px;
                margin: 0 20px;
            }
        }
    </style>
</head>
<body>
    <header class="header">
        <a href="/" class="logo">
            <span class="house-icon">🏠</span>
            BlueDwarf
        </a>
        <div class="header-buttons">
            <a href="/login" class="btn btn-login">Login</a>
            <a href="/signup" class="btn btn-primary">Get Started</a>
        </div>
    </header>
    
    <main class="main-content">
        <h1 class="main-title">
            <span class="house-icon">🏠</span>
            Property Analysis
        </h1>
        <p class="subtitle">Instant Data • Full US Coverage</p>
        
        <div class="search-card">
            <h2 class="search-title">Address</h2>
            <form id="searchForm">
                <div class="form-group">
                    <input 
                        type="text" 
                        class="form-input" 
                        id="address" 
                        name="address" 
                        placeholder="123 Pine Street, Any City, WA, 54321"
                        required
                    >
                </div>
                <button type="submit" class="btn-search">Search</button>
                <button type="button" class="btn-clear" onclick="clearForm()">Clear</button>
            </form>
        </div>
    </main>
    
    <footer class="footer">
        <p>© 2024 Elite Marketing Lab LLC. All rights reserved.</p>
        <p><a href="mailto:support@bluedwarf.io">support@bluedwarf.io</a></p>
    </footer>
    
    <script>
        document.getElementById('searchForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const address = document.getElementById('address').value;
            if (address.trim()) {
                // Here you would typically send the address to your backend
                alert('Searching for property: ' + address);
                // For now, just show an alert. In production, this would redirect to results page
            }
        });
        
        function clearForm() {
            document.getElementById('address').value = '';
        }
    </script>
</body>
</html>
"""

# Login page template
LOGIN_TEMPLATE = """
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
            color: white;
        }
        
        .login-card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
            max-width: 400px;
            width: 100%;
            margin: 20px;
        }
        
        .logo {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .logo-text {
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 28px;
            font-weight: 600;
            color: #2d3748;
            text-decoration: none;
        }
        
        .logo-text .house-icon {
            margin-right: 10px;
            font-size: 32px;
        }
        
        .login-title {
            color: #2d3748;
            font-size: 24px;
            font-weight: 600;
            margin-bottom: 30px;
            text-align: center;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-label {
            display: block;
            color: #4a5568;
            font-weight: 500;
            margin-bottom: 8px;
        }
        
        .form-input {
            width: 100%;
            padding: 12px 16px;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            font-size: 16px;
            color: #2d3748;
            background: white;
            transition: all 0.3s ease;
        }
        
        .form-input:focus {
            outline: none;
            border-color: #5a67d8;
            box-shadow: 0 0 0 3px rgba(90, 103, 216, 0.1);
        }
        
        .btn-login {
            width: 100%;
            padding: 14px;
            background: #5a67d8;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-bottom: 20px;
        }
        
        .btn-login:hover {
            background: #4c51bf;
        }
        
        .back-link {
            text-align: center;
        }
        
        .back-link a {
            color: #5a67d8;
            text-decoration: none;
            font-weight: 500;
        }
        
        .back-link a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="login-card">
        <div class="logo">
            <a href="/" class="logo-text">
                <span class="house-icon">🏠</span>
                BlueDwarf
            </a>
        </div>
        
        <h2 class="login-title">Welcome Back</h2>
        
        <form id="loginForm">
            <div class="form-group">
                <label for="email" class="form-label">Email</label>
                <input type="email" class="form-input" id="email" name="email" required>
            </div>
            
            <div class="form-group">
                <label for="password" class="form-label">Password</label>
                <input type="password" class="form-input" id="password" name="password" required>
            </div>
            
            <button type="submit" class="btn-login">Sign In</button>
        </form>
        
        <div class="back-link">
            <a href="/">← Back to Home</a>
        </div>
    </div>
    
    <script>
        document.getElementById('loginForm').addEventListener('submit', function(e) {
            e.preventDefault();
            alert('Login functionality will be implemented in the next phase.');
        });
    </script>
</body>
</html>
"""

# Signup page template
SIGNUP_TEMPLATE = """
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
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
        }
        
        .signup-card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
            max-width: 400px;
            width: 100%;
            margin: 20px;
        }
        
        .logo {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .logo-text {
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 28px;
            font-weight: 600;
            color: #2d3748;
            text-decoration: none;
        }
        
        .logo-text .house-icon {
            margin-right: 10px;
            font-size: 32px;
        }
        
        .signup-title {
            color: #2d3748;
            font-size: 24px;
            font-weight: 600;
            margin-bottom: 30px;
            text-align: center;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-label {
            display: block;
            color: #4a5568;
            font-weight: 500;
            margin-bottom: 8px;
        }
        
        .form-input {
            width: 100%;
            padding: 12px 16px;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            font-size: 16px;
            color: #2d3748;
            background: white;
            transition: all 0.3s ease;
        }
        
        .form-input:focus {
            outline: none;
            border-color: #5a67d8;
            box-shadow: 0 0 0 3px rgba(90, 103, 216, 0.1);
        }
        
        .btn-signup {
            width: 100%;
            padding: 14px;
            background: #5a67d8;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-bottom: 20px;
        }
        
        .btn-signup:hover {
            background: #4c51bf;
        }
        
        .back-link {
            text-align: center;
        }
        
        .back-link a {
            color: #5a67d8;
            text-decoration: none;
            font-weight: 500;
        }
        
        .back-link a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="signup-card">
        <div class="logo">
            <a href="/" class="logo-text">
                <span class="house-icon">🏠</span>
                BlueDwarf
            </a>
        </div>
        
        <h2 class="signup-title">Get Started</h2>
        
        <form id="signupForm">
            <div class="form-group">
                <label for="name" class="form-label">Full Name</label>
                <input type="text" class="form-input" id="name" name="name" required>
            </div>
            
            <div class="form-group">
                <label for="email" class="form-label">Email</label>
                <input type="email" class="form-input" id="email" name="email" required>
            </div>
            
            <div class="form-group">
                <label for="company" class="form-label">Company (Optional)</label>
                <input type="text" class="form-input" id="company" name="company">
            </div>
            
            <div class="form-group">
                <label for="password" class="form-label">Password</label>
                <input type="password" class="form-input" id="password" name="password" required>
            </div>
            
            <button type="submit" class="btn-signup">Create Account</button>
        </form>
        
        <div class="back-link">
            <a href="/">← Back to Home</a>
        </div>
    </div>
    
    <script>
        document.getElementById('signupForm').addEventListener('submit', function(e) {
            e.preventDefault();
            alert('Account creation functionality will be implemented in the next phase.');
        });
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HOME_TEMPLATE)

@app.route('/login')
def login():
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/signup')
def signup():
    return render_template_string(SIGNUP_TEMPLATE)

@app.route('/api/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "BlueDwarf Platform",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "message": "Platform is live and operational!",
        "environment": "production",
        "deployment": "Heroku",
        "endpoints": {
            "home": "/",
            "login": "/login", 
            "signup": "/signup",
            "health": "/api/health"
        }
    })

@app.route('/api/search', methods=['POST'])
def search_property():
    data = request.get_json()
    address = data.get('address', '') if data else ''
    
    # This is where you would integrate with property data APIs
    return jsonify({
        "status": "success",
        "address": address,
        "message": "Property search functionality will be implemented in the next phase",
        "timestamp": datetime.now().isoformat()
    })

# Document verification endpoint
@app.route('/api/verify/document', methods=['POST'])
def verify_document():
    return jsonify({
        "status": "success",
        "service": "document_verification",
        "message": "Document verification service ready",
        "timestamp": datetime.now().isoformat()
    })

# Identity verification endpoint  
@app.route('/api/verify/identity', methods=['POST'])
def verify_identity():
    return jsonify({
        "status": "success", 
        "service": "identity_verification",
        "message": "Identity verification service ready",
        "timestamp": datetime.now().isoformat()
    })

# License validation endpoint
@app.route('/api/verify/license', methods=['POST']) 
def verify_license():
    return jsonify({
        "status": "success",
        "service": "license_validation", 
        "message": "License validation service ready",
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
