import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # IMPORT CORS
from models import ChatInput, ChatOutput
from rag_engine import translate_and_normalize, find_best_match, calculate_quote, finalize_response

# 1. Setup Logging (So you can see what is happening in the terminal)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AztroSys AI Agent")

# 2. Add CORS Middleware (CRITICAL for connecting to Node.js/React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (change this to specific domains in production)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (POST, GET, etc.)
    allow_headers=["*"],  # Allows all headers
)

@app.post("/chat", response_model=ChatOutput)
async def chat_endpoint(data: ChatInput):
    logger.info(f"Received request from user: {data.user_id} on platform: {data.platform}")

    # STEP 1: Normalize Language
    analysis = translate_and_normalize(data.message)
    english_msg = analysis.get('english_query', data.message) # Safer .get()
    user_lang = analysis.get('detected_language', 'English')
    
    logger.info(f"Detected Language: {user_lang} | Query: {english_msg}")

    final_text = ""
    intent = ""
    confidence = 0.0
    suggested = []

    # STEP 2: Logic
    quote_response = calculate_quote(english_msg)
    
    if quote_response:
        final_text = quote_response
        intent = "quotation"
        confidence = 0.9
        suggested = ["Book a Call", "Download Rate Card"]
        
    else:
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