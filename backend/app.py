from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>BlueDwarf Platform - Live!</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                margin: 0; 
                padding: 40px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                min-height: 100vh;
            }
            .container { 
                max-width: 800px; 
                margin: 0 auto; 
                text-align: center; 
            }
            h1 { 
                font-size: 48px; 
                margin-bottom: 20px; 
            }
            .status { 
                background: rgba(46, 204, 113, 0.2); 
                border: 2px solid #2ecc71; 
                padding: 20px; 
                border-radius: 10px; 
                margin: 30px 0; 
            }
            .nav { 
                margin: 30px 0; 
            }
            .nav a { 
                color: white; 
                text-decoration: none; 
                margin: 0 15px; 
                padding: 10px 20px; 
                background: rgba(255,255,255,0.2); 
                border-radius: 5px; 
            }
            .nav a:hover { 
                background: rgba(255,255,255,0.3); 
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏠 BlueDwarf Platform</h1>
            
            <div class="status">
                <h2>✅ PLATFORM IS LIVE!</h2>
                <p>Your BlueDwarf property analysis platform is successfully deployed on Heroku</p>
            </div>
            
            <div class="nav">
                <a href="/">Home</a>
                <a href="/about">About</a>
                <a href="/contact">Contact</a>
                <a href="/api/health">API Status</a>
            </div>
            
            <h2>Professional Property Analysis Platform</h2>
            <p>Advanced verification services for real estate professionals</p>
            
            <h3>🎉 Deployment Successful!</h3>
            <p>Your platform is now live and accessible on the internet.</p>
        </div>
    </body>
    </html>
    '''

@app.route('/about')
def about():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>About - BlueDwarf Platform</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f4f4f4; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; }
            .nav a { margin-right: 20px; text-decoration: none; color: #3498db; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="nav">
                <a href="/">🏠 Home</a>
                <a href="/about">📖 About</a>
                <a href="/contact">📞 Contact</a>
                <a href="/api/health">🔧 API</a>
            </div>
            <h1>About BlueDwarf Platform</h1>
            <p>BlueDwarf is a comprehensive property analysis platform providing professional verification services.</p>
            <h2>Key Features</h2>
            <ul>
                <li>Document Verification</li>
                <li>Identity Verification</li>
                <li>License Validation</li>
                <li>Property Analysis</li>
            </ul>
        </div>
    </body>
    </html>
    '''

@app.route('/contact')
def contact():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Contact - BlueDwarf Platform</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f4f4f4; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; }
            .nav a { margin-right: 20px; text-decoration: none; color: #3498db; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="nav">
                <a href="/">🏠 Home</a>
                <a href="/about">📖 About</a>
                <a href="/contact">📞 Contact</a>
                <a href="/api/health">🔧 API</a>
            </div>
            <h1>Contact BlueDwarf Platform</h1>
            <p><strong>Email:</strong> support@bluedwarf.com</p>
            <p><strong>Phone:</strong> (555) 123-4567</p>
            <p><strong>Hours:</strong> Monday - Friday, 9:00 AM - 6:00 PM EST</p>
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
        "message": "Platform is live and operational!"
    }

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

