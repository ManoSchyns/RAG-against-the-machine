"""
1) Parcourir les fichiers dasn data / raw

2 ) utiliser la stratégie py / md en fonction du
nom du fichier. ignorer les autres
Les seuls extentions acceptées .py, .md et .txt

3) Export retrieved_sources
"""
from pathlib import Path
import sys
import json
from src.model import MinimalSource
from .strategies import python_strat


origin = Path("data/raw")
destination = "data/processed/datas.json"


def chunk_index(chunk_max_size: int) -> list[MinimalSource]:
    retrieved_sources: list[MinimalSource] = []

    for file in origin.rglob("*"):

        if not file.is_file():
            continue

        if file.suffix == ".py":
            retrieved_sources.extend(python_strat(chunk_max_size, str(file)))

        elif file.suffix in (".txt", ".md"):
            pass
    export_sources(retrieved_sources)
    return retrieved_sources


def export_sources(retrieved_sources: list[MinimalSource]) -> None:
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
