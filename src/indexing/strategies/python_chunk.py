import re


def python_spliter(level: int, data: str) -> list[str]:
    """
    Method for splitting part of the python file

    Args:
        level (int): the current level
        data (str): the part of the file to process

    Returns:
        list[str]: the split file content
    """
    size = len(data)

    level = level * 4
    pattern = rf'(?=^{" " * level}(?:class|def)\s+)'

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
