from flask import Flask, render_template_string, request, redirect, url_for, session, jsonify, flash
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
                        <h3 style="color: #667eea; margin-top: 0;">What's Next?</h3>
                        <ul style="color: #666; line-height: 1.8;">
                            <li>Complete your professional profile</li>
                            <li>Upload your license verification documents</li>
                            <li>Start receiving property analysis leads</li>
                            <li>Access our comprehensive property database</li>
                        </ul>
                    </div>
                    
                    <div style="text-align: center; margin: 2rem 0;">
                        <a href="https://bluedwarf-platform-7cae4752497f.herokuapp.com/login" 
                           style="background: #667eea; color: white; padding: 1rem 2rem; text-decoration: none; border-radius: 8px; display: inline-block;">
                            Login to Your Account
                        </a>
                    </div>
                    
                    <p style="color: #666; font-size: 0.9rem;">
                        If you have any questions, please contact us at 
                        <a href="mailto:support@bluedwarf.io" style="color: #667eea;">support@bluedwarf.io</a>
                    </p>
                </div>
                
                <div style="background: #f8f9fa; padding: 1rem; text-align: center; color: #666; font-size: 0.8rem;">
                    © 2025 Elite Marketing Lab LLC. All rights reserved.
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

def send_contact_notification(name, email, message, property_address=None):
    """Send contact form notification to admin"""
    try:
        subject = f"New Contact Form Submission - {name}"
        if property_address:
            subject += f" (Property: {property_address})"
            
        msg = Message(
            subject=subject,
            recipients=['support@bluedwarf.io'],
            html=f'''
            <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background: #667eea; padding: 1.5rem; text-align: center;">
                    <h1 style="color: white; margin: 0;">📧 New Contact Form Submission</h1>
                </div>
                
                <div style="padding: 2rem; background: white;">
                    <h2 style="color: #333;">Contact Details</h2>
                    
                    <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 8px; margin: 1rem 0;">
                        <p><strong>Name:</strong> {name}</p>
                        <p><strong>Email:</strong> {email}</p>
                        {f"<p><strong>Property Address:</strong> {property_address}</p>" if property_address else ""}
                    </div>
                    
                    <h3 style="color: #333;">Message:</h3>
                    <div style="background: white; border: 1px solid #ddd; padding: 1.5rem; border-radius: 8px;">
                        {message.replace('\n', '<br>')}
                    </div>
                    
                    <div style="margin-top: 2rem; padding: 1rem; background: #e3f2fd; border-radius: 8px;">
                        <p style="margin: 0; color: #1976d2;">
                            <strong>Action Required:</strong> Please respond to this inquiry within 24 hours.
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

def send_professional_inquiry(professional_type, property_address, client_name, client_email, client_message):
    """Send professional inquiry notification"""
    try:
        msg = Message(
            subject=f'New {professional_type} Inquiry - {property_address}',
            recipients=['support@bluedwarf.io'],
            html=f'''
            <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background: #667eea; padding: 1.5rem; text-align: center;">
                    <h1 style="color: white; margin: 0;">🏠 New Professional Inquiry</h1>
                </div>
                
                <div style="padding: 2rem; background: white;">
                    <h2 style="color: #333;">Professional Service Request</h2>
                    
                    <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 8px; margin: 1rem 0;">
                        <p><strong>Service Type:</strong> {professional_type}</p>
                        <p><strong>Property Address:</strong> {property_address}</p>
                        <p><strong>Client Name:</strong> {client_name}</p>
                        <p><strong>Client Email:</strong> {client_email}</p>
                    </div>
                    
                    <h3 style="color: #333;">Client Message:</h3>
                    <div style="background: white; border: 1px solid #ddd; padding: 1.5rem; border-radius: 8px;">
                        {client_message.replace('\n', '<br>')}
                    </div>
                    
                    <div style="margin-top: 2rem; padding: 1rem; background: #e8f5e8; border-radius: 8px;">
                        <p style="margin: 0; color: #2e7d32;">
                            <strong>Next Steps:</strong> Forward this inquiry to qualified {professional_type.lower()}s in the area.
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
        print(f"Professional inquiry failed: {e}")
        return False

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
            background: #ff6b6b;
            color: white;
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
            min-height: calc(100vh - 100px);
            padding: 2rem;
            text-align: center;
        }

        .title {
            font-size: 3rem;
            font-weight: bold;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        .subtitle {
            font-size: 1.2rem;
            margin-bottom: 3rem;
            opacity: 0.9;
        }

        .search-container {
            background: rgba(255, 255, 255, 0.95);
            padding: 2rem;
            border-radius: 16px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
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
            color: #333;
            background: white;
        }

        .search-input:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        .button-group {
            display: flex;
            gap: 1rem;
        }

        .search-btn, .clear-btn {
            flex: 1;
            padding: 1rem 3rem;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            min-width: 150px;
        }

        .search-btn {
            background: #667eea;
            color: white;
        }

        .clear-btn {
            background: #ff6b6b;
            color: white;
        }

        .search-btn:hover, .clear-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
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

        .flash-messages {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1000;
        }

        .flash-message {
            background: #4CAF50;
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            margin-bottom: 0.5rem;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
            animation: slideIn 0.3s ease;
        }

        .flash-message.error {
            background: #f44336;
        }

        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }

        @media (max-width: 768px) {
            .title {
                font-size: 2rem;
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
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            <div class="flash-messages">
                {% for category, message in messages %}
                    <div class="flash-message {{ 'error' if category == 'error' else '' }}">
                        {{ message }}
                    </div>
                {% endfor %}
            </div>
        {% endif %}
    {% endwith %}

    <header class="header">
        <a href="/" class="logo">🏠 BlueDwarf</a>
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

    <footer class="footer">
        <p>&copy; 2025 Elite Marketing Lab LLC. All rights reserved. | <a href="mailto:support@bluedwarf.io">support@bluedwarf.io</a></p>
    </footer>

    <script>
        // Auto-hide flash messages after 5 seconds
        setTimeout(function() {
            const flashMessages = document.querySelector('.flash-messages');
            if (flashMessages) {
                flashMessages.style.opacity = '0';
                flashMessages.style.transform = 'translateX(100%)';
                setTimeout(() => flashMessages.remove(), 300);
            }
        }, 5000);
    </script>
</body>
</html>
'''

# Registration template with email integration
SIGNUP_TEMPLATE = '''
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
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
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
            color: white;
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

        .container {
            max-width: 800px;
            margin: 2rem auto;
            padding: 0 2rem;
        }

        .registration-card {
            background: white;
            padding: 3rem;
            border-radius: 16px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }

        .form-title {
            font-size: 2rem;
            font-weight: bold;
            text-align: center;
            margin-bottom: 0.5rem;
            color: #333;
        }

        .form-subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 2rem;
        }

        .form-group {
            margin-bottom: 1.5rem;
        }

        .form-label {
            display: block;
            font-weight: 600;
            margin-bottom: 0.5rem;
            color: #333;
        }

        .form-input, .form-select, .form-textarea {
            width: 100%;
            padding: 1rem;
            border: 2px solid #e1e5e9;
            border-radius: 8px;
            font-size: 1rem;
            transition: border-color 0.3s ease;
        }

        .form-input:focus, .form-select:focus, .form-textarea:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        .form-textarea {
            resize: vertical;
            min-height: 100px;
        }

        .form-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1rem;
        }

        .submit-btn {
            width: 100%;
            padding: 1rem 2rem;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-top: 1rem;
        }

        .submit-btn:hover {
            background: #5a6fd8;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        }

        .back-link {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            color: #667eea;
            text-decoration: none;
            margin-bottom: 2rem;
            font-weight: 500;
        }

        .back-link:hover {
            color: #5a6fd8;
        }

        .flash-messages {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1000;
        }

        .flash-message {
            background: #4CAF50;
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            margin-bottom: 0.5rem;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
            animation: slideIn 0.3s ease;
        }

        .flash-message.error {
            background: #f44336;
        }

        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }

        @media (max-width: 768px) {
            .form-row {
                grid-template-columns: 1fr;
            }
            
            .registration-card {
                padding: 2rem;
                margin: 1rem;
            }
        }
    </style>
