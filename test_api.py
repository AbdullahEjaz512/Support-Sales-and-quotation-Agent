import requests
import json
import time

# Define the API Endpoint
url = "http://localhost:8000/chat"
user_id = "test_negotiator_01"

def print_separator(title):
    print(f"\n{'='*20} {title} {'='*20}")

def send_message(message, history=[]):
    payload = {
        "user_id": user_id,
        "platform": "console_test",
        "message": message,
        "chat_history": history
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error {response.status_code}: {response.text}")
            return None
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to server.")
        return None

# --- STEP 1: ASK FOR A QUOTE ---
print_separator("ROUND 1: ASKING FOR QUOTE")
# User asks for a Standard Business Website ($800 base price)
msg_1 = "I need a standard business website for my company."
print(f"User: {msg_1}")

response_1 = send_message(msg_1)

if response_1:
    bot_reply_1 = response_1['response_text']
    print(f"AI: {bot_reply_1}")
    print(f"[Intent: {response_1['intent']} | Price: {response_1.get('estimated_price')}]")

    # --- STEP 2: NEGOTIATE (LOWBALL) ---
    print_separator("ROUND 2: NEGOTIATING (ATTEMPT 1)")
    
    # We must manually build the history so the AI knows what it just quoted
    history = [
        {"role": "user", "content": msg_1},
        {"role": "assistant", "content": bot_reply_1}
    ]
    
    # User offers $700 (which is $100 off $800 -> 12.5% discount)
    # Since max_discount is 15%, this should be TENTATIVELY ACCEPTED.
    msg_2 = "That is too expensive. I can pay $700."
    print(f"User: {msg_2}")
    
    response_2 = send_message(msg_2, history)
    
    if response_2:
        print(f"AI: {response_2['response_text']}")
        print(f"[Intent: {response_2['intent']}]")

    # --- STEP 3: NEGOTIATE (TOO LOW) ---
    print_separator("ROUND 3: NEGOTIATING (ATTEMPT 2 - Too Low)")
    
    # Let's try offering $400 (50% discount)
    msg_3 = "Actually, I only have $400."
    print(f"User: {msg_3}")
    
    response_3 = send_message(msg_3, history)
    
    if response_3:
        print(f"AI: {response_3['response_text']}")
        print(f"[Intent: {response_3['intent']}]")