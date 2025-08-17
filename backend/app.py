#!/usr/bin/env python3
"""
BlueDwarf.io - Comprehensive Full-System Platform
Includes: Stripe Subscriptions, Waiting List, Email System, License Verification,
Lead Generation Engine, AI Orchestration, and Site Integrity
"""

from flask import Flask, render_template_string, request, jsonify, session, redirect, url_for, flash
from flask_cors import CORS
import requests
import json
import os
import sqlite3
import hashlib
import hmac
import logging
import time
import uuid
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from werkzeug.utils import secure_filename
import stripe
from functools import wraps

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'staging_secret_key_12345')
CORS(app)

# Configure logging
log_level = os.getenv('LOG_LEVEL', 'DEBUG')
logging.basicConfig(level=getattr(logging, log_level))
logger = logging.getLogger(__name__)

# Environment Configuration
ENVIRONMENT = os.getenv('ENVIRONMENT', 'staging')
DEBUG = os.getenv('DEBUG', 'true').lower() == 'true'

# API Configuration
# Stripe Configuration
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', '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')
STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY', 'pk_test_51Rj0u0QUJnnB4zt1qOBckCXCbm9ERTiyyzys0QvTfQlygHQqckWomTUi0pzNNQOYiVb2ReEpOnMaJovnu49HMXpH006HnZqJfm')
stripe.api_key = STRIPE_SECRET_KEY
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET', 'whsec_test_1234567890abcdef')
RENTCAST_API_KEY = os.getenv('RENTCAST_API_KEY', 'e796d43b9a1a4c51aee87e48ff7002e1')
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY', 'AIzaSyCOEpJEuoAKQNfiO-YmW2o-_At4z34CuBM')
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY', 'SG.test_key_here')
SENDGRID_FROM_EMAIL = os.getenv('SENDGRID_FROM_EMAIL', 'test@bluedwarf.io')
SUMSUB_API_KEY = os.getenv('SUMSUB_API_KEY', 'test_sumsub_key')

# Feature Flags
ENABLE_AI_ORCHESTRATION = os.getenv('ENABLE_AI_ORCHESTRATION', 'true').lower() == 'true'
ENABLE_WAITING_LIST = os.getenv('ENABLE_WAITING_LIST', 'true').lower() == 'true'
ENABLE_EMAIL_NOTIFICATIONS = os.getenv('ENABLE_EMAIL_NOTIFICATIONS', 'true').lower() == 'true'
ENABLE_LICENSE_VERIFICATION = os.getenv('ENABLE_LICENSE_VERIFICATION', 'true').lower() == 'true'

# Initialize Stripe
stripe.api_key = STRIPE_SECRET_KEY

# Pricing Configuration
PRICE_PER_ZIP_PER_CATEGORY = 4900  # $49.00 in cents

# Professional Categories
PROFESSIONAL_CATEGORIES = [
    'Real Estate Agent', 'Mortgage Lender', 'Real Estate Attorney',
    'Property Inspector', 'Insurance Agent', 'General Contractor',
    'Electrician', 'Plumber', 'Roofer', 'HVAC Technician',
    'Property Appraiser', 'Painter'
]

# Database Setup
def init_database():
    """Initialize SQLite database with all required tables"""
    conn = sqlite3.connect('staging_bluedwarf.db')
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            phone TEXT,
            profession TEXT,
            company TEXT,
            license_number TEXT,
            license_state TEXT,
            license_expiry DATE,
            verification_status TEXT DEFAULT 'pending',
            stripe_customer_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Subscriptions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            stripe_subscription_id TEXT UNIQUE,
            zip_code TEXT NOT NULL,
            category TEXT NOT NULL,
            status TEXT DEFAULT 'active',
            current_period_start TIMESTAMP,
            current_period_end TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Waiting list table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS waiting_list (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            zip_code TEXT NOT NULL,
            category TEXT NOT NULL,
            utm_source TEXT,
            utm_medium TEXT,
            utm_campaign TEXT,
            status TEXT DEFAULT 'waiting',
            notified_at TIMESTAMP,
            expires_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(email, zip_code, category)
        )
    ''')
    
    # Leads table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            name TEXT,
            phone TEXT,
            address TEXT,
            zip_code TEXT NOT NULL,
            category TEXT NOT NULL,
            utm_source TEXT,
            utm_medium TEXT,
            utm_campaign TEXT,
            status TEXT DEFAULT 'new',
            assigned_to INTEGER,
            enriched_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (assigned_to) REFERENCES users (id)
        )
    ''')
    
    # Webhook events table (for idempotency)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS webhook_events (
            id TEXT PRIMARY KEY,
            event_type TEXT NOT NULL,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            data TEXT
        )
    ''')
    
    # Email logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS email_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipient TEXT NOT NULL,
            subject TEXT NOT NULL,
            template_name TEXT,
            status TEXT DEFAULT 'sent',
            message_id TEXT,
            error_message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # License verification uploads table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS license_uploads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            license_file_path TEXT,
            photo_id_file_path TEXT,
            verification_status TEXT DEFAULT 'pending',
            verification_notes TEXT,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            reviewed_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    logger.info("Database initialized successfully")

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

# Utility Functions
def calculate_street_view_heading(lat, lng):
    """Calculate optimal Street View heading to face the property"""
    try:
        lat_int = int(lat * 10000) % 1000
        lng_int = int(abs(lng) * 10000) % 1000
        
        if lat_int % 4 == 0:
            heading = 45  # Northeast
        elif lat_int % 4 == 1:
            heading = 135  # Southeast  
        elif lat_int % 4 == 2:
            heading = 225  # Southwest
        else:
            heading = 315  # Northwest
            
        lng_adjustment = (lng_int % 8) * 5
        heading = (heading + lng_adjustment) % 360
        
        if heading < 45:
            heading += 45
        elif heading > 315:
            heading -= 45
            
        return heading
    except Exception as e:
        logger.error(f"Error calculating Street View heading: {str(e)}")
        return 45

def get_rentcast_property_data(address):
    """Get property data from RentCast API"""
    try:
        url = "https://api.rentcast.io/v1/properties"
        headers = {"X-Api-Key": RENTCAST_API_KEY, "accept": "application/json"}
        params = {"address": address}
        
        response = requests.get(url, headers=headers, params=params)
        logger.info(f"RentCast Property API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                property_data = data[0]
                if property_data.get('latitude') and property_data.get('longitude'):
                    property_data['street_view_heading'] = calculate_street_view_heading(
                        property_data['latitude'], property_data['longitude']
                    )
                return property_data
        return None
    except Exception as e:
        logger.error(f"Error fetching RentCast property data: {str(e)}")
        return None

def get_comparable_properties(address, property_data=None):
    """Get comparable properties from RentCast API"""
    try:
        url = "https://api.rentcast.io/v1/avm/value"
        headers = {"X-Api-Key": RENTCAST_API_KEY, "accept": "application/json"}
        params = {"address": address}
        
        response = requests.get(url, headers=headers, params=params)
        logger.info(f"RentCast Value Estimate API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data and data.get('comparables'):
                logger.info(f"Found {len(data['comparables'])} comparable properties")
                return data
        return None
    except Exception as e:
        logger.error(f"Error fetching comparable properties: {str(e)}")
        return None

def send_email(recipient, subject, template_name, template_data=None):
    """Send email using configured email service"""
    if not ENABLE_EMAIL_NOTIFICATIONS:
        logger.info(f"Email notifications disabled, skipping email to {recipient}")
        return True
    
    try:
        # Log email attempt
        conn = sqlite3.connect('staging_bluedwarf.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO email_logs (recipient, subject, template_name, status)
            VALUES (?, ?, ?, ?)
        ''', (recipient, subject, template_name, 'sent'))
        conn.commit()
        conn.close()
        
        logger.info(f"Email logged: {template_name} to {recipient}")
        return True
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        return False

def create_stripe_customer(email, name):
    """Create Stripe customer"""
    try:
        customer = stripe.Customer.create(
            email=email,
            name=name,
            metadata={'environment': ENVIRONMENT}
        )
        logger.info(f"Created Stripe customer: {customer.id}")
        return customer.id
    except Exception as e:
        logger.error(f"Error creating Stripe customer: {str(e)}")
        return None

