from pathlib import Path
import sys
import json
from src.model import MinimalSource
from .strategies import strat


origin = Path("data/raw")
destination = "data/processed/datas.json"


def chunk_index(chunk_max_size: int) -> list[MinimalSource]:
    """
    Iterate through the files and choose the best strategy
    for indexing the files.

    Args:
        chunk_max_size (int): The maximum size of each chunk.

    Returns:
        list[MinimalSource]: A list of chunks.
    """
    retrieved_sources: list[MinimalSource] = []

    for file in origin.rglob("*"):

        if not file.is_file():
            continue

        if file.suffix == ".py":
            retrieved_sources.extend(strat(chunk_max_size, str(file), 0))

        elif file.suffix == ".txt":
            pass
            #retrieved_sources.extend(start(chunk_max_size, str(file), 1))

        elif file.suffix == ".txt":
            pass
            #retrieved_sources.extend(start(chunk_max_size, str(file), 2))

    export_sources(retrieved_sources)
    return retrieved_sources


def export_sources(retrieved_sources: list[MinimalSource]) -> None:
    """
    Exports the resources to a file in JSON format

    Args:
        retrieved_sources (list[MinimalSource]): The data
    """
    try:
        with open(destination, "w") as file:
            json.dump(
                [source.to_json() for source in retrieved_sources],
                file, indent=4)
    except (FileNotFoundError, PermissionError) as e:
        print(f"Can't export index chunks: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"The JSON was poorly formatted.: {e}")
