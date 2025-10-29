from fastapi import FastAPI, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from app.api.router import router as api_router
from app.text2sql.router import smart_router
import uvicorn

app = FastAPI(
    title="Govedu Hybrid Chatbot",
    description="RAG + Text2SQL 통합형 온프레미스 챗봇 서버",
    version="2.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/webchat", response_class=HTMLResponse)
async def webchat(request: Request, query: str = Form(...)):
    result = smart_router(query)
    return templates.TemplateResponse("index.html", {"request": request, "result": result, "query": query})

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8090, reload=True)
