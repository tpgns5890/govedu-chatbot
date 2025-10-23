from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# ✅ 하이브리드 라우터 임포트
from app.api.router import router as chat_router

app = FastAPI(
    title="Govedu Hybrid AI Chatbot API",
    description="RAG + Text2SQL 통합형 온프레미스 챗봇 서버",
    version="2.0.0",
)

# ✅ CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ 라우터 등록 (이게 핵심!)
app.include_router(chat_router)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8090, reload=True)
