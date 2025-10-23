import os, sqlite3, pandas as pd

DB_PATH  = os.path.join("data", "db", "univ.db")
CSV_PATH = os.path.join("data", "db_seed", "대학주요정보.csv")

# CSV의 실제 헤더(줄바꿈 포함) → DB 컬럼명 매핑
COLMAP = {
    "No": "no",
    "학교명": "school_name",
    "본분교명": "campus_name",
    "학교종류": "school_class",
    "학교유형": "school_type",
    "설립유형": "establish_type",
    "지역명": "region",
    "입학정원(학부)\n(2025,명)": "admission_capacity_2025",
    "졸업생수(학부)\n(2025,명)": "graduates_2025",
    "전임교원수(학부+대학원)\n(2025,명)": "full_time_faculty_2025",
    "재학생(학부)\n(2025,명)": "enrolled_2025",
    "신입생 경쟁률(학부)\n(2025,:1)": "freshman_competition_2025",
    "신입생 충원율(학부)\n(2025,%)": "freshman_fill_rate_2025",
    "취업률(학부)\n(2024,%)": "employment_rate_2024",
    "외국인 학생 수(학부)\n(2025,명)": "intl_students_2025",
    "전임교원 1인당 학생 수(학생정원기준)(학부+대학원)\n(2025,명)": "students_per_faculty_2025",
    "전임교원 확보율(학생정원기준)(학부+대학원)\n(2025,%)": "faculty_secured_rate_quota_2025",
    "전임 교원 확보율(재학생 기준)(학부+대학원)\n(2025,%)": "faculty_secured_rate_enrolled_2025",
    "전임교원 강의 담당 비율(학부)\n(2025,%)": "faculty_teaching_ratio_2025",
    "학생 1인당 연간 장학금(학부)\n(2025,원)": "scholarship_per_student_2025_won",
    "연평균 등록금(학부)\n(2025,천원)": "tuition_avg_2025_thousand",
    "학생 1인당 교육비(학부+대학원)\n(2025,천원)": "edu_cost_per_student_2025_thousand",
    "기숙사 수용율(학부+대학원)\n(2024,%)": "dorm_capacity_rate_2024",
    "학생 1인당 도서 자료 수(학부+대학원)\n(2024,권)": "books_per_student_2024",
}

DDL = """
CREATE TABLE IF NOT EXISTS university_info (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  no INTEGER,
  school_name TEXT,
  campus_name TEXT,
  school_class TEXT,
  school_type TEXT,
  establish_type TEXT,
  region TEXT,
  admission_capacity_2025 INTEGER,
  graduates_2025 INTEGER,
  full_time_faculty_2025 INTEGER,
  enrolled_2025 INTEGER,
  freshman_competition_2025 REAL,
  freshman_fill_rate_2025 REAL,
  employment_rate_2024 REAL,
  intl_students_2025 INTEGER,
  students_per_faculty_2025 REAL,
  faculty_secured_rate_quota_2025 REAL,
  faculty_secured_rate_enrolled_2025 REAL,
  faculty_teaching_ratio_2025 REAL,
  scholarship_per_student_2025_won REAL,
  tuition_avg_2025_thousand REAL,
  edu_cost_per_student_2025_thousand REAL,
  dorm_capacity_rate_2024 REAL,
  books_per_student_2024 REAL
);
CREATE INDEX IF NOT EXISTS idx_univ_region ON university_info (school_name, region);
CREATE INDEX IF NOT EXISTS idx_employment_2024 ON university_info (employment_rate_2024);
"""

NUM_INT = [
  "no","admission_capacity_2025","graduates_2025","full_time_faculty_2025",
  "enrolled_2025","intl_students_2025"
]
NUM_FLOAT = [
  "freshman_competition_2025","freshman_fill_rate_2025","employment_rate_2024",
  "students_per_faculty_2025","faculty_secured_rate_quota_2025",
  "faculty_secured_rate_enrolled_2025","faculty_teaching_ratio_2025",
  "scholarship_per_student_2025_won","tuition_avg_2025_thousand",
  "edu_cost_per_student_2025_thousand","dorm_capacity_rate_2024",
  "books_per_student_2024"
]

def _to_number(s):
    if pd.isna(s): return s
    # 쉼표/공백 제거
    return str(s).replace(",", "").strip()

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    # CSV 로드 (한글 인코딩 호환)
    df = None
    for enc in ("utf-8", "utf-8-sig", "cp949", "euc-kr"):
        try:
            df = pd.read_csv(CSV_PATH, encoding=enc)
            break
        except Exception:
            continue
    if df is None:
        raise RuntimeError("CSV 파일을 읽을 수 없습니다. 인코딩을 확인하세요.")

    # 필요한 컬럼만 선택 + 영문 스키마명으로 리네임
    missing = [c for c in COLMAP.keys() if c not in df.columns]
    if missing:
        raise KeyError(f"CSV에 다음 컬럼이 없습니다: {missing}")
    df = df[list(COLMAP.keys())].rename(columns=COLMAP)

    # 숫자형 정리
    for c in NUM_INT + NUM_FLOAT:
        if c in df.columns:
            df[c] = df[c].map(_to_number)
    for c in NUM_INT:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype(int)
    for c in NUM_FLOAT:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # DB 생성 및 적재
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.executescript(DDL)
        conn.commit()
        df.to_sql("university_info", conn, if_exists="replace", index=False)

    print(f"✅ Inserted {len(df)} rows into university_info")
    print(f"✅ DB ready at {DB_PATH}")

if __name__ == "__main__":
    init_db()
