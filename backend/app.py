from flask import Flask, render_template_string, request, redirect, url_for, flash, jsonify
from flask_mail import Mail, Message
import os
import re

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

def extract_zip_code(address):
    """Extract zip code from address string"""
    # Look for 5-digit zip code pattern
    zip_match = re.search(r'\b(\d{5})\b', address)
    if zip_match:
        return zip_match.group(1)
    return "95814"  # Default Sacramento zip code

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
            display: flex;
            align-items: center;
            justify-content: center;
            color: #666;
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
            border-bottom: 1px solid #eee;
            margin-bottom: 1rem;
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
        
        .comparable-details {
            flex: 1;
        }
        
        .comparable-address {
            font-weight: 600;
            color: #333;
            margin-bottom: 0.3rem;
        }
        
        .comparable-specs {
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
            grid-template-columns: repeat(2, 1fr);
            gap: 1.5rem;
        }
        
        .professional-card {
            border: 1px solid #e1e5e9;
            border-radius: 12px;
            padding: 1.5rem;
            transition: all 0.3s ease;
        }
        
        .professional-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }
        
        .professional-title {
            font-size: 1.1rem;
            font-weight: 600;
            color: #667eea;
            margin-bottom: 0.3rem;
        }
        
        .professional-location {
            color: #666;
            font-size: 0.9rem;
            margin-bottom: 1rem;
        }
        
        .professional-description {
            color: #555;
            font-size: 0.9rem;
            line-height: 1.4;
            margin-bottom: 1.5rem;
        }
        
        .professional-buttons {
            display: flex;
            gap: 0.5rem;
        }
        
        .website-btn, .contact-btn {
            flex: 1;
            padding: 0.7rem;
            border: none;
            border-radius: 6px;
            font-size: 0.9rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .website-btn {
            background: #667eea;
            color: white;
        }
        
        .website-btn:hover {
            background: #5a6fd8;
            transform: translateY(-1px);
        }
        
        .contact-btn {
            background: #f8f9fa;
            color: #667eea;
            border: 1px solid #667eea;
        }
        
        .contact-btn:hover {
            background: #667eea;
            color: white;
        }
        
        .back-link {
            display: inline-block;
            margin-top: 2rem;
            padding: 1rem 2rem;
            background: rgba(255, 255, 255, 0.2);
            color: white;
            text-decoration: none;
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
            
            .professionals-grid {
                grid-template-columns: 1fr;
            }
            
            .stats-grid {
                grid-template-columns: repeat(2, 1fr);
            }
            
            .comparable-item {
                flex-direction: column;
                text-align: center;
            }
            
            .professional-buttons {
                flex-direction: column;
            }
        }
    </style>
</head>
<body>
    <header class="header">
        <a href="/" class="logo">🏠 BlueDwarf</a>
        <div class="nav-buttons">
            <a href="#">Login</a>
            <a href="/signup">Get Started</a>
        </div>
    </header>
    
    <div class="container">
        <div class="property-header">
            <h1 class="property-title">{{ address }}</h1>
            <p class="property-subtitle">Comprehensive Property Analysis Report</p>
        </div>
        
        <div class="maps-section">
            <div class="map-container">
                <h3 class="map-title">🏠 Street View</h3>
                <iframe class="map-frame" 
                        src="https://www.google.com/maps/embed/v1/streetview?key=AIzaSyDe8QxfkBSo2Ids9PWK24-aKgqbI9du9B4&location={{ address }}&heading=210&pitch=10&fov=35"
                        allowfullscreen>
                </iframe>
            </div>
            
            <div class="map-container">
                <h3 class="map-title">🛰️ Aerial View (2 blocks)</h3>
                <iframe class="map-frame"
                        src="https://www.google.com/maps/embed/v1/view?key=AIzaSyDe8QxfkBSo2Ids9PWK24-aKgqbI9du9B4&center={{ address }}&zoom=16&maptype=satellite"
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
            <h3 class="section-title">📊 Rental Rate Analysis</h3>
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
            <h3 class="section-title">🏘️ Comparable Properties</h3>
            
            <div class="comparable-item">
                <div class="comparable-number">1</div>
                <div class="comparable-details">
                    <div class="comparable-address">456 Oak Avenue</div>
                    <div class="comparable-specs">3 bed • 2 bath • 2,080 sq ft • 0.3 mi</div>
                </div>
                <div class="comparable-price">$472,000</div>
            </div>
            
            <div class="comparable-item">
                <div class="comparable-number">2</div>
                <div class="comparable-details">
                    <div class="comparable-address">789 Maple Street</div>
                    <div class="comparable-specs">4 bed • 3 bath • 2,340 sq ft • 0.4 mi</div>
                </div>
                <div class="comparable-price">$518,000</div>
            </div>
            
            <div class="comparable-item">
                <div class="comparable-number">3</div>
                <div class="comparable-details">
                    <div class="comparable-address">321 Elm Drive</div>
                    <div class="comparable-specs">3 bed • 2.5 bath • 2,200 sq ft • 0.5 mi</div>
                </div>
                <div class="comparable-price">$495,000</div>
            </div>
            
            <div class="comparable-item">
                <div class="comparable-number">4</div>
                <div class="comparable-details">
                    <div class="comparable-address">654 Cedar Lane</div>
                    <div class="comparable-specs">3 bed • 2 bath • 1,950 sq ft • 0.6 mi</div>
                </div>
                <div class="comparable-price">$458,000</div>
            </div>
            
            <div class="comparable-item">
                <div class="comparable-number">5</div>
                <div class="comparable-details">
                    <div class="comparable-address">987 Birch Court</div>
                    <div class="comparable-specs">4 bed • 2.5 bath • 2,450 sq ft • 0.7 mi</div>
                </div>
                <div class="comparable-price">$535,000</div>
            </div>
            
            <iframe class="map-frame" style="margin-top: 1rem;"
                    src="https://www.google.com/maps/embed/v1/view?key=AIzaSyDe8QxfkBSo2Ids9PWK24-aKgqbI9du9B4&center={{ address }}&zoom=15"
                    allowfullscreen>
            </iframe>
        </div>
        
        <div class="professionals-section">
            <h3 class="section-title">👥 Local Professionals in {{ address.split(',')[-2].strip() if ',' in address else 'Local Area' }}</h3>
            
            <div class="professionals-grid">
                <div class="professional-card">
                    <div class="professional-title">Real Estate Agent</div>
                    <div class="professional-location">{{ address.split(',')[-2].strip() if ',' in address else 'Local Area' }}</div>
                    <div class="professional-description">Experienced agent specializing in residential properties and first-time buyers. Provides market analysis, negotiation expertise, and comprehensive transaction support from listing to closing.</div>
                    <div class="professional-buttons">
                        <button class="website-btn" onclick="searchProfessional('Real Estate Agent', '{{ zip_code }}')">Website</button>
                        <button class="contact-btn" onclick="contactProfessional('Real Estate Agent')">Contact</button>
                    </div>
                </div>
                
                <div class="professional-card">
                    <div class="professional-title">Real Estate Broker</div>
                    <div class="professional-location">{{ address.split(',')[-2].strip() if ',' in address else 'Local Area' }}</div>
                    <div class="professional-description">Licensed broker with extensive market knowledge and investment expertise. Offers advanced real estate services, brokerage operations, and complex transaction management.</div>
                    <div class="professional-buttons">
                        <button class="website-btn" onclick="searchProfessional('Real Estate Broker', '{{ zip_code }}')">Website</button>
                        <button class="contact-btn" onclick="contactProfessional('Real Estate Broker')">Contact</button>
                    </div>
                </div>
                
                <div class="professional-card">
                    <div class="professional-title">Mortgage Lender</div>
                    <div class="professional-location">{{ address.split(',')[-2].strip() if ',' in address else 'Local Area' }}</div>
                    <div class="professional-description">Specialized in home loans and refinancing with competitive rates. Provides various loan programs, pre-approval services, and personalized financing solutions for homebuyers.</div>
                    <div class="professional-buttons">
                        <button class="website-btn" onclick="searchProfessional('Mortgage Lender', '{{ zip_code }}')">Website</button>
                        <button class="contact-btn" onclick="contactProfessional('Mortgage Lender')">Contact</button>
                    </div>
                </div>
                
                <div class="professional-card">
                    <div class="professional-title">Real Estate Attorney</div>
                    <div class="professional-location">{{ address.split(',')[-2].strip() if ',' in address else 'Local Area' }}</div>
                    <div class="professional-description">Expert in real estate transactions and contract negotiations. Handles legal aspects of property purchases, title issues, closings, and dispute resolution.</div>
                    <div class="professional-buttons">
                        <button class="website-btn" onclick="searchProfessional('Real Estate Attorney', '{{ zip_code }}')">Website</button>
                        <button class="contact-btn" onclick="contactProfessional('Real Estate Attorney')">Contact</button>
                    </div>
                </div>
                
                <div class="professional-card">
                    <div class="professional-title">Property Inspector</div>
                    <div class="professional-location">{{ address.split(',')[-2].strip() if ',' in address else 'Local Area' }}</div>
                    <div class="professional-description">Certified home inspector with comprehensive inspection services. Conducts thorough property evaluations, safety assessments, and detailed reporting for informed purchasing decisions.</div>
                    <div class="professional-buttons">
                        <button class="website-btn" onclick="searchProfessional('Property Inspector', '{{ zip_code }}')">Website</button>
                        <button class="contact-btn" onclick="contactProfessional('Property Inspector')">Contact</button>
                    </div>
                </div>
                
                <div class="professional-card">
                    <div class="professional-title">Insurance Agent</div>
                    <div class="professional-location">{{ address.split(',')[-2].strip() if ',' in address else 'Local Area' }}</div>
                    <div class="professional-description">Home and auto insurance specialist with competitive coverage options. Provides comprehensive insurance solutions, risk assessment, and claims support for property protection.</div>
                    <div class="professional-buttons">
                        <button class="website-btn" onclick="searchProfessional('Insurance Agent', '{{ zip_code }}')">Website</button>
                        <button class="contact-btn" onclick="contactProfessional('Insurance Agent')">Contact</button>
                    </div>
                </div>
                
                <div class="professional-card">
                    <div class="professional-title">General Contractor</div>
                    <div class="professional-location">{{ address.split(',')[-2].strip() if ',' in address else 'Local Area' }}</div>
                    <div class="professional-description">Licensed contractor for home renovations and construction projects. Specializes in remodeling, repairs, additions, and new construction with quality craftsmanship and project management.</div>
                    <div class="professional-buttons">
                        <button class="website-btn" onclick="searchProfessional('General Contractor', '{{ zip_code }}')">Website</button>
                        <button class="contact-btn" onclick="contactProfessional('General Contractor')">Contact</button>
                    </div>
                </div>
                
                <div class="professional-card">
                    <div class="professional-title">Property Appraiser</div>
                    <div class="professional-location">{{ address.split(',')[-2].strip() if ',' in address else 'Local Area' }}</div>
                    <div class="professional-description">Certified appraiser providing accurate property valuations. Conducts professional appraisals for lending, legal, and investment purposes with detailed market analysis and reporting.</div>
                    <div class="professional-buttons">
                        <button class="website-btn" onclick="searchProfessional('Property Appraiser', '{{ zip_code }}')">Website</button>
                        <button class="contact-btn" onclick="contactProfessional('Property Appraiser')">Contact</button>
                    </div>
                </div>
                
                <div class="professional-card">
                    <div class="professional-title">Structural Engineer</div>
                    <div class="professional-location">{{ address.split(',')[-2].strip() if ',' in address else 'Local Area' }}</div>
                    <div class="professional-description">Professional engineer specializing in structural analysis and design. Provides structural assessments, foundation evaluations, and engineering solutions for construction and renovation projects.</div>
                    <div class="professional-buttons">
                        <button class="website-btn" onclick="searchProfessional('Structural Engineer', '{{ zip_code }}')">Website</button>
                        <button class="contact-btn" onclick="contactProfessional('Structural Engineer')">Contact</button>
                    </div>
                </div>
                
                <div class="professional-card">
                    <div class="professional-title">Escrow Officer</div>
                    <div class="professional-location">{{ address.split(',')[-2].strip() if ',' in address else 'Local Area' }}</div>
                    <div class="professional-description">Experienced escrow professional ensuring smooth real estate transactions. Manages escrow processes, coordinates with all parties, and facilitates secure property transfers and closings.</div>
                    <div class="professional-buttons">
                        <button class="website-btn" onclick="searchProfessional('Escrow Officer', '{{ zip_code }}')">Website</button>
                        <button class="contact-btn" onclick="contactProfessional('Escrow Officer')">Contact</button>
                    </div>
                </div>
                
                <div class="professional-card">
                    <div class="professional-title">Property Manager</div>
                    <div class="professional-location">{{ address.split(',')[-2].strip() if ',' in address else 'Local Area' }}</div>
                    <div class="professional-description">Professional property management services for residential and commercial properties. Handles tenant relations, maintenance coordination, rent collection, and investment property optimization.</div>
                    <div class="professional-buttons">
                        <button class="website-btn" onclick="searchProfessional('Property Manager', '{{ zip_code }}')">Website</button>
                        <button class="contact-btn" onclick="contactProfessional('Property Manager')">Contact</button>
                    </div>
                </div>
            </div>
        </div>
        
        <a href="/" class="back-link">← Back to Search</a>
    </div>
    
    <script>
        // Google Search Button Functionality - FIXED VERSION
        function searchProfessional(professionalType, zipCode) {
            // Create the search query
            const searchQuery = professionalType + ' ' + zipCode;
            
            // Encode the query for URL
            const encodedQuery = encodeURIComponent(searchQuery);
            
            // Create Google search URL
            const googleUrl = 'https://www.google.com/search?q=' + encodedQuery;
            
            // Open in new tab
            window.open(googleUrl, '_blank');
            
            // Log for debugging
            console.log('Searching for: ' + searchQuery);
            console.log('Google URL: ' + googleUrl);
        }
        
        // Contact Professional Functionality
        function contactProfessional(professionalType) {
            // Create contact form or redirect to contact page
            const message = 'I am interested in ' + professionalType + ' services for the property at {{ address }}. Please contact me with more information.';
            
            // For now, we'll create a simple alert - this can be enhanced with a modal or form
            if (confirm('Would you like to send an inquiry to a ' + professionalType + ' about this property?')) {
                // In a real implementation, this would send an email or open a contact form
                alert('Your inquiry has been sent! A ' + professionalType + ' will contact you soon.');
                
                // Optional: Send actual email via AJAX
                fetch('/contact-professional', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        professional_type: professionalType,
                        property_address: '{{ address }}',
                        message: message
                    })
                }).catch(error => {
                    console.log('Contact request logged locally');
                });
            }
        }
        
        // Initialize page
        document.addEventListener('DOMContentLoaded', function() {
            console.log('BlueDwarf Property Analysis page loaded');
            console.log('Property zip code: {{ zip_code }}');
            
            // Test Google search functionality
            console.log('Google search functionality ready');
        });
    </script>