</head>
<body>
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            <div class="flash-messages">
                {% for category, message in messages %}
                    <div class="flash-message {{ 'error' if category == 'error' else '' }}">
                        {{ message }}
                    </div>
                {% endfor %}
            </div>
        {% endif %}
    {% endwith %}

    <header class="header">
        <a href="/" class="logo">🏠 BlueDwarf</a>
        <div class="nav-buttons">
            <a href="/login" class="nav-btn login-btn">Login</a>
        </div>
    </header>

    <div class="container">
        <a href="/" class="back-link">← Back to Home</a>
        
        <div class="registration-card">
            <h1 class="form-title">Professional Registration</h1>
            <p class="form-subtitle">Join our network of verified real estate professionals</p>
            
            <form method="POST" action="/signup">
                <div class="form-row">
                    <div class="form-group">
                        <label class="form-label" for="first_name">First Name *</label>
                        <input type="text" id="first_name" name="first_name" class="form-input" required>
                    </div>
                    <div class="form-group">
                        <label class="form-label" for="last_name">Last Name *</label>
                        <input type="text" id="last_name" name="last_name" class="form-input" required>
                    </div>
                </div>

                <div class="form-group">
                    <label class="form-label" for="email">Email Address *</label>
                    <input type="email" id="email" name="email" class="form-input" required>
                </div>

                <div class="form-group">
                    <label class="form-label" for="password">Password *</label>
                    <input type="password" id="password" name="password" class="form-input" required>
                </div>

                <div class="form-group">
                    <label class="form-label" for="business_address">Business Address *</label>
                    <input type="text" id="business_address" name="business_address" class="form-input" 
                           placeholder="123 Business St, City, State, ZIP" required>
                </div>

                <div class="form-group">
                    <label class="form-label" for="license_number">License Number *</label>
                    <input type="text" id="license_number" name="license_number" class="form-input" required>
                </div>

                <div class="form-group">
                    <label class="form-label" for="profession">Professional Category *</label>
                    <select id="profession" name="profession" class="form-select" required>
                        <option value="">Select your profession</option>
                        <option value="Real Estate Agent">Real Estate Agent</option>
                        <option value="Real Estate Broker">Real Estate Broker</option>
                        <option value="Property Manager">Property Manager</option>
                        <option value="Home Inspector">Home Inspector</option>
                        <option value="Appraiser">Appraiser</option>
                        <option value="Mortgage Broker">Mortgage Broker</option>
                        <option value="Real Estate Attorney">Real Estate Attorney</option>
                        <option value="Property Developer">Property Developer</option>
                        <option value="Investment Advisor">Investment Advisor</option>
                        <option value="Contractor">Contractor</option>
                        <option value="Property Photographer">Property Photographer</option>
                    </select>
                </div>

                <div class="form-group">
                    <label class="form-label" for="service_areas">Service Zip Codes *</label>
                    <input type="text" id="service_areas" name="service_areas" class="form-input" 
                           placeholder="95814, 95628, 95630" required>
                </div>

                <div class="form-group">
                    <label class="form-label" for="bio">Professional Bio</label>
                    <textarea id="bio" name="bio" class="form-textarea" 
                              placeholder="Tell potential clients about your experience and services..."></textarea>
                </div>

                <button type="submit" class="submit-btn">Create Account</button>
            </form>
        </div>
    </div>

    <script>
        // Auto-hide flash messages after 5 seconds
        setTimeout(function() {
            const flashMessages = document.querySelector('.flash-messages');
            if (flashMessages) {
                flashMessages.style.opacity = '0';
                flashMessages.style.transform = 'translateX(100%)';
                setTimeout(() => flashMessages.remove(), 300);
            }
        }, 5000);
    </script>
