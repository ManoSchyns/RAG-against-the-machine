from src.model import RagDataset, StudentSearchResults
from pydantic import ValidationError
import json
import sys


def evaluate(student_search_results_path: str, dataset_path: str):
    students_data: StudentSearchResults = get_students_data(student_search_results_path)
    validation_data: RagDataset = get_data_set(dataset_path)
    # TODO

def evaluate_one_question():
    # TODO
    pass

def get_data_set(dataset_path: str) -> RagDataset:
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
    except (FileNotFoundError, PermissionError) as e:
        print(f"Unable to open the dataset file: {e}")
    except (json.JSONDecodeError):
        print("The dataset JSON is poorly formatted.")
    except (ValidationError) as e:
        print(f"Error during dataset validation by Pydantic")
    sys.exit(1)

def get_students_data(dataset_path: str) -> StudentSearchResults:
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
    except (FileNotFoundError, PermissionError) as e:
        print(f"Unable to open the student data file: {e}")
    except (json.JSONDecodeError):
        print("The students dataset JSON is poorly formatted.")
    except (ValidationError) as e:
        print(f"Error during students dataset validation by Pydantic")
    sys.exit(1)