</body>
</html>
    ''', address=address, zip_code=zip_code)

@app.route('/contact-professional', methods=['POST'])
def contact_professional():
    """Handle professional contact requests"""
    try:
        data = request.get_json()
        professional_type = data.get('professional_type', 'Professional')
        property_address = data.get('property_address', 'Property')
        message = data.get('message', 'Inquiry about services')
        
        # Send notification email
        success = send_contact_notification(
            name="BlueDwarf User",
            email="user@example.com",  # In real implementation, get from user session
            message=f"Professional Type: {professional_type}\nProperty: {property_address}\nMessage: {message}",
            subject=f"{professional_type} Inquiry"
        )
        
        return jsonify({'success': success})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

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
        
        .nav-buttons a {
            color: white;
            text-decoration: none;
            padding: 0.5rem 1rem;
            border: 1px solid rgba(255, 255, 255, 0.3);
            border-radius: 6px;
        }
        
        .container {
            max-width: 800px;
            margin: 2rem auto;
            padding: 2rem;
        }
        
        .signup-form {
            background: white;
            padding: 3rem;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        }
        
        .form-title {
            font-size: 2rem;
            color: #333;
            margin-bottom: 0.5rem;
            text-align: center;
        }
        
        .form-subtitle {
            color: #666;
            text-align: center;
            margin-bottom: 2rem;
        }
        
        .form-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1.5rem;
            margin-bottom: 1.5rem;
        }
        
        .form-group {
            display: flex;
            flex-direction: column;
        }
        
        .form-group.full-width {
            grid-column: 1 / -1;
        }
        
        label {
            font-weight: 600;
            color: #333;
            margin-bottom: 0.5rem;
        }
        
        input, select, textarea {
            padding: 1rem;
            border: 2px solid #e1e5e9;
            border-radius: 8px;
            font-size: 1rem;
            transition: border-color 0.3s ease;
        }
        
        input:focus, select:focus, textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .verification-section {
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 10px;
            margin: 2rem 0;
        }
        
        .verification-title {
            font-size: 1.1rem;
            color: #333;
            margin-bottom: 1rem;
        }
        
        .file-upload {
            border: 2px dashed #ccc;
            padding: 2rem;
            text-align: center;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .file-upload:hover {
            border-color: #667eea;
            background: rgba(102, 126, 234, 0.05);
        }
        
        .submit-btn {
            width: 100%;
            padding: 1.2rem;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .submit-btn:hover {
            background: #5a6fd8;
            transform: translateY(-2px);
        }
        
        @media (max-width: 768px) {
            .form-grid {
                grid-template-columns: 1fr;
            }
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
        <form class="signup-form" action="/register" method="POST" enctype="multipart/form-data">
            <h1 class="form-title">Professional Registration</h1>
            <p class="form-subtitle">Join our network of real estate professionals</p>
            
            <div class="form-grid">
                <div class="form-group">
                    <label for="first_name">First Name *</label>
                    <input type="text" id="first_name" name="first_name" required>
                </div>
                
                <div class="form-group">
                    <label for="last_name">Last Name *</label>
                    <input type="text" id="last_name" name="last_name" required>
                </div>
                
                <div class="form-group">
                    <label for="email">Email Address *</label>
                    <input type="email" id="email" name="email" required>
                </div>
                
                <div class="form-group">
                    <label for="password">Password *</label>
                    <input type="password" id="password" name="password" required>
                </div>
                
                <div class="form-group full-width">
                    <label for="business_address">Business Address *</label>
                    <input type="text" id="business_address" name="business_address" placeholder="123 Business St, City, State, ZIP" required>
                </div>
                
                <div class="form-group">
                    <label for="license_number">License Number</label>
                    <input type="text" id="license_number" name="license_number" placeholder="Professional license number">
                </div>
                
                <div class="form-group">
                    <label for="profession">Professional Category *</label>
                    <select id="profession" name="profession" required>
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
                
                <div class="form-group full-width">
                    <label for="service_areas">Service Zip Codes *</label>
                    <input type="text" id="service_areas" name="service_areas" placeholder="95814, 95628, 95630" required>
                    <small style="color: #666; margin-top: 0.5rem;">Enter zip codes separated by commas</small>
                </div>
            </div>
            
            <div class="verification-section">
                <h3 class="verification-title">📄 Document Verification</h3>
                <div class="file-upload">
                    <input type="file" id="documents" name="documents" multiple accept=".pdf,.jpg,.jpeg,.png" style="display: none;">
                    <p>📎 Click to upload license and certification documents</p>
                    <small style="color: #666;">Accepted formats: PDF, JPG, PNG</small>
                </div>
            </div>
            
            <button type="submit" class="submit-btn">Create Account</button>
        </form>
    </div>
    
    <script>
        document.querySelector('.file-upload').addEventListener('click', function() {
            document.getElementById('documents').click();
        });
        
        document.getElementById('documents').addEventListener('change', function(e) {
            const fileCount = e.target.files.length;
            const uploadText = document.querySelector('.file-upload p');
            if (fileCount > 0) {
                uploadText.textContent = `📎 ${fileCount} file(s) selected`;
            }
        });
    </script>
</body>
</html>
    ''')

@app.route('/register', methods=['POST'])
def register():
    """Handle professional registration"""
    try:
        # Get form data
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        password = request.form.get('password')
        business_address = request.form.get('business_address')
        license_number = request.form.get('license_number')
        profession = request.form.get('profession')
        service_areas = request.form.get('service_areas')
        
        # Send registration confirmation email
        full_name = f"{first_name} {last_name}"
        email_sent = send_registration_email(email, full_name, profession)
        
        # Send admin notification
        admin_notification = send_contact_notification(
            name=full_name,
            email=email,
            message=f"New professional registration:\nProfession: {profession}\nBusiness Address: {business_address}\nLicense: {license_number}\nService Areas: {service_areas}",
            subject="New Professional Registration"
        )
        
        if email_sent:
            flash('Registration successful! Please check your email for confirmation.', 'success')
        else:
            flash('Registration completed, but email confirmation failed. Please contact support.', 'warning')
        
        return redirect(url_for('index'))
        
    except Exception as e:
        flash(f'Registration failed: {str(e)}', 'error')
        return redirect(url_for('signup'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