</body>
</html>
'''

# Contact form template
CONTACT_TEMPLATE = '''
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
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
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
            color: white;
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

        .container {
            max-width: 600px;
            margin: 2rem auto;
            padding: 0 2rem;
        }

        .contact-card {
            background: white;
            padding: 3rem;
            border-radius: 16px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }

        .form-title {
            font-size: 2rem;
            font-weight: bold;
            text-align: center;
            margin-bottom: 0.5rem;
            color: #333;
        }

        .form-subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 2rem;
        }

        .form-group {
            margin-bottom: 1.5rem;
        }

        .form-label {
            display: block;
            font-weight: 600;
            margin-bottom: 0.5rem;
            color: #333;
        }

        .form-input, .form-textarea {
            width: 100%;
            padding: 1rem;
            border: 2px solid #e1e5e9;
            border-radius: 8px;
            font-size: 1rem;
            transition: border-color 0.3s ease;
        }

        .form-input:focus, .form-textarea:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        .form-textarea {
            resize: vertical;
            min-height: 120px;
        }

        .submit-btn {
            width: 100%;
            padding: 1rem 2rem;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-top: 1rem;
        }

        .submit-btn:hover {
            background: #5a6fd8;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        }

        .back-link {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            color: #667eea;
            text-decoration: none;
            margin-bottom: 2rem;
            font-weight: 500;
        }

        .back-link:hover {
            color: #5a6fd8;
        }

        .flash-messages {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1000;
        }

        .flash-message {
            background: #4CAF50;
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            margin-bottom: 0.5rem;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
            animation: slideIn 0.3s ease;
        }

        .flash-message.error {
            background: #f44336;
        }

        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }

        @media (max-width: 768px) {
            .contact-card {
                padding: 2rem;
                margin: 1rem;
            }
        }
    </style>
</head>
<body>
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            <div class="flash-messages">
                {% for category, message in messages %}
                    <div class="flash-message {{ 'error' if category == 'error' else '' }}">
                        {{ message }}
                    </div>
                {% endfor %}
            </div>
        {% endif %}
    {% endwith %}

    <header class="header">
        <a href="/" class="logo">🏠 BlueDwarf</a>
        <div class="nav-buttons">
            <a href="/login" class="nav-btn login-btn">Login</a>
            <a href="/signup" class="nav-btn signup-btn">Get Started</a>
        </div>
    </header>

    <div class="container">
        <a href="/" class="back-link">← Back to Home</a>
        
        <div class="contact-card">
            <h1 class="form-title">Contact Us</h1>
            <p class="form-subtitle">Get in touch with our team</p>
            
            <form method="POST" action="/contact">
                <div class="form-group">
                    <label class="form-label" for="name">Your Name *</label>
                    <input type="text" id="name" name="name" class="form-input" required>
                </div>

                <div class="form-group">
                    <label class="form-label" for="email">Email Address *</label>
                    <input type="email" id="email" name="email" class="form-input" required>
                </div>

                <div class="form-group">
                    <label class="form-label" for="subject">Subject</label>
                    <input type="text" id="subject" name="subject" class="form-input" 
                           placeholder="What can we help you with?">
                </div>

                <div class="form-group">
                    <label class="form-label" for="message">Message *</label>
                    <textarea id="message" name="message" class="form-textarea" 
                              placeholder="Tell us how we can help..." required></textarea>
                </div>

                <button type="submit" class="submit-btn">Send Message</button>
            </form>
        </div>
    </div>

    <script>
        // Auto-hide flash messages after 5 seconds
        setTimeout(function() {
            const flashMessages = document.querySelector('.flash-messages');
            if (flashMessages) {
                flashMessages.style.opacity = '0';
                flashMessages.style.transform = 'translateX(100%)';
                setTimeout(() => flashMessages.remove(), 300);
            }
        }, 5000);
    </script>
