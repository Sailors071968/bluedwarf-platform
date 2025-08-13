from flask import Flask, render_template_string, request, redirect, url_for, session, jsonify
import os

app = Flask(__name__)
app.secret_key = 'bluedwarf-secret-key-2025'

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
</body>
</html>
'''

# Property Results template with corrected 6 rows x 2 columns professional listings
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

        .professional-btn {
            background: #667eea;
            color: white;
            padding: 0.5rem 1rem;
            border: none;
            border-radius: 6px;
            font-size: 0.9rem;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .professional-btn:hover {
            background: #5a6fd8;
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
        }
    </style>
</head>
<body>
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
                        src="https://www.google.com/maps/embed/v1/streetview?key=YOUR_GOOGLE_MAPS_API_KEY&location={{ address }}&heading=0&pitch=0&fov=75"
                        allowfullscreen>
                    </iframe>
                </div>
            </div>

            <div class="card">
                <h2 class="card-title">🛰️ Aerial View (2 blocks)</h2>
                <div class="aerial-view-container">
                    <iframe 
                        class="aerial-view-iframe"
                        src="https://www.google.com/maps/embed/v1/view?key=YOUR_GOOGLE_MAPS_API_KEY&center={{ address }}&zoom=17&maptype=satellite"
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
                <div class="detail-value">4</div>
                <div class="detail-label">Bedrooms</div>
            </div>
            <div class="detail-card">
                <div class="detail-value">2</div>
                <div class="detail-label">Bathrooms</div>
            </div>
            <div class="detail-card">
                <div class="detail-value">1,492</div>
                <div class="detail-label">Square Feet</div>
            </div>
            <div class="detail-card">
                <div class="detail-value">1964</div>
                <div class="detail-label">Year Built</div>
            </div>
            <div class="detail-card">
                <div class="detail-value">$2,510</div>
                <div class="detail-label">Monthly Rent Est</div>
            </div>
        </div>

        <div class="rental-analysis">
            <h2 class="card-title">📊 Rental Rate Analysis</h2>
            <div class="rental-bar">
                <div class="rental-marker"></div>
            </div>
            <div class="rental-labels">
                <span>$1,800 Low</span>
                <span>Current: $2,510/month</span>
                <span>$3,200 High</span>
            </div>
        </div>

        <div class="comparables-section">
            <h2 class="card-title">🏘️ Comparable Properties</h2>
            
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

            <!-- RentCast Comparables Map -->
            <div class="comparables-map">
                <iframe 
                    src="https://www.google.com/maps/embed/v1/view?key=YOUR_GOOGLE_MAPS_API_KEY&center={{ address }}&zoom=15"
                    width="100%" 
                    height="100%" 
                    style="border:0;" 
                    allowfullscreen="" 
                    loading="lazy">
                </iframe>
            </div>
        </div>

        <!-- Professional Listings Section - 6 rows x 2 columns -->
        <div class="professionals-section">
            <h2 class="card-title">👥 Local Professionals in {{ city }}, {{ state }}</h2>
            <div class="professionals-grid">
                <!-- Row 1 -->
                <div class="professional-card">
                    <div class="professional-title">Real Estate Agent</div>
                    <div class="professional-location">{{ city }}, {{ state }}</div>
                    <div class="professional-description">Experienced agent specializing in residential properties and first-time buyers</div>
                    <button class="professional-btn">Website</button>
                </div>

                <div class="professional-card">
                    <div class="professional-title">Real Estate Broker</div>
                    <div class="professional-location">{{ city }}, {{ state }}</div>
                    <div class="professional-description">Licensed broker with extensive market knowledge and investment expertise</div>
                    <button class="professional-btn">Website</button>
                </div>

                <!-- Row 2 -->
                <div class="professional-card">
                    <div class="professional-title">Mortgage Lender</div>
                    <div class="professional-location">{{ city }}, {{ state }}</div>
                    <div class="professional-description">Specialized in home loans and refinancing with competitive rates</div>
                    <button class="professional-btn">Website</button>
                </div>

                <div class="professional-card">
                    <div class="professional-title">Real Estate Attorney</div>
                    <div class="professional-location">{{ city }}, {{ state }}</div>
                    <div class="professional-description">Expert in real estate transactions and contract negotiations</div>
                    <button class="professional-btn">Website</button>
                </div>

                <!-- Row 3 -->
                <div class="professional-card">
                    <div class="professional-title">Property Inspector</div>
                    <div class="professional-location">{{ city }}, {{ state }}</div>
                    <div class="professional-description">Certified home inspector with comprehensive inspection services</div>
                    <button class="professional-btn">Website</button>
                </div>

                <div class="professional-card">
                    <div class="professional-title">Insurance Agent</div>
                    <div class="professional-location">{{ city }}, {{ state }}</div>
                    <div class="professional-description">Home and auto insurance specialist with competitive coverage options</div>
                    <button class="professional-btn">Website</button>
                </div>

                <!-- Row 4 -->
                <div class="professional-card">
                    <div class="professional-title">General Contractor</div>
                    <div class="professional-location">{{ city }}, {{ state }}</div>
                    <div class="professional-description">Licensed contractor for home renovations and construction projects</div>
                    <button class="professional-btn">Website</button>
                </div>

                <div class="professional-card">
                    <div class="professional-title">Property Appraiser</div>
                    <div class="professional-location">{{ city }}, {{ state }}</div>
                    <div class="professional-description">Certified appraiser providing accurate property valuations</div>
                    <button class="professional-btn">Website</button>
                </div>

                <!-- Row 5 -->
                <div class="professional-card">
                    <div class="professional-title">Structural Engineer</div>
                    <div class="professional-location">{{ city }}, {{ state }}</div>
                    <div class="professional-description">Professional engineer specializing in structural analysis and design</div>
                    <button class="professional-btn">Website</button>
                </div>

                <div class="professional-card">
                    <div class="professional-title">Escrow Officer</div>
                    <div class="professional-location">{{ city }}, {{ state }}</div>
                    <div class="professional-description">Experienced escrow professional ensuring smooth real estate transactions</div>
                    <button class="professional-btn">Website</button>
                </div>

                <!-- Row 6 -->
                <div class="professional-card">
                    <div class="professional-title">Property Manager</div>
                    <div class="professional-location">{{ city }}, {{ state }}</div>
                    <div class="professional-description">Professional property management services for residential and commercial properties</div>
                    <button class="professional-btn">Website</button>
                </div>

                <!-- Empty spot for 6x2 grid -->
                <div style="visibility: hidden;"></div>
            </div>
        </div>

        <a href="/" class="back-btn">← Back to Search</a>
    </div>
</body>
</html>
'''

