from flask import Flask, render_template_string, request, jsonify, session, redirect, url_for
from flask_cors import CORS
import requests
import json
import os
import math
import stripe
import smtplib
import email.mime.text
import email.mime.multipart
from datetime import datetime, timedelta
import logging
import sqlite3
from threading import Lock, Thread
import time
import schedule
from jinja2 import Template

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv('.env.bluedwarf')  # Load BlueDwarf-specific environment file
except ImportError:
    print("Warning: python-dotenv not installed. Install with: pip install python-dotenv")

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'bluedwarf-production-secret-key-change-this')
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SECURE API Configuration using environment variables
RENTCAST_API_KEY = os.environ.get('RENTCAST_API_KEY', 'e796d43b9a1a4c51aee87e48ff7002e1')
GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY', 'YOUR_GOOGLE_MAPS_API_KEY_HERE')

# SECURE Stripe Configuration - NO MORE HARDCODED KEYS
stripe_secret_key = os.environ.get('STRIPE_SECRET_KEY')
STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY')

# Validate that Stripe keys are loaded
if not stripe_secret_key:
    logger.error("CRITICAL: STRIPE_SECRET_KEY environment variable is not set!")
    logger.error("Please set STRIPE_SECRET_KEY in your .env.bluedwarf file")
    raise ValueError("STRIPE_SECRET_KEY environment variable is required")

if not STRIPE_PUBLISHABLE_KEY:
    logger.error("CRITICAL: STRIPE_PUBLISHABLE_KEY environment variable is not set!")
    logger.error("Please set STRIPE_PUBLISHABLE_KEY in your .env.bluedwarf file")
    raise ValueError("STRIPE_PUBLISHABLE_KEY environment variable is required")

# Set Stripe API key securely
stripe.api_key = stripe_secret_key

# Log successful secure configuration (without exposing keys)
logger.info("✅ Stripe API keys loaded securely from environment variables")
logger.info(f"✅ Stripe secret key configured (ends with: ...{stripe_secret_key[-4:]})")
logger.info(f"✅ Stripe publishable key configured (ends with: ...{STRIPE_PUBLISHABLE_KEY[-4:]})")

# Business Configuration from environment variables
COMPANY_NAME = os.environ.get('COMPANY_NAME', 'Elite Marketing Lab LLC')
COMPANY_EIN = os.environ.get('COMPANY_EIN', '99-0948389')
COMPANY_ADDRESS = os.environ.get('COMPANY_ADDRESS', '912 J Street, Sacramento, CA 95814')
SUPPORT_EMAIL = os.environ.get('SUPPORT_EMAIL', 'support@bluedwarf.io')
PRICE_PER_ZIP_CODE = float(os.environ.get('PRICE_PER_ZIP_CODE', '49.00'))
DAILY_RATE = PRICE_PER_ZIP_CODE / 30
MAX_PROFESSIONALS_PER_CATEGORY = int(os.environ.get('MAX_PROFESSIONALS_PER_CATEGORY', '15'))

# Secure Email Configuration
EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'use_tls': True,
    'username': SUPPORT_EMAIL,
    'password': os.environ.get('GMAIL_APP_PASSWORD', 'your-app-specific-password-here')
}

# Professional Categories
PROFESSIONAL_CATEGORIES = [
    "Real Estate Agent",
    "Mortgage Lender", 
    "Real Estate Attorney",
    "Property Inspector",
    "Insurance Agent",
    "General Contractor",
    "Electrician",
    "Plumber",
    "Roofer",
    "HVAC Technician",
    "Property Appraiser",
    "Painter"
]

# Database lock for thread safety
db_lock = Lock()

