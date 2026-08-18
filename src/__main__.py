from .indexing import index
from .retrieval import search, search_dataset
import fire

if __name__ == "__main__":
    fire.Fire({
        "index": index,
        "search": search,
        "search_dataset": search_dataset
    },
    name="rag"
    )
