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
import re


def python_strat(
    chunk_max_size: int,
    filename: str
) -> list[MinimalSource]:
    try:
        with open(filename, "r") as file:
            data = file.read()

        return chuncker(str(filename), chunk_max_size, data)

    except (FileNotFoundError, PermissionError):
        print(f"== :( == Error ===> Can't use file: {filename}")
        return []


def spliter(indentation: int, data: str) -> list[str]:
    size = len(data)

    pattern = rf'(?=^{" " * indentation}(?:class|def)\s+)'

    splitted = re.split(pattern, data, flags=re.MULTILINE)

    if len(splitted) == 1:

        indice = data.find("\n\n")
        if indice > 0:
            return [
                data[:indice],
                data[indice:]
            ]

        indice = data.find("\n")
        if indice > 0:
            return [
                data[:indice],
                data[indice:]
                ]

        middle = size // 2
        return [
            data[:middle],
            data[middle:]
        ]

    return splitted


def chuncker(
    filename: str,
    chunk_max_size: int,
    data: str
) -> list[MinimalSource]:

    sources: list[MinimalSource] = []

    def recursive_chucker(
        indent: int,
        curr_data: str,
        start_index: int
    ) -> None:

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

        # On découpe le bloc
        splitted_data = spliter(indent, curr_data)

        # Position du prochain bloc DANS curr_data
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