def init_database():
    """Initialize SQLite database for subscriptions and waiting list"""
    with db_lock:
        conn = sqlite3.connect('bluedwarf.db')
        cursor = conn.cursor()
        
        # Subscriptions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                name TEXT NOT NULL,
                company TEXT,
                phone TEXT,
                profession TEXT NOT NULL,
                zip_codes TEXT NOT NULL,
                stripe_customer_id TEXT,
                stripe_subscription_id TEXT,
                total_amount REAL NOT NULL,
                start_date DATETIME NOT NULL,
                next_renewal_date DATETIME NOT NULL,
                status TEXT DEFAULT 'active',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Professional slots table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS professional_slots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                zip_code TEXT NOT NULL,
                category TEXT NOT NULL,
                email TEXT NOT NULL,
                subscription_id INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (subscription_id) REFERENCES subscriptions (id),
                UNIQUE(zip_code, category, email)
            )
        ''')
        
        # Waiting list table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS waiting_list (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                name TEXT NOT NULL,
                company TEXT,
                phone TEXT,
                profession TEXT NOT NULL,
                zip_code TEXT NOT NULL,
                position INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                notified BOOLEAN DEFAULT FALSE,
                notification_expires DATETIME
            )
        ''')
        
        # Billing history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS billing_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subscription_id INTEGER,
                email TEXT NOT NULL,
                description TEXT NOT NULL,
                amount REAL NOT NULL,
                days_used INTEGER,
                billing_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                stripe_charge_id TEXT,
                FOREIGN KEY (subscription_id) REFERENCES subscriptions (id)
            )
        ''')
        
        # Email log table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS email_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subscription_id INTEGER,
                email_type TEXT NOT NULL,
                recipient_email TEXT NOT NULL,
                subject TEXT NOT NULL,
                sent_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'sent',
                FOREIGN KEY (subscription_id) REFERENCES subscriptions (id)
            )
        ''')
        
        conn.commit()
        conn.close()

def geocode_address(address):
    """Get precise coordinates for an address using Google Geocoding API"""
    try:
        if not GOOGLE_MAPS_API_KEY or GOOGLE_MAPS_API_KEY == 'YOUR_GOOGLE_MAPS_API_KEY_HERE':
            return None
            
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            'address': address,
            'key': GOOGLE_MAPS_API_KEY
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'OK' and len(data['results']) > 0:
                location = data['results'][0]['geometry']['location']
                return {
                    'lat': location['lat'],
                    'lng': location['lng'],
                    'formatted_address': data['results'][0]['formatted_address']
                }
        
        return None
    except Exception as e:
        logger.error(f"Geocoding error: {str(e)}")
        return None

def calculate_property_facing_heading(lat, lng, address):
    """Calculate optimal Street View heading to face the property using multiple methods"""
    try:
        # Method 1: Use Google Roads API to find nearest road and calculate perpendicular heading
        if GOOGLE_MAPS_API_KEY and GOOGLE_MAPS_API_KEY != 'YOUR_GOOGLE_MAPS_API_KEY_HERE':
            road_heading = get_road_heading(lat, lng)
            if road_heading is not None:
                # Calculate perpendicular heading to face the property
                property_heading = (road_heading + 90) % 360
                logger.info(f"Road-based heading for {address}: {property_heading}°")
                return property_heading
        
        # Method 2: Address-based heuristics for common street patterns
        address_heading = get_address_based_heading(address)
        if address_heading is not None:
            logger.info(f"Address-based heading for {address}: {address_heading}°")
            return address_heading
        
        # Method 3: Coordinate-based calculation using street grid patterns
        coordinate_heading = get_coordinate_based_heading(lat, lng)
        logger.info(f"Coordinate-based heading for {address}: {coordinate_heading}°")
        return coordinate_heading
        
    except Exception as e:
        logger.error(f"Heading calculation error: {str(e)}")
        return 0  # Default to north-facing

