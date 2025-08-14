from flask import Flask, render_template_string, request, redirect, url_for, flash, jsonify
from flask_mail import Mail, Message
import os
import re
import urllib.parse

app = Flask(__name__)
app.secret_key = 'bluedwarf-secret-key-2025'

# Email configuration using environment variables
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'support@bluedwarf.io')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', '')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME', 'support@bluedwarf.io')

# Initialize Flask-Mail
mail = Mail(app)

# Google Maps API Key - Replace with your actual key
GOOGLE_MAPS_API_KEY = "AIzaSyDe8QxfkBSo2Ids9PWK24-aKgqbI9du9B4"

def extract_zip_code(address):
    """Extract zip code from address string"""
    # Look for 5-digit zip code pattern
    zip_match = re.search(r'\b(\d{5})\b', address)
    if zip_match:
        return zip_match.group(1)
    return "95814"  # Default Sacramento zip code

def encode_address_for_maps(address):
    """Properly encode address for Google Maps API"""
    return urllib.parse.quote_plus(address)

# Email templates
def send_registration_email(user_email, user_name, profession):
    """Send registration confirmation email"""
    try:
        msg = Message(
            subject='Welcome to BlueDwarf - Registration Confirmed!',
            recipients=[user_email],
            html=f'''
            <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; text-align: center;">
                    <h1 style="color: white; margin: 0;">🏠 Welcome to BlueDwarf!</h1>
                </div>
                
                <div style="padding: 2rem; background: white;">
                    <h2 style="color: #333;">Hello {user_name}!</h2>
                    
                    <p style="color: #666; line-height: 1.6;">
                        Thank you for registering with BlueDwarf as a <strong>{profession}</strong>. 
                        Your account has been successfully created and is now active.
                    </p>
                    
                    <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 8px; margin: 1.5rem 0;">
                        <h3 style="color: #333; margin-top: 0;">What's Next?</h3>
                        <ul style="color: #666; line-height: 1.6;">
                            <li>Complete your professional profile</li>
                            <li>Upload verification documents</li>
                            <li>Start receiving client inquiries</li>
                            <li>Access our professional dashboard</li>
                        </ul>
                    </div>
                    
                    <div style="text-align: center; margin: 2rem 0;">
                        <a href="https://bluedwarf-platform-7cae4752497f.herokuapp.com/" 
                           style="background: #667eea; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">
                            Access Your Dashboard
                        </a>
                    </div>
                    
                    <p style="color: #666; font-size: 14px;">
                        If you have any questions, please contact us at support@bluedwarf.io
                    </p>
                </div>
                
                <div style="background: #f8f9fa; padding: 1rem; text-align: center; color: #666; font-size: 12px;">
                    © 2025 BlueDwarf Platform. All rights reserved.
                </div>
            </body>
            </html>
            '''
        )
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False

def send_contact_notification(name, email, message, subject="Contact Form Submission"):
    """Send contact form notification to admin"""
    try:
        msg = Message(
            subject=f'BlueDwarf Contact: {subject}',
            recipients=['support@bluedwarf.io'],
            html=f'''
            <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background: #667eea; padding: 1.5rem; text-align: center;">
                    <h2 style="color: white; margin: 0;">New Contact Form Submission</h2>
                </div>
                
                <div style="padding: 2rem; background: white;">
                    <h3 style="color: #333;">Contact Details:</h3>
                    <p><strong>Name:</strong> {name}</p>
                    <p><strong>Email:</strong> {email}</p>
                    <p><strong>Subject:</strong> {subject}</p>
                    
                    <h3 style="color: #333;">Message:</h3>
                    <div style="background: #f8f9fa; padding: 1rem; border-radius: 6px;">
                        {message}
                    </div>
                    
                    <div style="margin-top: 2rem; padding-top: 1rem; border-top: 1px solid #eee;">
                        <p style="color: #666; font-size: 14px;">
                            Respond to this inquiry by replying to: {email}
                        </p>
                    </div>
                </div>
            </body>
            </html>
            '''
        )
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Contact notification failed: {e}")
        return False

