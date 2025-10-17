from fastapi import FastAPI
from app.api.router import api_router

app = FastAPI(title="AI Chatbot On-Prem", version="0.1.0")

app.include_router(api_router)

@app.get("/", tags=["root"])
def root():
    return {"ok": True, "service": "ai-chatbot-onprem", "docs": "/docs"}