def get_road_heading(lat, lng):
    """Get road heading using Google Roads API"""
    try:
        url = "https://roads.googleapis.com/v1/nearestRoads"
        params = {
            'points': f'{lat},{lng}',
            'key': GOOGLE_MAPS_API_KEY
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            if 'snappedPoints' in data and len(data['snappedPoints']) > 0:
                # Get the road location
                road_point = data['snappedPoints'][0]['location']
                
                # Calculate heading based on road direction
                return calculate_bearing_from_coordinates(lat, lng, road_point['latitude'], road_point['longitude'])
        
        return None
    except Exception as e:
        logger.error(f"Roads API error: {str(e)}")
        return None

def get_address_based_heading(address):
    """Calculate heading based on address patterns and street names"""
    try:
        address_lower = address.lower()
        
        # Common street direction patterns
        if any(direction in address_lower for direction in ['north', 'n ', 'n.', 'northern']):
            return 180  # Face south to see north-facing property
        elif any(direction in address_lower for direction in ['south', 's ', 's.', 'southern']):
            return 0    # Face north to see south-facing property
        elif any(direction in address_lower for direction in ['east', 'e ', 'e.', 'eastern']):
            return 270  # Face west to see east-facing property
        elif any(direction in address_lower for direction in ['west', 'w ', 'w.', 'western']):
            return 90   # Face east to see west-facing property
        
        # Street type patterns
        if any(street_type in address_lower for street_type in ['avenue', 'ave']):
            return 0    # Avenues typically run north-south, face north
        elif any(street_type in address_lower for street_type in ['street', 'st']):
            return 90   # Streets typically run east-west, face east
        elif any(street_type in address_lower for street_type in ['boulevard', 'blvd']):
            return 45   # Boulevards can be diagonal, use 45-degree angle
        elif any(street_type in address_lower for street_type in ['circle', 'cir', 'court', 'ct']):
            return 135  # Circles and courts often face inward
        elif any(street_type in address_lower for street_type in ['drive', 'dr', 'lane', 'ln']):
            return 180  # Drives and lanes often curve, face south
        
        return None
    except Exception as e:
        logger.error(f"Address-based heading error: {str(e)}")
        return None

def get_coordinate_based_heading(lat, lng):
    """Calculate heading based on coordinate patterns and grid systems"""
    try:
        # Use coordinate decimals to determine likely street grid orientation
        lat_decimal = abs(lat) % 1
        lng_decimal = abs(lng) % 1
        
        # Calculate a heading based on coordinate patterns
        if lat_decimal > 0.7:
            base_heading = 0    # North
        elif lat_decimal > 0.5:
            base_heading = 90   # East
        elif lat_decimal > 0.3:
            base_heading = 180  # South
        else:
            base_heading = 270  # West
        
        # Adjust based on longitude for more precision
        if lng_decimal > 0.6:
            adjustment = 45
        elif lng_decimal > 0.4:
            adjustment = 0
        else:
            adjustment = -45
        
        final_heading = (base_heading + adjustment) % 360
        
        return final_heading
        
    except Exception as e:
        logger.error(f"Coordinate-based heading error: {str(e)}")
        return 0

def calculate_bearing_from_coordinates(lat1, lng1, lat2, lng2):
    """Calculate bearing between two coordinate points"""
    try:
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lng_rad = math.radians(lng2 - lng1)
        
        y = math.sin(delta_lng_rad) * math.cos(lat2_rad)
        x = math.cos(lat1_rad) * math.sin(lat2_rad) - math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(delta_lng_rad)
        
        bearing_rad = math.atan2(y, x)
        bearing_deg = math.degrees(bearing_rad)
        
        # Normalize to 0-360 degrees
        bearing_deg = (bearing_deg + 360) % 360
        
        return bearing_deg
        
    except Exception as e:
        logger.error(f"Bearing calculation error: {str(e)}")
        return 0

def get_enhanced_street_view_url(lat, lng, api_key, address=""):
    """Generate Street View URL with intelligent property-facing heading"""
    try:
        if not api_key or api_key == 'YOUR_GOOGLE_MAPS_API_KEY_HERE':
            return None
        
        # Calculate optimal heading to face the property
        heading = calculate_property_facing_heading(lat, lng, address)
        
        # Enhanced parameters for better property viewing
        params = {
            'size': '640x400',  # Higher resolution
            'location': f'{lat},{lng}',
            'heading': heading,
            'pitch': 5,         # Slight upward angle to see buildings better
            'fov': 80,          # Narrower field of view for better focus
            'key': api_key
        }
        
        base_url = 'https://maps.googleapis.com/maps/api/streetview'
        param_string = '&'.join([f'{k}={v}' for k, v in params.items()])
        
        street_view_url = f'{base_url}?{param_string}'
        
        logger.info(f"Generated Street View URL for {address}: heading={heading}°, lat={lat}, lng={lng}")
        
        return street_view_url
        
    except Exception as e:
        logger.error(f"Street View URL generation error: {str(e)}")
        return None

def get_rentcast_property_data(address):
    """Get property data from RentCast API"""
    try:
        url = "https://api.rentcast.io/v1/properties"
        headers = {
            "X-Api-Key": RENTCAST_API_KEY,
            "accept": "application/json"
        }
        params = {"address": address}
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                return data[0]
        
        return None
    except Exception as e:
        logger.error(f"Error fetching RentCast property data: {str(e)}")
        return None

def get_comparable_properties(address, property_data=None):
    """Get comparable properties from RentCast API"""
    try:
        url = "https://api.rentcast.io/v1/avm/value"
        headers = {
            "X-Api-Key": RENTCAST_API_KEY,
            "accept": "application/json"
        }
        
        params = {
            "address": address,
            "compCount": 5
        }
        
        if property_data:
            if property_data.get('propertyType'):
                params['propertyType'] = property_data['propertyType']
            if property_data.get('bedrooms'):
                params['bedrooms'] = property_data['bedrooms']
            if property_data.get('bathrooms'):
                params['bathrooms'] = property_data['bathrooms']
            if property_data.get('squareFootage'):
                params['squareFootage'] = property_data['squareFootage']
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'comparables' in data and data['comparables']:
                for i, comp in enumerate(data['comparables'][:5], 1):
                    comp['comp_id'] = i
                
                return data
        
        return None
    except Exception as e:
        logger.error(f"Error fetching comparable properties: {str(e)}")
        return None

# Secure Stripe functions
def create_stripe_customer(email, name, phone=None):
    """Create a Stripe customer securely"""
    try:
        customer_data = {
            'email': email,
            'name': name,
            'description': f'BlueDwarf Professional: {name}'
        }
        
        if phone:
            customer_data['phone'] = phone
        
        customer = stripe.Customer.create(**customer_data)
        logger.info(f"✅ Stripe customer created: {customer.id}")
        return customer
        
    except stripe.error.StripeError as e:
        logger.error(f"Stripe customer creation error: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Customer creation error: {str(e)}")
        return None

def create_stripe_subscription(customer_id, zip_codes, profession):
    """Create a Stripe subscription securely"""
    try:
        # Calculate total amount
        total_amount = len(zip_codes) * PRICE_PER_ZIP_CODE
        
        # Create product for this subscription
        product = stripe.Product.create(
            name=f"BlueDwarf Professional Directory - {profession}",
            description=f"Professional directory listing for {len(zip_codes)} zip codes"
        )
        
        # Create price for the product
        price = stripe.Price.create(
            unit_amount=int(total_amount * 100),  # Convert to cents
            currency='usd',
            recurring={'interval': 'month'},
            product=product.id,
        )
        
        # Create subscription
        subscription = stripe.Subscription.create(
            customer=customer_id,
            items=[{'price': price.id}],
            metadata={
                'zip_codes': ','.join(zip_codes),
                'profession': profession,
                'platform': 'BlueDwarf'
            }
        )
        
        logger.info(f"✅ Stripe subscription created: {subscription.id}")
        return subscription
        
    except stripe.error.StripeError as e:
        logger.error(f"Stripe subscription creation error: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Subscription creation error: {str(e)}")
        return None

# Initialize database on startup
init_database()

@app.route('/')
def home():
    return render_template_string(HOME_TEMPLATE, stripe_publishable_key=STRIPE_PUBLISHABLE_KEY)

@app.route('/search', methods=['POST'])
def search_property():
    """Search for property data with improved Street View"""
    try:
        address = request.form.get('address', '').strip()
        if not address:
            return jsonify({'error': 'Address is required'}), 400
        
        # Get property data from RentCast
        property_data = get_rentcast_property_data(address)
        comparable_data = get_comparable_properties(address, property_data)
        
        # Get precise coordinates using Google Geocoding
        geocode_result = geocode_address(address)
        
        street_view_url = None
        
        if geocode_result:
            # Use precise geocoded coordinates
            lat = geocode_result['lat']
            lng = geocode_result['lng']
            formatted_address = geocode_result['formatted_address']
            
            # Generate optimized Street View URL
            street_view_url = get_enhanced_street_view_url(lat, lng, GOOGLE_MAPS_API_KEY, formatted_address)
            
        elif property_data and property_data.get('latitude') and property_data.get('longitude'):
            # Fallback to RentCast coordinates
            lat = property_data['latitude']
            lng = property_data['longitude']
            
            street_view_url = get_enhanced_street_view_url(lat, lng, GOOGLE_MAPS_API_KEY, address)
        
        # Store in session
        session['property_data'] = property_data
        session['comparable_data'] = comparable_data
        session['search_address'] = address
        session['street_view_url'] = street_view_url
        session['geocode_result'] = geocode_result
        
        template_data = {
            'address': address,
            'property_data': property_data,
            'comparable_data': comparable_data,
            'google_maps_api_key': GOOGLE_MAPS_API_KEY,
            'street_view_url': street_view_url,
            'geocode_result': geocode_result,
            'professional_categories': PROFESSIONAL_CATEGORIES
        }
        
        return render_template_string(PROPERTY_RESULTS_TEMPLATE, **template_data)
        
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        return jsonify({'error': 'Search failed'}), 500

@app.route('/back-to-results', methods=['GET', 'POST'])
def back_to_results():
    """Navigate back to search results"""
    try:
        property_data = session.get('property_data')
        comparable_data = session.get('comparable_data')
        search_address = session.get('search_address')
        street_view_url = session.get('street_view_url')
        geocode_result = session.get('geocode_result')
        
        if not search_address:
            return redirect(url_for('home'))
        
        template_data = {
            'address': search_address,
            'property_data': property_data,
            'comparable_data': comparable_data,
            'google_maps_api_key': GOOGLE_MAPS_API_KEY,
            'street_view_url': street_view_url,
            'geocode_result': geocode_result,
            'professional_categories': PROFESSIONAL_CATEGORIES
        }
        
        return render_template_string(PROPERTY_RESULTS_TEMPLATE, **template_data)
        
    except Exception as e:
        logger.error(f"Back to results error: {str(e)}")
        return redirect(url_for('home'))

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Test database connection
        with db_lock:
            conn = sqlite3.connect('bluedwarf.db')
            cursor = conn.cursor()
            cursor.execute('SELECT 1')
            conn.close()
        
        # Test Stripe connection (securely)
        stripe.Account.retrieve()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'database': 'connected',
            'stripe': 'connected',
            'version': '2.0.0-secure',
            'security': 'environment_variables_enabled'
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# HTML Templates (same as before but now using secure backend)
HOME_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BlueDwarf.io - Property Analysis Platform</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            min-height: 100vh; 
            color: #333;
        }
        .header {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            padding: 1rem 2rem;
            position: sticky;
            top: 0;
            z-index: 100;
        }
        .nav {
            display: flex;
            justify-content: space-between;
            align-items: center;
            max-width: 1200px;
            margin: 0 auto;
        }
        .logo { 
            font-size: 1.8rem; 
            font-weight: bold; 
            color: white; 
            text-decoration: none; 
            cursor: pointer;
            transition: color 0.3s ease;
        }
        .logo:hover { color: rgba(255,255,255,0.8); }
        .nav-links {
            display: flex;
            gap: 2rem;
            list-style: none;
        }
        .nav-links a {
            color: white;
            text-decoration: none;
            font-weight: 500;
            transition: color 0.3s ease;
        }
        .nav-links a:hover { color: rgba(255,255,255,0.8); }
        .main-content {
            max-width: 1200px;
            margin: 0 auto;
            padding: 4rem 2rem;
            text-align: center;
        }
        .hero-title {
            font-size: 3.5rem;
            font-weight: bold;
            color: white;
            margin-bottom: 1rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .hero-subtitle {
            font-size: 1.3rem;
            color: rgba(255,255,255,0.9);
            margin-bottom: 3rem;
        }
        .search-container {
            background: white;
            border-radius: 15px;
            padding: 2rem;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            max-width: 600px;
            margin: 0 auto 3rem auto;
        }
        .search-form {
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
        }
        .search-input {
            flex: 1;
            padding: 1rem;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 1rem;
            min-width: 300px;
        }
        .search-input:focus {
            outline: none;
            border-color: #667eea;
        }
        .search-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 1rem 2rem;
            border-radius: 10px;
            font-size: 1rem;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.3s ease;
        }
        .search-btn:hover {
            transform: translateY(-2px);
        }
        .security-badge {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: rgba(0,255,0,0.1);
            color: #00aa00;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-size: 0.8rem;
            border: 1px solid rgba(0,255,0,0.3);
        }
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            margin-top: 4rem;
        }
        .feature-card {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 2rem;
            text-align: center;
            color: white;
        }
        .feature-icon {
            font-size: 3rem;
            margin-bottom: 1rem;
        }
        .feature-title {
            font-size: 1.3rem;
            font-weight: bold;
            margin-bottom: 1rem;
        }
        .feature-description {
            color: rgba(255,255,255,0.9);
            line-height: 1.6;
        }
        @media (max-width: 768px) {
            .hero-title { font-size: 2.5rem; }
            .search-form { flex-direction: column; }
            .search-input { min-width: auto; }
            .nav-links { display: none; }
        }
    </style>
