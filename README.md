# AI Chatbot On-Prem Starter (FastAPI · LangChain · CPU-only)

로컬 Windows 환경에서 시작 → 이후 폐쇄망/클라우드로 이식 가능한 **온프레미스 친화형** 스타터 키트입니다.
- 백엔드: FastAPI
- AI 파이프라인: LangChain 기반 RAG / Text2SQL
- 데이터: SQLite(운영 샘플), ChromaDB(문서 검색) — 둘 다 로컬 폴더 안에 생성
- 모델: llama.cpp (CPU), 이후 교체 가능 구조

## 1) 빠른 시작 (Windows, Python 3.13 기준)
```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -U pip
pip install -r requirements.txt

# 개발 서버 실행
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# 브라우저에서 http://localhost:8000/docs 확인
```

> Docker는 나중에 설치해도 됩니다. (Dockerfile/Compose 포함)

## 2) 환경 변수 설정
`.env.example`를 복사해 `.env`를 만들고 필요 시 경로 조정:
```env
APP_ENV=dev
DATA_DIR=./data
SQLITE_PATH=./data/structured/edu.db
VECTOR_DIR=./data/vector
LOG_DB_PATH=./data/logs/chatlog.db
MODEL_PATH=./models/llama3-8b-instruct.Q4_K_M.gguf
```

## 3) 폴더 구조
```text
app/
  api/           # REST 엔드포인트
  core/          # 설정/의존성
  rag/           # 문서 인덱싱/검색 (stub)
  text2sql/      # NL→SQL (stub)
  db/            # DB 초기화/마이그레이션
data/            # 실행 중 생성 (임베딩/DB 등)
models/          # GGUF 모델 파일 위치 (수동 다운로드)
scripts/         # 실행/도구 스크립트
```

## 4) 기본 API
- `GET /health` : 상태 확인
- `POST /chat`  : 간단한 더미 응답 (이후 RAG/Text2SQL 연결)

예시:
```bash
curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d "{\"query\": \"서울 4년제 IT계열 취업률 TOP5\"}"
```

## 5) 다음 단계
1. `/app/rag/indexer.py`에 PDF 폴더를 지정해 임베딩 생성(추후 작성)
2. `/app/text2sql/engine.py`에 스키마-프롬프트 템플릿 입력
3. llama.cpp 모델 파일을 `models/`에 배치하고 `/app/core/llm.py`에 경로 지정 (후속 추가)
4. 운영 전환 시 PostgreSQL/PGVector로 전환

## 6) 라이선스
이 프로젝트 템플릿은 MIT License.
