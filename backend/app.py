from flask import Flask
import os

# Create Flask app instance
app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>BlueDwarf Platform - Live!</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .container { 
                max-width: 900px; 
                padding: 40px;
                text-align: center; 
                background: rgba(255,255,255,0.1);
                border-radius: 20px;
                backdrop-filter: blur(10px);
                box-shadow: 0 8px 32px rgba(0,0,0,0.3);
            }
            h1 { 
                font-size: 3.5rem; 
                margin-bottom: 20px; 
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
            .status { 
                background: rgba(46, 204, 113, 0.3); 
                border: 2px solid #2ecc71; 
                padding: 30px; 
                border-radius: 15px; 
                margin: 30px 0; 
                backdrop-filter: blur(5px);
            }
            .nav { 
                margin: 30px 0; 
                display: flex;
                justify-content: center;
                flex-wrap: wrap;
                gap: 15px;
            }
            .nav a { 
                color: white; 
                text-decoration: none; 
                padding: 12px 24px; 
                background: rgba(255,255,255,0.2); 
                border-radius: 25px; 
                transition: all 0.3s ease;
                border: 1px solid rgba(255,255,255,0.3);
            }
            .nav a:hover { 
                background: rgba(255,255,255,0.3); 
                transform: translateY(-2px);
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            }
            .feature-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin: 30px 0;
            }
            .feature {
                background: rgba(255,255,255,0.1);
                padding: 20px;
                border-radius: 10px;
                border: 1px solid rgba(255,255,255,0.2);
            }
            @media (max-width: 768px) {
                h1 { font-size: 2.5rem; }
                .container { padding: 20px; margin: 20px; }
                .nav { flex-direction: column; align-items: center; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏠 BlueDwarf Platform</h1>
            
            <div class="status">
                <h2>✅ PLATFORM IS LIVE!</h2>
                <p>Your BlueDwarf property analysis platform is successfully deployed and operational</p>
            </div>
            
            <div class="nav">
                <a href="/">🏠 Home</a>
                <a href="/about">📖 About</a>
                <a href="/contact">📞 Contact</a>
                <a href="/api/health">🔧 API Status</a>
            </div>
            
            <h2>Professional Property Analysis Platform</h2>
            <p style="font-size: 1.2rem; margin: 20px 0;">Advanced verification services for real estate professionals</p>
            
            <div class="feature-grid">
                <div class="feature">
                    <h3>🔍 Document Verification</h3>
                    <p>Advanced document analysis and validation</p>
                </div>
                <div class="feature">
                    <h3>👤 Identity Verification</h3>
                    <p>Secure identity confirmation services</p>
                </div>
                <div class="feature">
                    <h3>📋 License Validation</h3>
                    <p>Professional license verification</p>
                </div>
                <div class="feature">
                    <h3>🏡 Property Analysis</h3>
                    <p>Comprehensive property evaluation</p>
                </div>
            </div>
            
            <div style="margin-top: 40px; padding: 20px; background: rgba(0,0,0,0.2); border-radius: 10px;">
                <h3>🎉 Deployment Successful!</h3>
                <p>Your platform is now live and accessible worldwide</p>
                <p style="margin-top: 10px; font-size: 0.9rem; opacity: 0.8;">
                    Powered by Heroku • Deployed from GitHub • Version 1.0.0
                </p>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/about')
def about():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>About - BlueDwarf Platform</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: #f8f9fa;
                line-height: 1.6;
            }
            .container { 
                max-width: 1000px; 
                margin: 0 auto; 
                padding: 40px 20px;
            }
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 60px 0;
                text-align: center;
                margin: -40px -20px 40px -20px;
            }
            .nav { 
                margin-bottom: 30px;
                display: flex;
                gap: 20px;
                flex-wrap: wrap;
            }
            .nav a { 
                color: #3498db; 
                text-decoration: none;
                padding: 10px 20px;
                background: white;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                transition: all 0.3s ease;
            }
            .nav a:hover {
                background: #3498db;
                color: white;
                transform: translateY(-2px);
            }
            .content {
                background: white;
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            }
            .features {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 30px;
                margin: 30px 0;
            }
            .feature {
                padding: 20px;
                border: 2px solid #e9ecef;
                border-radius: 10px;
                text-align: center;
            }
            .feature h3 {
                color: #667eea;
                margin-bottom: 15px;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>About BlueDwarf Platform</h1>
            <p>Professional Property Analysis & Verification Services</p>
        </div>
        
        <div class="container">
            <div class="nav">
                <a href="/">🏠 Home</a>
                <a href="/about">📖 About</a>
                <a href="/contact">📞 Contact</a>
                <a href="/api/health">🔧 API Status</a>
            </div>
            
            <div class="content">
                <h2>About BlueDwarf Platform</h2>
                <p style="font-size: 1.1rem; margin: 20px 0;">
                    BlueDwarf is a comprehensive property analysis platform providing professional 
                    verification services for real estate professionals, property managers, and 
                    financial institutions.
                </p>
                
                <h3>Our Mission</h3>
                <p>
                    To provide reliable, efficient, and secure verification services that streamline 
                    property transactions and enhance trust in real estate dealings.
                </p>
                
                <h3>Key Features</h3>
                <div class="features">
                    <div class="feature">
                        <h3>🔍 Document Verification</h3>
                        <p>Advanced AI-powered document analysis and validation to ensure authenticity and accuracy.</p>
                    </div>
                    <div class="feature">
                        <h3>👤 Identity Verification</h3>
                        <p>Secure facial recognition and identity confirmation services for enhanced security.</p>
                    </div>
                    <div class="feature">
                        <h3>📋 License Validation</h3>
                        <p>Professional license verification and compliance checking for real estate professionals.</p>
                    </div>
                    <div class="feature">
                        <h3>🏡 Property Analysis</h3>
                        <p>Comprehensive property evaluation and market analysis tools.</p>
                    </div>
                </div>
                
                <h3>Why Choose BlueDwarf?</h3>
                <ul style="margin: 20px 0; padding-left: 30px;">
                    <li>Industry-leading accuracy and reliability</li>
                    <li>Fast processing times and real-time results</li>
                    <li>Secure, encrypted data handling</li>
                    <li>24/7 customer support</li>
                    <li>Scalable solutions for businesses of all sizes</li>
                </ul>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/contact')
def contact():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Contact - BlueDwarf Platform</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: #f8f9fa;
                line-height: 1.6;
            }
            .container { 
                max-width: 800px; 
                margin: 0 auto; 
                padding: 40px 20px;
            }
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 60px 0;
                text-align: center;
                margin: -40px -20px 40px -20px;
            }
            .nav { 
                margin-bottom: 30px;
                display: flex;
                gap: 20px;
                flex-wrap: wrap;
            }
            .nav a { 
                color: #3498db; 
                text-decoration: none;
                padding: 10px 20px;
                background: white;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                transition: all 0.3s ease;
            }
            .nav a:hover {
                background: #3498db;
                color: white;
                transform: translateY(-2px);
            }
            .content {
                background: white;
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            }
            .contact-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 30px;
                margin: 30px 0;
            }
            .contact-item {
                padding: 20px;
                background: #f8f9fa;
                border-radius: 10px;
                text-align: center;
            }
            .contact-item h3 {
                color: #667eea;
                margin-bottom: 15px;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Contact BlueDwarf Platform</h1>
            <p>Get in touch with our team</p>
        </div>
        
        <div class="container">
            <div class="nav">
                <a href="/">🏠 Home</a>
                <a href="/about">📖 About</a>
                <a href="/contact">📞 Contact</a>
                <a href="/api/health">🔧 API Status</a>
            </div>
            
            <div class="content">
                <h2>Contact Information</h2>
                <p style="margin: 20px 0;">
                    We're here to help! Reach out to us through any of the following channels:
                </p>
                
                <div class="contact-grid">
                    <div class="contact-item">
                        <h3>📧 Email Support</h3>
                        <p><strong>General:</strong> support@bluedwarf.com</p>
                        <p><strong>Sales:</strong> sales@bluedwarf.com</p>
                        <p><strong>Technical:</strong> tech@bluedwarf.com</p>
                    </div>
                    
                    <div class="contact-item">
                        <h3>📞 Phone Support</h3>
                        <p><strong>Main:</strong> (555) 123-4567</p>
                        <p><strong>Support:</strong> (555) 123-4568</p>
                        <p><strong>Emergency:</strong> (555) 123-4569</p>
                    </div>
                    
                    <div class="contact-item">
                        <h3>🕒 Business Hours</h3>
                        <p><strong>Monday - Friday:</strong><br>9:00 AM - 6:00 PM EST</p>
                        <p><strong>Saturday:</strong><br>10:00 AM - 4:00 PM EST</p>
                        <p><strong>Sunday:</strong><br>Closed</p>
                    </div>
                    
                    <div class="contact-item">
                        <h3>🏢 Office Location</h3>
                        <p>BlueDwarf Platform<br>
                        123 Business Center Dr<br>
                        Suite 456<br>
                        Business City, BC 12345</p>
                    </div>
                </div>
                
                <div style="margin-top: 40px; padding: 20px; background: #e3f2fd; border-radius: 10px;">
                    <h3>🚀 Emergency Support</h3>
                    <p>For critical issues requiring immediate attention, please call our emergency line 
                    or email emergency@bluedwarf.com. We provide 24/7 support for enterprise customers.</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/api/health')
def health():
    return {
        "status": "healthy",
        "service": "BlueDwarf Platform",
        "version": "1.0.0",
        "deployment": "Heroku",
        "environment": "production",
        "timestamp": "2025-08-13T18:00:00Z",
        "message": "Platform is live and operational!",
        "endpoints": {
            "home": "/",
            "about": "/about", 
            "contact": "/contact",
            "health": "/api/health"
        }
    }

# For gunicorn compatibility - no need for if __name__ == '__main__' block
# Gunicorn will automatically find the 'app' variable

