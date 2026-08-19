from src.retrieval.utils import search_in, get_index, get_chunks
from src.model import MinimalSource
from .llm import Llm


def answer(query: str, k: int) -> str:
    """
    Answers a question using the index and the LLM

    Args:
        query (str): the question
        k (int): the number of sources for each query

    Returns:
        (str): the LLM's response
    """
    source: list[MinimalSource] = search_in(query, k,
                                            get_index(),
                                            get_chunks())
    model = Llm()

    model.generate_prompt(query, source)
    value = model.generate()
    return str(value)