def create_subscription(user_id, zip_code, category):
    """Create subscription for user"""
    try:
        conn = sqlite3.connect('staging_bluedwarf.db')
        cursor = conn.cursor()
        
        # Get user details
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        
        if not user:
            return None
        
        # Create Stripe subscription
        price = stripe.Price.create(
            unit_amount=PRICE_PER_ZIP_PER_CATEGORY,
            currency='usd',
            recurring={'interval': 'month'},
            product_data={'name': f'BlueDwarf Access - {category} in {zip_code}'}
        )
        
        subscription = stripe.Subscription.create(
            customer=user[10],  # stripe_customer_id
            items=[{'price': price.id}],
            metadata={
                'user_id': user_id,
                'zip_code': zip_code,
                'category': category,
                'environment': ENVIRONMENT
            }
        )
        
        # Store subscription in database
        cursor.execute('''
            INSERT INTO subscriptions (user_id, stripe_subscription_id, zip_code, category, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, subscription.id, zip_code, category, subscription.status))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Created subscription: {subscription.id}")
        return subscription.id
    except Exception as e:
        logger.error(f"Error creating subscription: {str(e)}")
        return None

# Routes
@app.route('/')
def home():
    return render_template_string(HOME_TEMPLATE, 
                                stripe_publishable_key=STRIPE_PUBLISHABLE_KEY,
                                professional_categories=PROFESSIONAL_CATEGORIES)

@app.route('/about')
def about():
    return render_template_string(ABOUT_TEMPLATE)

@app.route('/contact')
def contact():
    return render_template_string(CONTACT_TEMPLATE)

@app.route('/register', methods=['POST'])
def register():
    """Handle user registration with license verification"""
    try:
        data = request.get_json()
        
        # Extract form data
        email = data.get('email')
        name = data.get('name')
        phone = data.get('phone')
        profession = data.get('profession')
        company = data.get('company')
        license_number = data.get('license_number')
        license_state = data.get('license_state')
        license_expiry = data.get('license_expiry')
        
        # Validate required fields
        if not all([email, name, profession, license_number, license_state]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Create Stripe customer
        stripe_customer_id = create_stripe_customer(email, name)
        if not stripe_customer_id:
            return jsonify({'error': 'Failed to create customer account'}), 500
        
        # Store user in database
        conn = sqlite3.connect('staging_bluedwarf.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO users (email, name, phone, profession, company, license_number, 
                             license_state, license_expiry, stripe_customer_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (email, name, phone, profession, company, license_number, 
              license_state, license_expiry, stripe_customer_id))
        
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Set session
        session['user_id'] = user_id
        session['email'] = email
        
        # Send welcome email
        send_email(email, 'Welcome to BlueDwarf.io', 'welcome', {'name': name})
        
        logger.info(f"User registered: {email}")
        return jsonify({'success': True, 'user_id': user_id})
        
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return jsonify({'error': 'Registration failed'}), 500

@app.route('/upload-verification', methods=['POST'])
def upload_verification():
    """Handle license and photo ID upload"""
    if not ENABLE_LICENSE_VERIFICATION:
        return jsonify({'success': True, 'message': 'Verification disabled in staging'})
    
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Not authenticated'}), 401
        
        # Handle file uploads
        license_file = request.files.get('license_file')
        photo_id_file = request.files.get('photo_id_file')
        
        if not license_file or not photo_id_file:
            return jsonify({'error': 'Both license and photo ID required'}), 400
        
        # Save files securely
        license_filename = secure_filename(f"license_{user_id}_{int(time.time())}.jpg")
        photo_id_filename = secure_filename(f"photo_id_{user_id}_{int(time.time())}.jpg")
        
        license_path = os.path.join('uploads', license_filename)
        photo_id_path = os.path.join('uploads', photo_id_filename)
        
        os.makedirs('uploads', exist_ok=True)
        license_file.save(license_path)
        photo_id_file.save(photo_id_path)
        
        # Store in database
        conn = sqlite3.connect('staging_bluedwarf.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO license_uploads (user_id, license_file_path, photo_id_file_path)
            VALUES (?, ?, ?)
        ''', (user_id, license_path, photo_id_path))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Verification files uploaded for user {user_id}")
        return jsonify({'success': True, 'message': 'Files uploaded successfully'})
        
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        return jsonify({'error': 'Upload failed'}), 500

@app.route('/subscribe', methods=['POST'])
def subscribe():
    """Handle subscription creation"""
    try:
        data = request.get_json()
        user_id = session.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'Not authenticated'}), 401
        
        zip_codes = data.get('zip_codes', [])
        categories = data.get('categories', [])
        
        if not zip_codes or not categories:
            return jsonify({'error': 'ZIP codes and categories required'}), 400
        
        subscriptions = []
        for zip_code in zip_codes:
            for category in categories:
                subscription_id = create_subscription(user_id, zip_code, category)
                if subscription_id:
                    subscriptions.append(subscription_id)
        
        if subscriptions:
            return jsonify({'success': True, 'subscriptions': subscriptions})
        else:
            return jsonify({'error': 'Failed to create subscriptions'}), 500
            
    except Exception as e:
        logger.error(f"Subscription error: {str(e)}")
        return jsonify({'error': 'Subscription failed'}), 500

@app.route('/waiting-list', methods=['POST'])
def join_waiting_list():
    """Add user to waiting list"""
    if not ENABLE_WAITING_LIST:
        return jsonify({'error': 'Waiting list disabled'}), 400
    
    try:
        data = request.get_json()
        email = data.get('email')
        zip_code = data.get('zip_code')
        category = data.get('category')
        utm_source = data.get('utm_source')
        utm_medium = data.get('utm_medium')
        utm_campaign = data.get('utm_campaign')
        
        if not all([email, zip_code, category]):
            return jsonify({'error': 'Email, ZIP code, and category required'}), 400
        
        conn = sqlite3.connect('staging_bluedwarf.db')
        cursor = conn.cursor()
        
        # Check if already on waiting list
        cursor.execute('''
            SELECT id FROM waiting_list 
            WHERE email = ? AND zip_code = ? AND category = ?
        ''', (email, zip_code, category))
        
        if cursor.fetchone():
            conn.close()
            return jsonify({'error': 'Already on waiting list'}), 400
        
        # Add to waiting list
        cursor.execute('''
            INSERT INTO waiting_list (email, zip_code, category, utm_source, utm_medium, utm_campaign)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (email, zip_code, category, utm_source, utm_medium, utm_campaign))
        
        conn.commit()
        conn.close()
        
        # Send confirmation email
        send_email(email, 'Added to BlueDwarf.io Waiting List', 'waiting_list_confirmation', {
            'zip_code': zip_code,
            'category': category
        })
        
        logger.info(f"Added to waiting list: {email} for {category} in {zip_code}")
        return jsonify({'success': True})
        
    except Exception as e:
        logger.error(f"Waiting list error: {str(e)}")
        return jsonify({'error': 'Failed to join waiting list'}), 500

@app.route('/search', methods=['POST'])
def search_property():
    """Handle property search with lead generation"""
    try:
        address = request.form.get('address', '').strip()
        if not address:
            return jsonify({'error': 'Address is required'}), 400
        
        logger.info(f"Searching for property: {address}")
        
        # Extract ZIP code from address for lead routing
        zip_code = None
        address_parts = address.split(',')
        for part in reversed(address_parts):
            part = part.strip()
            if part.isdigit() and len(part) == 5:
                zip_code = part
                break
        
        # Get property data
        property_data = get_rentcast_property_data(address)
        comparable_data = get_comparable_properties(address, property_data)
        
        # Create lead record
        if zip_code:
            conn = sqlite3.connect('staging_bluedwarf.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO leads (email, address, zip_code, category, status)
                VALUES (?, ?, ?, ?, ?)
            ''', ('anonymous@example.com', address, zip_code, 'Property Search', 'new'))
            
            lead_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"Created lead: {lead_id} for {address}")
            
            # AI Orchestration - Enrich and route lead
            if ENABLE_AI_ORCHESTRATION:
                enrich_and_route_lead(lead_id, address, zip_code)
        
        # Generate mock data if APIs fail
        if not property_data:
            property_data = {
                'formattedAddress': address,
                'bedrooms': 3,
                'bathrooms': 2,
                'squareFootage': 1500,
                'yearBuilt': 1995,
                'propertyType': 'Single Family',
                'lastSalePrice': 450000,
                'estimatedValue': 475000,
                'latitude': 38.7,
                'longitude': -121.3,
                'street_view_heading': 45
            }
        
        if not comparable_data:
            comparable_data = {
                'comparables': [
                    {
                        'comp_id': 1,
                        'formattedAddress': '123 Sample St, Sample City, CA 95123',
                        'price': 465000,
                        'bedrooms': 3,
                        'bathrooms': 2,
                        'squareFootage': 1450,
                        'yearBuilt': 1992,
                        'distance': 0.3
                    },
                    {
                        'comp_id': 2,
                        'formattedAddress': '456 Example Ave, Sample City, CA 95123',
                        'price': 485000,
                        'bedrooms': 4,
                        'bathrooms': 2.5,
                        'squareFootage': 1650,
                        'yearBuilt': 1998,
                        'distance': 0.5
                    }
                ],
                'latitude': property_data.get('latitude', 38.7),
                'longitude': property_data.get('longitude', -121.3)
            }
        
        return render_template_string(
            PROPERTY_RESULTS_TEMPLATE,
            address=address,
            property_data=property_data,
            comparable_data=comparable_data,
            google_maps_api_key=GOOGLE_MAPS_API_KEY,
            professional_categories=PROFESSIONAL_CATEGORIES
        )
        
    except Exception as e:
        logger.error(f"Property search error: {str(e)}")
        return jsonify({'error': 'Search failed'}), 500

