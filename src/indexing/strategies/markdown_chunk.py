import re


def mk_spliter(level: int, data: str) -> list[str]:
    """
    Method for splitting part of the markdown file

    Args:
        level (int): the current level
        data (str): the part of the file to process

    Returns:
        list[str]: the split file content
    """
    size = len(data)

    pattern = r'(?=^(?:#|##|###|####|#####|######)\s+)'

    matches = list(re.finditer(pattern, data, flags=re.MULTILINE))

    if len(matches) > 1:
        match = matches[1]

        return [
            data[:match.start()],
            data[match.start():]
        ]

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
