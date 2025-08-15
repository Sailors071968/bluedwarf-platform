from flask import Flask, render_template_string, request
from flask_mail import Mail, Message
import urllib.parse
import re
import os

app = Flask(__name__)
app.secret_key = 'bluedwarf-secret-key-2025'

# Google Maps API Key
GOOGLE_MAPS_API_KEY = "AIzaSyDe8QxfkBSo2Ids9PWK24-aKgqbI9du9B4"

# Email configuration
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')

# Initialize Flask-Mail
try:
    mail = Mail(app)
except Exception as e:
    print(f"Mail configuration error: {e}")
    mail = None

def extract_zip_code(address):
    """Extract zip code from address string"""
    zip_match = re.search(r'\b(\d{5})\b', address)
    if zip_match:
        return zip_match.group(1)
    return "95814"

def encode_address_for_maps(address):
    """Encode address for Google Maps API"""
    return urllib.parse.quote_plus(address)

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
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .container {
            background: white;
            padding: 3rem;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            text-align: center;
            max-width: 600px;
            width: 90%;
        }
        
        .logo {
            font-size: 3rem;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 1rem;
        }
        
        .subtitle {
            color: #666;
            font-size: 1.2rem;
            margin-bottom: 2rem;
        }
        
        .search-form {
            margin-bottom: 2rem;
        }
        
        .search-input {
            width: 100%;
            padding: 1rem;
            font-size: 1.1rem;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            margin-bottom: 1rem;
            transition: border-color 0.3s;
        }
        
        .search-input:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .search-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem 2rem;
            border: none;
            border-radius: 10px;
            font-size: 1.1rem;
            cursor: pointer;
            transition: transform 0.3s;
        }
        
        .search-btn:hover {
            transform: translateY(-2px);
        }
        
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-top: 2rem;
        }
        
        .feature {
            padding: 1rem;
            background: #f8f9fa;
            border-radius: 10px;
            text-align: center;
        }
        
        .feature-icon {
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }
        
        .feature-title {
            font-weight: bold;
            margin-bottom: 0.5rem;
            color: #333;
        }
        
        .feature-desc {
            color: #666;
            font-size: 0.9rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">🏠 BlueDwarf</div>
        <div class="subtitle">Modern SaaS Platform for Property Valuation</div>
        
        <form class="search-form" action="/property-results" method="POST">
            <input type="text" name="address" class="search-input" 
                   placeholder="Enter property address (e.g., 123 Main St, Sacramento, CA)" required>
            <button type="submit" class="search-btn">🔍 Analyze Property</button>
        </form>
        
        <div class="features">
            <div class="feature">
                <div class="feature-icon">📊</div>
                <div class="feature-title">Property Analysis</div>
                <div class="feature-desc">Comprehensive property valuation and market analysis</div>
            </div>
            <div class="feature">
                <div class="feature-icon">🗺️</div>
                <div class="feature-title">Street View</div>
                <div class="feature-desc">Interactive street-level property visualization</div>
            </div>
            <div class="feature">
                <div class="feature-icon">🏘️</div>
                <div class="feature-title">Neighborhood Data</div>
                <div class="feature-desc">Local market trends and comparable properties</div>
            </div>
            <div class="feature">
                <div class="feature-icon">👥</div>
                <div class="feature-title">Professional Network</div>
                <div class="feature-desc">Connect with verified real estate professionals</div>
            </div>
        </div>
    </div>
</body>
</html>
    ''')

@app.route('/property-results', methods=['POST'])
def property_results():
    address = request.form.get('address', '')
    zip_code = extract_zip_code(address)
    encoded_address = encode_address_for_maps(address)
    api_key = GOOGLE_MAPS_API_KEY
    
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
            padding: 2rem;
        }
        
        .header {
            background: white;
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
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
        
        .maps-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
            margin-bottom: 2rem;
        }
        
        .map-section {
            background: white;
            border-radius: 15px;
            padding: 1.5rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        
        .map-title {
            font-size: 1.3rem;
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
        }
        
        .rental-analysis {
            background: white;
            border-radius: 15px;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        
        .rental-title {
            font-size: 1.5rem;
            color: #333;
            margin-bottom: 1rem;
        }
        
        .rental-estimate {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            border-radius: 10px;
            text-align: center;
            font-size: 2rem;
            font-weight: bold;
        }
        
        .comparables {
            background: white;
            border-radius: 15px;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        
        .comparables-title {
            font-size: 1.5rem;
            color: #333;
            margin-bottom: 1.5rem;
        }
        
        .comparable-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem;
            border: 1px solid #e0e0e0;
            border-radius: 10px;
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
        }
        
        .comparable-details {
            flex: 1;
            margin-left: 1rem;
        }
        
        .comparable-address {
            font-weight: bold;
            color: #333;
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
        
        .professionals {
            background: white;
            border-radius: 15px;
            padding: 2rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        
        .professionals-title {
            font-size: 1.5rem;
            color: #333;
            margin-bottom: 1.5rem;
            text-align: center;
        }
        
        .professionals-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1.5rem;
        }
        
        .professional-card {
            border: 1px solid #e0e0e0;
            border-radius: 10px;
            padding: 1.5rem;
            text-align: center;
            transition: transform 0.3s, box-shadow 0.3s;
        }
        
        .professional-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        }
        
        .professional-icon {
            font-size: 2rem;
            margin-bottom: 1rem;
        }
        
        .professional-title {
            font-size: 1.1rem;
            font-weight: bold;
            color: #333;
            margin-bottom: 0.5rem;
        }
        
        .professional-desc {
            color: #666;
            font-size: 0.9rem;
            margin-bottom: 1rem;
        }
        
        .professional-btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            cursor: pointer;
            font-size: 0.9rem;
            transition: background 0.3s;
        }
        
        .professional-btn:hover {
            background: #5a6fd8;
        }
        
        @media (max-width: 768px) {
            .maps-container {
                grid-template-columns: 1fr;
            }
            
            .professionals-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="property-title">{{ address }}</div>
        <div class="property-subtitle">Comprehensive Property Analysis Report</div>
    </div>
    
    <div class="maps-container">
        <div class="map-section">
            <div class="map-title">🏠 Street View</div>
            <iframe class="map-frame" 
                    src="https://www.google.com/maps/embed/v1/streetview?key={{ api_key }}&location={{ encoded_address }}&heading=0&pitch=0&fov=90">
            </iframe>
        </div>
        
        <div class="map-section">
            <div class="map-title">🛰️ Aerial View (2 blocks)</div>
            <iframe class="map-frame" 
                    src="https://www.google.com/maps/embed/v1/view?key={{ api_key }}&center={{ encoded_address }}&zoom=17&maptype=satellite">
            </iframe>
        </div>
    </div>
    
    <div class="rental-analysis">
        <div class="rental-title">💰 Rental Analysis</div>
        <div class="rental-estimate">$2,510/month</div>
    </div>
    
    <div class="comparables">
        <div class="comparables-title">🏘️ Comparable Properties</div>
        
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
                src="https://www.google.com/maps/embed/v1/view?key={{ api_key }}&center={{ encoded_address }}&zoom=15&maptype=roadmap">
        </iframe>
    </div>
    
    <div class="professionals">
        <div class="professionals-title">👥 Professional Network</div>
        <div class="professionals-grid">
            <div class="professional-card">
                <div class="professional-icon">🏡</div>
                <div class="professional-title">Real Estate Agent</div>
                <div class="professional-desc">Licensed real estate professional specializing in local market expertise</div>
                <button class="professional-btn" onclick="searchProfessional('Real Estate Agent', '{{ zip_code }}')">Website</button>
            </div>
            
            <div class="professional-card">
                <div class="professional-icon">🏦</div>
                <div class="professional-title">Mortgage Lender</div>
                <div class="professional-desc">Experienced mortgage specialist offering competitive loan programs</div>
                <button class="professional-btn" onclick="searchProfessional('Mortgage Lender', '{{ zip_code }}')">Website</button>
            </div>
            
            <div class="professional-card">
                <div class="professional-icon">⚖️</div>
                <div class="professional-title">Real Estate Attorney</div>
                <div class="professional-desc">Legal expert in real estate transactions and property law</div>
                <button class="professional-btn" onclick="searchProfessional('Real Estate Attorney', '{{ zip_code }}')">Website</button>
            </div>
            
            <div class="professional-card">
                <div class="professional-icon">📋</div>
                <div class="professional-title">Title Company</div>
                <div class="professional-desc">Professional title services ensuring clear property ownership</div>
                <button class="professional-btn" onclick="searchProfessional('Title Company', '{{ zip_code }}')">Website</button>
            </div>
            
            <div class="professional-card">
                <div class="professional-icon">🔍</div>
                <div class="professional-title">Property Inspector</div>
                <div class="professional-desc">Certified home inspector with comprehensive inspection services</div>
                <button class="professional-btn" onclick="searchProfessional('Property Inspector', '{{ zip_code }}')">Website</button>
            </div>
            
            <div class="professional-card">
                <div class="professional-icon">🛡️</div>
                <div class="professional-title">Insurance Agent</div>
                <div class="professional-desc">Home and auto insurance specialist with competitive coverage options</div>
                <button class="professional-btn" onclick="searchProfessional('Insurance Agent', '{{ zip_code }}')">Website</button>
            </div>
            
            <div class="professional-card">
                <div class="professional-icon">🔨</div>
                <div class="professional-title">General Contractor</div>
                <div class="professional-desc">Licensed contractor for home renovations and construction projects</div>
                <button class="professional-btn" onclick="searchProfessional('General Contractor', '{{ zip_code }}')">Website</button>
            </div>
            
            <div class="professional-card">
                <div class="professional-icon">📊</div>
                <div class="professional-title">Property Appraiser</div>
                <div class="professional-desc">Certified appraiser providing accurate property valuations</div>
                <button class="professional-btn" onclick="searchProfessional('Property Appraiser', '{{ zip_code }}')">Website</button>
            </div>
            
            <div class="professional-card">
                <div class="professional-icon">🏗️</div>
                <div class="professional-title">Structural Engineer</div>
                <div class="professional-desc">Professional engineer specializing in structural analysis and design</div>
                <button class="professional-btn" onclick="searchProfessional('Structural Engineer', '{{ zip_code }}')">Website</button>
            </div>
            
            <div class="professional-card">
                <div class="professional-icon">📝</div>
                <div class="professional-title">Escrow Officer</div>
                <div class="professional-desc">Experienced escrow professional ensuring smooth real estate transactions</div>
                <button class="professional-btn" onclick="searchProfessional('Escrow Officer', '{{ zip_code }}')">Website</button>
            </div>
            
            <div class="professional-card">
                <div class="professional-icon">🏢</div>
                <div class="professional-title">Property Manager</div>
                <div class="professional-desc">Professional property management services for residential and commercial properties</div>
                <button class="professional-btn" onclick="searchProfessional('Property Manager', '{{ zip_code }}')">Website</button>
            </div>
        </div>
    </div>
    
    <script>
        function searchProfessional(professionalType, zipCode) {
            console.log('Searching for:', professionalType, 'in', zipCode);
            const searchQuery = professionalType + ' ' + zipCode;
            const encodedQuery = encodeURIComponent(searchQuery);
            const googleUrl = 'https://www.google.com/search?q=' + encodedQuery;
            console.log('Opening URL:', googleUrl);
            window.open(googleUrl, '_blank');
        }
        
        // Test function availability
        console.log('searchProfessional function loaded:', typeof searchProfessional);
    </script>
</body>
</html>
    ''', address=address, zip_code=zip_code, encoded_address=encoded_address, api_key=api_key)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

