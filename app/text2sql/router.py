from app.text2sql.parser import parse_nl_to_sql
from app.text2sql.executor import run_sql
from app.rag.query_engine import query_rag

def smart_router(query: str):
    """
    질문 내용에 따라 Text2SQL 또는 RAG 경로로 자동 분기
    """
    # 🔍 Text2SQL 전용 키워드 (정량 데이터 관련 질의)
    sql_keywords = [
        "취업률", "평균", "비율", "순위", "등록금", "장학금", "정원", "졸업생", "교원", 
        "통계", "비교", "증가", "감소", "상위", "하위"
    ]
    # 🔍 RAG 전용 키워드 (정책/설명형 질의)
    rag_keywords = [
        "지원", "조건", "기준", "방법", "절차", "서류", "정의", "설명", 
        "신청", "대상", "필요", "왜", "무엇", "어떻게"
    ]

    # 🚧 소문자/공백 정리
    query = query.strip()

    # ✅ 분기 로직 강화
    sql_hit = any(kw in query for kw in sql_keywords)
    rag_hit = any(kw in query for kw in rag_keywords)

    # 🎯 하이브리드 판단 규칙
    if sql_hit and not rag_hit:
        print("🧮 [Router] Text2SQL 모드로 실행")
        sql = parse_nl_to_sql(query)
        df = run_sql(sql)
        return {
            "mode": "text2sql",
            "sql": sql,
            "rows": len(df),
            "result": df.to_dict(orient="records")
        }

    elif rag_hit and not sql_hit:
        print("📄 [Router] RAG 모드로 실행")
        answer = query_rag(query)
        return {
            "mode": "rag",
            "answer": answer
        }

    else:
        # ⚖️ 키워드가 섞여 있거나 애매한 경우 → RAG 우선
        print("🤔 [Router] 혼합 또는 모호 질의 → RAG 우선 처리")
        answer = query_rag(query)
        return {
            "mode": "rag",
            "answer": answer
        }