</body>
</html>
'''

# Enhanced Property Results template with Google search buttons and detailed descriptions
PROPERTY_RESULTS_TEMPLATE = '''
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
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
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
            color: white;
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
            background: #ff6b6b;
            color: white;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }

        .property-header {
            background: white;
            padding: 2rem;
            border-radius: 16px;
            margin-bottom: 2rem;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }

        .property-title {
            font-size: 2rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
            color: #333;
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
            padding: 1.5rem;
            border-radius: 16px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }

        .card-title {
            font-size: 1.3rem;
            font-weight: bold;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            color: #333;
        }

        .street-view-container, .aerial-view-container {
            width: 100%;
            height: 300px;
            border-radius: 12px;
            overflow: hidden;
            border: 2px solid #e1e5e9;
        }

        .street-view-iframe, .aerial-view-iframe {
            width: 100%;
            height: 100%;
            border: none;
        }

        .property-details {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }

        .detail-card {
            background: white;
            padding: 1.5rem;
            border-radius: 16px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            text-align: center;
        }

        .detail-value {
            font-size: 1.8rem;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 0.5rem;
        }

        .detail-label {
            color: #666;
            font-size: 0.9rem;
        }

        .rental-analysis {
            background: white;
            padding: 2rem;
            border-radius: 16px;
            margin-bottom: 2rem;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }

        .rental-bar {
            width: 100%;
            height: 20px;
            background: linear-gradient(to right, #4CAF50, #FFC107, #FF5722);
            border-radius: 10px;
            position: relative;
            margin: 1rem 0;
        }

        .rental-marker {
            position: absolute;
            top: -5px;
            left: 45%;
            width: 4px;
            height: 30px;
            background: #333;
            border-radius: 2px;
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
            border-radius: 16px;
            margin-bottom: 2rem;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }

        .comparable-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem;
            border-bottom: 1px solid #e1e5e9;
        }

        .comparable-item:last-child {
            border-bottom: none;
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
            margin-right: 1rem;
        }

        .comparable-info {
            flex: 1;
        }

        .comparable-address {
            font-weight: bold;
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

        .comparables-map {
            width: 100%;
            height: 400px;
            border-radius: 12px;
            overflow: hidden;
            border: 2px solid #e1e5e9;
            margin-top: 1rem;
        }

        .professionals-section {
            background: white;
            padding: 2rem;
            border-radius: 16px;
            margin-bottom: 2rem;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }

        .professionals-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1.5rem;
            margin-top: 1.5rem;
        }

        .professional-card {
            border: 2px solid #e1e5e9;
            border-radius: 12px;
            padding: 1.5rem;
            transition: all 0.3s ease;
        }

        .professional-card:hover {
            border-color: #667eea;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }

        .professional-title {
            font-size: 1.1rem;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 0.5rem;
        }

        .professional-location {
            color: #666;
            font-size: 0.9rem;
            margin-bottom: 1rem;
        }

        .professional-description {
            color: #333;
            font-size: 0.9rem;
            margin-bottom: 1rem;
            line-height: 1.4;
        }

        .professional-buttons {
            display: flex;
            gap: 0.75rem;
        }

        .professional-btn, .website-btn {
            flex: 1;
            padding: 0.5rem 1rem;
            border: none;
            border-radius: 6px;
            font-size: 0.9rem;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            text-align: center;
            display: inline-block;
        }

        .professional-btn {
            background: #667eea;
            color: white;
        }

        .website-btn {
            background: #28a745;
            color: white;
        }

        .professional-btn:hover {
            background: #5a6fd8;
            transform: translateY(-1px);
        }

        .website-btn:hover {
            background: #218838;
            transform: translateY(-1px);
        }

        .back-btn {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            background: #667eea;
            color: white;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 500;
            transition: all 0.3s ease;
            margin-top: 2rem;
        }

        .back-btn:hover {
            background: #5a6fd8;
            transform: translateY(-2px);
        }

        .flash-messages {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1000;
        }

        .flash-message {
            background: #4CAF50;
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            margin-bottom: 0.5rem;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
            animation: slideIn 0.3s ease;
        }

        .flash-message.error {
            background: #f44336;
        }

        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }

        @media (max-width: 768px) {
            .content-grid {
                grid-template-columns: 1fr;
            }
            
            .property-details {
                grid-template-columns: repeat(2, 1fr);
            }
            
            .professionals-grid {
                grid-template-columns: 1fr;
            }

            .professional-buttons {
                flex-direction: column;
            }
        }
    </style>
