from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.text2sql.router import smart_router

router = APIRouter()

# 요청 스키마
class ChatRequest(BaseModel):
    query: str
    k: int = 3  # (RAG 모드 시 문서 수)

@router.post("/chat")
def chat_endpoint(request: ChatRequest):
    """
    하이브리드 AI 챗봇 엔드포인트
    - Text2SQL: 수치/통계 질의
    - RAG: 문서 검색/설명 질의
    """
    try:
        print(f"[CHAT] 사용자 요청: {request.query}")
        result = smart_router(request.query)

        if result["mode"] == "text2sql":
            return {
                "mode": "text2sql",
                "sql": result["sql"],
                "rows": result["rows"],
                "data": result["result"],
                "message": f"{result['rows']}개의 데이터 반환"
            }

        elif result["mode"] == "rag":
            return {
                "mode": "rag",
                "answer": result["answer"],
                "message": "문서 기반 답변 생성 완료"
            }

        else:
            raise HTTPException(status_code=500, detail="알 수 없는 처리 모드")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
