# AztroSys AI Agent Service

This is the Python Microservice ("The Brain") for the AztroSys Omnichannel Agent. 
It handles Multilingual Natural Language Understanding (NLU), RAG (Retrieval-Augmented Generation), and Dynamic Pricing Estimation.

## 📂 Project Structure
- `main.py`: The FastAPI server entry point.
- `rag_engine.py`: Core logic for translation, search, and pricing.
- `models.py`: Data contracts (Input/Output validation).
- `knowledge_base.json`: Static FAQs and company info.
- `pricing_matrix.json`: Configurable pricing rules.

## 🚀 Setup & Run

### Option A: Using Docker (Recommended)
1. **Build the container:**
   ```bash
   docker build -t aztro-agent .