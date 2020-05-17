from typing import List, Union, Any


def extract_type(token: str, sep: str = "-") -> str:
    if sep not in token:
        return token
    return token.split(sep, maxsplit=1)[1]


def extract_function(token: str, sep: str = "-") -> str:
    if sep not in token:
        return token
    return token.split(sep, maxsplit=1)[0]


def replace_prefix(string: str, match: str, sub: str) -> str:
    if string.startswith(match):
        return sub + string[len(match) :]
    return string[:]


def safe_get(xs: List[str], idx: int) -> Union[Any, None]:
    if idx < 0 or idx >= len(xs):
        return None
    return xs[idx]
