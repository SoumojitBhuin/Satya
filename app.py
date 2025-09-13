from flask import Flask, render_template, request, jsonify, send_from_directory
import requests
from flask_cors import CORS
import os
import random
import base64
import json
from datetime import datetime
from PIL import Image
import google.generativeai as genai
from supabase_client import insert_report

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Configure Gemini API
genai.configure(api_key= os.getenv("MY_API_KEY"))

# Define the model
model = genai.GenerativeModel("gemini-2.0-flash")

#defining global variable
explanation_detailed = ""

#defining credentials
MY_API_KEY = os.getenv("MY_API_KEY")
MY_SEARCH_ENGINE_ID = os.getenv("MY_SEARCH_ENGINE_ID")

@app.route('/')
def index():
    """Serve the main application page"""
    return render_template( 'index.html')

@app.route('/report')
def report():
    """Serve the report page"""
    print("detailed explanation: ",explanation_detailed)
    return render_template('report.html',detailed_explanation=explanation_detailed)

@app.route('/verify', methods=['POST'])
def verify_content():
    """
    Verify content for potential scams
    
    Expected JSON format:
    {
        "type": "text|image|video",
        "data": "content_data"
    }
    """
    try:
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        data = request.get_json()
        
        if not data or 'type' not in data or 'data' not in data:
            return jsonify({'error': 'Missing required fields: type and data'}), 400
        
        content_type = data['type']
        content_data = data['data']
        
        
        if content_type not in ['text', 'image', 'video']:
            return jsonify({'error': 'Invalid content type'}), 400
        
        # Analyze content based on type
        result = analyze_content(content_type, content_data)
        
        return jsonify(result)
    
    except Exception as e:
        app.logger.error(f"Error in verify_content: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/report', methods=['POST'])
def submit_report():
    """
    Submit a scam report
    
    Expected JSON format:
    {
        "scam_type": "phishing",
        "platform": "whatsapp",
        "content_url": "optional_url",
        "description": "detailed_description",
        "additional_info": "optional_info",
        "contact_email": "optional_email"
    }
    """
    try:
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['scam_type', 'platform', 'description']
        for field in required_fields:
            if field not in data or not data[field].strip():
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # In a real application, you would save this to a database
        report_data = {
            'id': generate_report_id(),
            'scam_type': data['scam_type'],
            'platform': data['platform'],
            'content_url': data.get('content_url', ''),
            'description': data['description'],
            'additional_info': data.get('additional_info', ''),
            'contact_email': data.get('contact_email', ''),
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'received'
        }
        print(report_data,"\n")
        inserted = insert_report(report_data)
        print(inserted)
        # Log the report (in production, save to database)
        app.logger.info(f"New scam report received: {json.dumps(report_data, indent=2)}")
        
        return jsonify({
            'success': True,
            'report_id': report_data['id'],
            'message': 'Report submitted successfully'
        })
    
    except Exception as e:
        app.logger.error(f"Error in submit_report: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

def analyze_content(content_type, content_data):
    """
    Analyze content for potential scams
    This is a simplified simulation - in production, you'd use ML models
    """
    
    if content_type == 'text':
        return analyze_text(content_data)
    
    elif content_type == 'image':
        # Extract format from base64 header e.g. "data:image/jpeg;base64,..."
        if content_data.startswith("data:image/"):
            header, encoded = content_data.split(",", 1)
            extension = header.split("/")[1].split(";")[0]  # jpeg / png / jpg
        else:
            encoded = content_data
            extension = "jpg"  # default fallback

        # Decoding base64 to bytes
        image_bytes = base64.b64decode(encoded)

        # Saving with proper extension
        file_name = f"uploaded_image.{extension}"
        file_path = os.path.join("image_upload", file_name)
        with open(file_path, "wb") as f:
            f.write(image_bytes)
        return analyze_image(content_data)
    
    elif content_type == 'video':
        return analyze_video(content_data)
    else:
        return {
            'is_scam': False,
            'confidence_score': 0,
            'explanation': 'Unknown content type'
        }

def analyze_text(text_content):
    """Analyze text content for scam indicators"""
    #defining global varaible
    global explanation_detailed
    
    # Scam verification prompt
    prompt = f"""
    You are a sophisticated scam identification AI designed to provide structured JSON output. 
    Your task is to analyze text for scam indicators, search the web for corroborating evidence, 
    and return your findings in a precise JSON format.

    **Analyze the provided text for common scam indicators, including but not limited to:**
    * Urgency or Threats: "Act now," "your account will be suspended."
    * Unsolicited Prizes/Offers: "You've won a lottery," "unclaimed inheritance."
    * Suspicious Links/Requests: Mismatched URLs, requests for downloads, or remote access.
    * Requests for Personal/Financial Information: Asking for passwords, SSN, or bank details.
    * Unusual Payment Methods: Demands for payment via gift cards, wire transfers, or cryptocurrency.
    * Poor Grammar and Spelling: Unprofessional language and obvious errors.

    After analyzing the text and performing a web search for related known scams, 
    you must provide your conclusion in the following strict JSON format. 
    Do not include any text or formatting outside of this JSON object.

    **Input Text:**
    "{text_content}"

    **Output (JSON):**
    {{
      "confidence_score": "<authentic | misleading | false>",
      "verdict": "<Scam | Genuine>",
      "explanation": "<Simple and precise well framed reasoning for the conclusion based on the scam indicators found and web search results. Explaim what the input truly means.>",
      "title":"use 3 to 4 words to explain the input text for google search"
    }}
    ______
    Additionally, after providing the JSON response, include a 
    section titled "DETAILED EXPLANATION:" followed by a longer 
    detailed explanation (3–5 paragraphs) about the reasoning, 
    evidence, and context for your decision.
    """

    # Call Gemini API
    response = model.generate_content(prompt)

    raw_output = response.text

    # Split JSON and detailed explanation
    
  
    json_part, detailed_part = raw_output.split("DETAILED EXPLANATION:", 1)
    
    json_part=json_part.strip()
    json_part = json_part.strip("`")
    if json_part.startswith("json"):
        json_part = json_part[4:].strip()
   
    result=json.loads(json_part)
    
    
    reference_url = google_search_with_api(
        query=result["title"],
        api_key=MY_API_KEY,
        search_engine_id=MY_SEARCH_ENGINE_ID,
        num_results=3
    )
    
    print(reference_url,"\n\n")
    
    result["reference_urls"]=reference_url
    print(result,"\n\n")
    explanation_detailed = detailed_part.strip()
        

    return result
    

def analyze_image(image_data):
    """Analyze image content for scam indicators"""
    #defining global varaible
    global explanation_detailed
    
    # Scam verification prompt
    prompt = """
    You are a sophisticated scam identification AI designed to provide structured JSON output.
    Your task is to analyze the contents of the provided image for scam indicators, search the web
    for corroborating evidence, and return your findings in a precise JSON format.

    Analyze the image for common scam indicators, including but not limited to:
    * Urgency or Threats: "Act now," "your account will be suspended."
    * Unsolicited Prizes/Offers: "You've won a lottery," "unclaimed inheritance."
    * Suspicious Links/Requests: Mismatched URLs, requests for unusual actions.
    * Requests for Personal/Financial Information: Asking for passwords, bank details.
    * Unusual Payment Methods: Demands for payment via gift cards, wire transfers, or crypto.
    * Poor Grammar, Spelling, and Unprofessional Design.

    After analyzing the image and performing a web search for related known scams, you must provide
    your conclusion in the following strict JSON format, followed by a detailed explanation.
    Do not include any text or formatting before the JSON object.
    
    give the verdict based on the context of the image, what actually is it trying to convey and not based on what the image is. Try to fetch name of any notable person, monument, incident, or text that is being displayed in the image.
    

    **Output (JSON):**
    {{
      "confidence_score": "<authentic | misleading | false>",
      "verdict": "<Scam | Genuine>",
      "explanation": "<Simple and precise well framed reasoning for the conclusion based on the scam indicators found and web search results. Explaim what the input truly means. Fetch the latest related news from the web>",
      "title":"use 3 to 4 words to explain the input text for google search based on the explanation. Dont forget to add the most important keywords for search."
    }}
    ---
    Additionally, after providing the JSON response, include a 
    section titled "DETAILED EXPLANATION:" followed by a longer 
    detailed explanation (3–5 paragraphs) about the reasoning, 
    evidence, and context for your decision.
    """
    img = Image.open(r"C:\Users\soumo\.vscode\Kodovers\satya\satya_actual\image_upload\uploaded_image.jpeg")

    # Call Gemini API
    response = model.generate_content([prompt,img])

    raw_output = response.text

    # Split JSON and detailed explanation
  
    json_part, detailed_part = raw_output.split("DETAILED EXPLANATION:", 1)
    
    json_part=json_part.strip()
    json_part = json_part.strip("`")
    if json_part.startswith("json"):
        json_part = json_part[4:].strip()
   
    result=json.loads(json_part)
    print(result)
    
    reference_url = google_search_with_api(
        query=result["title"],
        api_key=MY_API_KEY,
        search_engine_id=MY_SEARCH_ENGINE_ID,
        num_results=3
    )
    
    print(reference_url,"\n\n")
    
    result["reference_urls"]=reference_url
    print(result,"\n\n")
    
    explanation_detailed = detailed_part.strip()
    
        

    return result
    
def analyze_video():
    pass

def google_search_with_api(query: str, api_key: str, search_engine_id: str, num_results: int = 3) -> list:
    """
    Performs a Google search using the official Custom Search JSON API.

    Args:
        query (str): The search term.
        api_key (str): Your Google API key.
        search_engine_id (str): Your Programmable Search Engine ID (CX).
        num_results (int): The number of results to return (max 10 per request).
        refinement_label (str, optional): The refinement label to trigger (e.g., 'news').

    Returns:
        list: A list of URL strings, or an empty list if an error occurs.
    """
    url = "https://www.googleapis.com/customsearch/v1"
    
    params = {
        'q': query,
        'key': api_key,
        'cx': search_engine_id,
        'num': num_results
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        search_results = response.json()
        urls = [item['link'] for item in search_results.get('items', [])]
        print(urls)
        return urls
    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the request: {e}")
        return []
    except KeyError:
        print("Error: Could not find 'items' in the API response. No results?")
        return []
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []

def generate_report_id():
    """Generate a unique report ID"""
    import uuid
    return f"RPT-{uuid.uuid4().hex[:8].upper()}"

@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'File too large'}), 413

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Configure logging
    import logging
    from logging.handlers import RotatingFileHandler
    
    if not app.debug:
        file_handler = RotatingFileHandler('logs/satya.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Satya application startup')
    
    # Run the application
    app.run(debug=True, host='0.0.0.0', port=5000)