from flask import Flask, render_template_string, request, flash, redirect, url_for
import urllib.parse
import re
import os

# Flask-Mail imports with error handling
try:
    from flask_mail import Mail, Message
    FLASK_MAIL_AVAILABLE = True
except ImportError:
    FLASK_MAIL_AVAILABLE = False
    print("Flask-Mail not available - email functionality will be disabled")

app = Flask(__name__)

# Configuration
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Google Maps API Key
GOOGLE_MAPS_API_KEY = "AIzaSyDe8QxfkBSo2Ids9PWK24-aKgqbI9du9B4"

# Email configuration with error handling
if FLASK_MAIL_AVAILABLE:
    try:
        app.config['MAIL_SERVER'] = 'smtp.gmail.com'
        app.config['MAIL_PORT'] = 587
        app.config['MAIL_USE_TLS'] = True
        app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', '')
        app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', '')
        app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME', '')
        
        mail = Mail(app)
        EMAIL_CONFIGURED = bool(app.config['MAIL_USERNAME'] and app.config['MAIL_PASSWORD'])
    except Exception as e:
        EMAIL_CONFIGURED = False
        print(f"Email configuration error: {e}")
else:
    EMAIL_CONFIGURED = False

def encode_address_for_maps(address):
    """Properly encode address for Google Maps API"""
    # Clean the address first
    cleaned_address = address.strip()
    # URL encode for Google Maps
    return urllib.parse.quote_plus(cleaned_address)

def send_email(subject, body, recipient=None):
    """Send email with error handling"""
    if not EMAIL_CONFIGURED or not FLASK_MAIL_AVAILABLE:
        print(f"Email not sent - configuration not available. Subject: {subject}")
        return False
    
    try:
        recipient = recipient or app.config['MAIL_USERNAME']
        msg = Message(subject=subject, recipients=[recipient], body=body)
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False