</head>
<body>
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            <div class="flash-messages">
                {% for category, message in messages %}
                    <div class="flash-message {{ 'error' if category == 'error' else '' }}">
                        {{ message }}
                    </div>
                {% endfor %}
            </div>
        {% endif %}
    {% endwith %}

    <header class="header">
        <a href="/" class="logo">🏠 BlueDwarf</a>
        <div class="nav-buttons">
            <a href="/login" class="nav-btn login-btn">Login</a>
            <a href="/signup" class="nav-btn signup-btn">Get Started</a>
        </div>
    </header>

    <div class="container">
        <div class="property-header">
            <h1 class="property-title">{{ address }}</h1>
            <p class="property-subtitle">Comprehensive Property Analysis Report</p>
        </div>

        <div class="content-grid">
            <div class="card">
                <h2 class="card-title">🏠 Street View</h2>
                <div class="street-view-container">
                    <iframe 
                        class="street-view-iframe"
                        src="https://www.google.com/maps/embed/v1/streetview?key=AIzaSyDe8QxfkBSo2Ids9PWK24-aKgqbI9du9B4&location={{ address }}&heading=0&pitch=0&fov=75"
                        allowfullscreen>
                    </iframe>
                </div>
            </div>

            <div class="card">
                <h2 class="card-title">🛰️ Aerial View (2 blocks)</h2>
                <div class="aerial-view-container">
                    <iframe 
                        class="aerial-view-iframe"
                        src="https://www.google.com/maps/embed/v1/view?key=AIzaSyDe8QxfkBSo2Ids9PWK24-aKgqbI9du9B4&center={{ address }}&zoom=17&maptype=satellite"
                        allowfullscreen>
                    </iframe>
                </div>
            </div>
        </div>

        <div class="property-details">
            <div class="detail-card">
                <div class="detail-value">$485,000</div>
                <div class="detail-label">Estimated Value</div>
            </div>
            <div class="detail-card">
                <div class="detail-value">3</div>
                <div class="detail-label">Bedrooms</div>
            </div>
            <div class="detail-card">
                <div class="detail-value">2</div>
                <div class="detail-label">Bathrooms</div>
            </div>
            <div class="detail-card">
                <div class="detail-value">1,850</div>
                <div class="detail-label">Square Feet</div>
            </div>
            <div class="detail-card">
                <div class="detail-value">1995</div>
                <div class="detail-label">Year Built</div>
            </div>
            <div class="detail-card">
                <div class="detail-value">0.25</div>
                <div class="detail-label">Lot Size (acres)</div>
            </div>
        </div>

        <div class="rental-analysis">
            <h2 class="card-title">💰 Rental Rate Analysis</h2>
            <p style="color: #666; margin-bottom: 1rem;">Based on comparable properties in the area</p>
            
            <div class="rental-bar">
                <div class="rental-marker"></div>
            </div>
            
            <div class="rental-labels">
                <span>$1,800/mo</span>
                <span style="font-weight: bold; color: #333;">$2,250/mo (Estimated)</span>
                <span>$2,800/mo</span>
            </div>
            
            <p style="color: #666; font-size: 0.9rem; margin-top: 1rem;">
                This property is estimated to rent for <strong>$2,250/month</strong> based on recent comparable rentals.
            </p>
        </div>

        <div class="comparables-section">
            <h2 class="card-title">📊 Comparable Properties</h2>
            <p style="color: #666; margin-bottom: 1rem;">Recent sales within 0.5 miles</p>
            
            <div class="comparable-item">
                <div style="display: flex; align-items: center;">
                    <div class="comparable-number">1</div>
                    <div class="comparable-info">
                        <div class="comparable-address">456 Oak Street</div>
                        <div class="comparable-details">3 bed • 2 bath • 1,920 sq ft • Sold 2 months ago</div>
                    </div>
                </div>
                <div class="comparable-price">$492,000</div>
            </div>
            
            <div class="comparable-item">
                <div style="display: flex; align-items: center;">
                    <div class="comparable-number">2</div>
                    <div class="comparable-info">
                        <div class="comparable-address">789 Maple Avenue</div>
                        <div class="comparable-details">3 bed • 2 bath • 1,780 sq ft • Sold 1 month ago</div>
                    </div>
                </div>
                <div class="comparable-price">$478,000</div>
            </div>
            
            <div class="comparable-item">
                <div style="display: flex; align-items: center;">
                    <div class="comparable-number">3</div>
                    <div class="comparable-info">
                        <div class="comparable-address">321 Elm Drive</div>
                        <div class="comparable-details">4 bed • 2.5 bath • 2,100 sq ft • Sold 3 weeks ago</div>
                    </div>
                </div>
                <div class="comparable-price">$515,000</div>
            </div>
            
            <div class="comparable-item">
                <div style="display: flex; align-items: center;">
                    <div class="comparable-number">4</div>
                    <div class="comparable-info">
                        <div class="comparable-address">654 Pine Court</div>
                        <div class="comparable-details">3 bed • 1.5 bath • 1,650 sq ft • Sold 6 weeks ago</div>
                    </div>
                </div>
                <div class="comparable-price">$445,000</div>
            </div>
            
            <div class="comparable-item">
                <div style="display: flex; align-items: center;">
                    <div class="comparable-number">5</div>
                    <div class="comparable-info">
                        <div class="comparable-address">987 Cedar Lane</div>
                        <div class="comparable-details">3 bed • 2 bath • 1,900 sq ft • Sold 1 month ago</div>
                    </div>
                </div>
                <div class="comparable-price">$488,000</div>
            </div>
            
            <div class="comparables-map">
                <iframe 
                    src="https://www.google.com/maps/embed/v1/view?key=AIzaSyDe8QxfkBSo2Ids9PWK24-aKgqbI9du9B4&center={{ address }}&zoom=15"
                    width="100%" 
                    height="100%" 
                    style="border:0;" 
                    allowfullscreen>
                </iframe>
            </div>
        </div>

        <div class="professionals-section">
            <h2 class="card-title">👥 Local Real Estate Professionals</h2>
            <p style="color: #666; margin-bottom: 1rem;">Connect with verified professionals in your area</p>
            
            <div class="professionals-grid">
                <div class="professional-card">
                    <div class="professional-title">Real Estate Agent</div>
                    <div class="professional-location">Local Area Specialists</div>
                    <div class="professional-description">Licensed professionals who help buyers and sellers navigate property transactions. They provide market analysis, negotiate deals, handle paperwork, and guide clients through the entire buying or selling process from listing to closing.</div>
                    <div class="professional-buttons">
                        <button class="professional-btn" onclick="contactProfessional('Real Estate Agent', '{{ address }}')">Contact</button>
                        <a href="#" class="website-btn" onclick="searchProfessional('Real Estate Agent', '{{ zip_code }}'); return false;">Website</a>
                    </div>
                </div>
                
                <div class="professional-card">
                    <div class="professional-title">Real Estate Broker</div>
                    <div class="professional-location">Licensed Brokerage Services</div>
                    <div class="professional-description">Senior-level real estate professionals with additional licensing who can own and operate real estate firms. They supervise agents, handle complex transactions, provide advanced market expertise, and offer comprehensive brokerage services for high-value properties.</div>
                    <div class="professional-buttons">
                        <button class="professional-btn" onclick="contactProfessional('Real Estate Broker', '{{ address }}')">Contact</button>
                        <a href="#" class="website-btn" onclick="searchProfessional('Real Estate Broker', '{{ zip_code }}'); return false;">Website</a>
                    </div>
                </div>
                
                <div class="professional-card">
                    <div class="professional-title">Property Manager</div>
                    <div class="professional-location">Rental Property Specialists</div>
                    <div class="professional-description">Professionals who handle day-to-day operations of rental properties. They manage tenant relations, collect rent, coordinate maintenance and repairs, handle lease agreements, conduct property inspections, and maximize rental income for property owners.</div>
                    <div class="professional-buttons">
                        <button class="professional-btn" onclick="contactProfessional('Property Manager', '{{ address }}')">Contact</button>
                        <a href="#" class="website-btn" onclick="searchProfessional('Property Manager', '{{ zip_code }}'); return false;">Website</a>
                    </div>
                </div>
                
                <div class="professional-card">
                    <div class="professional-title">Home Inspector</div>
                    <div class="professional-location">Property Condition Experts</div>
                    <div class="professional-description">Certified professionals who conduct thorough property inspections to identify potential issues. They examine structural elements, electrical systems, plumbing, HVAC, roofing, and safety features, providing detailed reports to help buyers make informed decisions.</div>
                    <div class="professional-buttons">
                        <button class="professional-btn" onclick="contactProfessional('Home Inspector', '{{ address }}')">Contact</button>
                        <a href="#" class="website-btn" onclick="searchProfessional('Home Inspector', '{{ zip_code }}'); return false;">Website</a>
                    </div>
                </div>
                
                <div class="professional-card">
                    <div class="professional-title">Appraiser</div>
                    <div class="professional-location">Property Valuation Specialists</div>
                    <div class="professional-description">Licensed professionals who determine accurate property values for mortgage lending, insurance, tax assessments, and legal purposes. They analyze market data, comparable sales, and property conditions to provide official valuation reports required for financing.</div>
                    <div class="professional-buttons">
                        <button class="professional-btn" onclick="contactProfessional('Appraiser', '{{ address }}')">Contact</button>
                        <a href="#" class="website-btn" onclick="searchProfessional('Appraiser', '{{ zip_code }}'); return false;">Website</a>
                    </div>
                </div>
                
                <div class="professional-card">
                    <div class="professional-title">Mortgage Broker</div>
                    <div class="professional-location">Financing Solutions Experts</div>
                    <div class="professional-description">Licensed professionals who connect borrowers with multiple lenders to find the best mortgage terms. They compare loan options, negotiate rates, handle application processes, and guide clients through financing for property purchases and refinancing.</div>
                    <div class="professional-buttons">
                        <button class="professional-btn" onclick="contactProfessional('Mortgage Broker', '{{ address }}')">Contact</button>
                        <a href="#" class="website-btn" onclick="searchProfessional('Mortgage Broker', '{{ zip_code }}'); return false;">Website</a>
                    </div>
                </div>
                
                <div class="professional-card">
                    <div class="professional-title">Real Estate Attorney</div>
                    <div class="professional-location">Legal Transaction Specialists</div>
                    <div class="professional-description">Specialized lawyers who handle legal aspects of property transactions. They review contracts, resolve title issues, conduct closings, handle disputes, ensure compliance with local laws, and protect clients' legal interests throughout real estate deals.</div>
                    <div class="professional-buttons">
                        <button class="professional-btn" onclick="contactProfessional('Real Estate Attorney', '{{ address }}')">Contact</button>
                        <a href="#" class="website-btn" onclick="searchProfessional('Real Estate Attorney', '{{ zip_code }}'); return false;">Website</a>
                    </div>
                </div>
                
                <div class="professional-card">
                    <div class="professional-title">Property Developer</div>
                    <div class="professional-location">Development & Construction</div>
                    <div class="professional-description">Professionals who acquire land and oversee the creation of new properties or major renovations. They manage construction projects, coordinate with architects and contractors, handle permits and zoning, and create residential or commercial developments.</div>
                    <div class="professional-buttons">
                        <button class="professional-btn" onclick="contactProfessional('Property Developer', '{{ address }}')">Contact</button>
                        <a href="#" class="website-btn" onclick="searchProfessional('Property Developer', '{{ zip_code }}'); return false;">Website</a>
                    </div>
                </div>
                
                <div class="professional-card">
                    <div class="professional-title">Investment Advisor</div>
                    <div class="professional-location">Real Estate Investment Experts</div>
                    <div class="professional-description">Financial professionals specializing in real estate investments. They analyze market trends, evaluate investment opportunities, provide portfolio strategies, calculate ROI projections, and help clients build wealth through strategic property investments and REIT portfolios.</div>
                    <div class="professional-buttons">
                        <button class="professional-btn" onclick="contactProfessional('Investment Advisor', '{{ address }}')">Contact</button>
                        <a href="#" class="website-btn" onclick="searchProfessional('Investment Advisor', '{{ zip_code }}'); return false;">Website</a>
                    </div>
                </div>
                
                <div class="professional-card">
                    <div class="professional-title">Contractor</div>
                    <div class="professional-location">Construction & Renovation</div>
                    <div class="professional-description">Licensed construction professionals who handle property improvements, repairs, and renovations. They manage remodeling projects, coordinate subcontractors, ensure building code compliance, and transform properties to increase value and functionality.</div>
                    <div class="professional-buttons">
                        <button class="professional-btn" onclick="contactProfessional('Contractor', '{{ address }}')">Contact</button>
                        <a href="#" class="website-btn" onclick="searchProfessional('Contractor', '{{ zip_code }}'); return false;">Website</a>
                    </div>
                </div>
                
                <div class="professional-card">
                    <div class="professional-title">Property Photographer</div>
                    <div class="professional-location">Real Estate Marketing</div>
                    <div class="professional-description">Specialized photographers who create high-quality images and virtual tours for property listings. They use professional equipment and techniques to showcase properties in the best light, helping sellers attract buyers and achieve faster sales at better prices.</div>
                    <div class="professional-buttons">
                        <button class="professional-btn" onclick="contactProfessional('Property Photographer', '{{ address }}')">Contact</button>
                        <a href="#" class="website-btn" onclick="searchProfessional('Property Photographer', '{{ zip_code }}'); return false;">Website</a>
                    </div>
                </div>
            </div>
        </div>

        <a href="/" class="back-btn">← Back to Search</a>
    </div>

    <script>
        function contactProfessional(professionalType, propertyAddress) {
            // Create a simple contact form
            const name = prompt(`Contact ${professionalType}\n\nYour name:`);
            if (!name) return;
            
            const email = prompt('Your email address:');
            if (!email) return;
            
            const message = prompt('Your message (optional):') || `I'm interested in ${professionalType.toLowerCase()} services for the property at ${propertyAddress}. Please contact me to discuss.`;
            
            // Send the inquiry
            fetch('/professional-inquiry', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    professional_type: professionalType,
                    property_address: propertyAddress,
                    client_name: name,
                    client_email: email,
                    client_message: message
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Your inquiry has been sent! A professional will contact you soon.');
                } else {
                    alert('Sorry, there was an error sending your inquiry. Please try again.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Sorry, there was an error sending your inquiry. Please try again.');
            });
        }

        function searchProfessional(professionalType, zipCode) {
            // Create Google search URL for professional type + zip code
            const searchQuery = encodeURIComponent(`${professionalType} ${zipCode}`);
            const googleSearchUrl = `https://www.google.com/search?q=${searchQuery}`;
            
            // Open Google search in new tab
            window.open(googleSearchUrl, '_blank');
        }

        // Auto-hide flash messages after 5 seconds
        setTimeout(function() {
            const flashMessages = document.querySelector('.flash-messages');
            if (flashMessages) {
                flashMessages.style.opacity = '0';
                flashMessages.style.transform = 'translateX(100%)';
                setTimeout(() => flashMessages.remove(), 300);
            }
        }, 5000);
    </script>
