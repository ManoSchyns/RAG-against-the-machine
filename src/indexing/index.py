from pathlib import Path
import sys
import json
from tqdm import tqdm
from src.model import MinimalSource
from .strategies import strat


origin = Path("data/raw")
destination = "data/processed/datas.json"


def index(max_chunk_size: int = 2000) -> None:
    """
    Iterate through the files and choose the best strategy
    for indexing the files.

    Args:
        max_chunk_size (int): The maximum size of each chunk.

    Returns:
        list[MinimalSource]: A list of chunks.
    """
    if max_chunk_size < 1 or max_chunk_size > 2000:
        print("max_chunk_size must be between 1 and 2000")
        sys.exit(1)
    retrieved_sources: list[MinimalSource] = []

    files: list[Path] = [
        file for file in origin.rglob("*")
        if file.is_file()
    ]

    for file in tqdm(files, desc="Chunking", ncols=100, unit=" file"):

        if not file.is_file():
            continue

        if file.suffix == ".py":
            retrieved_sources.extend(strat(max_chunk_size, str(file), 0))

        elif file.suffix == ".txt":
            retrieved_sources.extend(strat(max_chunk_size, str(file), 1))

        elif file.suffix == ".md":
            retrieved_sources.extend(strat(max_chunk_size, str(file), 2))

    export_sources(retrieved_sources)
    print(f"Ingestion Complete! Indexed {len(retrieved_sources)} "
          "chunks under data/processed")


def export_sources(retrieved_sources: list[MinimalSource]) -> None:
    """
    Exports the resources to a file in JSON format

    Args:
        retrieved_sources (list[MinimalSource]): The data
    """
    try:
        with open(destination, "w") as file:
            file.write("[\n")

            for i, source in enumerate(
                tqdm(retrieved_sources, desc="Exporting",
                     ncols=100, unit="chunk")
            ):
                json.dump(source.model_dump(), file, indent=4)

                if i < len(retrieved_sources) - 1:
                    file.write(",\n")

            file.write("\n]")
    except (FileNotFoundError, PermissionError) as e:
        print(f"Can't export index chunks: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"The JSON was poorly formatted.: {e}")
        sys.exit(1)