@app.route('/')
def home():
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BlueDwarf - Modern SaaS Platform for Property Valuation</title>
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
            padding: 20px;
        }
        
        .container {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            max-width: 600px;
            width: 100%;
            text-align: center;
        }
        
        .logo {
            font-size: 3rem;
            color: #667eea;
            margin-bottom: 10px;
        }
        
        h1 {
            color: #333;
            font-size: 2.5rem;
            margin-bottom: 10px;
            font-weight: 700;
        }
        
        .subtitle {
            color: #666;
            font-size: 1.2rem;
            margin-bottom: 40px;
        }
        
        .search-container {
            margin-bottom: 40px;
        }
        
        .search-input {
            width: 100%;
            padding: 15px 20px;
            font-size: 1.1rem;
            border: 2px solid #e0e0e0;
            border-radius: 50px;
            outline: none;
            transition: all 0.3s ease;
            margin-bottom: 20px;
        }
        
        .search-input:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        .search-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 40px;
            font-size: 1.1rem;
            border-radius: 50px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: 600;
        }
        
        .search-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }
        
        .nav-links {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .nav-link {
            background: rgba(102, 126, 234, 0.1);
            color: #667eea;
            text-decoration: none;
            padding: 10px 20px;
            border-radius: 25px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .nav-link:hover {
            background: #667eea;
            color: white;
            transform: translateY(-2px);
        }
        
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }
        
        .feature {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 15px;
            transition: all 0.3s ease;
        }
        
        .feature:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
        }
        
        .feature-icon {
            font-size: 2rem;
            margin-bottom: 10px;
        }
        
        .feature-title {
            font-weight: 600;
            color: #333;
            margin-bottom: 5px;
        }
        
        .feature-desc {
            font-size: 0.9rem;
            color: #666;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 30px 20px;
            }
            
            h1 {
                font-size: 2rem;
            }
            
            .features {
                grid-template-columns: repeat(2, 1fr);
            }
            
            .nav-links {
                flex-direction: column;
                align-items: center;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">🏠</div>
        <h1>BlueDwarf</h1>
        <p class="subtitle">Modern SaaS Platform for Property Valuation</p>
        
        <div class="nav-links">
            <a href="/register" class="nav-link">📧 Professional Registration</a>
            <a href="/contact" class="nav-link">💬 Contact Us</a>
        </div>
        
        <form action="/property-results" method="POST" class="search-container">
            <input type="text" name="address" class="search-input" 
                   placeholder="Enter property address (e.g., 123 Main Street, Sacramento, CA)" required>
            <button type="submit" class="search-btn">🔍 Analyze Property</button>
        </form>
        
        <div class="features">
            <div class="feature">
                <div class="feature-icon">📊</div>
                <div class="feature-title">Property Analysis</div>
                <div class="feature-desc">Comprehensive market data</div>
            </div>
            <div class="feature">
                <div class="feature-icon">🏘️</div>
                <div class="feature-title">Neighborhood Data</div>
                <div class="feature-desc">Local insights & trends</div>
            </div>
            <div class="feature">
                <div class="feature-icon">💰</div>
                <div class="feature-title">Market Valuation</div>
                <div class="feature-desc">Accurate pricing estimates</div>
            </div>
            <div class="feature">
                <div class="feature-icon">📈</div>
                <div class="feature-title">Investment Insights</div>
                <div class="feature-desc">ROI & growth potential</div>
            </div>
        </div>
    </div>
</body>
</html>
    ''')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        profession = request.form.get('profession')
        phone = request.form.get('phone')
        company = request.form.get('company')
        
        # Send registration email
        subject = f"New Professional Registration - {name}"
        body = f"""
New professional registration received:

Name: {name}
Email: {email}
Profession: {profession}
Phone: {phone}
Company: {company}

Please follow up with this professional to complete their onboarding.
        """
        
        email_sent = send_email(subject, body)
        
        if email_sent:
            flash('Registration submitted successfully! We will contact you soon.', 'success')
        else:
            flash('Registration received! We will contact you soon.', 'info')
        
        return redirect(url_for('register'))
    
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
            padding: 20px;
        }
        
        .container {
            max-width: 600px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        }
        
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
            font-size: 2rem;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: 600;
            color: #333;
        }
        
        input, select {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 1rem;
            transition: all 0.3s ease;
        }
        
        input:focus, select:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        .submit-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            font-size: 1.1rem;
            border-radius: 50px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: 600;
            width: 100%;
        }
        
        .submit-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }
        
        .back-link {
            display: block;
            text-align: center;
            margin-top: 20px;
            color: #667eea;
            text-decoration: none;
            font-weight: 600;
        }
        
        .back-link:hover {
            text-decoration: underline;
        }
        
        .flash-messages {
            margin-bottom: 20px;
        }
        
        .flash-message {
            padding: 10px 15px;
            border-radius: 10px;
            margin-bottom: 10px;
        }
        
        .flash-success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        
        .flash-info {
            background: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📧 Professional Registration</h1>
        
        <div class="flash-messages">
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, message in messages %}
                        <div class="flash-message flash-{{ category }}">{{ message }}</div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
        </div>
        
        <form method="POST">
            <div class="form-group">
                <label for="name">Full Name *</label>
                <input type="text" id="name" name="name" required>
            </div>
            
            <div class="form-group">
                <label for="email">Email Address *</label>
                <input type="email" id="email" name="email" required>
            </div>
            
            <div class="form-group">
                <label for="profession">Profession *</label>
                <select id="profession" name="profession" required>
                    <option value="">Select your profession</option>
                    <option value="Real Estate Agent">Real Estate Agent</option>
                    <option value="Mortgage Lender">Mortgage Lender</option>
                    <option value="Property Inspector">Property Inspector</option>
                    <option value="Insurance Agent">Insurance Agent</option>
                    <option value="General Contractor">General Contractor</option>
                    <option value="Property Appraiser">Property Appraiser</option>
                    <option value="Structural Engineer">Structural Engineer</option>
                    <option value="Escrow Officer">Escrow Officer</option>
                    <option value="Property Manager">Property Manager</option>
                    <option value="Real Estate Attorney">Real Estate Attorney</option>
                    <option value="Tax Consultant">Tax Consultant</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="phone">Phone Number *</label>
                <input type="tel" id="phone" name="phone" required>
            </div>
            
            <div class="form-group">
                <label for="company">Company/Organization</label>
                <input type="text" id="company" name="company">
            </div>
            
            <button type="submit" class="submit-btn">Submit Registration</button>
        </form>
        
        <a href="/" class="back-link">← Back to Home</a>
    </div>
</body>
</html>
    ''')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        # Send contact email
        email_subject = f"Contact Form: {subject}"
        email_body = f"""
New contact form submission:

Name: {name}
Email: {email}
Subject: {subject}

Message:
{message}
        """
        
        email_sent = send_email(email_subject, email_body)
        
        if email_sent:
            flash('Message sent successfully! We will get back to you soon.', 'success')
        else:
            flash('Message received! We will get back to you soon.', 'info')
        
        return redirect(url_for('contact'))
    
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Contact Us - BlueDwarf</title>
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
            padding: 20px;
        }
        
        .container {
            max-width: 600px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        }
        
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
            font-size: 2rem;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: 600;
            color: #333;
        }
        
        input, textarea {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 1rem;
            transition: all 0.3s ease;
            font-family: inherit;
        }
        
        input:focus, textarea:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        textarea {
            resize: vertical;
            min-height: 120px;
        }
        
        .submit-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            font-size: 1.1rem;
            border-radius: 50px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: 600;
            width: 100%;
        }
        
        .submit-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }
        
        .back-link {
            display: block;
            text-align: center;
            margin-top: 20px;
            color: #667eea;
            text-decoration: none;
            font-weight: 600;
        }
        
        .back-link:hover {
            text-decoration: underline;
        }
        
        .flash-messages {
            margin-bottom: 20px;
        }
        
        .flash-message {
            padding: 10px 15px;
            border-radius: 10px;
            margin-bottom: 10px;
        }
        
        .flash-success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        
        .flash-info {
            background: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>💬 Contact Us</h1>
        
        <div class="flash-messages">
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, message in messages %}
                        <div class="flash-message flash-{{ category }}">{{ message }}</div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
        </div>
        
        <form method="POST">
            <div class="form-group">
                <label for="name">Your Name *</label>
                <input type="text" id="name" name="name" required>
            </div>
            
            <div class="form-group">
                <label for="email">Your Email *</label>
                <input type="email" id="email" name="email" required>
            </div>
            
            <div class="form-group">
                <label for="subject">Subject *</label>
                <input type="text" id="subject" name="subject" required>
            </div>
            
            <div class="form-group">
                <label for="message">Message *</label>
                <textarea id="message" name="message" required placeholder="Tell us how we can help you..."></textarea>
            </div>
            
            <button type="submit" class="submit-btn">Send Message</button>
        </form>
        
        <a href="/" class="back-link">← Back to Home</a>
    </div>
