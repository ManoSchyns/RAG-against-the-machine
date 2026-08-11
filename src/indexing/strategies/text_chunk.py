def text_spliter(indentation: int, data: str) -> list[str]:
    """
    Method for splitting part of the text file

    Args:
        indentation (int): the current indentation
        data (str): the part of the file to process

    Returns:
        list[str]: the split file content
    """
    size = len(data)

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
