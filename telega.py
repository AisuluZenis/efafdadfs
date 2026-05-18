import telebot
from typing import Callable, Optional
import note_manager


class BotConfig:
    "Конфигурация Telegram-бота."""

    API_TOKEN = "8290128902:AAFvyCAo1ZiIs4YD_OMOYXKgOiuXSa09KdE"


class BotMessages:
    """Сообщения Telegram-бота."""

    WELCOME = (
        "👋 Привет! Я кроссплатформенный бот «Умные заметки».\n\n"
        "Доступные команды:\n"
        "/notes - Просмотреть список всех заметок\n"
        "/add - Создать новую заметку\n"
        "/open - Открыть и прочитать заметку\n"
        "/edit - Редактировать текст заметки\n"
        "/delete - Удалить заметку"
    )

    EMPTY_LIST = "💭 Список заметок пуст."
    LIST_HEADER = "📋 *Список ваших заметок:*"

    PROMPT_TITLE = "Введите название заметки:"
    PROMPT_TEXT = "Введите текст заметки:"
    PROMPT_OPEN = "Введите название заметки, которую хотите открыть:"
    PROMPT_EDIT = "Введите название заметки, которую хотите изменить:"
    PROMPT_DELETE = "Введите название заметки для удаления:"

    EMPTY_TITLE = ❌ Название не может быть пустым. Отмена."
    DUPLICATE = ❌ Заметка с таким названием уже существует. Отмена."
    NOT_FOUND = ❌ Заметка не найдена."
    SAVED = ✅ Заметка сохранена"
    UPDATED = ✅ Заметка '{title}' обновлена!"
    DELETED = 🗑 Заметка '{title}' успешно удалена."
    ERROR = ❌ Ошибка: {error}"
    CURRENT_TEXT = "Текущий текст заметки:\n`{text}`\n\nВведите новый текст:"


bot = telebot.TeleBot(BotConfig.API_TOKEN)

def _get_note_title_from_user(message) -> Optional[str]:
    """Отредактировать и получить название заметки."""
    return message.text.strip() if message.text else None


def _note_exists(title: str) -> bool:
    """Проверить, существует ли заметка."""
    return title in note_manager.load_notes()


@bot.message_handler(commands=["start", "help"])
def send_welcome(message) -> None:
    """Отправить приветственное сообщение с помощью."""
    bot.reply_to(message, BotMessages.WELCOME)

# --- ПРОСМОТР СПИСКА ЗАМЕТОК ---
@bot.message_handler(commands=["notes"])
def list_notes(message) -> None:
    """Отобразить список всех заметок."""
    notes = note_manager.load_notes()
    if not notes:
        bot.send_message(message.chat.id, BotMessages.EMPTY_LIST)
    else:
        response = BotMessages.LIST_HEADER + "\n" + "\n".join([f"\u2022 {title}" for title in notes.keys()])
        bot.send_message(message.chat.id, response, parse_mode="Markdown")

# --- СОЗДАНИЕ ЗАМЕТКИ (/add) ---
@bot.message_handler(commands=["add"])
def add_note_start(message) -> None:
    """Начать процесс создания заметки."""
    msg = bot.send_message(message.chat.id, BotMessages.PROMPT_TITLE)
    bot.register_next_step_handler(msg, process_add_title)


def process_add_title(message) -> None:
    """Обработать название заметки."""
    title = _get_note_title_from_user(message)
    if not title:
        bot.send_message(message.chat.id, BotMessages.EMPTY_TITLE)
        return

    if _note_exists(title):
        bot.send_message(message.chat.id, BotMessages.DUPLICATE)
        return

    msg = bot.send_message(message.chat.id, BotMessages.PROMPT_TEXT)
    bot.register_next_step_handler(msg, process_add_text, title)


def process_add_text(message, title: str) -> None:
    """Обработать текст заметки."""
    text = message.text
    try:
        note_manager.add_note(title, text)
        bot.send_message(message.chat.id, BotMessages.SAVED)
    except Exception as e:
        bot.send_message(message.chat.id, BotMessages.ERROR.format(error=e))

# --- ПРОСМОТР ЗАМЕТКИ (/open) ---
@bot.message_handler(commands=["open"])
def open_note_start(message) -> None:
    """Начать процесс открытия заметки."""
    msg = bot.send_message(message.chat.id, BotMessages.PROMPT_OPEN)
    bot.register_next_step_handler(msg, process_open_note)


def process_open_note(message) -> None:
    """Обработать открытие заметки."""
    title = _get_note_title_from_user(message)
    notes = note_manager.load_notes()
    if title and title in notes:
        bot.send_message(message.chat.id, f"\ud83d\udccf *{title}*\n\n{notes[title]}", parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, BotMessages.NOT_FOUND)

# --- РЕДАКТИРОВАНИЕ ЗАМЕТКИ (/edit) ---
@bot.message_handler(commands=["edit"])
def edit_note_start(message) -> None:
    """Начать процесс редактирования заметки."""
    msg = bot.send_message(message.chat.id, BotMessages.PROMPT_EDIT)
    bot.register_next_step_handler(msg, process_edit_title)


def process_edit_title(message) -> None:
    """Обработать название для редактирования."""
    title = _get_note_title_from_user(message)
    notes = note_manager.load_notes()
    if not title or title not in notes:
        bot.send_message(message.chat.id, BotMessages.NOT_FOUND)
        return

    current_text = BotMessages.CURRENT_TEXT.format(text=notes[title])
    msg = bot.send_message(message.chat.id, current_text, parse_mode="Markdown")
    bot.register_next_step_handler(msg, process_edit_text, title)


def process_edit_text(message, title: str) -> None:
    """Обработать новый текст для редактирования."""
    text = message.text
    try:
        note_manager.update_note(title, text)
        bot.send_message(message.chat.id, BotMessages.UPDATED.format(title=title))
    except Exception as e:
        bot.send_message(message.chat.id, BotMessages.ERROR.format(error=e))

# --- УДАЛЕНИЕ ЗАМЕТКИ (/delete) ---
@bot.message_handler(commands=["delete"])
def delete_note_start(message) -> None:
    """Начать процесс удаления заметки."""
    msg = bot.send_message(message.chat.id, BotMessages.PROMPT_DELETE)
    bot.register_next_step_handler(msg, process_delete_note)


def process_delete_note(message) -> None:
    """Обработать удаление заметки."""
    title = _get_note_title_from_user(message)
    if not title:
        bot.send_message(message.chat.id, BotMessages.EMPTY_TITLE)
        return

    try:
        note_manager.delete_note(title)
        bot.send_message(message.chat.id, BotMessages.DELETED.format(title=title))
    except KeyError:
        bot.send_message(message.chat.id, BotMessages.NOT_FOUND)
    except Exception as e:
        bot.send_message(message.chat.id, BotMessages.ERROR.format(error=e))


if __name__ == "__main__":
    print("🤖 Telegram-бот успешно запущен и ожидает сообщений...")
    bot.infinity_polling()