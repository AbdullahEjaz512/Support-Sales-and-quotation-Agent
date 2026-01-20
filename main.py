from fastapi import FastAPI, HTTPException
from models import ChatInput, ChatOutput
from rag_engine import find_best_match, calculate_quote

app = FastAPI(title="AztroSys AI Agent")

@app.post("/chat", response_model=ChatOutput)
async def chat_endpoint(data: ChatInput):
    user_msg = data.message.lower()
    
    # 1. Check for Pricing/Quotation Intent first
    if any(word in user_msg for word in ["price", "cost", "quote", "how much", "rate", "estimate"]):
        quote_response = calculate_quote(user_msg)
        if quote_response:
            return ChatOutput(
                response_text=quote_response,
                intent="quotation",
                estimated_price="Calculated",
                confidence_score=0.9,
                suggested_actions=["Book a Call", "Download Rate Card"]
            )
            
    # 2. If not pricing, check General Knowledge Base
    kb_match = find_best_match(user_msg)
    
    if kb_match:
        return ChatOutput(
            response_text=kb_match['answer'],
            intent="general_info",
            confidence_score=0.85,
            suggested_actions=["Ask about Pricing", "View Portfolio"]
        )

    # 3. Fallback (If nothing found)
    return ChatOutput(
        response_text="I'm not sure about that specific detail. Let me connect you with a human expert at info@aztrosys.com.",
        intent="human_handoff",
        confidence_score=0.2,
        suggested_actions=["Contact Support"]
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)