import re
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from app.rag.llm import load_llm

def parse_nl_to_sql(query: str) -> str:
    """
    자연어 → SQL 변환
    """
    llm = load_llm()
    db = SQLDatabase.from_uri("sqlite:///data/db/univ.db")
    chain = create_sql_query_chain(llm, db)

    result = chain.invoke({"question": query})
    # result는 "Question: … SQLQuery: SELECT …" 형태
    sql_match = re.search(r"SQLQuery:\s*(SELECT.*)", result, re.S | re.I)
    sql = sql_match.group(1).strip() if sql_match else result.strip()

    print("📜 Generated SQL:", sql)
    return sql
