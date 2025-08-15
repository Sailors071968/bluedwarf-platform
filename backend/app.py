from flask import Flask, render_template_string, request
import urllib.parse
import re

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Google Maps API Key
GOOGLE_MAPS_API_KEY = "AIzaSyDe8QxfkBSo2Ids9PWK24-aKgqbI9du9B4"

def encode_address_for_maps(address):
    """Encode address for Google Maps API"""
    return urllib.parse.quote_plus(address)

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
        }
        
        .container {
            background: rgba(255, 255, 255, 0.95);
            padding: 3rem;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            text-align: center;
            max-width: 600px;
            width: 90%;
        }
        
        .logo {
            font-size: 3rem;
            font-weight: bold;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 1rem;
        }
        
        .tagline {
            font-size: 1.2rem;
            color: #666;
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
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
            margin-top: 2rem;
        }
        
        .feature {
            padding: 1rem;
            background: rgba(102, 126, 234, 0.1);
            border-radius: 10px;
            font-size: 0.9rem;
            color: #555;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">🏠 BlueDwarf</div>
        <div class="tagline">Modern SaaS Platform for Property Valuation</div>
        
        <form class="search-form" action="/property-results" method="POST">
            <input type="text" name="address" class="search-input" 
                   placeholder="Enter property address (e.g., 123 Main Street, Sacramento, CA)" required>
            <button type="submit" class="search-btn">🔍 Analyze Property</button>
        </form>
        
        <div class="features">
            <div class="feature">📊 Property Analysis</div>
            <div class="feature">🏘️ Neighborhood Data</div>
            <div class="feature">💰 Market Valuation</div>
            <div class="feature">📈 Investment Insights</div>
        </div>
    </div>
</body>
</html>
    ''')

@app.route('/property-results', methods=['POST'])
def property_results():
    address = request.form.get('address', '')
    
    # Encode address for Google Maps
    encoded_address = encode_address_for_maps(address)
    api_key = GOOGLE_MAPS_API_KEY
    
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
            padding: 2rem;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 2rem;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        }
        
        .header {
            text-align: center;
            margin-bottom: 2rem;
            padding: 1.5rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 15px;
        }
        
        .header h1 {
            font-size: 1.8rem;
            margin-bottom: 0.5rem;
        }
        
        .header p {
            font-size: 1.1rem;
            opacity: 0.9;
        }
        
        .maps-section {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
            margin-bottom: 3rem;
        }
        
        .map-container {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 1.5rem;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }
        
        .map-title {
            font-size: 1.3rem;
            font-weight: bold;
            margin-bottom: 1rem;
            color: #333;
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
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 3rem;
            text-align: center;
        }
        
        .rental-analysis h2 {
            font-size: 1.8rem;
            margin-bottom: 1rem;
        }
        
        .rental-price {
            font-size: 3rem;
            font-weight: bold;
            margin: 1rem 0;
        }
        
        .comparables-section {
            margin-bottom: 3rem;
        }
        
        .section-title {
            font-size: 1.8rem;
            font-weight: bold;
            margin-bottom: 1.5rem;
            color: #333;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .comparables-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }
        
        .comparable-item {
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .comparable-info h3 {
            font-size: 1.2rem;
            color: #333;
            margin-bottom: 0.5rem;
        }
        
        .comparable-details {
            color: #666;
            font-size: 0.9rem;
        }
        
        .comparable-price {
            font-size: 1.5rem;
            font-weight: bold;
            color: #667eea;
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
        
        .comparables-map {
            width: 100%;
            height: 400px;
            border: none;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }
        
        .professionals-section {
            margin-top: 3rem;
        }
        
        .professionals-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1.5rem;
        }
        
        .professional-card {
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s;
        }
        
        .professional-card:hover {
            transform: translateY(-5px);
        }
        
        .professional-title {
            font-size: 1.3rem;
            font-weight: bold;
            color: #333;
            margin-bottom: 0.5rem;
        }
        
        .professional-description {
            color: #666;
            margin-bottom: 1rem;
            line-height: 1.5;
        }
        
        .professional-buttons {
            display: flex;
            gap: 0.5rem;
        }
        
        .btn {
            padding: 0.7rem 1.2rem;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.9rem;
            transition: all 0.3s;
            text-decoration: none;
            display: inline-block;
            text-align: center;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .btn-secondary {
            background: #e9ecef;
            color: #495057;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
        }
        
        @media (max-width: 768px) {
            .maps-section {
                grid-template-columns: 1fr;
            }
            
            .professionals-grid {
                grid-template-columns: 1fr;
            }
            
            .comparable-item {
                flex-direction: column;
                text-align: center;
                gap: 1rem;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{{ address }}</h1>
            <p>Comprehensive Property Analysis Report</p>
        </div>
        
        <div class="maps-section">
            <div class="map-container">
                <div class="map-title">🏠 Street View</div>
                <iframe class="map-frame" 
                        src="https://www.google.com/maps/embed/v1/streetview?key={{ api_key }}&location={{ encoded_address }}&heading=0&pitch=0&fov=90">
                </iframe>
            </div>
            
            <div class="map-container">
                <div class="map-title">🛰️ Aerial View (2 blocks)</div>
                <iframe class="map-frame" 
                        src="https://www.google.com/maps/embed/v1/view?key={{ api_key }}&center={{ encoded_address }}&zoom=17&maptype=satellite">
                </iframe>
            </div>
        </div>
        
        <div class="rental-analysis">
            <h2>💰 Rental Analysis</h2>
            <div class="rental-price">$2,510/month</div>
            <p>Estimated monthly rental income based on comparable properties in the area</p>
        </div>
        
        <div class="comparables-section">
            <div class="section-title">🏘️ Comparable Properties</div>
            
            <div class="comparables-grid">
                <div class="comparable-item">
                    <div style="display: flex; align-items: center;">
                        <div class="comparable-number">1</div>
                        <div class="comparable-info">
                            <h3>456 Oak Avenue</h3>
                            <div class="comparable-details">3 bed • 2 bath • 2,080 sq ft • 0.3 mi</div>
                        </div>
                    </div>
                    <div class="comparable-price">$472,000</div>
                </div>
                
                <div class="comparable-item">
                    <div style="display: flex; align-items: center;">
                        <div class="comparable-number">2</div>
                        <div class="comparable-info">
                            <h3>789 Maple Street</h3>
                            <div class="comparable-details">4 bed • 3 bath • 2,340 sq ft • 0.4 mi</div>
                        </div>
                    </div>
                    <div class="comparable-price">$518,000</div>
                </div>
                
                <div class="comparable-item">
                    <div style="display: flex; align-items: center;">
                        <div class="comparable-number">3</div>
                        <div class="comparable-info">
                            <h3>321 Elm Drive</h3>
                            <div class="comparable-details">3 bed • 2.5 bath • 2,200 sq ft • 0.5 mi</div>
                        </div>
                    </div>
                    <div class="comparable-price">$495,000</div>
                </div>
                
                <div class="comparable-item">
                    <div style="display: flex; align-items: center;">
                        <div class="comparable-number">4</div>
                        <div class="comparable-info">
                            <h3>654 Cedar Lane</h3>
                            <div class="comparable-details">3 bed • 2 bath • 1,950 sq ft • 0.6 mi</div>
                        </div>
                    </div>
                    <div class="comparable-price">$458,000</div>
                </div>
                
                <div class="comparable-item">
                    <div style="display: flex; align-items: center;">
                        <div class="comparable-number">5</div>
                        <div class="comparable-info">
                            <h3>987 Birch Court</h3>
                            <div class="comparable-details">4 bed • 2.5 bath • 2,450 sq ft • 0.7 mi</div>
                        </div>
                    </div>
                    <div class="comparable-price">$535,000</div>
                </div>
            </div>
            
            <iframe class="comparables-map" 
                    src="https://www.google.com/maps/embed/v1/view?key={{ api_key }}&center={{ encoded_address }}&zoom=15&maptype=roadmap">
            </iframe>
        </div>
        
        <div class="professionals-section">
            <div class="section-title">👥 Professional Network</div>
            
            <div class="professionals-grid">
                <div class="professional-card">
                    <div class="professional-title">Real Estate Agent</div>
                    <div class="professional-description">Licensed real estate professional specializing in residential properties and market analysis</div>
                    <div class="professional-buttons">
                        <button class="btn btn-primary" onclick="searchProfessional('Real Estate Agent', '{{ zip_code }}')">Website</button>
                        <button class="btn btn-secondary">Contact</button>
                    </div>
                </div>
                
                <div class="professional-card">
                    <div class="professional-title">Mortgage Broker</div>
                    <div class="professional-description">Expert mortgage advisor providing competitive rates and personalized financing solutions</div>
                    <div class="professional-buttons">
                        <button class="btn btn-primary" onclick="searchProfessional('Mortgage Broker', '{{ zip_code }}')">Website</button>
                        <button class="btn btn-secondary">Contact</button>
                    </div>
                </div>
                
                <div class="professional-card">
                    <div class="professional-title">Home Inspector</div>
                    <div class="professional-description">Certified home inspector with comprehensive inspection services and detailed reporting</div>
                    <div class="professional-buttons">
                        <button class="btn btn-primary" onclick="searchProfessional('Home Inspector', '{{ zip_code }}')">Website</button>
                        <button class="btn btn-secondary">Contact</button>
                    </div>
                </div>
                
                <div class="professional-card">
                    <div class="professional-title">Property Attorney</div>
                    <div class="professional-description">Experienced real estate attorney handling transactions, contracts, and legal matters</div>
                    <div class="professional-buttons">
                        <button class="btn btn-primary" onclick="searchProfessional('Property Attorney', '{{ zip_code }}')">Website</button>
                        <button class="btn btn-secondary">Contact</button>
                    </div>
                </div>
                
                <div class="professional-card">
                    <div class="professional-title">Property Inspector</div>
                    <div class="professional-description">Certified home inspector with comprehensive inspection services</div>
                    <div class="professional-buttons">
                        <button class="btn btn-primary" onclick="searchProfessional('Property Inspector', '{{ zip_code }}')">Website</button>
                        <button class="btn btn-secondary">Contact</button>
                    </div>
                </div>
                
                <div class="professional-card">
                    <div class="professional-title">Insurance Agent</div>
                    <div class="professional-description">Home and auto insurance specialist with competitive coverage options</div>
                    <div class="professional-buttons">
                        <button class="btn btn-primary" onclick="searchProfessional('Insurance Agent', '{{ zip_code }}')">Website</button>
                        <button class="btn btn-secondary">Contact</button>
                    </div>
                </div>
                
                <div class="professional-card">
                    <div class="professional-title">General Contractor</div>
                    <div class="professional-description">Licensed contractor for home renovations and construction projects</div>
                    <div class="professional-buttons">
                        <button class="btn btn-primary" onclick="searchProfessional('General Contractor', '{{ zip_code }}')">Website</button>
                        <button class="btn btn-secondary">Contact</button>
                    </div>
                </div>
                
                <div class="professional-card">
                    <div class="professional-title">Property Appraiser</div>
                    <div class="professional-description">Certified appraiser providing accurate property valuations</div>
                    <div class="professional-buttons">
                        <button class="btn btn-primary" onclick="searchProfessional('Property Appraiser', '{{ zip_code }}')">Website</button>
                        <button class="btn btn-secondary">Contact</button>
                    </div>
                </div>
                
                <div class="professional-card">
                    <div class="professional-title">Structural Engineer</div>
                    <div class="professional-description">Professional engineer specializing in structural analysis and design</div>
                    <div class="professional-buttons">
                        <button class="btn btn-primary" onclick="searchProfessional('Structural Engineer', '{{ zip_code }}')">Website</button>
                        <button class="btn btn-secondary">Contact</button>
                    </div>
                </div>
                
                <div class="professional-card">
                    <div class="professional-title">Escrow Officer</div>
                    <div class="professional-description">Experienced escrow professional ensuring smooth real estate transactions</div>
                    <div class="professional-buttons">
                        <button class="btn btn-primary" onclick="searchProfessional('Escrow Officer', '{{ zip_code }}')">Website</button>
                        <button class="btn btn-secondary">Contact</button>
                    </div>
                </div>
                
                <div class="professional-card">
                    <div class="professional-title">Property Manager</div>
                    <div class="professional-description">Professional property management services for residential and commercial properties</div>
                    <div class="professional-buttons">
                        <button class="btn btn-primary" onclick="searchProfessional('Property Manager', '{{ zip_code }}')">Website</button>
                        <button class="btn btn-secondary">Contact</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        function searchProfessional(professionalType, zipCode) {
            console.log('Searching for:', professionalType, 'in', zipCode);
            
            if (!professionalType || !zipCode) {
                console.error('Missing professional type or zip code');
                alert('Error: Missing search parameters');
                return;
            }
            
            const searchQuery = professionalType + ' ' + zipCode;
            const encodedQuery = encodeURIComponent(searchQuery);
            const googleUrl = 'https://www.google.com/search?q=' + encodedQuery;
            
            console.log('Opening URL:', googleUrl);
            window.open(googleUrl, '_blank');
        }
    </script>
</body>
</html>
    ''', address=address, encoded_address=encoded_address, api_key=api_key, zip_code=zip_code)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

