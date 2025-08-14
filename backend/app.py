from flask import Flask, render_template_string, request
import urllib.parse
import re

app = Flask(__name__)
app.secret_key = 'bluedwarf-secret-key-2025'

# Google Maps API Key
GOOGLE_MAPS_API_KEY = "AIzaSyDe8QxfkBSo2Ids9PWK24-aKgqbI9du9B4"

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
            <a href="#" class="signup-btn">Get Started</a>
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
        
        .professionals-section {
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
        
        .professionals-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
        }
        
        .professional-card {
            border: 1px solid #e1e5e9;
            border-radius: 10px;
            padding: 1.5rem;
            transition: all 0.3s ease;
        }
        
        .professional-card:hover {
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            transform: translateY(-2px);
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
            color: #555;
            line-height: 1.5;
            margin-bottom: 1rem;
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
            padding: 0.5rem 1rem;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 6px;
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
        }
    </style>
</head>
<body>
    <header class="header">
        <a href="/" class="logo">🏠 BlueDwarf</a>
        <div class="nav-buttons">
            <a href="#" class="login-btn">Login</a>
            <a href="#" class="signup-btn">Get Started</a>
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
                        src="https://www.google.com/maps/embed/v1/streetview?key={{ api_key }}&location={{ encoded_address }}&heading=0&pitch=0&fov=90"
                        allowfullscreen>
                </iframe>
            </div>
            
            <div class="map-container">
                <h3 class="map-title">🛰️ Aerial View (2 blocks)</h3>
                <iframe class="map-frame"
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
        
        <div class="professionals-section">
            <h2 class="section-title">👥 Local Professionals in {{ zip_code }}</h2>
            <div class="professionals-grid">
                <div class="professional-card">
                    <div class="professional-title">Real Estate Agent</div>
                    <div class="professional-location">{{ zip_code }}</div>
                    <div class="professional-description">Experienced agent specializing in residential properties and first-time buyers</div>
                    <button class="website-btn" onclick="searchProfessional('Real Estate Agent', '{{ zip_code }}')">Website</button>
                </div>
                
                <div class="professional-card">
                    <div class="professional-title">Real Estate Broker</div>
                    <div class="professional-location">{{ zip_code }}</div>
                    <div class="professional-description">Licensed broker with extensive market knowledge and investment expertise</div>
                    <button class="website-btn" onclick="searchProfessional('Real Estate Broker', '{{ zip_code }}')">Website</button>
                </div>
                
                <div class="professional-card">
                    <div class="professional-title">Mortgage Lender</div>
                    <div class="professional-location">{{ zip_code }}</div>
                    <div class="professional-description">Specialized in home loans and refinancing with competitive rates</div>
                    <button class="website-btn" onclick="searchProfessional('Mortgage Lender', '{{ zip_code }}')">Website</button>
                </div>
                
                <div class="professional-card">
                    <div class="professional-title">Real Estate Attorney</div>
                    <div class="professional-location">{{ zip_code }}</div>
                    <div class="professional-description">Expert in real estate transactions and contract negotiations</div>
                    <button class="website-btn" onclick="searchProfessional('Real Estate Attorney', '{{ zip_code }}')">Website</button>
                </div>
                
                <div class="professional-card">
                    <div class="professional-title">Property Inspector</div>
                    <div class="professional-location">{{ zip_code }}</div>
                    <div class="professional-description">Certified home inspector with comprehensive inspection services</div>
                    <button class="website-btn" onclick="searchProfessional('Property Inspector', '{{ zip_code }}')">Website</button>
                </div>
                
                <div class="professional-card">
                    <div class="professional-title">Insurance Agent</div>
                    <div class="professional-location">{{ zip_code }}</div>
                    <div class="professional-description">Home and auto insurance specialist with competitive coverage options</div>
                    <button class="website-btn" onclick="searchProfessional('Insurance Agent', '{{ zip_code }}')">Website</button>
                </div>
                
                <div class="professional-card">
                    <div class="professional-title">General Contractor</div>
                    <div class="professional-location">{{ zip_code }}</div>
                    <div class="professional-description">Licensed contractor for home renovations and construction projects</div>
                    <button class="website-btn" onclick="searchProfessional('General Contractor', '{{ zip_code }}')">Website</button>
                </div>
                
                <div class="professional-card">
                    <div class="professional-title">Property Appraiser</div>
                    <div class="professional-location">{{ zip_code }}</div>
                    <div class="professional-description">Certified appraiser providing accurate property valuations</div>
                    <button class="website-btn" onclick="searchProfessional('Property Appraiser', '{{ zip_code }}')">Website</button>
                </div>
                
                <div class="professional-card">
                    <div class="professional-title">Structural Engineer</div>
                    <div class="professional-location">{{ zip_code }}</div>
                    <div class="professional-description">Professional engineer specializing in structural analysis and design</div>
                    <button class="website-btn" onclick="searchProfessional('Structural Engineer', '{{ zip_code }}')">Website</button>
                </div>
                
                <div class="professional-card">
                    <div class="professional-title">Escrow Officer</div>
                    <div class="professional-location">{{ zip_code }}</div>
                    <div class="professional-description">Experienced escrow professional ensuring smooth real estate transactions</div>
                    <button class="website-btn" onclick="searchProfessional('Escrow Officer', '{{ zip_code }}')">Website</button>
                </div>
                
                <div class="professional-card">
                    <div class="professional-title">Property Manager</div>
                    <div class="professional-location">{{ zip_code }}</div>
                    <div class="professional-description">Professional property management services for residential and commercial properties</div>
                    <button class="website-btn" onclick="searchProfessional('Property Manager', '{{ zip_code }}')">Website</button>
                </div>
            </div>
        </div>
        
        <a href="/" class="back-link">← Back to Search</a>
    </div>
    
    <script>
        function searchProfessional(professionalType, zipCode) {
            const searchQuery = professionalType + ' ' + zipCode;
            const encodedQuery = encodeURIComponent(searchQuery);
            const googleUrl = 'https://www.google.com/search?q=' + encodedQuery;
            window.open(googleUrl, '_blank');
        }
    </script>
</body>
</html>
    ''', address=address, zip_code=zip_code, encoded_address=encoded_address, api_key=api_key)

if __name__ == '__main__':
    app.run(debug=True)

