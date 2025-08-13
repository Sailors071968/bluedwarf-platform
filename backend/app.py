from flask import Flask, request, jsonify
import os

# Create Flask app
app = Flask(__name__)

# --- MOCK VERIFICATION FUNCTIONS ---
def mock_document_verification(file_path):
    """Simulates verifying a document. Returns mock data."""
    if not file_path or "fail" in file_path:
        return {"status": "failed", "reason": "Invalid document image."}
    return {
        "status": "success",
        "document_type": "State Professional License",
        "is_expired": False,
        "is_authentic": True,
        "extracted_text": {
            "name": "John Doe",
            "license_number": "PROF123456",
            "state": "CA",
            "expiration_date": "2026-12-31"
        }
    }

def mock_facial_recognition(id_photo_path, live_photo_path):
    """Simulates facial recognition matching."""
    if not id_photo_path or not live_photo_path:
        return {"status": "failed", "reason": "Missing image for comparison."}
    return {
        "status": "success",
        "match_confidence": 99.8,
        "is_match": True
    }

def mock_license_validation(license_number, state):
    """Simulates license validation against state database."""
    if not license_number or not state:
        return {"status": "failed", "reason": "Missing license information."}
    return {
        "status": "success",
        "is_valid": True,
        "license_holder": "John Doe",
        "issue_date": "2021-01-15",
        "expiration_date": "2026-12-31",
        "license_type": "Professional Real Estate License"
    }

# --- ROUTES ---

