from functools import lru_cache
from langchain.llms import Ollama

@lru_cache(maxsize=1)
def load_llm(model_name: str = "Meta-Llama-3-Ko-Instruct-8B", temperature: float = 0.2):
    """
    Ollama LLM 로더 (최초 1회만 초기화; 이후 캐시 사용)
    - model_name: ollama list 로 확인 가능한 로컬 모델명
    """
    print("🚀 LLM 모델 초기화 (최초 1회)")
    return Ollama(
        model=model_name,
        system=(
            "당신은 한국어로만 답변하는 AI 어시스턴트입니다. "
            "문서 근거 범위 내에서만 답변하고, 불필요한 영어를 사용하지 마세요."
        ),
        temperature=temperature,
        num_ctx=4096,
    )