@app.route('/')
def index():
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
        }
        
        .logo {
            font-size: 1.5rem;
            font-weight: bold;
            color: white;
            text-decoration: none;
        }
        
        .nav-buttons {
            display: flex;
            gap: 1rem;
        }
        
        .nav-buttons a {
            padding: 0.5rem 1rem;
            border-radius: 6px;
            text-decoration: none;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        
        .login-btn {
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }
        
        .login-btn:hover {
            background: rgba(255, 255, 255, 0.1);
        }
        
        .signup-btn {
            background: rgba(255, 255, 255, 0.2);
            color: white;
        }
        
        .signup-btn:hover {
            background: rgba(255, 255, 255, 0.3);
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
        
        .hero-section {
            max-width: 800px;
            margin-bottom: 3rem;
        }
        
        .hero-title {
            font-size: 3rem;
            color: white;
            margin-bottom: 1rem;
            font-weight: 700;
        }
        
        .hero-subtitle {
            font-size: 1.2rem;
            color: rgba(255, 255, 255, 0.9);
            margin-bottom: 2rem;
        }
        
        .search-container {
            background: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            max-width: 600px;
            width: 100%;
        }
        
        .search-form {
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }
        
        .search-input {
            padding: 1rem;
            border: 2px solid #e1e5e9;
            border-radius: 8px;
            font-size: 1rem;
            transition: border-color 0.3s ease;
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
            padding: 1rem;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .search-btn {
            background: #667eea;
            color: white;
        }
        
        .search-btn:hover {
            background: #5a6fd8;
            transform: translateY(-2px);
        }
        
        .clear-btn {
            background: #ff6b6b;
            color: white;
        }
        
        .clear-btn:hover {
            background: #ff5252;
            transform: translateY(-2px);
        }
        
        @media (max-width: 768px) {
            .hero-title {
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
        <a href="/" class="logo">🏠 BlueDwarf</a>
        <div class="nav-buttons">
            <a href="#" class="login-btn">Login</a>
            <a href="/signup" class="signup-btn">Get Started</a>
        </div>
    </header>
    
    <main class="main-content">
        <div class="hero-section">
            <h1 class="hero-title">🏠 Property Analysis</h1>
            <p class="hero-subtitle">Instant Data • Full US Coverage</p>
        </div>
        
        <div class="search-container">
            <form class="search-form" action="/property-results" method="POST">
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
</body>
</html>
    ''')

@app.route('/property-results', methods=['POST'])
def property_results():
    address = request.form.get('address', '123 Main Street, Sacramento, CA 95814')
    zip_code = extract_zip_code(address)
    encoded_address = encode_address_for_maps(address)
    
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
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .logo {
            font-size: 1.5rem;
            font-weight: bold;
            color: white;
            text-decoration: none;
        }
        
        .nav-buttons {
            display: flex;
            gap: 1rem;
        }
        
        .nav-buttons a {
            padding: 0.5rem 1rem;
            border-radius: 6px;
            text-decoration: none;
            font-weight: 500;
            transition: all 0.3s ease;
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }
        
        .nav-buttons a:hover {
            background: rgba(255, 255, 255, 0.1);
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        .property-header {
            background: white;
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        
        .property-title {
            font-size: 2rem;
            color: #333;
            margin-bottom: 0.5rem;
        }
        
        .property-subtitle {
            color: #666;
            font-size: 1.1rem;
        }
        
        .maps-section {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
            margin-bottom: 2rem;
        }
        
        .map-container {
            background: white;
            border-radius: 15px;
            padding: 1.5rem;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        
        .map-title {
            font-size: 1.2rem;
            color: #333;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .map-frame {
            width: 100%;
            height: 300px;
            border: none;
            border-radius: 10px;
            background: #f8f9fa;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }
        
        .stat-card {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }
        
        .stat-value {
            font-size: 1.8rem;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 0.5rem;
        }
        
        .stat-label {
            color: #666;
            font-size: 0.9rem;
        }
        
        .rental-analysis {
            background: white;
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        
        .section-title {
            font-size: 1.3rem;
            color: #333;
            margin-bottom: 1.5rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .rental-range {
            background: linear-gradient(90deg, #4CAF50 0%, #FFC107 50%, #FF5722 100%);
            height: 10px;
            border-radius: 5px;
            margin: 1rem 0;
            position: relative;
        }
        
        .rental-indicator {
            position: absolute;
            top: -5px;
            width: 2px;
            height: 20px;
            background: #333;
            left: 50%;
        }
        
        .rental-labels {
            display: flex;
            justify-content: space-between;
            font-size: 0.9rem;
            color: #666;
        }
        
        .comparables-section {
            background: white;
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        
        .comparable-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem;
            border-bottom: 1px solid #f0f0f0;
            transition: background-color 0.3s ease;
        }
        
        .comparable-item:hover {
            background-color: #f8f9fa;
        }
        
        .comparable-item:last-child {
            border-bottom: none;
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
            margin-right: 1rem;
        }
        
        .comparable-info {
            flex: 1;
        }
        
        .comparable-address {
            font-weight: 600;
            color: #333;
            margin-bottom: 0.25rem;
        }
        
        .comparable-details {
            color: #666;
            font-size: 0.9rem;
        }
        
        .comparable-price {
            font-size: 1.2rem;
            font-weight: bold;
            color: #667eea;
        }
        
        .professionals-section {
            background: white;
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        
        .professionals-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 1.5rem;
            margin-top: 1.5rem;
        }
        
        .professional-card {
            border: 1px solid #e1e5e9;
            border-radius: 10px;
            padding: 1.5rem;
            transition: all 0.3s ease;
        }
        
        .professional-card:hover {
            border-color: #667eea;
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.1);
        }
        
        .professional-title {
            font-size: 1.1rem;
            font-weight: 600;
            color: #667eea;
            margin-bottom: 0.5rem;
        }
        
        .professional-location {
            color: #666;
            font-size: 0.9rem;
            margin-bottom: 0.75rem;
        }
        
        .professional-description {
            color: #555;
            line-height: 1.5;
            margin-bottom: 1rem;
        }
        
        .professional-buttons {
            display: flex;
            gap: 0.75rem;
        }
        
        .website-btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        
        .website-btn:hover {
            background: #5a6fd8;
            transform: translateY(-1px);
        }
        
        .back-link {
            display: inline-block;
            margin-top: 2rem;
            color: white;
            text-decoration: none;
            padding: 0.75rem 1.5rem;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 8px;
            transition: all 0.3s ease;
        }
        
        .back-link:hover {
            background: rgba(255, 255, 255, 0.3);
        }
        
        @media (max-width: 768px) {
            .maps-section {
                grid-template-columns: 1fr;
            }
            
            .stats-grid {
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            }
            
            .professionals-grid {
                grid-template-columns: 1fr;
            }
            
            .comparable-item {
                flex-direction: column;
                align-items: flex-start;
                gap: 0.5rem;
            }
        }
    </style>
</head>
<body>
    <header class="header">
        <a href="/" class="logo">🏠 BlueDwarf</a>
        <div class="nav-buttons">
            <a href="#" class="login-btn">Login</a>
            <a href="/signup" class="signup-btn">Get Started</a>
        </div>
    </header>
    
    <div class="container">
        <div class="property-header">
            <h1 class="property-title">{{ address }}</h1>
            <p class="property-subtitle">Comprehensive Property Analysis Report</p>
        </div>
        
        <div class="maps-section">
            <div class="map-container">
                <h2 class="map-title">🏠 Street View</h2>
                <iframe 
                    class="map-frame"
                    src="https://www.google.com/maps/embed/v1/streetview?key={{ api_key }}&location={{ encoded_address }}&heading=0&pitch=0&fov=90"
                    allowfullscreen>
                </iframe>
            </div>
            
            <div class="map-container">
                <h2 class="map-title">🛰️ Aerial View (2 blocks)</h2>
                <iframe 
                    class="map-frame"
                    src="https://www.google.com/maps/embed/v1/view?key={{ api_key }}&center={{ encoded_address }}&zoom=17&maptype=satellite"
                    allowfullscreen>
                </iframe>
            </div>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">$485,000</div>
                <div class="stat-label">Estimated Value</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">4</div>
                <div class="stat-label">Bedrooms</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">2</div>
                <div class="stat-label">Bathrooms</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">1,492</div>
                <div class="stat-label">Square Feet</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">1964</div>
                <div class="stat-label">Year Built</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">$2,510</div>
                <div class="stat-label">Monthly Rent Est</div>
            </div>
        </div>
        
        <div class="rental-analysis">
            <h2 class="section-title">📊 Rental Rate Analysis</h2>
            <div class="rental-range">
                <div class="rental-indicator"></div>
            </div>
            <div class="rental-labels">
                <span>$1,800 Low</span>
                <span>Current: $2,510/month</span>
                <span>$3,200 High</span>
            </div>
        </div>
        
        <div class="comparables-section">
            <h2 class="section-title">🏘️ Comparable Properties</h2>
            
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
        
        <div class="professionals-section">
            <h2 class="section-title">👥 Local Professionals in {{ zip_code }}</h2>
            
            <div class="professionals-grid">
                <div class="professional-card">
                    <div class="professional-title">Real Estate Agent</div>
                    <div class="professional-location">{{ zip_code }}</div>
                    <div class="professional-description">Experienced agent specializing in residential properties and first-time buyers</div>
                    <div class="professional-buttons">
                        <button class="website-btn" onclick="searchProfessional('Real Estate Agent', '{{ zip_code }}')">Website</button>
                    </div>
                </div>
                
                <div class="professional-card">
                    <div class="professional-title">Real Estate Broker</div>
                    <div class="professional-location">{{ zip_code }}</div>
                    <div class="professional-description">Licensed broker with extensive market knowledge and investment expertise</div>
                    <div class="professional-buttons">
                        <button class="website-btn" onclick="searchProfessional('Real Estate Broker', '{{ zip_code }}')">Website</button>
                    </div>
                </div>
                
                <div class="professional-card">
                    <div class="professional-title">Mortgage Lender</div>
                    <div class="professional-location">{{ zip_code }}</div>
                    <div class="professional-description">Specialized in home loans and refinancing with competitive rates</div>
                    <div class="professional-buttons">
                        <button class="website-btn" onclick="searchProfessional('Mortgage Lender', '{{ zip_code }}')">Website</button>
                    </div>
                </div>
                
                <div class="professional-card">
                    <div class="professional-title">Real Estate Attorney</div>
                    <div class="professional-location">{{ zip_code }}</div>
                    <div class="professional-description">Expert in real estate transactions and contract negotiations</div>
                    <div class="professional-buttons">
                        <button class="website-btn" onclick="searchProfessional('Real Estate Attorney', '{{ zip_code }}')">Website</button>
                    </div>
                </div>
                
                <div class="professional-card">
                    <div class="professional-title">Property Inspector</div>
                    <div class="professional-location">{{ zip_code }}</div>
                    <div class="professional-description">Certified home inspector with comprehensive inspection services</div>
                    <div class="professional-buttons">
                        <button class="website-btn" onclick="searchProfessional('Property Inspector', '{{ zip_code }}')">Website</button>
                    </div>
                </div>
                
                <div class="professional-card">
                    <div class="professional-title">Insurance Agent</div>
                    <div class="professional-location">{{ zip_code }}</div>
                    <div class="professional-description">Home and auto insurance specialist with competitive coverage options</div>
                    <div class="professional-buttons">
                        <button class="website-btn" onclick="searchProfessional('Insurance Agent', '{{ zip_code }}')">Website</button>
                    </div>
                </div>
                
                <div class="professional-card">
                    <div class="professional-title">General Contractor</div>
                    <div class="professional-location">{{ zip_code }}</div>
                    <div class="professional-description">Licensed contractor for home renovations and construction projects</div>
                    <div class="professional-buttons">
                        <button class="website-btn" onclick="searchProfessional('General Contractor', '{{ zip_code }}')">Website</button>
                    </div>
                </div>
                
                <div class="professional-card">
                    <div class="professional-title">Property Appraiser</div>
                    <div class="professional-location">{{ zip_code }}</div>
                    <div class="professional-description">Certified appraiser providing accurate property valuations</div>
                    <div class="professional-buttons">
                        <button class="website-btn" onclick="searchProfessional('Property Appraiser', '{{ zip_code }}')">Website</button>
                    </div>
                </div>
                
                <div class="professional-card">
                    <div class="professional-title">Structural Engineer</div>
                    <div class="professional-location">{{ zip_code }}</div>
                    <div class="professional-description">Professional engineer specializing in structural analysis and design</div>
                    <div class="professional-buttons">
                        <button class="website-btn" onclick="searchProfessional('Structural Engineer', '{{ zip_code }}')">Website</button>
                    </div>
                </div>
                
                <div class="professional-card">
                    <div class="professional-title">Escrow Officer</div>
                    <div class="professional-location">{{ zip_code }}</div>
                    <div class="professional-description">Experienced escrow professional ensuring smooth real estate transactions</div>
                    <div class="professional-buttons">
                        <button class="website-btn" onclick="searchProfessional('Escrow Officer', '{{ zip_code }}')">Website</button>
                    </div>
                </div>
                
                <div class="professional-card">
                    <div class="professional-title">Property Manager</div>
                    <div class="professional-location">{{ zip_code }}</div>
                    <div class="professional-description">Professional property management services for residential and commercial properties</div>
                    <div class="professional-buttons">
                        <button class="website-btn" onclick="searchProfessional('Property Manager', '{{ zip_code }}')">Website</button>
                    </div>
                </div>
            </div>
        </div>
        
        <a href="/" class="back-link">← Back to Search</a>
    </div>
    
    <script>
        // BlueDwarf Platform - Working Google Search Button Fix
        
        // Main Google search function
        function searchProfessional(professionalType, zipCode) {
            try {
                // Validate inputs
                if (!professionalType || !zipCode) {
                    console.error('BlueDwarf: Missing professional type or zip code');
                    alert('Unable to search - missing location information');
                    return;
                }

                // Create search query
                const searchQuery = professionalType + ' ' + zipCode;
                
                // Encode for URL
                const encodedQuery = encodeURIComponent(searchQuery);
                
                // Create Google search URL
                const googleUrl = 'https://www.google.com/search?q=' + encodedQuery;
                
                // Log for debugging
                console.log('BlueDwarf: Searching for "' + searchQuery + '"');
                console.log('BlueDwarf: Opening URL: ' + googleUrl);
                
                // Open in new tab
                window.open(googleUrl, '_blank');
                
            } catch (error) {
                console.error('BlueDwarf: Error in searchProfessional:', error);
                alert('Unable to open search - please try again');
            }
        }

        // Contact professional function
        function contactProfessional(professionalType) {
            try {
                const message = 'I am interested in connecting with a ' + professionalType + ' for property services. Please provide contact information or have them reach out to me.';
                const subject = encodeURIComponent('BlueDwarf Inquiry: ' + professionalType + ' Services');
                const body = encodeURIComponent(message);
                const mailtoUrl = 'mailto:support@bluedwarf.io?subject=' + subject + '&body=' + body;
                
                window.location.href = mailtoUrl;
                
            } catch (error) {
                console.error('BlueDwarf: Error in contactProfessional:', error);
                alert('Unable to create contact - please try again');
            }
        }

        // Initialize when page loads
        document.addEventListener('DOMContentLoaded', function() {
            console.log('BlueDwarf: Google search functionality loaded successfully');
        });

        // Make functions globally available
        window.searchProfessional = searchProfessional;
        window.contactProfessional = contactProfessional;

        console.log('BlueDwarf: Google search button fix loaded');
    </script>
</body>
</html>
    ''', address=address, zip_code=zip_code, encoded_address=encoded_address, api_key=GOOGLE_MAPS_API_KEY)

@app.route('/signup')
def signup():
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
        
        .header {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .logo {
            font-size: 1.5rem;
            font-weight: bold;
            color: white;
            text-decoration: none;
        }
        
        .nav-buttons {
            display: flex;
            gap: 1rem;
        }
        
        .nav-buttons a {
            padding: 0.5rem 1rem;
            border-radius: 6px;
            text-decoration: none;
            font-weight: 500;
            transition: all 0.3s ease;
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }
        
        .nav-buttons a:hover {
            background: rgba(255, 255, 255, 0.1);
        }
        
        .container {
            max-width: 600px;
            margin: 2rem auto;
            padding: 2rem;
        }
        
        .signup-card {
            background: white;
            padding: 3rem;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        }
        
        .signup-title {
            font-size: 2rem;
            color: #333;
            margin-bottom: 0.5rem;
            text-align: center;
        }
        
        .signup-subtitle {
            color: #666;
            text-align: center;
            margin-bottom: 2rem;
        }
        
        .form-group {
            margin-bottom: 1.5rem;
        }
        
        .form-label {
            display: block;
            margin-bottom: 0.5rem;
            color: #333;
            font-weight: 500;
        }
        
        .form-input, .form-select {
            width: 100%;
            padding: 1rem;
            border: 2px solid #e1e5e9;
            border-radius: 8px;
            font-size: 1rem;
            transition: border-color 0.3s ease;
        }
        
        .form-input:focus, .form-select:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .submit-btn {
            width: 100%;
            padding: 1rem;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .submit-btn:hover {
            background: #5a6fd8;
            transform: translateY(-2px);
        }
        
        .success-message {
            background: #d4edda;
            color: #155724;
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
            border: 1px solid #c3e6cb;
        }
        
        .error-message {
            background: #f8d7da;
            color: #721c24;
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
            border: 1px solid #f5c6cb;
        }
    </style>
</head>
<body>
    <header class="header">
        <a href="/" class="logo">🏠 BlueDwarf</a>
        <div class="nav-buttons">
            <a href="/">← Back to Home</a>
        </div>
    </header>
    
    <div class="container">
        <div class="signup-card">
            <h1 class="signup-title">Join Our Professional Network</h1>
            <p class="signup-subtitle">Connect with property buyers and sellers in your area</p>
            
            {% with messages = get_flashed_messages() %}
                {% if messages %}
                    {% for message in messages %}
                        <div class="success-message">{{ message }}</div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
            
            <form method="POST" action="/register">
                <div class="form-group">
                    <label class="form-label" for="name">Full Name</label>
                    <input type="text" id="name" name="name" class="form-input" required>
                </div>
                
                <div class="form-group">
                    <label class="form-label" for="email">Email Address</label>
                    <input type="email" id="email" name="email" class="form-input" required>
                </div>
                
                <div class="form-group">
                    <label class="form-label" for="profession">Professional Category</label>
                    <select id="profession" name="profession" class="form-select" required>
                        <option value="">Select your profession</option>
                        <option value="Real Estate Agent">Real Estate Agent</option>
                        <option value="Real Estate Broker">Real Estate Broker</option>
                        <option value="Mortgage Lender">Mortgage Lender</option>
                        <option value="Real Estate Attorney">Real Estate Attorney</option>
                        <option value="Property Inspector">Property Inspector</option>
                        <option value="Insurance Agent">Insurance Agent</option>
                        <option value="General Contractor">General Contractor</option>
                        <option value="Property Appraiser">Property Appraiser</option>
                        <option value="Structural Engineer">Structural Engineer</option>
                        <option value="Escrow Officer">Escrow Officer</option>
                        <option value="Property Manager">Property Manager</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label class="form-label" for="phone">Phone Number</label>
                    <input type="tel" id="phone" name="phone" class="form-input" required>
                </div>
                
                <div class="form-group">
                    <label class="form-label" for="license">License Number (if applicable)</label>
                    <input type="text" id="license" name="license" class="form-input">
                </div>
                
                <div class="form-group">
                    <label class="form-label" for="experience">Years of Experience</label>
                    <select id="experience" name="experience" class="form-select" required>
                        <option value="">Select experience level</option>
                        <option value="0-2 years">0-2 years</option>
                        <option value="3-5 years">3-5 years</option>
                        <option value="6-10 years">6-10 years</option>
                        <option value="11-15 years">11-15 years</option>
                        <option value="16+ years">16+ years</option>
                    </select>
                </div>
                
                <button type="submit" class="submit-btn">Register as Professional</button>
            </form>
        </div>
    </div>
</body>
</html>
    ''')

@app.route('/register', methods=['POST'])
def register():
    try:
        name = request.form.get('name')
        email = request.form.get('email')
        profession = request.form.get('profession')
        phone = request.form.get('phone')
        license_num = request.form.get('license')
        experience = request.form.get('experience')
        
        # Send registration email
        email_sent = send_registration_email(email, name, profession)
        
        if email_sent:
            flash(f'Registration successful! Welcome to BlueDwarf, {name}. Check your email for confirmation details.')
        else:
            flash('Registration completed, but there was an issue sending the confirmation email. Please contact support if needed.')
        
        return redirect(url_for('signup'))
        
    except Exception as e:
        flash('Registration failed. Please try again or contact support.')
        return redirect(url_for('signup'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

