import json
import os
from typing import Dict, Optional


class Constants:
    """Константы для модуля управления заметками."""

    FILENAME = "notes.json"
    ENCODING = "utf-8"
    JSON_INDENT = 4


class ErrorMessages:
    """Сообщения об ошибках для пользователя."""

    EMPTY_TITLE = "Название заметки не может быть пустым."
    DUPLICATE_TITLE = "Заметка с таким названием уже существует."
    NOT_FOUND = "Заметка не найдена."
    DELETE_NOT_FOUND = "Попытка удалить несуществующую заметку."
    JSON_CORRUPTED = "Ошибка: файл JSON повреждён. Возвращён пустой словарь."


def _load_json_file() -> Optional[Dict]:
    """Загрузить JSON-файл с ошибочной обработкой.

    Возвращает None если файла не существует, словарь если успешно,
    или пустой словарь при ошибке парсинга JSON.
    """
    if not os.path.exists(Constants.FILENAME):
        return None
    try:
        with open(Constants.FILENAME, "r", encoding=Constants.ENCODING) as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(ErrorMessages.JSON_CORRUPTED)
        return {}


def load_notes() -> Dict[str, str]:
    """Загрузить заметки из JSON-файла.

    Если файла нет или он повреждён, возвращается пустой словарь.
    """
    data = _load_json_file()
    if data is None:
        return {}
    return data if isinstance(data, dict) else {}


def save_notes(notes: Dict[str, str]) -> None:
    """Сохранить заметки в JSON-файл."""
    with open(Constants.FILENAME, "w", encoding=Constants.ENCODING) as f:
        json.dump(notes, f, ensure_ascii=False, indent=Constants.JSON_INDENT)

def add_note(title: str, text: str) -> None:
    """Добавить новую заметку с проверкой имени.

    Args:
        title: Название заметки (будет обрезано с концов).
        text: Текст содержимого заметки.

    Raises:
        ValueError: Если название пусто или заметка уже существует.
    """
    title = title.strip()
    if not title:
        raise ValueError(ErrorMessages.EMPTY_TITLE)

    notes = load_notes()
    if title in notes:
        raise ValueError(ErrorMessages.DUPLICATE_TITLE)

    notes[title] = text
    save_notes(notes)


def update_note(title: str, text: str) -> None:
    """Обновить текст существующей заметки.

    Args:
        title: Название заметки для обновления.
        text: Новый текст содержимого.

    Raises:
        KeyError: Если заметка не найдена.
    """
    notes = load_notes()
    if title not in notes:
        raise KeyError(ErrorMessages.NOT_FOUND)

    notes[title] = text
    save_notes(notes)


def delete_note(title: str) -> None:
    """Удалить заметку по названию.

    Args:
        title: Название заметки для удаления.

    Raises:
        KeyError: Если заметка не существует.
    """
    notes = load_notes()
    if title not in notes:
        raise KeyError(ErrorMessages.DELETE_NOT_FOUND)

    del notes[title]
    save_notes(notes)