from app.text2sql.parser import parse_nl_to_sql
from app.text2sql.executor import run_sql
from app.rag.query_engine import query_rag
from app.rag.llm import load_llm

def classify_query_llm(query: str) -> str:
    """
    LLM을 이용해 질의 유형 분류
    """
    llm = load_llm()
    prompt = f"""
    사용자의 질문이 다음 세 가지 중 어느 유형에 속하는지 판단하세요.
    1. 수치형/데이터 질의 (예: 취업률, 등록금, 평균 등) → "text2sql"
    2. 정책·설명형 질의 (예: 국가장학금 기준, 신청 절차 등) → "rag"
    3. 일반 대화 (예: 안녕, 고마워, 오늘 날씨 어때 등) → "chat"

    질문: {query}
    당신의 답변은 반드시 아래 형식으로만 출력하세요.
    Answer: <text2sql | rag | chat>
    """
    resp = llm.invoke(prompt)
    if "text2sql" in resp.lower():
        return "text2sql"
    elif "rag" in resp.lower():
        return "rag"
    else:
        return "chat"
    
def smart_router(query: str):
    """
    하이브리드 분기 로직: 키워드 우선, 모호하면 LLM 판단
    """
    # 🔍 RAG 전용 키워드 (정책/설명형 질의)
    rag_keywords = [
        "지원", "조건", "기준", "방법", "절차", "서류", "정의", "설명",
        "신청", "대상", "필요", "왜", "무엇", "어떻게",
        "일정", "기간", "날짜", "년도", "시기", "공고", "모집"
    ]

    # 🔍 Text2SQL 전용 키워드 (정량 데이터 관련 질의)
    sql_keywords = [
        "취업률", "평균", "비율", "순위", "등록금", "장학금", "정원", "졸업생", "교원", 
        "통계", "비교", "증가", "감소", "상위", "하위"
    ]
    
    # 🚧 소문자/공백 정리
    query = query.strip()

    # ✅ 분기 로직 강화
    sql_hit = any(kw in query for kw in sql_keywords)
    rag_hit = any(kw in query for kw in rag_keywords)

    # ✅ 우선순위 1: 명확히 구분되는 경우
    if sql_hit and not rag_hit:
        print("🧮 [Router] Text2SQL 모드 (규칙기반)")
        sql = parse_nl_to_sql(query)
        df = run_sql(sql)
        return {"mode": "text2sql", "sql": sql, "rows": len(df), "result": df.to_dict(orient="records")}

    if rag_hit and not sql_hit:
        print("📄 [Router] RAG 모드 (규칙기반)")
        answer = query_rag(query)
        return {"mode": "rag", "answer": answer}

    # ✅ 우선순위 2: 모호할 경우 LLM에게 판단 요청
    print("🧠 [Router] LLM이 질의 유형 분류 중...")
    mode = classify_query_llm(query)

    if mode == "text2sql":
        print("🧮 [Router] Text2SQL 모드 (LLM 판단)")
        sql = parse_nl_to_sql(query)
        df = run_sql(sql)
        return {"mode": "text2sql", "sql": sql, "rows": len(df), "result": df.to_dict(orient="records")}

    elif mode == "rag":
        print("📄 [Router] RAG 모드 (LLM 판단)")
        answer = query_rag(query)
        return {"mode": "rag", "answer": answer}

    else:
        print("💬 [Router] 일반 대화 모드 (LLM 판단)")
        llm = load_llm()
        response = llm.invoke(query)
        return {"mode": "chat", "answer": response}
