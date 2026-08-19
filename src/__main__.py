from .indexing import index
from .retrieval import search, search_dataset
from .answer import answer
from .answer import answer_dataset
import fire

if __name__ == "__main__":
    fire.Fire({
        "index": index,
        "search": search,
        "search_dataset": search_dataset,
        "answer": answer,
        "answer_dataset": answer_dataset
    },
        name="rag")
