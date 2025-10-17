from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from app.core.config import settings

api_router = APIRouter()

class ChatRequest(BaseModel):
    query: str = Field(..., description="사용자 입력 질의")
    mode: Optional[str] = Field(default="auto", description="auto|rag|sql")

@api_router.get("/health", tags=["system"])
def health():
    return {
        "status": "ok",
        "env": settings.APP_ENV,
        "sqlite": settings.SQLITE_PATH,
        "vector_dir": settings.VECTOR_DIR
    }

@api_router.post("/chat", tags=["chat"])
def chat(req: ChatRequest):
    # 자리표시자: 간단한 분기. 추후 RAG/Text2SQL 연결
    q = req.query.strip()
    mode = (req.mode or "auto").lower()

    if not q:
        raise HTTPException(status_code=400, detail="query is empty")

    # Simple heuristic for demo
    if mode == "sql" or ("취업률" in q or "TOP" in q or "비율" in q):
        route = "text2sql"
    elif mode == "rag" or ("정책" in q or "차이점" in q or "설명" in q):
        route = "rag"
    else:
        route = "auto"

    return {
        "route": route,
        "answer": f"[DEMO] '{q}' 에 대한 임시 응답입니다. (추후 RAG/SQL 연결)",
    }
