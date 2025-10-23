import argparse
from pathlib import Path
from typing import List

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# 프로젝트 기본 경로
DEFAULT_POLICIES_DIR = Path("data/policies")
DEFAULT_VECTOR_DIR = Path("data/vector")

# 한국어 임베딩 모델 (무료/CPU OK)
EMBED_MODEL_NAME = "jhgan/ko-sroberta-multitask"

def load_pdfs(policies_dir: Path) -> List:
    docs = []
    for pdf in sorted(policies_dir.glob("*.pdf")):
        loader = PyPDFLoader(str(pdf))
        docs.extend(loader.load())
    if not docs:
        raise FileNotFoundError(f"PDF가 없습니다: {policies_dir.resolve()}")
    return docs

def split_docs(docs: List):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=900, chunk_overlap=150, separators=["\n\n", "\n", " ", ""]
    )
    return splitter.split_documents(docs)

def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name=EMBED_MODEL_NAME,
        # sentence-transformers 기본 세팅: CPU에서 자동 동작
        encode_kwargs={"normalize_embeddings": True}
    )

def build_index(policies_dir: Path = DEFAULT_POLICIES_DIR,
                vector_dir: Path = DEFAULT_VECTOR_DIR):
    policies_dir.mkdir(parents=True, exist_ok=True)
    vector_dir.mkdir(parents=True, exist_ok=True)

    print(f"[1/4] PDF 로딩: {policies_dir.resolve()}")
    docs = load_pdfs(policies_dir)

    print(f"[2/4] 청크 분할 (문서 → 작업 단위)")
    chunks = split_docs(docs)
    print(f" - 문서 수: {len(docs)}, 청크 수: {len(chunks)}")

    print(f"[3/4] 임베딩 모델 로딩: {EMBED_MODEL_NAME}")
    embeddings = get_embeddings()

    print(f"[4/4] ChromaDB 적재: {vector_dir.resolve()}")
    Chroma.from_documents(documents=chunks, embedding=embeddings, persist_directory=str(vector_dir))
    print("✅ 인덱스 구축 완료")

def query_index(query: str,
                vector_dir: Path = DEFAULT_VECTOR_DIR,
                k: int = 5):
    if not any(vector_dir.iterdir()):
        raise RuntimeError(f"인덱스가 없습니다. 먼저 인덱스를 구축하세요: {vector_dir.resolve()}")

    embeddings = get_embeddings()
    vectordb = Chroma(persist_directory=str(vector_dir), embedding_function=embeddings)
    results = vectordb.similarity_search(query, k=k)

    print(f"\n[검색 질의] {query}")
    print("— 상위 결과 —")
    for i, doc in enumerate(results, 1):
        meta = doc.metadata or {}
        src = meta.get("source", "unknown")
        page = meta.get("page", "?")
        text = (doc.page_content or "").replace("\n", " ")
        if len(text) > 220:
            text = text[:220] + "..."
        print(f"{i}. {src} (p.{page})")
        print(f"   {text}\n")

def main():
    parser = argparse.ArgumentParser(description="RAG Indexer (PDF → ChromaDB)")
    sub = parser.add_subparsers(dest="cmd")

    b = sub.add_parser("build", help="PDF 인덱스 구축")
    b.add_argument("--policies", default=str(DEFAULT_POLICIES_DIR), help="PDF 폴더 경로")
    b.add_argument("--vector", default=str(DEFAULT_VECTOR_DIR), help="ChromaDB 폴더 경로")

    q = sub.add_parser("query", help="인덱스 질의")
    q.add_argument("--vector", default=str(DEFAULT_VECTOR_DIR), help="ChromaDB 폴더 경로")
    q.add_argument("--k", type=int, default=5, help="상위 문서 수")
    q.add_argument("text", nargs="+", help="질의 문장")

    args = parser.parse_args()

    if args.cmd == "build":
        build_index(Path(args.policies), Path(args.vector))
    elif args.cmd == "query":
        query = " ".join(args.text)
        query_index(query, Path(args.vector), args.k)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()