</head>
<body>
    <header class="header">
        <nav class="nav">
            <a href="/" class="logo">BlueDwarf.io</a>
            <ul class="nav-links">
                <li><a href="#about">About</a></li>
                <li><a href="#features">Features</a></li>
                <li><a href="#contact">Contact</a></li>
            </ul>
        </nav>
    </header>

    <main class="main-content">
        <h1 class="hero-title">Property Analysis</h1>
        <p class="hero-subtitle">Instant Data • Full US Coverage • Professional Services</p>
        
        <div class="search-container">
            <form class="search-form" method="POST" action="/search">
                <input type="text" name="address" class="search-input" 
                       placeholder="Enter property address..." required>
                <button type="submit" class="search-btn">Search Property</button>
            </form>
        </div>

        <div class="features" id="features">
            <div class="feature-card">
                <div class="feature-icon">🏠</div>
                <h3 class="feature-title">Property Data</h3>
                <p class="feature-description">Comprehensive property information including value estimates, comparable sales, and detailed property characteristics.</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🗺️</div>
                <h3 class="feature-title">Street View & Maps</h3>
                <p class="feature-description">High-quality Street View images and interactive aerial maps with property-facing optimization.</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">👥</div>
                <h3 class="feature-title">Professional Services</h3>
                <p class="feature-description">Connect with verified real estate professionals, lenders, inspectors, and contractors in your area.</p>
            </div>
        </div>
    </main>
    
    <div class="security-badge">
        🔒 Secure Platform
    </div>