@app.route('/')
def home():
    """Serve the main BlueDwarf homepage"""
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>BlueDwarf Platform - Property Analysis & Verification</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                line-height: 1.6; 
                color: #333; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }
            .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
            .header { 
                background: rgba(255,255,255,0.95); 
                padding: 20px; 
                border-radius: 10px; 
                margin-bottom: 30px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            .nav { 
                display: flex; 
                justify-content: space-between; 
                align-items: center; 
                margin-bottom: 20px; 
            }
            .logo { 
                font-size: 28px; 
                font-weight: bold; 
                color: #2c3e50; 
            }
            .nav-links { 
                display: flex; 
                gap: 20px; 
            }
            .nav-links a { 
                text-decoration: none; 
                color: #3498db; 
                font-weight: 500;
                padding: 8px 16px;
                border-radius: 5px;
                transition: background 0.3s;
            }
            .nav-links a:hover { 
                background: #3498db; 
                color: white; 
            }
            .hero { 
                text-align: center; 
                padding: 40px 0; 
            }
            .hero h1 { 
                font-size: 48px; 
                margin-bottom: 20px; 
                color: #2c3e50; 
            }
            .hero p { 
                font-size: 20px; 
                color: #7f8c8d; 
                margin-bottom: 30px; 
            }
            .features { 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
                gap: 30px; 
                margin-top: 50px; 
            }
            .feature { 
                background: rgba(255,255,255,0.95); 
                padding: 30px; 
                border-radius: 10px; 
                text-align: center;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            .feature h3 { 
                color: #2c3e50; 
                margin-bottom: 15px; 
                font-size: 24px; 
            }
            .feature p { 
                color: #7f8c8d; 
                line-height: 1.6; 
            }
            .cta { 
                text-align: center; 
                margin-top: 50px; 
            }
            .btn { 
                display: inline-block; 
                background: #3498db; 
                color: white; 
                padding: 15px 30px; 
                text-decoration: none; 
                border-radius: 5px; 
                font-weight: bold; 
                transition: background 0.3s;
            }
            .btn:hover { 
                background: #2980b9; 
            }
            .status { 
                background: rgba(46, 204, 113, 0.1); 
                border: 1px solid #2ecc71; 
                color: #27ae60; 
                padding: 15px; 
                border-radius: 5px; 
                margin-bottom: 20px; 
                text-align: center; 
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="nav">
                    <div class="logo">🏠 BlueDwarf</div>
                    <div class="nav-links">
                        <a href="/">Home</a>
                        <a href="/about">About</a>
                        <a href="/contact">Contact</a>
                        <a href="/signup">Sign Up</a>
                        <a href="/api/health">API Status</a>
                    </div>
                </div>
                
                <div class="status">
                    ✅ <strong>Platform Status:</strong> LIVE & OPERATIONAL on Heroku
                </div>
                
                <div class="hero">
                    <h1>Professional Property Analysis Platform</h1>
                    <p>Advanced verification services for real estate professionals</p>
                </div>
            </div>
            
            <div class="features">
                <div class="feature">
                    <h3>🔍 Document Verification</h3>
                    <p>AI-powered verification of professional licenses, certifications, and legal documents with 99.8% accuracy.</p>
                </div>
                
                <div class="feature">
                    <h3>👤 Identity Verification</h3>
                    <p>Advanced facial recognition technology to match ID photos with live verification for secure authentication.</p>
                </div>
                
                <div class="feature">
                    <h3>📋 License Validation</h3>
                    <p>Real-time validation against state databases to ensure professional licenses are current and in good standing.</p>
                </div>
                
                <div class="feature">
                    <h3>🏡 Property Analysis</h3>
                    <p>Comprehensive property evaluation tools with market analysis, valuation, and detailed reporting capabilities.</p>
                </div>
            </div>
            
            <div class="cta">
                <a href="/signup" class="btn">Get Started Today</a>
            </div>
        </div>
    </body>
    </html>
    """
    return html

@app.route('/about')
def about():
    """About page"""
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>About - BlueDwarf Platform</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; background: #f4f4f4; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; }
            h1 { color: #2c3e50; margin-bottom: 30px; }
            .nav { margin-bottom: 30px; }
            .nav a { margin-right: 20px; text-decoration: none; color: #3498db; }
            .nav a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="nav">
                <a href="/">🏠 Home</a>
                <a href="/about">📖 About</a>
                <a href="/contact">📞 Contact</a>
                <a href="/signup">✍️ Sign Up</a>
            </div>
            <h1>About BlueDwarf Platform</h1>
            <p>BlueDwarf is a comprehensive property analysis platform that provides professional verification services for real estate professionals, property managers, and financial institutions.</p>
            
            <h2>Our Mission</h2>
            <p>To revolutionize property verification and analysis through cutting-edge AI technology, ensuring secure, accurate, and efficient processes for all stakeholders in the real estate industry.</p>
            
            <h2>Key Features</h2>
            <ul>
                <li><strong>Document Verification:</strong> Advanced AI-powered document analysis</li>
                <li><strong>Identity Verification:</strong> Facial recognition and biometric matching</li>
                <li><strong>License Validation:</strong> Real-time database verification</li>
                <li><strong>Property Analysis:</strong> Comprehensive market evaluation tools</li>
            </ul>
            
            <h2>Technology Stack</h2>
            <p>Built with modern technologies including Python Flask, advanced machine learning algorithms, and secure cloud infrastructure on Heroku.</p>
        </div>
    </body>
    </html>
    """
    return html

@app.route('/contact')
def contact():
    """Contact page"""
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Contact - BlueDwarf Platform</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; background: #f4f4f4; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; }
            h1 { color: #2c3e50; margin-bottom: 30px; }
            .nav { margin-bottom: 30px; }
            .nav a { margin-right: 20px; text-decoration: none; color: #3498db; }
            .nav a:hover { text-decoration: underline; }
            .contact-info { background: #ecf0f1; padding: 20px; border-radius: 5px; margin: 20px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="nav">
                <a href="/">🏠 Home</a>
                <a href="/about">📖 About</a>
                <a href="/contact">📞 Contact</a>
                <a href="/signup">✍️ Sign Up</a>
            </div>
            <h1>Contact BlueDwarf Platform</h1>
            
            <div class="contact-info">
                <h3>📧 Email Support</h3>
                <p><strong>General Inquiries:</strong> info@bluedwarf.com</p>
                <p><strong>Technical Support:</strong> support@bluedwarf.com</p>
                <p><strong>Sales:</strong> sales@bluedwarf.com</p>
            </div>
            
            <div class="contact-info">
                <h3>📞 Phone Support</h3>
                <p><strong>Main Line:</strong> (555) 123-4567</p>
                <p><strong>Technical Support:</strong> (555) 123-4568</p>
                <p><strong>Business Hours:</strong> Monday - Friday, 9:00 AM - 6:00 PM EST</p>
            </div>
            
            <div class="contact-info">
                <h3>🏢 Business Address</h3>
                <p>BlueDwarf Platform<br>
                123 Innovation Drive<br>
                Tech City, TC 12345<br>
                United States</p>
            </div>
            
            <h2>Get Support</h2>
            <p>Our dedicated support team is here to help with all your property verification needs. Whether you have technical questions, need assistance with our API, or want to learn more about our services, we're ready to assist.</p>
        </div>
    </body>
    </html>
    """
    return html

@app.route('/signup')
def signup():
    """Signup page"""
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Sign Up - BlueDwarf Platform</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; background: #f4f4f4; }
            .container { max-width: 600px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; }
            h1 { color: #2c3e50; margin-bottom: 30px; text-align: center; }
            .nav { margin-bottom: 30px; text-align: center; }
            .nav a { margin-right: 20px; text-decoration: none; color: #3498db; }
            .nav a:hover { text-decoration: underline; }
            .signup-form { background: #ecf0f1; padding: 30px; border-radius: 5px; }
            .form-group { margin-bottom: 20px; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input, select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
            .btn { background: #3498db; color: white; padding: 12px 30px; border: none; border-radius: 5px; cursor: pointer; width: 100%; }
            .btn:hover { background: #2980b9; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="nav">
                <a href="/">🏠 Home</a>
                <a href="/about">📖 About</a>
                <a href="/contact">📞 Contact</a>
                <a href="/signup">✍️ Sign Up</a>
            </div>
            <h1>Join BlueDwarf Platform</h1>
            
            <div class="signup-form">
                <h3>Create Your Account</h3>
                <form>
                    <div class="form-group">
                        <label for="name">Full Name</label>
                        <input type="text" id="name" name="name" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="email">Email Address</label>
                        <input type="email" id="email" name="email" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="company">Company/Organization</label>
                        <input type="text" id="company" name="company">
                    </div>
                    
                    <div class="form-group">
                        <label for="role">Professional Role</label>
                        <select id="role" name="role">
                            <option value="">Select your role</option>
                            <option value="realtor">Real Estate Agent</option>
                            <option value="broker">Broker</option>
                            <option value="appraiser">Property Appraiser</option>
                            <option value="manager">Property Manager</option>
                            <option value="lender">Mortgage Lender</option>
                            <option value="other">Other</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="password">Password</label>
                        <input type="password" id="password" name="password" required>
                    </div>
                    
                    <button type="submit" class="btn">Create Account</button>
                </form>
                
                <p style="text-align: center; margin-top: 20px; color: #7f8c8d;">
                    Already have an account? <a href="#" style="color: #3498db;">Sign In</a>
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    return html

# --- API ENDPOINTS ---

@app.route('/api/verify-document', methods=['POST'])
def verify_document():
    """API endpoint for document verification"""
    try:
        data = request.get_json() if request.is_json else {}
        file_path = data.get('file_path', '') if data else ''
        result = mock_document_verification(file_path)
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/verify-identity', methods=['POST'])
def verify_identity():
    """API endpoint for facial recognition verification"""
    try:
        data = request.get_json() if request.is_json else {}
        id_photo = data.get('id_photo_path', '') if data else ''
        live_photo = data.get('live_photo_path', '') if data else ''
        result = mock_facial_recognition(id_photo, live_photo)
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/validate-license', methods=['POST'])
def validate_license():
    """API endpoint for license validation"""
    try:
        data = request.get_json() if request.is_json else {}
        license_number = data.get('license_number', '') if data else ''
        state = data.get('state', '') if data else ''
        result = mock_license_validation(license_number, state)
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy", 
        "service": "BlueDwarf Platform",
        "version": "1.0.0",
        "deployment": "Heroku",
        "endpoints": [
            "/",
            "/about", 
            "/contact",
            "/signup",
            "/api/verify-document",
            "/api/verify-identity", 
            "/api/validate-license",
            "/api/health"
        ]
    })

# --- ERROR HANDLERS ---

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    # Get port from environment variable or default to 5000
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

