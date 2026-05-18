import note_manager
from typing import Callable, Dict


class MessageStrings:
    """Константы для сообщений консоли."""

    MENU_HEADER = "\nВыберите действие:"
    MENU_LIST = "1 - Список заметок"
    MENU_CREATE = "2 - Создать заметку"
    MENU_EDIT = "3 - Изменить заметку"
    MENU_DELETE = "4 - Удалить заметку"
    MENU_EXIT = "5 - Выход"

    PROMPT_ACTION = "Введите номер действия: "
    PROMPT_TITLE = "Введите название заметки: "
    PROMPT_TEXT = "Введите текст заметки: "
    PROMPT_EDIT_TITLE = "Введите название изменяемой заметки: "
    PROMPT_NEW_TEXT = "Введите новый текст заметки: "
    PROMPT_DELETE_TITLE = "Введите название удаляемой заметки: "

    MSG_EMPTY_LIST = "Список заметок пуст."
    MSG_LIST_HEADER = "\nСписок ваших заметок:"
    MSG_CREATED = "Заметка успешно создана!"
    MSG_UPDATED = "Заметка успешно изменена!"
    MSG_DELETED = "Заметка успешно удалена!"
    MSG_NOT_FOUND = "Ошибка: Заметка не найдена."
    MSG_CURRENT_TEXT = "Текущий текст: "
    MSG_ERROR = "Ошибка: "
    MSG_INVALID_INPUT = "Неверный ввод. Пожалуйста, выберите пункт от 1 до 5."
    MSG_EXIT = "Выход из программы."


def print_menu() -> None:
    """Вывести меню действий."""
    print(MessageStrings.MENU_HEADER)
    print(MessageStrings.MENU_LIST)
    print(MessageStrings.MENU_CREATE)
    print(MessageStrings.MENU_EDIT)
    print(MessageStrings.MENU_DELETE)
    print(MessageStrings.MENU_EXIT)


def list_notes() -> None:
    """Вывести все заметки."""
    notes = note_manager.load_notes()
    if not notes:
        print(MessageStrings.MSG_EMPTY_LIST)
        return
    print(MessageStrings.MSG_LIST_HEADER)
    for title in notes:
        print(f"- {title}")


def create_note() -> None:
    """Создать новую заметку."""
    title = input(MessageStrings.PROMPT_TITLE).strip()
    text = input(MessageStrings.PROMPT_TEXT)
    try:
        note_manager.add_note(title, text)
        print(MessageStrings.MSG_CREATED)
    except ValueError as e:
        print(f"{MessageStrings.MSG_ERROR}{e}")


def edit_note() -> None:
    """Изменить текст существующей заметки."""
    title = input(MessageStrings.PROMPT_EDIT_TITLE).strip()
    notes = note_manager.load_notes()
    if title not in notes:
        print(MessageStrings.MSG_NOT_FOUND)
        return
    print(f"{MessageStrings.MSG_CURRENT_TEXT}{notes[title]}")
    text = input(MessageStrings.PROMPT_NEW_TEXT)
    try:
        note_manager.update_note(title, text)
        print(MessageStrings.MSG_UPDATED)
    except KeyError as e:
        print(f"{MessageStrings.MSG_ERROR}{e}")


def delete_note() -> None:
    """Удалить выбранную заметку."""
    title = input(MessageStrings.PROMPT_DELETE_TITLE).strip()
    try:
        note_manager.delete_note(title)
        print(MessageStrings.MSG_DELETED)
    except KeyError as e:
        print(f"{MessageStrings.MSG_ERROR}{e}")


def _get_user_choice() -> str:
    """Получить выбор пользователя."""
    return input(MessageStrings.PROMPT_ACTION).strip()


def _execute_action(actions: Dict[str, Callable[[], None]], choice: str) -> bool:
    """Выполнить действие по выбору пользователя.

    Возвращает False, если пользователь хочет выйти, иначе True.
    """
    if choice == "5":
        print(MessageStrings.MSG_EXIT)
        return False

    action = actions.get(choice)
    if action:
        action()
    else:
        print(MessageStrings.MSG_INVALID_INPUT)

    return True


def main() -> None:
    """Главная функция приложения."""
    actions: Dict[str, Callable[[], None]] = {
        "1": list_notes,
        "2": create_note,
        "3": edit_note,
        "4": delete_note,
    }

    while True:
        print_menu()
        choice = _get_user_choice()
        if not _execute_action(actions, choice):
            break


if __name__ == "__main__":
    main()