</body>
</html>
'''

# Simple login template
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
            color: #333;
        }

        .login-container {
            background: white;
            padding: 3rem;
            border-radius: 16px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            width: 100%;
            max-width: 400px;
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
            font-weight: 600;
            margin-bottom: 0.5rem;
            color: #333;
        }

        .form-input {
            width: 100%;
            padding: 1rem;
            border: 2px solid #e1e5e9;
            border-radius: 8px;
            font-size: 1rem;
            transition: border-color 0.3s ease;
        }

        .form-input:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        .login-btn {
            width: 100%;
            padding: 1rem 2rem;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-bottom: 1rem;
        }

        .login-btn:hover {
            background: #5a6fd8;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        }

        .back-link {
            display: block;
            text-align: center;
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
        }

        .back-link:hover {
            color: #5a6fd8;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <h1 class="login-title">🏠 BlueDwarf Login</h1>
        
        <form method="POST" action="/login">
            <div class="form-group">
                <label class="form-label" for="email">Email Address</label>
                <input type="email" id="email" name="email" class="form-input" required>
            </div>

            <div class="form-group">
                <label class="form-label" for="password">Password</label>
                <input type="password" id="password" name="password" class="form-input" required>
            </div>

            <button type="submit" class="login-btn">Login</button>
        </form>
        
        <a href="/" class="back-link">← Back to Home</a>
    </div>
</body>
</html>
'''

