import json
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure the AI (Gemini)
# Make sure your .env file has the key!
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

# Load Data
def load_json(filename):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

knowledge_base = load_json('knowledge_base.json')
pricing_data = load_json('pricing_matrix.json')

def translate_and_normalize(user_query):
    """
    Uses AI to:
    1. Detect the user's language.
    2. Translate the query to English (for searching).
    3. Return both the English query and the detected language.
    """
    prompt = f"""
    Analyze this user message: "{user_query}"
    1. Detect the language (e.g., English, Urdu, Spanish).
    2. Translate the message to English.
    
    Return ONLY a JSON string like this:
    {{"detected_language": "Urdu", "english_query": "How much for a website?"}}
    """
    try:
        response = model.generate_content(prompt)
        # Clean up the response to ensure it's valid JSON
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        result = json.loads(clean_text)
        return result
    except Exception as e:
        # Fallback if AI fails: assume English
        return {"detected_language": "English", "english_query": user_query}

def find_best_match(english_query):
    """
    Searches the Knowledge Base using the TRANSLATED English query.
    """
    english_query = english_query.lower()
    best_match = None
    highest_score = 0

    for entry in knowledge_base:
        score = 0
        for keyword in entry.get('keywords', []):
            if keyword in english_query:
                score += 1
        
        if score > highest_score:
            highest_score = score
            best_match = entry

    return best_match if highest_score > 0 else None

def calculate_quote(english_query):
    """
    Calculates price using the TRANSLATED English query.
    """
    english_query = english_query.lower()
    found_services = []
    total_price = 0
    total_days = 0

    services_list = pricing_data.get("services", [])
    for service in services_list:
        keywords = service['id'].split('_') 
        if any(k in english_query for k in keywords):
            found_services.append(service)
            total_price += service['base_price']
            total_days = max(total_days, service['avg_days'])

    if not found_services:
        return None

    # Return the raw English response
    service_names = ", ".join([s['name'] for s in found_services])
    response = (
        f"Based on your request for: {service_names}.\n"
        f"ESTIMATED RANGE: ${total_price} - ${total_price * 1.2} (USD)\n"
        f"TIMELINE: Approx {total_days} business days.\n"
        f"Note: {pricing_data.get('disclaimer')}"
    )
    return response

def finalize_response(english_response, target_language):
    """
    Translates the final answer back to the user's language.
    """
    if target_language == "English":
        return english_response
        
    prompt = f"""
    Translate this response into {target_language}.
    Keep the prices and numbers exactly the same.
    Maintain a professional tone.
    
    Response to translate:
    "{english_response}"
    """
    response = model.generate_content(prompt)
    return response.text