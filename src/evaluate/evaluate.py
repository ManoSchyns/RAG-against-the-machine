from src.model import (RagDataset, StudentSearchResults,
                       AnsweredQuestion, MinimalSearchResults,
                       UnansweredQuestion)
from pydantic import ValidationError
from typing import Any
import json
import sys

OVERLAP = 0.05


def evaluate(student_search_results_path: str, dataset_path: str) -> None:
    """
    Evaluate the student's search results by
    comparing them with the dataset

    Args:
        student_search_results_path (str):
        the file containing the student's search results

        dataset_path (str): the correct data for comparison
    """
    students_data: StudentSearchResults = get_students_data(
        student_search_results_path)
    validation_data: RagDataset = get_data_set(dataset_path)

    prev_check(students_data, validation_data)

    recall: dict[int, float] = {
        1: 0.0,
        3: 0.0,
        5: 0.0,
        10: 0.0
    }
    question_n: int = len(validation_data.rag_questions)

    for valid_question in validation_data.rag_questions:
        to_evaluate: MinimalSearchResults | None = next(
            (
                search_result
                for search_result in students_data.search_results
                if search_result.question_id == valid_question.question_id
            ),
            None
        )
        if to_evaluate is not None and isinstance(valid_question,
                                                  AnsweredQuestion):
            evaluate_one_question(recall, valid_question, to_evaluate)

    show_evaluation(recall, question_n)


def show_evaluation(recall: dict[int, float], question_n: int) -> None:
    """
    Displays the observed results

    Args:
        recall (dict[int, float]): the results for each metric
        question_n (int): the total number of questions
    """
    print("🎯 Evaluation Results")
    print("========================================")
    print(f"📊 Questions evaluated: {question_n}")

    for metric, value in recall.items():
        recall[metric] = value / question_n
        print(f"📈 Recall@{metric}: {recall[metric]:.3f} "
              f"({recall[metric] * 100:.1f}%)")

    print(recall)


def prev_check(stud_data: StudentSearchResults,
               validation_data: RagDataset) -> None:
    """
    Performs checks prior to calculations

    Args:
        stud_data (StudentSearchResults): Student data
        validation_data (RagDataset): Valid data
    """

    def get_count_sources(quest_list: list[Any]) -> int:
        """
        Calculates the sources of a question list

        Args:

        quest_list(list): The question list

        Returns:

        (int): The number of sources
        """
        count: int = 0

        for quest in quest_list:
            if isinstance(quest, AnsweredQuestion):
                if len(quest.sources) > 0:
                    count += 1
            elif isinstance(quest, MinimalSearchResults):
                if len(quest.retrieved_sources) > 0:
                    count += 1
        return count

    valid_questions: list[AnsweredQuestion |
                          UnansweredQuestion] = validation_data.rag_questions
    stud_quest: list[MinimalSearchResults] = stud_data.search_results

    total_valid_quest: int = len(valid_questions)

    source_valid_quest: int = get_count_sources(valid_questions)
    source_stud_quest: int = get_count_sources(stud_quest)

    print(f"Total number of questions: {total_valid_quest}")
    print(f"Total number of questions with sources: {source_valid_quest}")
    print("Total number of questions with student sources: "
          f"{source_stud_quest}\n")


def calculate_iou(
    start1: int,
    end1: int,
    start2: int,
    end2: int,
) -> float:
    """
    Calculates the distance between two index ranges

    Args:
        start1 (int): start index of the first source
        end1 (int): end index of the first source
        start2 (int): start index of the second source
        end2 (int): end index of the second source

    Returns:
        (float): the distance
    """
    intersection = max(
        0,
        min(end1, end2) - max(start1, start2)
    )

    union = max(end1, end2) - min(start1, start2)

    return intersection / union if union > 0 else 0.0


def evaluate_one_question(recall: dict[int, float],
                          valid_quest: AnsweredQuestion,
                          to_evaluate: MinimalSearchResults) -> None:
    """
    Evaluates the student's sources for a question by
    comparing them to the valid sources.

    Args:
        recall (dict): A dictionary containing a value for each metric.
        valid_question: The reference question, including valid sources.
        to_evaluate: The question containing the student's sources.
    """

    def evaluate_on_recall(
        metric: int,
        valid_quest: AnsweredQuestion,
        to_evaluate: MinimalSearchResults,
    ) -> float:
        """
        For a given metric, compares a question's sources with the valid ones.

        Args:
            metric (int): the number of sources to compare
            valid_quest: the valid sources
            to_evaluate: the sources to compare

        Returns:
            (float): the result of the comparison
        """

        found_sources: set[int] = set()

        for stud_source in to_evaluate.retrieved_sources[:metric]:

            for valid_index, valid_source in enumerate(valid_quest.sources):

                if valid_index in found_sources:
                    continue

                if stud_source.file_path != valid_source.file_path:
                    continue

                iou = calculate_iou(
                    stud_source.first_character_index,
                    stud_source.last_character_index,
                    valid_source.first_character_index,
                    valid_source.last_character_index,
                )

                if iou >= OVERLAP:
                    found_sources.add(valid_index)
                    break

        total_to_find = len(valid_quest.sources)

        if total_to_find == 0:
            return 0.0

        return len(found_sources) / total_to_find

    for metric in recall.keys():
        recall[metric] += evaluate_on_recall(metric, valid_quest, to_evaluate)


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
            result = RagDataset(**datas)
            if not isinstance(result.rag_questions[0], AnsweredQuestion):
                raise ValidationError("None")
            return result
    except (FileNotFoundError, PermissionError) as e:
        print(f"Unable to open the dataset file: {e}")
    except (json.JSONDecodeError):
        print("The dataset JSON is poorly formatted.")
    except (ValidationError):
        print("Error during dataset validation by Pydantic")
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
            stud_data = StudentSearchResults(**datas)

            print("Student data is valid: True")
            return stud_data
    except (FileNotFoundError, PermissionError) as e:
        print(f"Unable to open the student data file: {e}")
    except (json.JSONDecodeError):
        print("The students dataset JSON is poorly formatted.")
    except (ValidationError):
        print("Student data is valid: False")
    sys.exit(1)
