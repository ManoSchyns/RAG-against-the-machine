from src.model import (StudentSearchResultsAndAnswer,
                       StudentSearchResults, MinimalAnswer)
import json
from pydantic import ValidationError
import sys
from pathlib import Path
from tqdm import tqdm
from .llm import Llm


def answer_dataset(student_search_results_path: str,
                   save_directory: str) -> None:
    """
    Uses the LLM and the research performed to answer the questions
    Saves the result to the directory

    Args:
        student_search_results_path (str): the file containing the data
        save_directory (str): the output directory
    """

    answer_result: list[MinimalAnswer] = []
    search_result: StudentSearchResults = get_unanswered_search_result(
        student_search_results_path)

    model: Llm = Llm()

    for elem in tqdm(search_result.search_results,
                     desc="Answering", ncols=100, unit=" questions"):

        model.generate_prompt(elem.question, elem.retrieved_sources)
        answer = model.generate()

        answer_result.append(
            MinimalAnswer(
                answer=answer,
                question_id=elem.question_id,
                question=elem.question,
                retrieved_sources=elem.retrieved_sources
            )
        )
        model.reset()

    save_file = save_directory + "/" + get_file(student_search_results_path)
    export_result(save_file,
                  StudentSearchResultsAndAnswer(
                    search_results=answer_result,
                    k=search_result.k
                  ))
    len_questions = len(answer_result)

    print(f"Loaded {len_questions} questions ... Processed "
          f"{len_questions} of {len_questions} questions"
          f"\nSaved student_search_results_and_answer to {save_file}")


def export_result(save_file: str,
                  result: StudentSearchResultsAndAnswer) -> None:
    """
    Exports the result to the file

    Args:
        save_file (str): The file to export to
        result (StudentSearchResultsAndAnswer): The result
    """
    try:
        with open(save_file, "w") as file:
            json.dump(result.model_dump(),
                      file, indent=4)
        print(f"Saved student_search_results to {save_file}")
    except (FileNotFoundError, PermissionError):
        print("Unable to open the save directory")


def get_unanswered_search_result(dataset_path: str) -> StudentSearchResults:
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
            return StudentSearchResults(**datas)
    except (FileNotFoundError, PermissionError):
        print("Unable to open the dataset file")
    except (json.JSONDecodeError):
        print("The dataset JSON is poorly formatted.")
    except (ValidationError):
        print("Error during dataset validation by Pydantic")
    sys.exit(1)


def get_file(path_file: str) -> str:
    """
    Returns the filename without the path

    Args:
        path_file (str): The full path to the file

    Returns:
        (str): The name
    """
    return Path(path_file).name