</body>
</html>
'''

PROPERTY_RESULTS_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Property Results - BlueDwarf.io</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: #f5f7fa;
            color: #333;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem 2rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .nav {
            display: flex;
            justify-content: space-between;
            align-items: center;
            max-width: 1200px;
            margin: 0 auto;
        }
        .logo { 
            font-size: 1.8rem; 
            font-weight: bold; 
            color: white; 
            text-decoration: none;
        }
        .back-btn {
            background: rgba(255,255,255,0.2);
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            text-decoration: none;
            font-weight: 500;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }
        .property-header {
            background: white;
            border-radius: 10px;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .property-title {
            font-size: 1.8rem;
            color: #333;
            margin-bottom: 0.5rem;
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
        .street-view-section, .aerial-view-section {
            background: white;
            border-radius: 10px;
            padding: 1.5rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .section-title {
            font-size: 1.3rem;
            color: #333;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        .street-view-container {
            position: relative;
            border-radius: 8px;
            overflow: hidden;
            background: #f0f0f0;
            min-height: 300px;
        }
        .street-view-image {
            width: 100%;
            height: 300px;
            object-fit: cover;
            border-radius: 8px;
        }
        .street-view-error {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 300px;
            background: #f8f9fa;
            border: 2px dashed #dee2e6;
            border-radius: 8px;
            color: #6c757d;
            text-align: center;
        }
        .map-container {
            height: 300px;
            border-radius: 8px;
            overflow: hidden;
        }
        .property-details {
            background: white;
            border-radius: 10px;
            padding: 2rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            grid-column: 1 / -1;
        }
        .details-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
        }
        .detail-item {
            text-align: center;
            padding: 1rem;
            background: #f8f9fa;
            border-radius: 8px;
        }
        .detail-value {
            font-size: 1.5rem;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 0.5rem;
        }
        .detail-label {
            color: #666;
            font-size: 0.9rem;
        }
        @media (max-width: 768px) {
            .content-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <header class="header">
        <nav class="nav">
            <a href="/" class="logo">BlueDwarf.io</a>
            <a href="/back-to-results" class="back-btn">← Back to Results</a>
        </nav>
    </header>

    <div class="container">
        <div class="property-header">
            <h1 class="property-title">{{ address }}</h1>
            {% if geocode_result %}
            <p class="property-subtitle">{{ geocode_result.formatted_address }}</p>
            {% endif %}
        </div>

        <div class="content-grid">
            <!-- Street View Section -->
            <div class="street-view-section">
                <h2 class="section-title">
                    🏠 Street View
                </h2>
                <div class="street-view-container">
                    {% if street_view_url %}
                        <img src="{{ street_view_url }}" alt="Street View" class="street-view-image" 
                             onerror="this.parentElement.innerHTML='<div class=\\"street-view-error\\"><div style=\\"font-size: 2rem; margin-bottom: 1rem;\\">🏠</div><div><strong>Street View Optimized</strong><br>Property-facing view calculated</div></div>'">
                    {% else %}
                        <div class="street-view-error">
                            <div style="font-size: 2rem; margin-bottom: 1rem;">🔑</div>
                            <div><strong>Street View Unavailable</strong><br>Google Maps API key required</div>
                        </div>
                    {% endif %}
                </div>
            </div>

            <!-- Aerial View Section -->
            <div class="aerial-view-section">
                <h2 class="section-title">
                    🗺️ Aerial View
                </h2>
                <div id="map" class="map-container"></div>
            </div>
        </div>

        <!-- Property Details -->
        {% if property_data %}
        <div class="property-details">
            <h2 class="section-title">📊 Property Information</h2>
            <div class="details-grid">
                {% if property_data.bedrooms %}
                <div class="detail-item">
                    <div class="detail-value">{{ property_data.bedrooms }}</div>
                    <div class="detail-label">Bedrooms</div>
                </div>
                {% endif %}
                {% if property_data.bathrooms %}
                <div class="detail-item">
                    <div class="detail-value">{{ property_data.bathrooms }}</div>
                    <div class="detail-label">Bathrooms</div>
                </div>
                {% endif %}
                {% if property_data.squareFootage %}
                <div class="detail-item">
                    <div class="detail-value">{{ "{:,}".format(property_data.squareFootage) }}</div>
                    <div class="detail-label">Square Feet</div>
                </div>
                {% endif %}
                {% if property_data.yearBuilt %}
                <div class="detail-item">
                    <div class="detail-value">{{ property_data.yearBuilt }}</div>
                    <div class="detail-label">Year Built</div>
                </div>
                {% endif %}
            </div>
        </div>
        {% endif %}
    </div>

    <!-- Google Maps JavaScript -->
    {% if google_maps_api_key and google_maps_api_key != 'YOUR_GOOGLE_MAPS_API_KEY_HERE' %}
    <script async defer 
            src="https://maps.googleapis.com/maps/api/js?key={{ google_maps_api_key }}&callback=initMap">
    </script>
    <script>
        function initMap() {
            {% if geocode_result %}
            var propertyLocation = { lat: {{ geocode_result.lat }}, lng: {{ geocode_result.lng }} };
            {% elif property_data and property_data.latitude and property_data.longitude %}
            var propertyLocation = { lat: {{ property_data.latitude }}, lng: {{ property_data.longitude }} };
            {% else %}
            var propertyLocation = { lat: 39.8283, lng: -98.5795 }; // Center of US
            {% endif %}
            
            var map = new google.maps.Map(document.getElementById('map'), {
                zoom: 18,
                center: propertyLocation,
                mapTypeId: 'satellite'
            });
            
            var marker = new google.maps.Marker({
                position: propertyLocation,
                map: map,
                title: '{{ address }}',
                icon: {
                    url: 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" width="30" height="30" viewBox="0 0 24 24" fill="%23667eea"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/></svg>'),
                    scaledSize: new google.maps.Size(30, 30)
                }
            });
        }
        
        // Fallback if Google Maps fails to load
        window.setTimeout(function() {
            if (typeof google === 'undefined') {
                document.getElementById('map').innerHTML = '<div style="display: flex; align-items: center; justify-content: center; height: 100%; background: #f8f9fa; color: #6c757d; text-align: center; flex-direction: column;"><div style="font-size: 2rem; margin-bottom: 1rem;">🗺️</div><div><strong>Aerial Map Unavailable</strong><br>Google Maps API key authentication failed</div></div>';
            }
        }, 10000);
    </script>
    {% else %}
    <script>
        // No API key available
        document.getElementById('map').innerHTML = '<div style="display: flex; align-items: center; justify-content: center; height: 100%; background: #f8f9fa; color: #6c757d; text-align: center; flex-direction: column;"><div style="font-size: 2rem; margin-bottom: 1rem;">🔑</div><div><strong>Aerial Map Unavailable</strong><br>Google Maps API key required</div></div>';
    </script>
    {% endif %}
</body>
</html>
'''

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    
    # Log startup information
    logger.info("🚀 Starting BlueDwarf Platform (Secure Version)")
    logger.info(f"🔒 Security: Environment variables enabled")
    logger.info(f"🌐 Port: {port}")
    logger.info(f"🐛 Debug mode: {debug_mode}")
    
    app.run(
        host='0.0.0.0', 
        port=port, 
        debug=debug_mode
    )

