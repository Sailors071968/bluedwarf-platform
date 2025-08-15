from flask import Flask, render_template_string, request, redirect, url_for, flash
import urllib.parse
import re

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Google Maps API Key
GOOGLE_MAPS_API_KEY = "AIzaSyDe8QxfkBSo2Ids9PWK24-aKgqbI9du9B4"

def encode_address_for_maps(address):
    """Encode address for Google Maps Embed API"""
    # Clean address and use proper encoding for Google Maps
    cleaned = ' '.join(address.split())
    # Replace spaces with + and commas with %2C for Google Maps API
    return cleaned.replace(' ', '+').replace(',', '%2C')

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
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
            text-align: center;
            max-width: 600px;
            width: 100%;
        }
        
        .logo {
            font-size: 3rem;
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
        
        .nav-links {
            display: flex;
            gap: 20px;
            justify-content: center;
            margin-bottom: 30px;
        }
        
        .nav-link {
            background: #4CAF50;
            color: white;
            padding: 12px 24px;
            border-radius: 25px;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.3s ease;
            border: 2px solid #4CAF50;
        }
        
        .nav-link:hover {
            background: #45a049;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(76, 175, 80, 0.3);
        }
        
        .nav-link.contact {
            background: #2196F3;
            border-color: #2196F3;
        }
        
        .nav-link.contact:hover {
            background: #1976D2;
        }
        
        .search-container {
            margin: 30px 0;
        }
        
        input[type="text"] {
            width: 100%;
            padding: 15px 20px;
            border: 3px solid #ddd;
            border-radius: 25px;
            font-size: 1.1rem;
            margin-bottom: 20px;
            transition: border-color 0.3s ease;
        }
        
        input[type="text"]:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .analyze-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 40px;
            border: none;
            border-radius: 25px;
            font-size: 1.2rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .analyze-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        }
        
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 30px;
            margin-top: 40px;
        }
        
        .feature {
            text-align: center;
            padding: 20px;
        }
        
        .feature-icon {
            font-size: 3rem;
            margin-bottom: 15px;
        }
        
        .feature h3 {
            color: #333;
            font-size: 1.3rem;
            margin-bottom: 10px;
        }
        
        .feature p {
            color: #666;
            line-height: 1.6;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 30px 20px;
            }
            
            h1 {
                font-size: 2rem;
            }
            
            .nav-links {
                flex-direction: column;
                align-items: center;
            }
            
            .features {
                grid-template-columns: 1fr;
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
            <a href="/contact" class="nav-link contact">💬 Contact Us</a>
        </div>
        
        <form action="/property-results" method="POST" class="search-container">
            <input type="text" name="address" placeholder="Enter property address (e.g., 123 Main Street, Sacramento, CA)" required>
            <button type="submit" class="analyze-btn">🔍 Analyze Property</button>
        </form>
        
        <div class="features">
            <div class="feature">
                <div class="feature-icon">📊</div>
                <h3>Property Analysis</h3>
                <p>Comprehensive market data</p>
            </div>
            <div class="feature">
                <div class="feature-icon">🏘️</div>
                <h3>Neighborhood Data</h3>
                <p>Local insights & trends</p>
            </div>
            <div class="feature">
                <div class="feature-icon">💰</div>
                <h3>Market Valuation</h3>
                <p>Accurate pricing estimates</p>
            </div>
            <div class="feature">
                <div class="feature-icon">📈</div>
                <h3>Investment Insights</h3>
                <p>ROI & growth potential</p>
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
        company = request.form.get('company', '')
        
        # Store registration info (in production, save to database)
        flash('Registration received! We will contact you within 24 hours to complete your professional profile setup.', 'success')
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
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .container {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
            max-width: 500px;
            width: 100%;
        }
        
        h1 {
            color: #333;
            font-size: 2rem;
            margin-bottom: 30px;
            text-align: center;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            color: #333;
            font-weight: 600;
            margin-bottom: 8px;
        }
        
        input, select {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #ddd;
            border-radius: 10px;
            font-size: 1rem;
            transition: border-color 0.3s ease;
        }
        
        input:focus, select:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .submit-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 30px;
            border: none;
            border-radius: 10px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            width: 100%;
            transition: all 0.3s ease;
            margin-bottom: 20px;
        }
        
        .submit-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        }
        
        .back-link {
            display: block;
            text-align: center;
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
            padding: 12px 15px;
            border-radius: 10px;
            margin-bottom: 10px;
        }
        
        .flash-success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        
        .flash-info {
            background: #cce7ff;
            color: #004085;
            border: 1px solid #b3d9ff;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📧 Professional Registration</h1>
        
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                <div class="flash-messages">
                    {% for category, message in messages %}
                        <div class="flash-message flash-{{ category }}">{{ message }}</div>
                    {% endfor %}
                </div>
            {% endif %}
        {% endwith %}
        
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
                    <option value="Home Inspector">Home Inspector</option>
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
        
        # Store contact info (in production, save to database)
        flash('Message received! We will respond to your inquiry within 24 hours.', 'success')
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
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .container {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
            max-width: 500px;
            width: 100%;
        }
        
        h1 {
            color: #333;
            font-size: 2rem;
            margin-bottom: 30px;
            text-align: center;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            color: #333;
            font-weight: 600;
            margin-bottom: 8px;
        }
        
        input, textarea {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #ddd;
            border-radius: 10px;
            font-size: 1rem;
            transition: border-color 0.3s ease;
            font-family: inherit;
        }
        
        input:focus, textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        
        textarea {
            height: 120px;
            resize: vertical;
        }
        
        .submit-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 30px;
            border: none;
            border-radius: 10px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            width: 100%;
            transition: all 0.3s ease;
            margin-bottom: 20px;
        }
        
        .submit-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        }
        
        .back-link {
            display: block;
            text-align: center;
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
            padding: 12px 15px;
            border-radius: 10px;
            margin-bottom: 10px;
        }
        
        .flash-success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        
        .flash-info {
            background: #cce7ff;
            color: #004085;
            border: 1px solid #b3d9ff;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>💬 Contact Us</h1>
        
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                <div class="flash-messages">
                    {% for category, message in messages %}
                        <div class="flash-message flash-{{ category }}">{{ message }}</div>
                    {% endfor %}
                </div>
            {% endif %}
        {% endwith %}
        
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
                <textarea id="message" name="message" placeholder="Tell us how we can help you..." required></textarea>
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
    
    # Encode address for Google Maps with improved method
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
            font-size: 2.2rem;
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
        
        .rental-section {
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
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .rental-amount {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 15px;
        }
        
        .rental-description {
            color: #666;
            text-align: center;
            font-size: 1.1rem;
        }
        
        .comparables-section {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 40px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        
        .section-title {
            font-size: 1.5rem;
            font-weight: 600;
            color: #333;
            margin-bottom: 25px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .comparable-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px;
            border: 2px solid #f0f0f0;
            border-radius: 12px;
            margin-bottom: 15px;
            transition: all 0.3s ease;
        }
        
        .comparable-item:hover {
            border-color: #667eea;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.1);
        }
        
        .comparable-number {
            background: #667eea;
            color: white;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            font-size: 1.2rem;
        }
        
        .comparable-details {
            flex: 1;
            margin-left: 20px;
        }
        
        .comparable-address {
            font-weight: 600;
            color: #333;
            font-size: 1.1rem;
            margin-bottom: 5px;
        }
        
        .comparable-specs {
            color: #666;
            font-size: 0.95rem;
        }
        
        .comparable-price {
            font-size: 1.4rem;
            font-weight: 700;
            color: #2196F3;
        }
        
        .professionals-section {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 40px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        
        .professionals-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 25px;
        }
        
        .professional-card {
            border: 2px solid #f0f0f0;
            border-radius: 12px;
            padding: 20px;
            transition: all 0.3s ease;
        }
        
        .professional-card:hover {
            border-color: #667eea;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.1);
        }
        
        .professional-title {
            font-weight: 600;
            color: #333;
            font-size: 1.2rem;
            margin-bottom: 10px;
        }
        
        .professional-description {
            color: #666;
            font-size: 0.95rem;
            margin-bottom: 15px;
            line-height: 1.5;
        }
        
        .professional-buttons {
            display: flex;
            gap: 10px;
        }
        
        .website-btn {
            background: #4CAF50;
            color: white;
            padding: 8px 16px;
            border: none;
            border-radius: 6px;
            text-decoration: none;
            font-size: 0.9rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .website-btn:hover {
            background: #45a049;
            transform: translateY(-1px);
        }
        
        .contact-btn {
            background: #2196F3;
            color: white;
            padding: 8px 16px;
            border: none;
            border-radius: 6px;
            text-decoration: none;
            font-size: 0.9rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .contact-btn:hover {
            background: #1976D2;
            transform: translateY(-1px);
        }
        
        .back-link {
            display: inline-block;
            background: rgba(255, 255, 255, 0.95);
            color: #667eea;
            padding: 15px 30px;
            border-radius: 25px;
            text-decoration: none;
            font-weight: 600;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
        }
        
        .back-link:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.2);
        }
        
        @media (max-width: 768px) {
            .maps-container {
                grid-template-columns: 1fr;
            }
            
            .comparable-item {
                flex-direction: column;
                text-align: center;
                gap: 15px;
            }
            
            .comparable-details {
                margin-left: 0;
            }
            
            .professionals-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
    <script>
        function searchProfessional(professionalType, zipCode) {
            const searchQuery = professionalType + ' ' + zipCode;
            const encodedQuery = encodeURIComponent(searchQuery);
            const googleUrl = 'https://www.google.com/search?q=' + encodedQuery;
            window.open(googleUrl, '_blank');
        }
    </script>
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
    
    <div class="rental-section">
        <h2 class="rental-title">💰 Rental Analysis</h2>
        <div class="rental-amount">$2,510 / month</div>
        <p class="rental-description">Estimated monthly rental income based on comparable properties in the area</p>
    </div>
    
    <div class="comparables-section">
        <h2 class="section-title">🏘️ Comparable Properties</h2>
        
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
    </div>
    
    <div class="professionals-section">
        <h2 class="section-title">🤝 Professional Network</h2>
        
        <div class="professionals-grid">
            <div class="professional-card">
                <div class="professional-title">Real Estate Agent</div>
                <div class="professional-description">Licensed real estate professional with local market expertise and proven track record</div>
                <div class="professional-buttons">
                    <button class="website-btn" onclick="searchProfessional('Real Estate Agent', '{{ zip_code }}')">Website</button>
                    <a href="/contact" class="contact-btn">Contact</a>
                </div>
            </div>
            
            <div class="professional-card">
                <div class="professional-title">Mortgage Lender</div>
                <div class="professional-description">Experienced mortgage specialist offering competitive rates and personalized loan solutions</div>
                <div class="professional-buttons">
                    <button class="website-btn" onclick="searchProfessional('Mortgage Lender', '{{ zip_code }}')">Website</button>
                    <a href="/contact" class="contact-btn">Contact</a>
                </div>
            </div>
            
            <div class="professional-card">
                <div class="professional-title">Home Inspector</div>
                <div class="professional-description">Certified home inspector with comprehensive inspection services and detailed reporting</div>
                <div class="professional-buttons">
                    <button class="website-btn" onclick="searchProfessional('Home Inspector', '{{ zip_code }}')">Website</button>
                    <a href="/contact" class="contact-btn">Contact</a>
                </div>
            </div>
            
            <div class="professional-card">
                <div class="professional-title">Insurance Agent</div>
                <div class="professional-description">Home and auto insurance specialist with competitive coverage options and excellent service</div>
                <div class="professional-buttons">
                    <button class="website-btn" onclick="searchProfessional('Insurance Agent', '{{ zip_code }}')">Website</button>
                    <a href="/contact" class="contact-btn">Contact</a>
                </div>
            </div>
            
            <div class="professional-card">
                <div class="professional-title">General Contractor</div>
                <div class="professional-description">Licensed contractor for home renovations and construction projects with quality craftsmanship</div>
                <div class="professional-buttons">
                    <button class="website-btn" onclick="searchProfessional('General Contractor', '{{ zip_code }}')">Website</button>
                    <a href="/contact" class="contact-btn">Contact</a>
                </div>
            </div>
            
            <div class="professional-card">
                <div class="professional-title">Property Appraiser</div>
                <div class="professional-description">Certified appraiser providing accurate property valuations for various real estate needs</div>
                <div class="professional-buttons">
                    <button class="website-btn" onclick="searchProfessional('Property Appraiser', '{{ zip_code }}')">Website</button>
                    <a href="/contact" class="contact-btn">Contact</a>
                </div>
            </div>
            
            <div class="professional-card">
                <div class="professional-title">Structural Engineer</div>
                <div class="professional-description">Professional engineer specializing in structural analysis and design for residential properties</div>
                <div class="professional-buttons">
                    <button class="website-btn" onclick="searchProfessional('Structural Engineer', '{{ zip_code }}')">Website</button>
                    <a href="/contact" class="contact-btn">Contact</a>
                </div>
            </div>
            
            <div class="professional-card">
                <div class="professional-title">Escrow Officer</div>
                <div class="professional-description">Experienced escrow professional ensuring smooth real estate transactions and closings</div>
                <div class="professional-buttons">
                    <button class="website-btn" onclick="searchProfessional('Escrow Officer', '{{ zip_code }}')">Website</button>
                    <a href="/contact" class="contact-btn">Contact</a>
                </div>
            </div>
            
            <div class="professional-card">
                <div class="professional-title">Property Manager</div>
                <div class="professional-description">Professional property management services for residential and commercial properties</div>
                <div class="professional-buttons">
                    <button class="website-btn" onclick="searchProfessional('Property Manager', '{{ zip_code }}')">Website</button>
                    <a href="/contact" class="contact-btn">Contact</a>
                </div>
            </div>
            
            <div class="professional-card">
                <div class="professional-title">Real Estate Attorney</div>
                <div class="professional-description">Experienced real estate attorney providing legal guidance for property transactions</div>
                <div class="professional-buttons">
                    <button class="website-btn" onclick="searchProfessional('Real Estate Attorney', '{{ zip_code }}')">Website</button>
                    <a href="/contact" class="contact-btn">Contact</a>
                </div>
            </div>
            
            <div class="professional-card">
                <div class="professional-title">Tax Consultant</div>
                <div class="professional-description">Tax professional specializing in real estate investments and property tax optimization</div>
                <div class="professional-buttons">
                    <button class="website-btn" onclick="searchProfessional('Tax Consultant', '{{ zip_code }}')">Website</button>
                    <a href="/contact" class="contact-btn">Contact</a>
                </div>
            </div>
        </div>
    </div>
    
    <a href="/" class="back-link">← Back to Search</a>
</body>
</html>
    ''', address=address, encoded_address=encoded_address, api_key=GOOGLE_MAPS_API_KEY, zip_code=zip_code)

if __name__ == '__main__':
    app.run(debug=True)

