import logging
import re # Added for finding numbers
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models import ChatInput, ChatOutput
# IMPORTANT: Added 'evaluate_offer' to imports
from rag_engine import translate_and_normalize, find_best_match, calculate_quote, finalize_response, evaluate_offer

# 1. Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AztroSys AI Agent")

# 2. Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat", response_model=ChatOutput)
async def chat_endpoint(data: ChatInput):
    logger.info(f"Received request from user: {data.user_id} on platform: {data.platform}")

    # STEP 1: Normalize Language
    analysis = translate_and_normalize(data.message)
    english_msg = analysis.get('english_query', data.message)
    user_lang = analysis.get('detected_language', 'English')
    
    logger.info(f"Detected Language: {user_lang} | Query: {english_msg}")

    final_text = ""
    intent = ""
    confidence = 0.0
    suggested = []
    
    # --- NEGOTIATION LOGIC START ---
    # We check this FIRST. If the user is negotiating, we skip the standard search.
    is_negotiating = False
    
    # Check if there is history and the user sent a number (e.g. "1700")
    if data.chat_history and any(char.isdigit() for char in english_msg):
        last_msg = data.chat_history[-1]
        
        # Did the bot just give a quote?
        if last_msg.get('role') == 'assistant' and "$" in last_msg.get('content', ''):
            
            # 1. Extract the Bot's Previous Price (e.g., from "$2000 - $2400")
            # We look for the first number after "$" in the bot's history
            prev_price_match = re.search(r'\$(\d+)', last_msg['content'])
            
            if prev_price_match:
                current_calculated_price = float(prev_price_match.group(1))
                
                # 2. Extract User's Offer
                user_offer_match = re.search(r'(\d+)', english_msg)
                if user_offer_match:
                    user_offer = float(user_offer_match.group(1))
                    
                    # 3. Evaluate
                    decision = evaluate_offer(english_msg, current_calculated_price)
                    is_negotiating = True # Mark as handled
                    
                    if decision == "accept_immediately":
                        final_text = f"Great! We can certainly accept ${user_offer}. I'll mark this as approved."
                        intent = "lead_capture"
                        confidence = 0.98
                        suggested = ["Finalize Deal"]

                    elif decision == "tentative_approval":
                        final_text = f"That is slightly below our standard, but I can tentatively accept ${user_offer} pending manager approval. Please provide your email to lock this rate."
                        intent = "lead_capture"
                        confidence = 0.95
                        suggested = ["Provide Email"]
                    
                    elif decision == "reject_lowball":
                        lowest_price = current_calculated_price * 0.85 # Example: 15% limit
                        final_text = f"I'm afraid ${user_offer} is too low for the quality we deliver. The lowest we can go for this scope is approx ${int(lowest_price)}. Would you like to remove some features to fit your budget?"
                        intent = "negotiation_reject"
                        confidence = 0.9
                        suggested = ["Adjust Scope", "Accept Standard Rate"]
                    else:
                        # If unknown/error
                        is_negotiating = False 

    # --- STANDARD LOGIC (If not negotiating) ---
    if not is_negotiating:
        # Check Pricing
        quote_response = calculate_quote(english_msg)
        
        if quote_response:
            final_text = quote_response
            intent = "quotation"
            confidence = 0.9
            suggested = ["Book a Call", "Download Rate Card"]
            
        else:
            # Check Knowledge Base
            kb_match = find_best_match(english_msg)
            if kb_match:
                final_text = kb_match['answer']
                intent = "general_info"
                confidence = 0.85
                suggested = ["Ask about Pricing", "View Portfolio"]
            else:
                final_text = "I'm not sure about that. Let me connect you with a human expert."
                intent = "human_handoff"
                confidence = 0.2
                suggested = ["Contact Support"]

    # STEP 3: Translate Back
    translated_text = finalize_response(final_text, user_lang)
    
    logger.info(f"Response sent. Intent: {intent}")

    return ChatOutput(
        response_text=translated_text,
        intent=intent,
        estimated_price="Calculated" if intent == "quotation" else None,
        confidence_score=confidence,
        suggested_actions=suggested
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)