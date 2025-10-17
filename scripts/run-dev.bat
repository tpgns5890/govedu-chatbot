\
    @echo off
    setlocal
    if not exist .venv (
      python -m venv .venv
    )
    call .venv\Scripts\activate
    pip install -U pip
    pip install -r requirements.txt
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    endlocal
