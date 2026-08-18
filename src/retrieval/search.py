from .utils import search_in, get_chunks, get_index
import sys


def search(query: str, k: int) -> str:
    """
    Return the top-k sources for a single query

    Returns:
        str: the top-k sources for a single query 
    """
    ret_val: str = ""

    chunks = get_chunks()
    index = get_index()

    datas = search_in(query, k, index, chunks)

    if len(datas) == 0:
        sys.exit(1)

    for i, data in enumerate(datas):
        ret_val += f"{data.file_path} "
        f"[{data.first_character_index}:{data.last_character_index}]"
        if i < len(datas) - 1:
            ret_val += "\n"
    return ret_val
