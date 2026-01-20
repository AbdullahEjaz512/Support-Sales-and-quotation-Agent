import json
import re

# Load Data on Startup
def load_json(filename):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

knowledge_base = load_json('knowledge_base.json')
pricing_data = load_json('pricing_matrix.json')

def find_best_match(user_query):
    """
    Simple keyword matching for the Knowledge Base.
    (In production, replace this with Vector Search/Embeddings)
    """
    user_query = user_query.lower()
    best_match = None
    highest_score = 0

    for entry in knowledge_base:
        score = 0
        for keyword in entry.get('keywords', []):
            if keyword in user_query:
                score += 1
        
        if score > highest_score:
            highest_score = score
            best_match = entry

    return best_match if highest_score > 0 else None

def calculate_quote(user_query):
    """
    Scans the query for service keywords and returns a price estimate.
    """
    user_query = user_query.lower()
    found_services = []
    total_price = 0
    total_days = 0

    # Check against Pricing Matrix
    services_list = pricing_data.get("services", [])
    for service in services_list:
        # Check if the service name words appear in the query
        # e.g., if query has "ecommerce" and service is "E-Commerce Store"
        keywords = service['id'].split('_') 
        if any(k in user_query for k in keywords):
            found_services.append(service)
            total_price += service['base_price']
            total_days = max(total_days, service['avg_days'])

    if not found_services:
        return None

    # Construct the Quote Response
    service_names = ", ".join([s['name'] for s in found_services])
    response = (
        f"Based on your request for: {service_names}.\n"
        f"ESTIMATED RANGE: ${total_price} - ${total_price * 1.2} (USD)\n"
        f"TIMELINE: Approx {total_days} business days.\n"
        f"Note: {pricing_data.get('disclaimer')}"
    )
    return response