# Routes
@app.route('/')
def home():
    return render_template_string(HOME_TEMPLATE)

@app.route('/property-results', methods=['POST'])
def property_results():
    address = request.form.get('address', 'Property Address')
    zip_code = extract_zip_code(address)
    return render_template_string(PROPERTY_RESULTS_TEMPLATE, address=address, zip_code=zip_code)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Get form data
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        password = request.form.get('password')
        business_address = request.form.get('business_address')
        license_number = request.form.get('license_number')
        profession = request.form.get('profession')
        service_areas = request.form.get('service_areas')
        bio = request.form.get('bio', '')
        
        # Basic validation
        if not all([first_name, last_name, email, password, business_address, license_number, profession, service_areas]):
            flash('Please fill in all required fields.', 'error')
            return render_template_string(SIGNUP_TEMPLATE)
        
        # Send registration email
        full_name = f"{first_name} {last_name}"
        email_sent = send_registration_email(email, full_name, profession)
        
        if email_sent:
            flash(f'Registration successful! Welcome to BlueDwarf, {full_name}. Please check your email for confirmation.', 'success')
            return redirect(url_for('home'))
        else:
            flash('Registration completed, but there was an issue sending the confirmation email. Please contact support if needed.', 'error')
            return redirect(url_for('home'))
    
    return render_template_string(SIGNUP_TEMPLATE)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject', 'General Inquiry')
        message = request.form.get('message')
        
        if not all([name, email, message]):
            flash('Please fill in all required fields.', 'error')
            return render_template_string(CONTACT_TEMPLATE)
        
        # Send contact notification
        email_sent = send_contact_notification(name, email, message)
        
        if email_sent:
            flash('Thank you for your message! We will get back to you within 24 hours.', 'success')
            return redirect(url_for('home'))
        else:
            flash('Sorry, there was an error sending your message. Please try again or contact us directly at support@bluedwarf.io.', 'error')
    
    return render_template_string(CONTACT_TEMPLATE)

@app.route('/professional-inquiry', methods=['POST'])
def professional_inquiry():
    try:
        data = request.get_json()
        
        professional_type = data.get('professional_type')
        property_address = data.get('property_address')
        client_name = data.get('client_name')
        client_email = data.get('client_email')
        client_message = data.get('client_message')
        
        if not all([professional_type, property_address, client_name, client_email, client_message]):
            return jsonify({'success': False, 'error': 'Missing required fields'})
        
        # Send professional inquiry notification
        email_sent = send_professional_inquiry(
            professional_type, property_address, client_name, client_email, client_message
        )
        
        return jsonify({'success': email_sent})
    
    except Exception as e:
        print(f"Professional inquiry error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Simple login logic (you can enhance this with a database)
        if email and password:
            session['user_email'] = email
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password.', 'error')
    
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/logout')
def logout():
    session.pop('user_email', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))

# Health check endpoint
@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'email_configured': bool(app.config.get('MAIL_USERNAME')),
        'timestamp': '2025-08-14'
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