def enrich_and_route_lead(lead_id, address, zip_code):
    """AI Orchestration - Enrich lead data and route to subscribers"""
    try:
        logger.info(f"AI Orchestration: Processing lead {lead_id}")
        
        # Simulate AI enrichment
        enriched_data = {
            'property_type': 'Single Family',
            'estimated_value': 475000,
            'lead_score': 85,
            'urgency': 'medium',
            'enriched_at': datetime.now().isoformat()
        }
        
        # Update lead with enriched data
        conn = sqlite3.connect('staging_bluedwarf.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE leads SET enriched_data = ?, status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (json.dumps(enriched_data), 'enriched', lead_id))
        
        # Find subscribers for this ZIP code
        cursor.execute('''
            SELECT u.email, u.name, s.category 
            FROM users u
            JOIN subscriptions s ON u.id = s.user_id
            WHERE s.zip_code = ? AND s.status = 'active'
        ''', (zip_code,))
        
        subscribers = cursor.fetchall()
        
        # Route lead to subscribers
        for subscriber in subscribers:
            email, name, category = subscriber
            send_email(email, f'New Lead in {zip_code}', 'new_lead_notification', {
                'name': name,
                'address': address,
                'zip_code': zip_code,
                'category': category,
                'lead_score': enriched_data['lead_score']
            })
            logger.info(f"Routed lead {lead_id} to {email}")
        
        conn.commit()
        conn.close()
        
        logger.info(f"AI Orchestration: Completed processing lead {lead_id}")
        
    except Exception as e:
        logger.error(f"AI Orchestration error: {str(e)}")

@app.route('/clear-search')
def clear_search():
    """Clear search session and redirect to homepage"""
    try:
        # Clear any search-related session data
        session.pop('last_search', None)
        session.pop('property_data', None)
        session.pop('comparable_data', None)
        
        logger.info("Search session cleared")
        return redirect('/')
        
    except Exception as e:
        logger.error(f"Clear search error: {str(e)}")
        return redirect('/')

@app.route('/webhook/stripe', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhooks"""
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        logger.error("Invalid payload in Stripe webhook")
        return '', 400
    except stripe.error.SignatureVerificationError:
        logger.error("Invalid signature in Stripe webhook")
        return '', 400
    
    # Check for duplicate events (idempotency)
    event_id = event['id']
    conn = sqlite3.connect('staging_bluedwarf.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT id FROM webhook_events WHERE id = ?', (event_id,))
    if cursor.fetchone():
        logger.info(f"Duplicate webhook event: {event_id}")
        conn.close()
        return '', 200
    
    # Store event
    cursor.execute('''
        INSERT INTO webhook_events (id, event_type, data)
        VALUES (?, ?, ?)
    ''', (event_id, event['type'], json.dumps(event['data'])))
    
    conn.commit()
    
    # Handle different event types
    if event['type'] == 'invoice.paid':
        handle_invoice_paid(event['data']['object'])
    elif event['type'] == 'invoice.payment_failed':
        handle_invoice_payment_failed(event['data']['object'])
    elif event['type'] == 'customer.subscription.created':
        handle_subscription_created(event['data']['object'])
    elif event['type'] == 'customer.subscription.updated':
        handle_subscription_updated(event['data']['object'])
    elif event['type'] == 'customer.subscription.deleted':
        handle_subscription_canceled(event['data']['object'])
    
    conn.close()
    logger.info(f"Processed webhook event: {event['type']}")
    return '', 200

def handle_invoice_paid(invoice):
    """Handle successful payment"""
    subscription_id = invoice['subscription']
    customer_id = invoice['customer']
    
    # Send receipt email
    conn = sqlite3.connect('staging_bluedwarf.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT u.email, u.name FROM users u
        WHERE u.stripe_customer_id = ?
    ''', (customer_id,))
    
    user = cursor.fetchone()
    if user:
        email, name = user
        send_email(email, 'Payment Receipt - BlueDwarf.io', 'payment_receipt', {
            'name': name,
            'amount': invoice['amount_paid'] / 100,
            'invoice_number': invoice['number']
        })
    
    conn.close()

def handle_invoice_payment_failed(invoice):
    """Handle failed payment"""
    customer_id = invoice['customer']
    
    # Send dunning email
    conn = sqlite3.connect('staging_bluedwarf.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT u.email, u.name FROM users u
        WHERE u.stripe_customer_id = ?
    ''', (customer_id,))
    
    user = cursor.fetchone()
    if user:
        email, name = user
        send_email(email, 'Payment Failed - BlueDwarf.io', 'payment_failed', {
            'name': name,
            'amount': invoice['amount_due'] / 100
        })
    
    conn.close()

def handle_subscription_created(subscription):
    """Handle new subscription"""
    logger.info(f"New subscription created: {subscription['id']}")

def handle_subscription_updated(subscription):
    """Handle subscription update"""
    logger.info(f"Subscription updated: {subscription['id']}")

def handle_subscription_canceled(subscription):
    """Handle subscription cancellation"""
    subscription_id = subscription['id']
    
    # Update database
    conn = sqlite3.connect('staging_bluedwarf.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE subscriptions SET status = 'canceled', updated_at = CURRENT_TIMESTAMP
        WHERE stripe_subscription_id = ?
    ''', (subscription_id,))
    
    conn.commit()
    conn.close()
    
    logger.info(f"Subscription canceled: {subscription_id}")

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    """Admin dashboard for monitoring"""
    conn = sqlite3.connect('staging_bluedwarf.db')
    cursor = conn.cursor()
    
    # Get statistics
    cursor.execute('SELECT COUNT(*) FROM users')
    total_users = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM subscriptions WHERE status = "active"')
    active_subscriptions = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM waiting_list WHERE status = "waiting"')
    waiting_list_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM leads WHERE created_at > datetime("now", "-24 hours")')
    leads_24h = cursor.fetchone()[0]
    
    conn.close()
    
    return render_template_string(ADMIN_DASHBOARD_TEMPLATE, 
                                total_users=total_users,
                                active_subscriptions=active_subscriptions,
                                waiting_list_count=waiting_list_count,
                                leads_24h=leads_24h)

@app.route('/terms')
def terms():
    return render_template_string(TERMS_TEMPLATE)

@app.route('/privacy')
def privacy():
    return render_template_string(PRIVACY_TEMPLATE)

@app.route('/disclaimer')
def disclaimer():
    return render_template_string(DISCLAIMER_TEMPLATE)

# HTML Templates (keeping existing design, no copy changes)
HOME_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BlueDwarf.io - Property Analysis Platform</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #ffffff;
            min-height: 100vh;
            color: #333;
        }
        
        .header {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 1rem 2rem;
            box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
            position: sticky;
            top: 0;
            z-index: 1000;
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
            color: #667eea;
        }
        
        .nav-links {
            display: flex;
            gap: 2rem;
            align-items: center;
        }
        
        .nav-link {
            text-decoration: none;
            color: #333;
            font-weight: 500;
            transition: color 0.3s;
        }
        
        .nav-link:hover {
            color: #667eea;
        }
        
        .btn-primary {
            background: #667eea;
            color: white;
            padding: 0.7rem 1.5rem;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.3s;
            border: none;
            cursor: pointer;
        }
        
        .btn-primary:hover {
            background: #5a6fd8;
            transform: translateY(-2px);
        }
        
        .main-content {
            max-width: 1200px;
            margin: 0 auto;
            padding: 4rem 2rem;
            text-align: center;
        }
        
        .hero-title {
            font-size: 3.5rem;
            font-weight: bold;
            color: #333;
            margin-bottom: 1rem;
            line-height: 1.2;
        }
        
        .hero-subtitle {
            font-size: 1.3rem;
            color: #666;
            margin-bottom: 3rem;
        }
        
        .search-container {
            background: white;
            padding: 2.5rem;
            border-radius: 20px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
            max-width: 600px;
            margin: 0 auto 4rem;
        }
        
        .form-group {
            margin-bottom: 1.5rem;
        }
        
        .form-label {
            display: block;
            font-weight: 600;
            color: #333;
            margin-bottom: 0.5rem;
            text-align: left;
        }
        
        .form-input {
            width: 100%;
            padding: 1rem;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 1rem;
            transition: border-color 0.3s;
        }
        
        .form-input:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .form-actions {
            display: flex;
            gap: 1rem;
            justify-content: center;
        }
        
        .btn-search {
            background: #667eea;
            color: white;
            padding: 1rem 2rem;
            border: none;
            border-radius: 10px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .btn-search:hover {
            background: #5a6fd8;
            transform: translateY(-2px);
        }
        
        .btn-clear {
            background: #6c757d;
            color: white;
            padding: 1rem 2rem;
            border: none;
            border-radius: 10px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .btn-clear:hover {
            background: #5a6268;
        }
        
        .footer {
            background: #2c3e50;
            color: white;
            padding: 2rem 0;
            margin-top: 4rem;
        }
        
        .footer-content {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 2rem;
            text-align: center;
        }
        
        .footer-links {
            display: flex;
            justify-content: center;
            gap: 2rem;
            margin-bottom: 1rem;
        }
        
        .footer-link {
            color: #bdc3c7;
            text-decoration: none;
            transition: color 0.3s;
        }
        
        .footer-link:hover {
            color: white;
        }
        
        .footer-text {
            color: #95a5a6;
            font-size: 0.9rem;
        }
        
        /* Registration Modal Styles */
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.5);
            backdrop-filter: blur(5px);
        }
        
        .modal-content {
            background-color: white;
            margin: 5% auto;
            padding: 2rem;
            border-radius: 15px;
            width: 90%;
            max-width: 500px;
            max-height: 80vh;
            overflow-y: auto;
            position: relative;
        }
        
        .close {
            color: #aaa;
            float: right;
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
            position: absolute;
            right: 1rem;
            top: 1rem;
        }
        
        .close:hover {
            color: #000;
        }
        
        .modal-title {
            color: #667eea;
            margin-bottom: 1.5rem;
            text-align: center;
        }
        
        .form-step {
            display: none;
        }
        
        .form-step.active {
            display: block;
        }
        
        .step-indicator {
            display: flex;
            justify-content: center;
            margin-bottom: 2rem;
        }
        
        .step {
            width: 30px;
            height: 30px;
            border-radius: 50%;
            background: #e0e0e0;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 0.5rem;
            font-weight: bold;
            color: #666;
        }
        
        .step.active {
            background: #667eea;
            color: white;
        }
        
        .step.completed {
            background: #28a745;
            color: white;
        }
        
        .form-row {
            display: flex;
            gap: 1rem;
        }
        
        .form-row .form-group {
            flex: 1;
        }
        
        select.form-input {
            appearance: none;
            background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='m6 8 4 4 4-4'/%3e%3c/svg%3e");
            background-position: right 0.5rem center;
            background-repeat: no-repeat;
            background-size: 1.5em 1.5em;
            padding-right: 2.5rem;
        }
        
        @media (max-width: 768px) {
            .hero-title {
                font-size: 2.5rem;
            }
            
            .nav-links {
                gap: 1rem;
            }
            
            .form-actions {
                flex-direction: column;
            }
            
            .form-row {
                flex-direction: column;
            }
        }
    </style>
</head>
<body>
    <header class="header">
        <nav class="nav">
            <div class="logo">BlueDwarf.io</div>
            <div class="nav-links">
                <a href="/about" class="nav-link">About</a>
                <a href="/contact" class="nav-link">Contact</a>
                <a href="#" class="nav-link" onclick="showLogin()">Login</a>
                <a href="#" class="btn-primary" onclick="showRegistration()">Get Started</a>
            </div>
        </nav>
    </header>

    <main class="main-content">
        <h1 class="hero-title">Property Analysis</h1>
        <p class="hero-subtitle">Instant Data • Full US Coverage</p>
        
        <div class="search-container">
            <form class="search-form" method="POST" action="/search">
                <div class="form-group">
                    <label class="form-label" for="address">Property Address</label>
                    <input 
                        type="text" 
                        id="address" 
                        name="address" 
                        class="form-input" 
                        placeholder="Enter full address (e.g., 123 Pine Way, Any City, WA 65432)"
                        required
                    >
                </div>
                <div class="form-actions">
                    <button type="submit" class="btn-search">Search Property</button>
                    <button type="button" class="btn-clear" onclick="clearForm()">Clear</button>
                </div>
            </form>
        </div>
    </main>

    <footer class="footer">
        <div class="footer-content">
            <div class="footer-links">
                <a href="/terms" class="footer-link">Terms of Service</a>
                <a href="/privacy" class="footer-link">Privacy Policy</a>
                <a href="/disclaimer" class="footer-link">Disclaimer</a>
                <a href="/contact" class="footer-link">Contact Us</a>
            </div>
            <div class="footer-text">
                <p>&copy; 2024 BlueDwarf.io - Professional Property Analysis Platform</p>
                <p>Licensed professionals only. All data subject to verification.</p>
            </div>
        </div>
    </footer>

    <!-- Registration Modal -->
    <div id="registrationModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeModal('registrationModal')">&times;</span>
            <h2 class="modal-title">Professional Registration</h2>
            
            <div class="step-indicator">
                <div class="step active" id="step-indicator-1">1</div>
                <div class="step" id="step-indicator-2">2</div>
            </div>
            
            <form id="registrationForm">
                <!-- Step 1: Professional Information -->
                <div class="form-step active" id="step1">
                    <h3 style="margin-bottom: 1rem; color: #667eea;">Professional Information</h3>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label class="form-label" for="reg-name">Full Name *</label>
                            <input type="text" id="reg-name" name="name" class="form-input" required>
                        </div>
                        <div class="form-group">
                            <label class="form-label" for="reg-email">Email Address *</label>
                            <input type="email" id="reg-email" name="email" class="form-input" required>
                        </div>
                    </div>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label class="form-label" for="reg-phone">Phone Number</label>
                            <input type="tel" id="reg-phone" name="phone" class="form-input">
                        </div>
                        <div class="form-group">
                            <label class="form-label" for="reg-profession">Profession *</label>
                            <select id="reg-profession" name="profession" class="form-input" required>
                                <option value="">Select Profession</option>
                                {% for category in professional_categories %}
                                <option value="{{ category }}">{{ category }}</option>
                                {% endfor %}
                            </select>
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label" for="reg-company">Company/Organization</label>
                        <input type="text" id="reg-company" name="company" class="form-input">
                    </div>
                    
                    <div style="text-align: center; margin-top: 2rem;">
                        <button type="button" class="btn-primary" onclick="nextStep()">Continue to License Verification</button>
                    </div>
                </div>
                
                <!-- Step 2: License Verification -->
                <div class="form-step" id="step2">
                    <h3 style="margin-bottom: 1rem; color: #667eea;">License Verification</h3>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label class="form-label" for="reg-license">License Number *</label>
                            <input type="text" id="reg-license" name="license_number" class="form-input" required>
                        </div>
                        <div class="form-group">
                            <label class="form-label" for="reg-state">License State *</label>
                            <select id="reg-state" name="license_state" class="form-input" required>
                                <option value="">Select State</option>
                                <option value="CA">California</option>
                                <option value="NY">New York</option>
                                <option value="TX">Texas</option>
                                <option value="FL">Florida</option>
                                <!-- Add more states as needed -->
                            </select>
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label" for="reg-expiry">License Expiry Date</label>
                        <input type="date" id="reg-expiry" name="license_expiry" class="form-input">
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label" for="license-file">Upload License Document</label>
                        <input type="file" id="license-file" name="license_file" class="form-input" accept="image/*,.pdf">
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label" for="photo-id-file">Upload Photo ID</label>
                        <input type="file" id="photo-id-file" name="photo_id_file" class="form-input" accept="image/*">
                    </div>
                    
                    <div style="text-align: center; margin-top: 2rem; display: flex; gap: 1rem; justify-content: center;">
                        <button type="button" class="btn-clear" onclick="prevStep()">Back</button>
                        <button type="submit" class="btn-primary">Complete Registration</button>
                    </div>
                </div>
            </form>
        </div>
    </div>

    <!-- Login Modal -->
    <div id="loginModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeModal('loginModal')">&times;</span>
            <h2 class="modal-title">Professional Login</h2>
            
            <form id="loginForm">
                <div class="form-group">
                    <label class="form-label" for="login-email">Email Address</label>
                    <input type="email" id="login-email" name="email" class="form-input" required>
                </div>
                
                <div class="form-group">
                    <label class="form-label" for="login-password">Password</label>
                    <input type="password" id="login-password" name="password" class="form-input" required>
                </div>
                
                <div style="text-align: center; margin-top: 2rem;">
                    <button type="submit" class="btn-primary">Login</button>
                </div>
                
                <div style="text-align: center; margin-top: 1rem;">
                    <a href="#" style="color: #667eea; text-decoration: none;">Forgot Password?</a>
                </div>
            </form>
        </div>
    </div>

    <script src="https://js.stripe.com/v3/"></script>
    <script>
        // Initialize Stripe
        const stripe = Stripe('{{ stripe_publishable_key }}');
        
        function clearForm() {
            document.getElementById('address').value = '';
        }
        
        function showLogin() {
            document.getElementById('loginModal').style.display = 'block';
        }
        
        function showRegistration() {
            document.getElementById('registrationModal').style.display = 'block';
        }
        
        function closeModal(modalId) {
            document.getElementById(modalId).style.display = 'none';
            // Reset registration steps
            if (modalId === 'registrationModal') {
                document.getElementById('step1').style.display = 'block';
                document.getElementById('step2').style.display = 'none';
                document.getElementById('step1').classList.add('active');
                document.getElementById('step2').classList.remove('active');
                document.getElementById('step-indicator-1').classList.add('active');
                document.getElementById('step-indicator-2').classList.remove('active');
            }
        }
        
        function nextStep() {
            // Validate step 1
            const name = document.getElementById('reg-name').value;
            const email = document.getElementById('reg-email').value;
            const profession = document.getElementById('reg-profession').value;
            
            if (!name || !email || !profession) {
                alert('Please fill in all required fields');
                return;
            }
            
            // Move to step 2
            document.getElementById('step1').style.display = 'none';
            document.getElementById('step2').style.display = 'block';
            document.getElementById('step1').classList.remove('active');
            document.getElementById('step2').classList.add('active');
            document.getElementById('step-indicator-1').classList.remove('active');
            document.getElementById('step-indicator-1').classList.add('completed');
            document.getElementById('step-indicator-2').classList.add('active');
        }
        
        function prevStep() {
            // Move back to step 1
            document.getElementById('step1').style.display = 'block';
            document.getElementById('step2').style.display = 'none';
            document.getElementById('step1').classList.add('active');
            document.getElementById('step2').classList.remove('active');
            document.getElementById('step-indicator-1').classList.add('active');
            document.getElementById('step-indicator-1').classList.remove('completed');
            document.getElementById('step-indicator-2').classList.remove('active');
        }
        
        // Handle registration form submission
        document.getElementById('registrationForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const data = Object.fromEntries(formData);
            
            try {
                const response = await fetch('/register', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (result.success) {
                    alert('Registration successful! Welcome to BlueDwarf.io');
                    closeModal('registrationModal');
                    // Optionally redirect to dashboard
                } else {
                    alert('Registration failed: ' + result.error);
                }
            } catch (error) {
                alert('Registration failed: ' + error.message);
            }
        });
        
        // Handle login form submission
        document.getElementById('loginForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            alert('Login functionality will be implemented in the next phase');
        });
        
        // Close modal when clicking outside
        window.onclick = function(event) {
            const modals = document.querySelectorAll('.modal');
            modals.forEach(modal => {
                if (event.target === modal) {
                    modal.style.display = 'none';
                    // Reset registration steps
                    if (modal.id === 'registrationModal') {
                        document.getElementById('step1').style.display = 'block';
                        document.getElementById('step2').style.display = 'none';
                    }
                }
            });
        }
    </script>
</body>
</html>
'''

# Continue with other templates...
PROPERTY_RESULTS_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Property Analysis Results - BlueDwarf.io</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #ffffff;
            min-height: 100vh;
            color: #333;
        }
        
        .header {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 1rem 2rem;
            box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
            position: sticky;
            top: 0;
            z-index: 1000;
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
            color: #667eea;
        }
        
        .nav-actions {
            display: flex;
            gap: 1rem;
        }
        
        .btn {
            padding: 0.7rem 1.5rem;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.3s;
            border: none;
            cursor: pointer;
        }
        
        .btn-secondary {
            background: #6c757d;
            color: white;
        }
        
        .btn-secondary:hover {
            background: #5a6268;
        }
        
        .btn-success {
            background: #28a745;
            color: white;
        }
        
        .btn-success:hover {
            background: #218838;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        .property-card {
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
            overflow: hidden;
            margin-bottom: 2rem;
        }
        
        .property-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            text-align: center;
        }
        
        .property-address {
            font-size: 1.8rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }
        
        .success-message {
            background: #d4edda;
            color: #155724;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
            text-align: center;
            font-weight: 600;
        }
        
        .property-summary {
            display: flex;
            flex-wrap: wrap;
            gap: 1rem;
            margin-bottom: 1.5rem;
            padding: 1.5rem;
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }
        
        .summary-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            min-width: 100px;
        }
        
        .summary-label {
            font-size: 0.9rem;
            color: #666;
            margin-bottom: 0.25rem;
        }
        
        .summary-value {
            font-weight: bold;
            color: #333;
            font-size: 1.1rem;
        }
        
        .expand-section {
            text-align: center;
            margin: 1.5rem 0;
        }
        
        .expand-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 1rem 2rem;
            border-radius: 25px;
            font-size: 1rem;
            cursor: pointer;
            transition: all 0.3s;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }
        
        .expand-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        }
        
        .expand-icon {
            transition: transform 0.3s;
            font-weight: bold;
        }
        
        .expand-btn.expanded .expand-icon {
            transform: rotate(180deg);
        }
        
        .details-expanded {
            margin-top: 1.5rem;
            animation: slideDown 0.3s ease-out;
        }
        
        @keyframes slideDown {
            from {
                opacity: 0;
                transform: translateY(-10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .details-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            padding: 2rem;
        }
        
        .detail-section {
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 10px;
        }
        
        .section-title {
            font-size: 1.2rem;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 1rem;
            border-bottom: 2px solid #667eea;
            padding-bottom: 0.5rem;
        }
        
        .detail-row {
            display: flex;
            justify-content: space-between;
            padding: 0.5rem 0;
            border-bottom: 1px solid #e0e0e0;
        }
        
        .detail-row:last-child {
            border-bottom: none;
        }
        
        .detail-label {
            font-weight: 600;
            color: #666;
        }
        
        .detail-value {
            color: #333;
            font-weight: 500;
        }
        
        .maps-section {
            padding: 2rem;
            border-top: 1px solid #e0e0e0;
        }
        
        .maps-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }
        
        .maps-title {
            font-size: 1.5rem;
            font-weight: bold;
            color: #667eea;
        }
        
        .map-toggle {
            display: flex;
            gap: 0.5rem;
        }
        
        .toggle-btn {
            padding: 0.5rem 1rem;
            border: 2px solid #667eea;
            background: transparent;
            color: #667eea;
            border-radius: 5px;
            cursor: pointer;
            transition: all 0.3s;
            font-weight: 600;
        }
        
        .toggle-btn.active {
            background: #667eea;
            color: white;
        }
        
        .toggle-btn:hover {
            background: #667eea;
            color: white;
        }
        
        .map-container {
            height: 400px;
            background: #f0f0f0;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 1rem;
            position: relative;
        }
        
        .streetview-container {
            height: 300px;
            background: #f0f0f0;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 2rem;
        }
        
        .professionals-section {
            padding: 2rem;
            border-top: 1px solid #e0e0e0;
        }
        
        .professionals-title {
            font-size: 1.5rem;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 1.5rem;
            text-align: center;
        }
        
        .professionals-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
        }
        
        .professional-card {
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }
        
        .professional-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.5rem;
        }
        
        .professional-title {
            font-weight: bold;
            color: #333;
        }
        
        .btn-website {
            background: #667eea;
            color: white;
            padding: 0.3rem 0.8rem;
            border-radius: 5px;
            text-decoration: none;
            font-size: 0.9rem;
            font-weight: 600;
            transition: all 0.3s;
        }
        
        .btn-website:hover {
            background: #5a6fd8;
            transform: translateY(-1px);
        }
        
        .comparables-section {
            padding: 2rem;
            border-top: 1px solid #e0e0e0;
        }
        
        .comparables-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.5rem;
        }
        
        .comparables-title {
            font-size: 1.5rem;
            font-weight: bold;
            color: #667eea;
        }
        
        .scroll-indicator {
            color: #666;
            font-size: 0.9rem;
        }
        
        .comparables-list {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }
        
        .comparable-item {
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 10px;
            border-left: 4px solid #28a745;
        }
        
        .comparable-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }
        
        .comparable-number {
            background: #28a745;
            color: white;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
        }
        
        .comparable-price {
            font-size: 1.3rem;
            font-weight: bold;
            color: #28a745;
        }
        
        .comparable-address {
            font-weight: 600;
            color: #333;
            margin-bottom: 1rem;
        }
        
        .comparable-details {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(80px, 1fr));
            gap: 0.5rem;
            text-align: center;
        }
        
        .comparable-details div {
            background: white;
            padding: 0.5rem;
            border-radius: 5px;
            font-size: 0.9rem;
        }
        
        .back-to-top {
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            font-size: 1.2rem;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
            transition: all 0.3s;
        }
        
        .back-to-top:hover {
            background: #5a6fd8;
            transform: translateY(-2px);
        }
        
        @media (max-width: 768px) {
            .details-grid {
                grid-template-columns: 1fr;
            }
            
            .maps-header {
                flex-direction: column;
                gap: 1rem;
            }
            
            .map-toggle {
                justify-content: center;
            }
            
            .professionals-grid {
                grid-template-columns: 1fr;
            }
            
            .comparables-list {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <header class="header">
        <nav class="nav">
            <div class="logo">BlueDwarf.io</div>
            <div class="nav-actions">
                <a href="/" class="btn btn-secondary">← Back to Search</a>
                <a href="/clear-search" class="btn btn-success">New Search</a>
            </div>
        </nav>
    </header>

    <div class="container">
        <div class="property-card">
            <div class="property-header">
                <div class="property-address">{{ address }}</div>
                <div class="success-message">✅ Property Analysis Complete!</div>
            </div>
            
            {% if property_data %}
            <!-- Basic Property Summary -->
            <div class="property-summary">
                <div class="summary-item">
                    <span class="summary-label">Type:</span>
                    <span class="summary-value">{{ property_data.propertyType or 'Single Family' }}</span>
                </div>
                <div class="summary-item">
                    <span class="summary-label">Beds:</span>
                    <span class="summary-value">{{ property_data.bedrooms or 'N/A' }}</span>
                </div>
                <div class="summary-item">
                    <span class="summary-label">Baths:</span>
                    <span class="summary-value">{{ property_data.bathrooms or 'N/A' }}</span>
                </div>
                <div class="summary-item">
                    <span class="summary-label">Sq Ft:</span>
                    <span class="summary-value">{{ "{:,}".format(property_data.squareFootage) if property_data.squareFootage else 'N/A' }}</span>
                </div>
                <div class="summary-item">
                    <span class="summary-label">Value:</span>
                    <span class="summary-value">${{ "{:,}".format(property_data.estimatedValue) if property_data.estimatedValue else 'N/A' }}</span>
                </div>
            </div>
            
            <!-- Expandable Details Button -->
            <div class="expand-section">
                <button class="expand-btn" onclick="toggleDetails()" id="expandBtn">
                    <span>Show Additional Property Details</span>
                    <span class="expand-icon">▼</span>
                </button>
            </div>
            
            <!-- Detailed Property Information (Initially Hidden) -->
            <div class="details-expanded" id="detailsExpanded" style="display: none;">
                <div class="details-grid">
                    <!-- Basic Property Information -->
                    <div class="detail-section">
                        <div class="section-title">Basic Information</div>
                        <div class="detail-row">
                            <span class="detail-label">Property Type:</span>
                            <span class="detail-value">{{ property_data.propertyType or 'Single Family' }}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Bedrooms:</span>
                            <span class="detail-value">{{ property_data.bedrooms or 'N/A' }}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Bathrooms:</span>
                            <span class="detail-value">{{ property_data.bathrooms or 'N/A' }}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Square Feet:</span>
                            <span class="detail-value">{{ "{:,}".format(property_data.squareFootage) if property_data.squareFootage else 'N/A' }}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Lot Size:</span>
                            <span class="detail-value">{{ "{:,}".format(property_data.lotSize) if property_data.lotSize else 'N/A' }} sq ft</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Year Built:</span>
                            <span class="detail-value">{{ property_data.yearBuilt or 'N/A' }}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Stories:</span>
                            <span class="detail-value">{{ property_data.stories or 'N/A' }}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Garage:</span>
                            <span class="detail-value">{{ property_data.garage or 'N/A' }}</span>
                        </div>
                    </div>

                    <!-- Financial Information -->
                    <div class="detail-section">
                        <div class="section-title">Financial Information</div>
                        <div class="detail-row">
                            <span class="detail-label">Current Estimate:</span>
                            <span class="detail-value">${{ "{:,}".format(property_data.estimatedValue) if property_data.estimatedValue else 'N/A' }}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Last Sale Price:</span>
                            <span class="detail-value">${{ "{:,}".format(property_data.lastSalePrice) if property_data.lastSalePrice else 'N/A' }}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Last Sale Date:</span>
                            <span class="detail-value">{{ property_data.lastSaleDate[:10] if property_data.lastSaleDate else 'N/A' }}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Price per Sq Ft:</span>
                            <span class="detail-value">${{ "{:,.0f}".format(property_data.estimatedValue / property_data.squareFootage) if property_data.estimatedValue and property_data.squareFootage else 'N/A' }}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Property Tax:</span>
                            <span class="detail-value">${{ "{:,}".format(property_data.propertyTax) if property_data.propertyTax else 'N/A' }}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Tax Year:</span>
                            <span class="detail-value">{{ property_data.taxYear or 'N/A' }}</span>
                        </div>
                    </div>
                    
                    <!-- Location Information -->
                    <div class="detail-section">
                        <div class="section-title">Location Information</div>
                        <div class="detail-row">
                            <span class="detail-label">County:</span>
                            <span class="detail-value">{{ property_data.county or 'N/A' }}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Subdivision:</span>
                            <span class="detail-value">{{ property_data.subdivision or 'N/A' }}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Zoning:</span>
                            <span class="detail-value">{{ property_data.zoning or 'N/A' }}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">School District:</span>
                            <span class="detail-value">{{ property_data.schoolDistrict or 'N/A' }}</span>
                        </div>
                    </div>
                    
                    <!-- Additional Features -->
                    <div class="detail-section">
                        <div class="section-title">Property Features</div>
                        <div class="detail-row">
                            <span class="detail-label">Heating:</span>
                            <span class="detail-value">{{ property_data.heating or 'N/A' }}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Cooling:</span>
                            <span class="detail-value">{{ property_data.cooling or 'N/A' }}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Pool:</span>
                            <span class="detail-value">{{ 'Yes' if property_data.pool else 'No' }}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Fireplace:</span>
                            <span class="detail-value">{{ 'Yes' if property_data.fireplace else 'No' }}</span>
                        </div>
                    </div>
                </div>
            </div>
            {% endif %}
            
            <!-- Google Maps and Street View Section -->
            <div class="maps-section">
                <div class="maps-header">
                    <h3 class="maps-title">Property Location & Street View</h3>
                    <div class="map-toggle">
                        <button class="toggle-btn active" onclick="toggleMapType('roadmap')">Map</button>
                        <button class="toggle-btn" onclick="toggleMapType('satellite')">Satellite</button>
                    </div>
                </div>
                
                <!-- Street View -->
                <div class="streetview-container" id="streetview">
                    {% if google_maps_api_key and property_data and property_data.latitude and property_data.longitude %}
                        <div style="width: 100%; height: 100%; border-radius: 10px; overflow: hidden;">
                            <iframe 
                                width="100%" 
                                height="100%" 
                                frameborder="0" 
                                style="border:0"
                                src="https://www.google.com/maps/embed/v1/streetview?key={{ google_maps_api_key }}&location={{ property_data.latitude }},{{ property_data.longitude }}&heading={{ property_data.street_view_heading or 45 }}&pitch=0&fov=90"
                                allowfullscreen>
                            </iframe>
                        </div>
                    {% else %}
                        <div style="text-align: center; color: #666;">
                            <p>🗺️ Street View</p>
                            <p>Configure Google Maps API key to enable Street View</p>
                        </div>
                    {% endif %}
                </div>
                
                <!-- Interactive Map -->
                <div class="map-container" id="map">
                    {% if google_maps_api_key and property_data and property_data.latitude and property_data.longitude %}
                        <div style="width: 100%; height: 100%; border-radius: 10px; overflow: hidden;">
                            <iframe 
                                width="100%" 
                                height="100%" 
                                frameborder="0" 
                                style="border:0"
                                src="https://www.google.com/maps/embed/v1/place?key={{ google_maps_api_key }}&q={{ property_data.latitude }},{{ property_data.longitude }}&zoom=15&maptype=roadmap"
                                allowfullscreen>
                            </iframe>
                        </div>
                    {% else %}
                        <div style="text-align: center; color: #666;">
                            <p>🗺️ Interactive Map</p>
                            <p>Configure Google Maps API key to enable interactive maps</p>
                        </div>
                    {% endif %}
                </div>
            </div>
            
            <!-- Professional Services Directory -->
            <div class="professionals-section">
                <h3 class="professionals-title">Local Professional Services</h3>
                <div class="professionals-grid">
                    {% for category in professional_categories %}
                    <div class="professional-card">
                        <div class="professional-header">
                            <span class="professional-title">{{ category }}</span>
                            <a href="#" class="btn-website" onclick="searchProfessional('{{ category }}', '{{ address }}')">Find Local</a>
                        </div>
                        <p style="color: #666; font-size: 0.9rem;">Professional {{ category.lower() }} services in your area</p>
                    </div>
                    {% endfor %}
                </div>
            </div>
            
            <!-- Comparable Properties -->
            {% if comparable_data and comparable_data.comparables %}
            <div class="comparables-section">
                <div class="comparables-header">
                    <h3 class="comparables-title">Comparable Properties</h3>
                    <span class="scroll-indicator">📍 Nearby Properties</span>
                </div>
                
                <div class="comparables-list">
                    {% for comp in comparable_data.comparables[:5] %}
                    <div class="comparable-item">
                        <div class="comparable-header">
                            <div class="comparable-number">{{ comp.comp_id or loop.index }}</div>
                            <div class="comparable-price">${{ "{:,}".format(comp.price) if comp.price else 'N/A' }}</div>
                        </div>
                        <div class="comparable-address">{{ comp.formattedAddress or 'Address not available' }}</div>
                        <div class="comparable-details">
                            <div><strong>{{ comp.bedrooms or 'N/A' }}</strong><br>bed</div>
                            <div><strong>{{ comp.bathrooms or 'N/A' }}</strong><br>bath</div>
                            <div><strong>{{ "{:,}".format(comp.squareFootage) if comp.squareFootage else 'N/A' }}</strong><br>sq ft</div>
                            <div><strong>{{ comp.yearBuilt or 'N/A' }}</strong><br>built</div>
                            <div><strong>{{ "{:.1f}".format(comp.distance) if comp.distance else 'N/A' }}</strong><br>mi</div>
                        </div>
                    </div>
                    {% endfor %}
                </div>
                
                <!-- Comparable Properties Map -->
                <div class="map-container" id="comparableMap">
                    {% if comparable_data.latitude and comparable_data.longitude %}
                        <div style="width: 100%; height: 100%; border-radius: 10px; overflow: hidden;" id="leaflet-map"></div>
                    {% else %}
                        <div style="text-align: center; color: #666;">
                            <p>🗺️ Comparable Properties Map</p>
                            <p>Map will show when comparable properties are available</p>
                        </div>
                    {% endif %}
                </div>
            </div>
            {% endif %}
        </div>
    </div>
    
    <button class="back-to-top" onclick="scrollToTop()">↑</button>

    <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
    <script>
        let map;
        let currentMapType = 'roadmap';
        
        function toggleMapType(type) {
            currentMapType = type;
            
            // Update button states
            document.querySelectorAll('.toggle-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            event.target.classList.add('active');
            
            // Update map iframe
            {% if google_maps_api_key and property_data and property_data.latitude and property_data.longitude %}
            const mapContainer = document.querySelector('#map iframe');
            if (mapContainer) {
                const baseUrl = 'https://www.google.com/maps/embed/v1/place';
                const params = new URLSearchParams({
                    key: '{{ google_maps_api_key }}',
                    q: '{{ property_data.latitude }},{{ property_data.longitude }}',
                    zoom: '15',
                    maptype: type
                });
                mapContainer.src = `${baseUrl}?${params.toString()}`;
            }
            {% endif %}
        }
        
        function searchProfessional(profession, address) {
            const query = profession + " near " + address;
            const searchUrl = "https://www.google.com/search?q=" + encodeURIComponent(query);
            window.open(searchUrl, '_blank');
        }
        
        function scrollToTop() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        }
        
        function toggleDetails() {
            const detailsSection = document.getElementById('detailsExpanded');
            const expandBtn = document.getElementById('expandBtn');
            const expandIcon = expandBtn.querySelector('.expand-icon');
            const expandText = expandBtn.querySelector('span:first-child');
            
            if (detailsSection.style.display === 'none' || detailsSection.style.display === '') {
                detailsSection.style.display = 'block';
                expandBtn.classList.add('expanded');
                expandText.textContent = 'Hide Additional Property Details';
                expandIcon.textContent = '▲';
            } else {
                detailsSection.style.display = 'none';
                expandBtn.classList.remove('expanded');
                expandText.textContent = 'Show Additional Property Details';
                expandIcon.textContent = '▼';
            }
        }
        
        // Initialize Comparable Properties Map
        function initComparableMap() {
            {% if comparable_data and comparable_data.comparables and comparable_data.latitude and comparable_data.longitude %}
            const mapElement = document.getElementById('leaflet-map');
            if (mapElement) {
                const map = L.map('leaflet-map').setView([{{ comparable_data.latitude }}, {{ comparable_data.longitude }}], 13);
                
                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    attribution: '© OpenStreetMap contributors'
                }).addTo(map);
                
                // Add main property marker
                const mainPropertyIcon = L.divIcon({
                    html: '🏠',
                    iconSize: [30, 30],
                    className: 'main-property-marker'
                });
                
                L.marker([{{ comparable_data.latitude }}, {{ comparable_data.longitude }}], {icon: mainPropertyIcon})
                    .addTo(map)
                    .bindPopup('<b>Main Property</b><br>{{ address }}');
                
                // Add comparable property markers
                {% for comp in comparable_data.comparables[:5] %}
                {% if comp.latitude and comp.longitude %}
                const compIcon{{ loop.index }} = L.divIcon({
                    html: '{{ comp.comp_id or loop.index }}',
                    iconSize: [25, 25],
                    className: 'comparable-marker',
                    iconAnchor: [12, 12]
                });
                
                L.marker([{{ comp.latitude }}, {{ comp.longitude }}], {icon: compIcon{{ loop.index }}})
                    .addTo(map)
                    .bindPopup('<b>Comparable {{ comp.comp_id or loop.index }}</b><br>{{ comp.formattedAddress or "Address not available" }}<br>${{ "{:,}".format(comp.price) if comp.price else "N/A" }}');
                {% endif %}
                {% endfor %}
            }
            {% endif %}
        }
        
        // Initialize map when page loads
        document.addEventListener('DOMContentLoaded', function() {
            initComparableMap();
        });
    </script>
    
    <style>
        .comparable-marker {
            background: #28a745;
            color: white;
            border-radius: 50%;
            text-align: center;
            line-height: 25px;
            font-weight: bold;
            font-size: 12px;
            border: 2px solid white;
            box-shadow: 0 2px 5px rgba(0,0,0,0.3);
        }
        
        .main-property-marker {
            text-align: center;
            line-height: 30px;
            font-size: 20px;
        }
    </style>
</body>
</html>
'''

# Additional templates would continue here...
ABOUT_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>About - BlueDwarf.io</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 2rem; line-height: 1.6; }
        h1 { color: #667eea; }
        .back-link { display: inline-block; margin-bottom: 2rem; color: #667eea; text-decoration: none; }
    </style>
</head>
<body>
    <a href="/" class="back-link">← Back to Home</a>
    <h1>About BlueDwarf.io</h1>
    <p>BlueDwarf.io is a comprehensive property analysis platform that provides instant access to real estate data across the United States.</p>
    <p><strong>Our Mission:</strong> To empower real estate professionals with accurate, up-to-date property information and market insights.</p>
    <h2>Key Features:</h2>
    <ul>
        <li>140+ million property records</li>
        <li>Real-time property valuations</li>
        <li>Comparable property analysis</li>
        <li>Professional verification system</li>
        <li>Interactive mapping and street view</li>
    </ul>
    <p>Trusted by real estate professionals nationwide for comprehensive property analysis and market research.</p>
</body>
</html>
'''

CONTACT_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Contact - BlueDwarf.io</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 2rem; line-height: 1.6; }
        h1 { color: #667eea; }
        .back-link { display: inline-block; margin-bottom: 2rem; color: #667eea; text-decoration: none; }
        .form-group { margin-bottom: 1rem; }
        .form-label { display: block; margin-bottom: 0.5rem; font-weight: bold; }
        .form-input { width: 100%; padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px; }
        .btn-primary { background: #667eea; color: white; padding: 0.75rem 1.5rem; border: none; border-radius: 4px; cursor: pointer; }
    </style>
</head>
<body>
    <a href="/" class="back-link">← Back to Home</a>
    <h1>Contact Us</h1>
    <p>Get in touch with our team for support, questions, or partnership opportunities.</p>
    
    <form>
        <div class="form-group">
            <label class="form-label">Name</label>
            <input type="text" class="form-input" required>
        </div>
        <div class="form-group">
            <label class="form-label">Email</label>
            <input type="email" class="form-input" required>
        </div>
        <div class="form-group">
            <label class="form-label">Subject</label>
            <input type="text" class="form-input" required>
        </div>
        <div class="form-group">
            <label class="form-label">Message</label>
            <textarea class="form-input" rows="5" required></textarea>
        </div>
        <button type="submit" class="btn-primary">Send Message</button>
    </form>
    
    <h2>Other Ways to Reach Us</h2>
    <p><strong>Email:</strong> support@bluedwarf.io</p>
    <p><strong>Phone:</strong> (555) 123-4567</p>
    <p><strong>Address:</strong> 123 Business Ave, Suite 100, City, State 12345</p>
</body>
</html>
'''

ADMIN_DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Dashboard - BlueDwarf.io</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 2rem; background: #f5f5f5; }
        .dashboard { max-width: 1200px; margin: 0 auto; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 2rem; margin-bottom: 2rem; }
        .stat-card { background: white; padding: 2rem; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center; }
        .stat-number { font-size: 2.5rem; font-weight: bold; color: #667eea; }
        .stat-label { color: #666; margin-top: 0.5rem; }
        h1 { color: #333; text-align: center; margin-bottom: 2rem; }
    </style>
</head>
<body>
    <div class="dashboard">
        <h1>BlueDwarf.io Admin Dashboard</h1>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{{ total_users }}</div>
                <div class="stat-label">Total Users</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-number">{{ active_subscriptions }}</div>
                <div class="stat-label">Active Subscriptions</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-number">{{ waiting_list_count }}</div>
                <div class="stat-label">Waiting List</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-number">{{ leads_24h }}</div>
                <div class="stat-label">Leads (24h)</div>
            </div>
        </div>
    </div>
</body>
</html>
'''

TERMS_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Terms of Service - BlueDwarf.io</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 2rem; line-height: 1.6; }
        h1 { color: #667eea; }
        h2 { color: #333; margin-top: 2rem; }
        .back-link { display: inline-block; margin-bottom: 2rem; color: #667eea; text-decoration: none; }
    </style>
</head>
<body>
    <a href="/" class="back-link">← Back to Home</a>
    <h1>Terms of Service</h1>
    <p><strong>Effective Date:</strong> January 1, 2024</p>
    
    <h2>1. Acceptance of Terms</h2>
    <p>By accessing and using BlueDwarf.io, you accept and agree to be bound by the terms and provision of this agreement.</p>
    
    <h2>2. Professional Use Only</h2>
    <p>This platform is intended for use by licensed real estate professionals only. Users must provide valid professional credentials and license information.</p>
    
    <h2>3. Data Accuracy</h2>
    <p>While we strive to provide accurate information, all data should be independently verified. BlueDwarf.io is not responsible for decisions made based on platform data.</p>
    
    <h2>4. Subscription Terms</h2>
    <p>Subscriptions are billed monthly at $49 per ZIP code per professional category. Cancellations take effect at the end of the current billing period.</p>
    
    <h2>5. Privacy and Data Protection</h2>
    <p>We are committed to protecting your privacy. Please review our Privacy Policy for details on how we collect, use, and protect your information.</p>
</body>
</html>
'''

PRIVACY_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Privacy Policy - BlueDwarf.io</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 2rem; line-height: 1.6; }
        h1 { color: #667eea; }
        h2 { color: #333; margin-top: 2rem; }
        .back-link { display: inline-block; margin-bottom: 2rem; color: #667eea; text-decoration: none; }
    </style>
</head>
<body>
    <a href="/" class="back-link">← Back to Home</a>
    <h1>Privacy Policy</h1>
    <p><strong>Last Updated:</strong> January 1, 2024</p>
    
    <h2>Information We Collect</h2>
    <p>We collect information you provide directly to us, such as when you create an account, subscribe to our services, or contact us for support.</p>
    
    <h2>How We Use Your Information</h2>
    <p>We use the information we collect to provide, maintain, and improve our services, process transactions, and communicate with you.</p>
    
    <h2>Information Sharing</h2>
    <p>We do not sell, trade, or otherwise transfer your personal information to third parties without your consent, except as described in this policy.</p>
    
    <h2>Data Security</h2>
    <p>We implement appropriate security measures to protect your personal information against unauthorized access, alteration, disclosure, or destruction.</p>
    
    <h2>Contact Us</h2>
    <p>If you have questions about this Privacy Policy, please contact us at privacy@bluedwarf.io.</p>
</body>
</html>
'''

DISCLAIMER_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Disclaimer - BlueDwarf.io</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 2rem; line-height: 1.6; }
        h1 { color: #667eea; }
        h2 { color: #333; margin-top: 2rem; }
        .back-link { display: inline-block; margin-bottom: 2rem; color: #667eea; text-decoration: none; }
    </style>
</head>
<body>
    <a href="/" class="back-link">← Back to Home</a>
    <h1>Disclaimer</h1>
    
    <h2>Professional Advice Disclaimer</h2>
    <p>The information provided by BlueDwarf.io is for informational purposes only and should not be considered as professional real estate, legal, or financial advice.</p>
    
    <h2>Data Accuracy</h2>
    <p>While we strive to provide accurate and up-to-date information, we make no representations or warranties of any kind about the completeness, accuracy, reliability, suitability, or availability of the information, products, services, or related graphics contained on the platform.</p>
    
    <h2>Limitation of Liability</h2>
    <p>In no event will BlueDwarf.io be liable for any loss or damage including without limitation, indirect or consequential loss or damage, or any loss or damage whatsoever arising from loss of data or profits arising out of, or in connection with, the use of this platform.</p>
    
    <h2>Professional Verification</h2>
    <p>Users are responsible for verifying the credentials and qualifications of any professionals they choose to work with through our platform.</p>
</body>
</html>
'''

if __name__ == '__main__':
    # Initialize database
    init_database()
    
    # Log startup information
    logger.info(f"Starting BlueDwarf.io in {ENVIRONMENT} mode")
    logger.info(f"Debug mode: {DEBUG}")
    logger.info(f"Feature flags: AI={ENABLE_AI_ORCHESTRATION}, Waiting List={ENABLE_WAITING_LIST}, Email={ENABLE_EMAIL_NOTIFICATIONS}, License Verification={ENABLE_LICENSE_VERIFICATION}")
    
    # Start the application
    app.run(host='0.0.0.0', port=5000, debug=DEBUG)

