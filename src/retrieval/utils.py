from src.config import CHUNK_DESTINATION, INDEX_FOLDER
import bm25s
from src.model import MinimalSource
from pydantic import ValidationError
import sys
import json


def get_chunks() -> list[MinimalSource]:
    try:
        with open(CHUNK_DESTINATION, "r") as file:
            datas = json.load(file)
            return [MinimalSource(**data) for data in datas]
    except (FileNotFoundError, PermissionError,
            ValidationError, json.JSONDecodeError):
        print("It is impossible to work. The index has not been created.")
    sys.exit(1)


def get_index() -> bm25s.BM25:
    try:
        return bm25s.BM25.load(INDEX_FOLDER)
    except (FileNotFoundError, PermissionError):
        print("It is impossible to work. The index has not been created.")
    sys.exit(1)


def search_in(query: str, k: int, index: bm25s.BM25,
              chunks: list[MinimalSource]) -> list[MinimalSource]:
    if not query.strip():
        print("The query must contains caracters")
        return []
    if k <= 0:
        print("The top-k value must be more than 0")
        return []

    query_tokens = bm25s.tokenize(query)
    chunk_ids = index.retrieve(query_tokens, k=k)
    return [chunks[ids] for ids in chunk_ids[0][0]]