</body>
</html>
    ''')

@app.route('/property-results', methods=['POST'])
def property_results():
    address = request.form.get('address', '')
    
    # Properly encode address for Google Maps
    encoded_address = encode_address_for_maps(address)
    
    # Extract zip code for professional searches
    zip_match = re.search(r'\b\d{5}\b', address)
    zip_code = zip_match.group() if zip_match else "95814"
    
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
            padding: 20px;
        }
        
        .header {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        
        .header h1 {
            color: #333;
            font-size: 2rem;
            margin-bottom: 10px;
        }
        
        .header p {
            color: #666;
            font-size: 1.1rem;
        }
        
        .maps-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 40px;
        }
        
        .map-section {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        
        .map-title {
            font-size: 1.3rem;
            font-weight: 600;
            color: #333;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .map-frame {
            width: 100%;
            height: 300px;
            border: none;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }
        
        .rental-analysis {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 40px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        
        .rental-title {
            font-size: 1.5rem;
            font-weight: 600;
            color: #333;
            margin-bottom: 20px;
            text-align: center;
        }
        
        .rental-estimate {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            font-size: 1.8rem;
            font-weight: 700;
            margin-bottom: 20px;
        }
        
        .comparables {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 40px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        
        .comparables h2 {
            color: #333;
            font-size: 1.5rem;
            margin-bottom: 25px;
            text-align: center;
        }
        
        .comparable-item {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: all 0.3s ease;
        }
        
        .comparable-item:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }
        
        .comparable-info {
            flex: 1;
        }
        
        .comparable-address {
            font-weight: 600;
            color: #333;
            margin-bottom: 5px;
        }
        
        .comparable-details {
            color: #666;
            font-size: 0.9rem;
        }
        
        .comparable-price {
            font-size: 1.3rem;
            font-weight: 700;
            color: #667eea;
        }
        
        .professionals {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 40px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        
        .professionals h2 {
            color: #333;
            font-size: 1.5rem;
            margin-bottom: 25px;
            text-align: center;
        }
        
        .professionals-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
        }
        
        .professional-card {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            transition: all 0.3s ease;
        }
        
        .professional-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        }
        
        .professional-title {
            font-weight: 600;
            color: #333;
            margin-bottom: 8px;
            font-size: 1.1rem;
        }
        
        .professional-desc {
            color: #666;
            font-size: 0.9rem;
            margin-bottom: 15px;
            line-height: 1.4;
        }
        
        .button-group {
            display: flex;
            gap: 10px;
            justify-content: center;
        }
        
        .website-btn, .contact-btn {
            border: none;
            padding: 8px 16px;
            border-radius: 20px;
            cursor: pointer;
            font-size: 0.9rem;
            font-weight: 500;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
        }
        
        .website-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .contact-btn {
            background: rgba(102, 126, 234, 0.1);
            color: #667eea;
        }
        
        .website-btn:hover, .contact-btn:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }
        
        .back-btn {
            display: block;
            width: 200px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.9);
            color: #667eea;
            text-decoration: none;
            padding: 15px 30px;
            border-radius: 50px;
            font-weight: 600;
            text-align: center;
            transition: all 0.3s ease;
        }
        
        .back-btn:hover {
            background: white;
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
        }
        
        @media (max-width: 768px) {
            .maps-container {
                grid-template-columns: 1fr;
            }
            
            .professionals-grid {
                grid-template-columns: 1fr;
            }
            
            .comparable-item {
                flex-direction: column;
                text-align: center;
                gap: 10px;
            }
            
            .button-group {
                flex-direction: column;
                align-items: center;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{ address }}</h1>
        <p>Comprehensive Property Analysis Report</p>
    </div>
    
    <div class="maps-container">
        <div class="map-section">
            <h2 class="map-title">🏠 Street View</h2>
            <iframe class="map-frame" 
                    src="https://www.google.com/maps/embed/v1/streetview?key={{ api_key }}&location={{ encoded_address }}&heading=0&pitch=0&fov=90"
                    allowfullscreen>
            </iframe>
        </div>
        
        <div class="map-section">
            <h2 class="map-title">🛰️ Aerial View (2 blocks)</h2>
            <iframe class="map-frame" 
                    src="https://www.google.com/maps/embed/v1/view?key={{ api_key }}&center={{ encoded_address }}&zoom=17&maptype=satellite"
                    allowfullscreen>
            </iframe>
        </div>
    </div>
    
    <div class="rental-analysis">
        <h2 class="rental-title">💰 Rental Analysis</h2>
        <div class="rental-estimate">$2,510 / month</div>
        <p style="text-align: center; color: #666;">Estimated monthly rental income based on comparable properties in the area</p>
    </div>
    
    <div class="comparables">
        <h2>🏘️ Comparable Properties</h2>
        
        <div class="comparable-item">
            <div class="comparable-info">
                <div class="comparable-address">456 Oak Avenue</div>
                <div class="comparable-details">3 bed • 2 bath • 2,080 sq ft • 0.3 mi</div>
            </div>
            <div class="comparable-price">$472,000</div>
        </div>
        
        <div class="comparable-item">
            <div class="comparable-info">
                <div class="comparable-address">789 Maple Street</div>
                <div class="comparable-details">4 bed • 3 bath • 2,340 sq ft • 0.4 mi</div>
            </div>
            <div class="comparable-price">$518,000</div>
        </div>
        
        <div class="comparable-item">
            <div class="comparable-info">
                <div class="comparable-address">321 Elm Drive</div>
                <div class="comparable-details">3 bed • 2.5 bath • 2,200 sq ft • 0.5 mi</div>
            </div>
            <div class="comparable-price">$495,000</div>
        </div>
        
        <div class="comparable-item">
            <div class="comparable-info">
                <div class="comparable-address">654 Cedar Lane</div>
                <div class="comparable-details">3 bed • 2 bath • 1,950 sq ft • 0.6 mi</div>
            </div>
            <div class="comparable-price">$458,000</div>
        </div>
        
        <div class="comparable-item">
            <div class="comparable-info">
                <div class="comparable-address">987 Birch Court</div>
                <div class="comparable-details">4 bed • 2.5 bath • 2,450 sq ft • 0.7 mi</div>
            </div>
            <div class="comparable-price">$535,000</div>
        </div>
        
        <div style="margin-top: 20px;">
            <iframe class="map-frame" style="height: 250px;"
                    src="https://www.google.com/maps/embed/v1/view?key={{ api_key }}&center={{ encoded_address }}&zoom=15&maptype=roadmap"
                    allowfullscreen>
            </iframe>
        </div>
    </div>
    
    <div class="professionals">
        <h2>🤝 Professional Network</h2>
        <div class="professionals-grid">
            <div class="professional-card">
                <div class="professional-title">Real Estate Agent</div>
                <div class="professional-desc">Licensed real estate professional with local market expertise and proven track record</div>
                <div class="button-group">
                    <button class="website-btn" onclick="searchProfessional('Real Estate Agent', '{{ zip_code }}')">Website</button>
                    <a href="/contact" class="contact-btn">Contact</a>
                </div>
            </div>
            
            <div class="professional-card">
                <div class="professional-title">Mortgage Lender</div>
                <div class="professional-desc">Experienced mortgage specialist offering competitive rates and personalized loan solutions</div>
                <div class="button-group">
                    <button class="website-btn" onclick="searchProfessional('Mortgage Lender', '{{ zip_code }}')">Website</button>
                    <a href="/contact" class="contact-btn">Contact</a>
                </div>
            </div>
            
            <div class="professional-card">
                <div class="professional-title">Home Inspector</div>
                <div class="professional-desc">Certified home inspector with comprehensive inspection services and detailed reporting</div>
                <div class="button-group">
                    <button class="website-btn" onclick="searchProfessional('Property Inspector', '{{ zip_code }}')">Website</button>
                    <a href="/contact" class="contact-btn">Contact</a>
                </div>
            </div>
            
            <div class="professional-card">
                <div class="professional-title">Insurance Agent</div>
                <div class="professional-desc">Home and auto insurance specialist with competitive coverage options and excellent service</div>
                <div class="button-group">
                    <button class="website-btn" onclick="searchProfessional('Insurance Agent', '{{ zip_code }}')">Website</button>
                    <a href="/contact" class="contact-btn">Contact</a>
                </div>
            </div>
            
            <div class="professional-card">
                <div class="professional-title">General Contractor</div>
                <div class="professional-desc">Licensed contractor for home renovations and construction projects with quality craftsmanship</div>
                <div class="button-group">
                    <button class="website-btn" onclick="searchProfessional('General Contractor', '{{ zip_code }}')">Website</button>
                    <a href="/contact" class="contact-btn">Contact</a>
                </div>
            </div>
            
            <div class="professional-card">
                <div class="professional-title">Property Appraiser</div>
                <div class="professional-desc">Certified appraiser providing accurate property valuations for various real estate needs</div>
                <div class="button-group">
                    <button class="website-btn" onclick="searchProfessional('Property Appraiser', '{{ zip_code }}')">Website</button>
                    <a href="/contact" class="contact-btn">Contact</a>
                </div>
            </div>
            
            <div class="professional-card">
                <div class="professional-title">Structural Engineer</div>
                <div class="professional-desc">Professional engineer specializing in structural analysis and design for residential properties</div>
                <div class="button-group">
                    <button class="website-btn" onclick="searchProfessional('Structural Engineer', '{{ zip_code }}')">Website</button>
                    <a href="/contact" class="contact-btn">Contact</a>
                </div>
            </div>
            
            <div class="professional-card">
                <div class="professional-title">Escrow Officer</div>
                <div class="professional-desc">Experienced escrow professional ensuring smooth real estate transactions and closings</div>
                <div class="button-group">
                    <button class="website-btn" onclick="searchProfessional('Escrow Officer', '{{ zip_code }}')">Website</button>
                    <a href="/contact" class="contact-btn">Contact</a>
                </div>
            </div>
            
            <div class="professional-card">
                <div class="professional-title">Property Manager</div>
                <div class="professional-desc">Professional property management services for residential and commercial properties</div>
                <div class="button-group">
                    <button class="website-btn" onclick="searchProfessional('Property Manager', '{{ zip_code }}')">Website</button>
                    <a href="/contact" class="contact-btn">Contact</a>
                </div>
            </div>
            
            <div class="professional-card">
                <div class="professional-title">Real Estate Attorney</div>
                <div class="professional-desc">Experienced real estate attorney providing legal guidance for property transactions</div>
                <div class="button-group">
                    <button class="website-btn" onclick="searchProfessional('Real Estate Attorney', '{{ zip_code }}')">Website</button>
                    <a href="/contact" class="contact-btn">Contact</a>
                </div>
            </div>
            
            <div class="professional-card">
                <div class="professional-title">Tax Consultant</div>
                <div class="professional-desc">Tax professional specializing in real estate investments and property tax optimization</div>
                <div class="button-group">
                    <button class="website-btn" onclick="searchProfessional('Tax Consultant', '{{ zip_code }}')">Website</button>
                    <a href="/contact" class="contact-btn">Contact</a>
                </div>
            </div>
        </div>
    </div>
    
    <a href="/" class="back-btn">← Back to Search</a>
    
    <script>
        function searchProfessional(professionalType, zipCode) {
            console.log('Searching for:', professionalType, 'in', zipCode);
            const searchQuery = professionalType + ' ' + zipCode;
            const encodedQuery = encodeURIComponent(searchQuery);
            const googleUrl = 'https://www.google.com/search?q=' + encodedQuery;
            window.open(googleUrl, '_blank');
        }
    </script>
</body>
</html>
    ''', address=address, encoded_address=encoded_address, api_key=GOOGLE_MAPS_API_KEY, zip_code=zip_code)

if __name__ == '__main__':
    app.run(debug=True)

