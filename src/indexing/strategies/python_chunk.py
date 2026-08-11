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

import re

def python_spliter(indentation: int, data: str) -> list[str]:
    """
    Method for splitting part of the python file

    Args:
        indentation (int): the current indentation
        data (str): the part of the file to process

    Returns:
        list[str]: the split file content
    """
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
