from .utils import search_in, get_chunks, get_index
from src.model import MinimalSearchResults, StudentSearchResults, RagDataset
from pydantic import ValidationError
from pathlib import Path
import json
import sys


def search_dataset(dataset_path: str, k: int, save_directory: str) -> None:
    """
    Run search over a whole dataset and write a StudentSearchResults JSON file.

    Args:
        dataset_path (str): the path to the dataset
        k (int): the number of sources for each query
        save_directory (str): the path to the output directory
    """
    index = get_index()
    chunks = get_chunks()
    questions: RagDataset = get_unanswered_question(dataset_path)

    search_results: list[MinimalSearchResults] = []

    if len(questions.rag_questions) == 0:
        print("The dataset should not be empty.")
        sys.exit(1)

    for question in questions.rag_questions:
        search_results.append(
            MinimalSearchResults(
                question_id=question.question_id,
                question=question.question,
                retrieved_sources=search_in(question.question,
                                            k, index, chunks)))

    student_search_result = StudentSearchResults(
        search_results=search_results,
        k=k
    )
    export_result(save_directory + "/" + get_file(dataset_path),
                  student_search_result)


def export_result(save_file: str, result: StudentSearchResults) -> None:
    """
    Exports the result to the file

    Args:
        save_file (str): The file to export to
        result (StudentSearchResults): The result
    """
    try:
        with open(save_file, "w") as file:
            json.dump(result.model_dump(),
                      file, indent=4)
        print(f"Saved student_search_results to {save_file}")
    except (FileNotFoundError, PermissionError):
        print("Unable to open the save directory")


def get_unanswered_question(dataset_path: str) -> RagDataset:
    """
    Retrieve data from the file

    Args:
        dataset_path (str): the data file
    
    Returns:
        Usable data
    """
    try:
        with open(dataset_path, "r") as file:
            datas = json.load(file)
            return RagDataset(**datas)
    except (FileNotFoundError, PermissionError):
        print("Unable to open the dataset file")
    except (json.JSONDecodeError):
        print("The dataset JSON is poorly formatted.")
    except (ValidationError):
        print("Error during dataset validation by Pydantic")
    sys.exit(1)


def get_file(save_directory: str) -> str:
    """
    Returns the filename without the path

    Args:
        save_directory (str): The full path to the file
    
    Returns:
        (str): The name
    """
    return Path(save_directory).name
