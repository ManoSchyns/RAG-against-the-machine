"""
Startégie python.

Comment faire ??

On nous donne un chunck max size

La stratégie serait ->

Faire en fonction de la taille. Si la taille est grande -> Sépration par classe

Si moins grande séparation par fonctions

Si moins grande séparation par bloc.

Dès qu'on a un bloc valide on le garde et on diminue les blocs plus grands

Et on réduit encore et encore en bloc plus petit jusqu'a avoir que des
éléments de la taille souhaitée
"""
from src.model import MinimalSource
from .python_chunk import python_spliter
from .text_chunk import text_spliter
from .markdown_chunk import mk_spliter

SPLITERS: list[callable] = [
    python_spliter,
    text_spliter,
    mk_spliter
]


def strat(
    chunk_max_size: int,
    filename: str,
    indice: int
) -> list[MinimalSource]:
    """
    Strategy for indexing the file

    Args:
        chunk_max_size (int): the maximum size of a chunk
        filename (str): the file to index
        indide (int): the extension index

    Returns:
        retrieved_sources (list[MinimalSource]): The data from the indexed file
    """
    try:
        with open(filename, "r") as file:
            data = file.read()

        return chuncker(str(filename), chunk_max_size, data, indice)

    except (FileNotFoundError, PermissionError):
        print(f"== :( == Error ===> Can't use file: {filename}")
        return []

def chuncker(
    filename: str,
    chunk_max_size: int,
    data: str,
    index: int
) -> list[MinimalSource]:
    """
    Function that indexes the file

    Args:
        filename (str): file name
        chunk_max_size (int): maximum chunk size
        data: file content
        indide (int): the extension index

    Returns:
        retrieved_sources (list[MinimalSource]): The data from the indexed file
    """

    sources: list[MinimalSource] = []

    def recursive_chucker(
        indent: int,
        curr_data: str,
        start_index: int
    ) -> None:
        """Recursively split data into chunks within the maximum size.

        Args:
            indent: Current indentation level used for structural splitting.
            curr_data: Current portion of the file being processed.
            start_index: Character index of curr_data in the original file.

        Returns:
            None. Valid chunks are added to the sources list.
        """

        # Le chunk est suffisamment petit
        if len(curr_data) <= chunk_max_size:
            sources.append(
                MinimalSource(
                    file_path=filename,
                    first_character_index=start_index,
                    last_character_index=start_index + len(curr_data) - 1
                )
            )
            return

        splitted_data = SPLITERS[index](indent, curr_data)

        local_index = 0

        for block in splitted_data:

            recursive_chucker(
                indent + 4,
                block,
                start_index + local_index
            )

            local_index += len(block)

    recursive_chucker(
        0,
        data,
        0
    )
    return sources
