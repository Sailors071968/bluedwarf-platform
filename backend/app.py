# Google Maps Fix - Replace the property_results route in your app.py

@app.route('/property-results', methods=['POST'])
def property_results():
    address = request.form.get('address', '')
    
    # Clean and format address for Google Maps
    # Remove extra spaces and normalize
    cleaned_address = ' '.join(address.split())
    
    # For Google Maps Embed API, we need to use a different encoding approach
    # Use + for spaces and %2C for commas
    maps_address = cleaned_address.replace(' ', '+').replace(',', '%2C')
    
    # Alternative: Use coordinates if address fails
    # For Sacramento, CA area as fallback
    fallback_coords = "38.5816,-121.4944"
    
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
        /* Same CSS styles as before */
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
        
        /* Rest of styles remain the same... */
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
                    src="https://www.google.com/maps/embed/v1/streetview?key={{ api_key }}&location={{ maps_address }}&heading=0&pitch=0&fov=90"
                    allowfullscreen>
            </iframe>
        </div>
        
        <div class="map-section">
            <h2 class="map-title">🛰️ Aerial View (2 blocks)</h2>
            <iframe class="map-frame" 
                    src="https://www.google.com/maps/embed/v1/view?key={{ api_key }}&center={{ maps_address }}&zoom=17&maptype=satellite"
                    allowfullscreen>
            </iframe>
        </div>
    </div>
    
    <!-- Rest of the template remains the same... -->
    
</body>
</html>
    ''', address=address, maps_address=maps_address, api_key=GOOGLE_MAPS_API_KEY, zip_code=zip_code)

# Alternative approach using coordinates:
# If the above still doesn't work, replace the iframe src with:
# Street View: src="https://www.google.com/maps/embed/v1/streetview?key={{ api_key }}&location={{ fallback_coords }}&heading=0&pitch=0&fov=90"
# Aerial View: src="https://www.google.com/maps/embed/v1/view?key={{ api_key }}&center={{ fallback_coords }}&zoom=17&maptype=satellite"

