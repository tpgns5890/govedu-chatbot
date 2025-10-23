import os
from langchain_community.embeddings import HuggingFaceEmbeddings  # <- community에서 임포트
from langchain_community.vectorstores import Chroma               # <- community에서 임포트
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

from app.rag.llm import load_llm


def query_rag(question: str) -> str:
    """
    질문 -> (Chroma 검색) -> (LLM 생성)까지 수행하여 한국어 답변을 반환.
    """
    print("RAG 쿼리 실행:", question)

    # 1) 임베딩 모델 (indexer.py와 동일 모델 유지)
    embeddings = HuggingFaceEmbeddings(model_name="jhgan/ko-sroberta-multitask")

    # 2) 벡터DB 로드
    vector_path = os.path.join("data", "vector")
    if not os.path.isdir(vector_path):
        raise FileNotFoundError("data/vector 가 없습니다. 먼저 indexer를 실행해 인덱스를 생성하세요.")
    vectordb = Chroma(persist_directory=vector_path, embedding_function=embeddings)
    retriever = vectordb.as_retriever(search_kwargs={"k": 3})

    # 3) LLM (Ollama) 로드 — load_llm 내부에 캐시/한국어 system prompt 포함
    llm = load_llm()

    # 4) 한국어 전용 프롬프트
    prompt = ChatPromptTemplate.from_template(
        """
        당신은 한국어로만 답변하는 AI 어시스턴트입니다.
        아래 문서 내용을 근거로, 질문에 정확하고 간결하게 답변하세요.
        근거가 불충분하면 "문서에 근거가 없습니다"라고 말하세요.
        불필요한 영어를 사용하지 마세요.

        [문서]
        {context}

        [질문]
        {input}
        """
    )

    # 5) 체인 구성 (최신 API)
    document_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, document_chain)

    # 6) 실행
    result = rag_chain.invoke({"input": question})
    return result.get("answer", "답변을 생성하지 못했습니다.")
