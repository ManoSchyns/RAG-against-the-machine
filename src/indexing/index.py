from pathlib import Path
import bm25s
import sys
import json
from tqdm import tqdm
from src.model import MinimalSource
from .strategies import strat
from src.config import (CHUNK_FOLDER,
                        INDEX_FOLDER,
                        CHUNK_DESTINATION)

try:
    origin = Path("data/raw")

    Path(CHUNK_FOLDER).mkdir(exist_ok=True)
    Path(INDEX_FOLDER).mkdir(exist_ok=True)
except Exception:
    print("Please set up the folders and files.")
    sys.exit(1)


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
    chunks: list[MinimalSource] = []

    files: list[Path] = [
        file for file in origin.rglob("*")
        if file.is_file()
    ]
    if len(files) == 0:
        print("No files in the raw data. Impossible to work.")
        sys.exit(1)

    for file in tqdm(files, desc="Chunking", ncols=100, unit=" file"):

        if not file.is_file():
            continue

        if file.suffix == ".py":
            chunks.extend(strat(max_chunk_size, str(file), 0))

        elif file.suffix == ".txt" or file.suffix == ".md":
            chunks.extend(strat(max_chunk_size, str(file), 1))

    export_chunks(chunks)
    index_creator(chunks)
    print(f"Ingestion Complete! Indexed {len(chunks)} "
          "chunks under data/processed")


def index_creator(chunks: list[MinimalSource]) -> None:
    """
    Create the index for the chunks and save it to data/processed/index.
    """
    try:
        contents = [
            chunk.content
            for chunk in chunks
            ]

        tokenized_chunks = bm25s.tokenize(contents)

        indexer = bm25s.BM25()
        indexer.index(tokenized_chunks, show_progress=True)
        indexer.save(INDEX_FOLDER, show_progress=True)
    except (PermissionError) as e:
        print(f"Error: {e}")
        sys.exit(1)


def export_chunks(chunks: list[MinimalSource]) -> None:
    """
    Exports the resources to a file in JSON format

    Args:
        chunks (list[MinimalSource]): The data
    """
    try:
        with open(CHUNK_DESTINATION, "w") as file:
            file.write("[\n")

            for i, source in enumerate(
                tqdm(chunks, desc="Exporting chunks",
                     ncols=100, unit="chunk")
            ):
                json.dump(source.model_dump(), file, indent=4)

                if i < len(chunks) - 1:
                    file.write(",\n")

            file.write("\n]")
    except (FileNotFoundError, PermissionError) as e:
        print(f"Can't export index chunks: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"The JSON was poorly formatted.: {e}")
        sys.exit(1)