# Login template
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
            color: white;
        }

        .login-container {
            background: rgba(255, 255, 255, 0.95);
            padding: 3rem;
            border-radius: 16px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
            max-width: 400px;
            width: 100%;
            color: #333;
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
            margin-bottom: 0.5rem;
            font-weight: 500;
            color: #333;
        }

        .form-input {
            width: 100%;
            padding: 1rem;
            border: 2px solid #e1e5e9;
            border-radius: 8px;
            font-size: 1rem;
            color: #333;
            background: white;
        }

        .form-input:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        .login-btn {
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

        .login-btn:hover {
            background: #5a6fd8;
            transform: translateY(-2px);
        }

        .signup-link {
            text-align: center;
            margin-top: 1.5rem;
        }

        .signup-link a {
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
        }

        .back-link {
            text-align: center;
            margin-top: 1rem;
        }

        .back-link a {
            color: #666;
            text-decoration: none;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <h1 class="login-title">Welcome Back</h1>
        <form action="/login" method="POST">
            <div class="form-group">
                <label for="email" class="form-label">Email</label>
                <input type="email" id="email" name="email" class="form-input" required>
            </div>
            <div class="form-group">
                <label for="password" class="form-label">Password</label>
                <input type="password" id="password" name="password" class="form-input" required>
            </div>
            <button type="submit" class="login-btn">Sign In</button>
        </form>
        <div class="signup-link">
            <p>Don't have an account? <a href="/signup">Create Account</a></p>
        </div>
        <div class="back-link">
            <a href="/">← Back to Home</a>
        </div>
    </div>
</body>
</html>
'''

# Enhanced Signup template with professional verification
SIGNUP_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Create Account - BlueDwarf</title>
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
            padding: 2rem 0;
            color: white;
        }

        .signup-container {
            background: rgba(255, 255, 255, 0.95);
            padding: 3rem;
            border-radius: 16px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
            max-width: 800px;
            width: 100%;
            margin: 0 auto;
            color: #333;
        }

        .signup-title {
            font-size: 2rem;
            font-weight: bold;
            text-align: center;
            margin-bottom: 2rem;
            color: #333;
        }

        .form-section {
            margin-bottom: 2rem;
            padding: 1.5rem;
            border: 2px solid #e1e5e9;
            border-radius: 12px;
            background: #f8f9fa;
        }

        .section-title {
            font-size: 1.2rem;
            font-weight: bold;
            margin-bottom: 1rem;
            color: #333;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .form-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1rem;
            margin-bottom: 1.5rem;
        }

        .form-group {
            margin-bottom: 1.5rem;
        }

        .form-group.full-width {
            grid-column: 1 / -1;
        }

        .form-label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 500;
            color: #333;
        }

        .form-input, .form-select {
            width: 100%;
            padding: 1rem;
            border: 2px solid #e1e5e9;
            border-radius: 8px;
            font-size: 1rem;
            color: #333;
            background: white;
        }

        .form-input:focus, .form-select:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        .file-upload {
            border: 2px dashed #667eea;
            border-radius: 8px;
            padding: 2rem;
            text-align: center;
            background: white;
            transition: all 0.3s ease;
            cursor: pointer;
        }

        .file-upload:hover {
            border-color: #5a6fd8;
            background: #f8f9ff;
        }

        .file-upload input {
            display: none;
        }

        .camera-section {
            text-align: center;
            padding: 2rem;
            border: 2px solid #e1e5e9;
            border-radius: 8px;
            background: white;
        }

        .camera-preview {
            width: 300px;
            height: 200px;
            background: #f0f0f0;
            border-radius: 8px;
            margin: 1rem auto;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #666;
        }

        .camera-btn {
            background: #667eea;
            color: white;
            padding: 0.75rem 1.5rem;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            cursor: pointer;
            margin: 0.5rem;
        }

        .signup-btn {
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
            margin-top: 2rem;
        }

        .signup-btn:hover {
            background: #5a6fd8;
            transform: translateY(-2px);
        }

        .login-link {
            text-align: center;
            margin-top: 1.5rem;
        }

        .login-link a {
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
        }

        .back-link {
            text-align: center;
            margin-top: 1rem;
        }

        .back-link a {
            color: #666;
            text-decoration: none;
        }

        @media (max-width: 768px) {
            .form-row {
                grid-template-columns: 1fr;
            }
            
            .signup-container {
                padding: 2rem;
                margin: 1rem;
            }
        }
    </style>
</head>
<body>
    <div class="signup-container">
        <h1 class="signup-title">Create Account</h1>
        <form action="/signup" method="POST" enctype="multipart/form-data">
            
            <!-- Personal Information -->
            <div class="form-section">
                <h2 class="section-title">👤 Personal Information</h2>
                <div class="form-row">
                    <div class="form-group">
                        <label for="first_name" class="form-label">First Name</label>
                        <input type="text" id="first_name" name="first_name" class="form-input" required>
                    </div>
                    <div class="form-group">
                        <label for="last_name" class="form-label">Last Name</label>
                        <input type="text" id="last_name" name="last_name" class="form-input" required>
                    </div>
                </div>
                <div class="form-group">
                    <label for="email" class="form-label">Email</label>
                    <input type="email" id="email" name="email" class="form-input" required>
                </div>
                <div class="form-group">
                    <label for="password" class="form-label">Password</label>
                    <input type="password" id="password" name="password" class="form-input" required>
                </div>
            </div>

            <!-- Professional Information -->
            <div class="form-section">
                <h2 class="section-title">🏢 Professional Information</h2>
                <div class="form-group">
                    <label for="business_address" class="form-label">Business Address</label>
                    <input type="text" id="business_address" name="business_address" class="form-input" required>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label for="license_number" class="form-label">License Number</label>
                        <input type="text" id="license_number" name="license_number" class="form-input" required>
                    </div>
                    <div class="form-group">
                        <label for="website" class="form-label">Website (Optional)</label>
                        <input type="url" id="website" name="website" class="form-input">
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label for="profession" class="form-label">Profession</label>
                        <select id="profession" name="profession" class="form-select" required>
                            <option value="">Select your profession</option>
                            <option value="real_estate_agent">Real Estate Agent</option>
                            <option value="real_estate_broker">Real Estate Broker</option>
                            <option value="mortgage_lender">Mortgage Lender</option>
                            <option value="real_estate_attorney">Real Estate Attorney</option>
                            <option value="property_inspector">Property Inspector</option>
                            <option value="insurance_agent">Insurance Agent</option>
                            <option value="general_contractor">General Contractor</option>
                            <option value="property_appraiser">Property Appraiser</option>
                            <option value="structural_engineer">Structural Engineer</option>
                            <option value="escrow_officer">Escrow Officer</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="service_zip_codes" class="form-label">Service Zip Codes</label>
                        <input type="text" id="service_zip_codes" name="service_zip_codes" class="form-input" placeholder="95628, 95814, 95630" required>
                    </div>
                </div>
            </div>

            <!-- Document Verification -->
            <div class="form-section">
                <h2 class="section-title">📄 Document Verification</h2>
                <div class="form-row">
                    <div class="form-group">
                        <label class="form-label">Professional License Upload</label>
                        <div class="file-upload" onclick="document.getElementById('license_upload').click()">
                            <input type="file" id="license_upload" name="license_upload" accept=".pdf,.jpg,.jpeg,.png" required>
                            <p>📄 Click to upload your professional license</p>
                            <small>PDF, JPG, or PNG format</small>
                        </div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Photo ID Upload</label>
                        <div class="file-upload" onclick="document.getElementById('photo_id_upload').click()">
                            <input type="file" id="photo_id_upload" name="photo_id_upload" accept=".jpg,.jpeg,.png" required>
                            <p>🆔 Click to upload your photo ID</p>
                            <small>State-issued ID or driver's license</small>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Live Photo Verification -->
            <div class="form-section">
                <h2 class="section-title">📸 Live Photo Verification</h2>
                <div class="camera-section">
                    <p>Take a live photo for facial recognition verification</p>
                    <div class="camera-preview" id="camera-preview">
                        📷 Camera Preview
                    </div>
                    <button type="button" class="camera-btn" onclick="startCamera()">Start Camera</button>
                    <button type="button" class="camera-btn" onclick="capturePhoto()">Capture Photo</button>
                </div>
            </div>

            <button type="submit" class="signup-btn">Create Account</button>
        </form>
        
        <div class="login-link">
            <p>Already have an account? <a href="/login">Sign In</a></p>
        </div>
        <div class="back-link">
            <a href="/">← Back to Home</a>
        </div>
    </div>

    <script>
        let stream = null;
        let capturedPhoto = null;

        async function startCamera() {
            try {
                stream = await navigator.mediaDevices.getUserMedia({ video: true });
                const preview = document.getElementById('camera-preview');
                const video = document.createElement('video');
                video.srcObject = stream;
                video.autoplay = true;
                video.style.width = '100%';
                video.style.height = '100%';
                video.style.objectFit = 'cover';
                preview.innerHTML = '';
                preview.appendChild(video);
            } catch (err) {
                alert('Camera access denied or not available');
            }
        }

        function capturePhoto() {
            if (!stream) {
                alert('Please start the camera first');
                return;
            }
            
            const video = document.querySelector('#camera-preview video');
            const canvas = document.createElement('canvas');
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(video, 0, 0);
            
            capturedPhoto = canvas.toDataURL('image/jpeg');
            
            // Stop camera
            stream.getTracks().forEach(track => track.stop());
            
            // Show captured photo
            const preview = document.getElementById('camera-preview');
            preview.innerHTML = '<img src="' + capturedPhoto + '" style="width: 100%; height: 100%; object-fit: cover;">';
            
            alert('Photo captured successfully!');
        }

        // File upload feedback
        document.getElementById('license_upload').addEventListener('change', function(e) {
            const fileName = e.target.files[0]?.name;
            if (fileName) {
                e.target.parentElement.innerHTML = '<p>✅ ' + fileName + '</p>';
            }
        });

        document.getElementById('photo_id_upload').addEventListener('change', function(e) {
            const fileName = e.target.files[0]?.name;
            if (fileName) {
                e.target.parentElement.innerHTML = '<p>✅ ' + fileName + '</p>';
            }
        });
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HOME_TEMPLATE)

@app.route('/property-results', methods=['GET', 'POST'])
def property_results():
    if request.method == 'POST':
        address = request.form.get('address', '456 Oak Avenue, Portland, OR 97205')
    else:
        address = request.args.get('address', '456 Oak Avenue, Portland, OR 97205')
    
    # Extract city and state from address for professional listings
    address_parts = address.split(',')
    city = address_parts[1].strip() if len(address_parts) > 1 else "Fair Oaks"
    state = address_parts[2].strip().split()[0] if len(address_parts) > 2 else "CA"
    
    return render_template_string(PROPERTY_RESULTS_TEMPLATE, 
                                address=address, 
                                city=city, 
                                state=state)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        # Add authentication logic here
        session['user'] = email
        return redirect(url_for('home'))
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Handle form submission
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        password = request.form.get('password')
        business_address = request.form.get('business_address')
        license_number = request.form.get('license_number')
        website = request.form.get('website')
        profession = request.form.get('profession')
        service_zip_codes = request.form.get('service_zip_codes')
        
        # Handle file uploads
        license_upload = request.files.get('license_upload')
        photo_id_upload = request.files.get('photo_id_upload')
        
        # Add user registration logic here
        session['user'] = email
        return redirect(url_for('home'))
    return render_template_string(SIGNUP_TEMPLATE)

@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'BlueDwarf Platform',
        'version': '1.0.0',
        'message': 'Platform is live and operational!',
        'timestamp': '2025-08-13T18:00:00Z',
        'environment': 'production',
        'deployment': 'Heroku',
        'endpoints': {
            'home': '/',
            'about': '/about',
            'contact': '/contact',
            'health': '/api/health'
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

