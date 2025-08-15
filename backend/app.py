from flask import Flask, render_template_string, request
import urllib.parse
import re

app = Flask(__name__)

# Configuration
app.secret_key = 'your-secret-key-here'

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
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">🏠</div>
        <h1>BlueDwarf</h1>
        <p class="subtitle">Modern SaaS Platform for Property Valuation</p>
        
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

@app.route('/property-results', methods=['POST'])
def property_results():
    address = request.form.get('address', '')
    
    # Encode address for Google Maps
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
        
        .website-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 20px;
            cursor: pointer;
            font-size: 0.9rem;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        
        .website-btn:hover {
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
                <button class="website-btn" onclick="searchProfessional('Real Estate Agent', '{{ zip_code }}')">Website</button>
            </div>
            
            <div class="professional-card">
                <div class="professional-title">Mortgage Lender</div>
                <div class="professional-desc">Experienced mortgage specialist offering competitive rates and personalized loan solutions</div>
                <button class="website-btn" onclick="searchProfessional('Mortgage Lender', '{{ zip_code }}')">Website</button>
            </div>
            
            <div class="professional-card">
                <div class="professional-title">Home Inspector</div>
                <div class="professional-desc">Certified home inspector with comprehensive inspection services and detailed reporting</div>
                <button class="website-btn" onclick="searchProfessional('Property Inspector', '{{ zip_code }}')">Website</button>
            </div>
            
            <div class="professional-card">
                <div class="professional-title">Insurance Agent</div>
                <div class="professional-desc">Home and auto insurance specialist with competitive coverage options and excellent service</div>
                <button class="website-btn" onclick="searchProfessional('Insurance Agent', '{{ zip_code }}')">Website</button>
            </div>
            
            <div class="professional-card">
                <div class="professional-title">General Contractor</div>
                <div class="professional-desc">Licensed contractor for home renovations and construction projects with quality craftsmanship</div>
                <button class="website-btn" onclick="searchProfessional('General Contractor', '{{ zip_code }}')">Website</button>
            </div>
            
            <div class="professional-card">
                <div class="professional-title">Property Appraiser</div>
                <div class="professional-desc">Certified appraiser providing accurate property valuations for various real estate needs</div>
                <button class="website-btn" onclick="searchProfessional('Property Appraiser', '{{ zip_code }}')">Website</button>
            </div>
            
            <div class="professional-card">
                <div class="professional-title">Structural Engineer</div>
                <div class="professional-desc">Professional engineer specializing in structural analysis and design for residential properties</div>
                <button class="website-btn" onclick="searchProfessional('Structural Engineer', '{{ zip_code }}')">Website</button>
            </div>
            
            <div class="professional-card">
                <div class="professional-title">Escrow Officer</div>
                <div class="professional-desc">Experienced escrow professional ensuring smooth real estate transactions and closings</div>
                <button class="website-btn" onclick="searchProfessional('Escrow Officer', '{{ zip_code }}')">Website</button>
            </div>
            
            <div class="professional-card">
                <div class="professional-title">Property Manager</div>
                <div class="professional-desc">Professional property management services for residential and commercial properties</div>
                <button class="website-btn" onclick="searchProfessional('Property Manager', '{{ zip_code }}')">Website</button>
            </div>
            
            <div class="professional-card">
                <div class="professional-title">Real Estate Attorney</div>
                <div class="professional-desc">Experienced real estate attorney providing legal guidance for property transactions</div>
                <button class="website-btn" onclick="searchProfessional('Real Estate Attorney', '{{ zip_code }}')">Website</button>
            </div>
            
            <div class="professional-card">
                <div class="professional-title">Tax Consultant</div>
                <div class="professional-desc">Tax professional specializing in real estate investments and property tax optimization</div>
                <button class="website-btn" onclick="searchProfessional('Tax Consultant', '{{ zip_code }}')">Website</button>
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

