def replaceAll(string: str, keys: list, words: list) -> str:
    if len(keys) != len(words): raise ValueError
    for i, item in enumerate(keys):
        if words[i] is None: words[i] = 'Не указано'
        string = string.replace(item, str(words[i]))
    return string