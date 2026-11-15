"""Формирование слагов (человекочитаемых частей URL) из русских имён."""

from django.utils.text import slugify

TRANSLIT = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "e",
    "ж": "zh", "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m",
    "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
    "ф": "f", "х": "h", "ц": "ts", "ч": "ch", "ш": "sh", "щ": "sch",
    "ъ": "", "ы": "y", "ь": "", "э": "e", "ю": "yu", "я": "ya",
}


def transliterate(text: str) -> str:
    return "".join(TRANSLIT.get(char, char) for char in text.lower())


def make_slug(text: str, taken: set[str], max_length: int = 60) -> str:
    """Возвращает слаг, которого ещё нет в множестве taken.

    «Анна» -> «anna»; при совпадении добавляется номер: «anna-2».
    """
    base = slugify(transliterate(text))[:max_length] or "user"
    slug = base
    number = 2
    while slug in taken:
        slug = f"{base}-{number}"
        number += 1
    return slug
