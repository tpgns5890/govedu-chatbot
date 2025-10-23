import sqlite3
import pandas as pd

def run_sql(sql: str):
    """
    SQL을 실행하고 결과를 DataFrame으로 반환
    """
    conn = sqlite3.connect("data/db/univ.db")
    try:
        df = pd.read_sql_query(sql, conn)
        return df
    except Exception as e:
        print("❌ SQL 실행 오류:", e)
        return pd.DataFrame()
    finally:
        conn.close()
