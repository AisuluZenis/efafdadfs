import sys
from typing import Dict
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QListWidget,
    QTextEdit,
    QPushButton,
    QInputDialog,
    QMessageBox,
)
import note_manager


class UIStrings:
    """Константы для текста пользовательского интерфейса."""

    WINDOW_TITLE = "Умные заметки"
    PLACEHOLDER_TEXT = "Выберите заметку или создайте новую..."
    BTN_CREATE = "Создать"
    BTN_SAVE = "Сохранить"
    BTN_DELETE = "Удалить"

    DIALOG_NEW_NOTE = "Новая заметка"
    DIALOG_NEW_NOTE_PROMPT = "Введите название заметки:"
    DIALOG_DELETE = "Удаление"
    DIALOG_ERROR = "Ошибка"
    DIALOG_SUCCESS = "Успех"

    MSG_EMPTY_LIST = "Список заметок пуст."
    MSG_SAVED = "успешно сохранена!"
    MSG_SELECT_SAVE = "Выберите заметку из списка для сохранения."
    MSG_SELECT_DELETE = "Выберите заметку для удаления."
    MSG_CONFIRM_DELETE = "Вы уверены, что хотите удалить заметку"


class NotesApp(QWidget):
    """Приложение для управления заметками с графическим интерфейсом."""
    def __init__(self) -> None:
        super().__init__()
        self.init_ui()
        self.load_notes_to_list()

    def init_ui(self) -> None:
        self.setWindowTitle(UIStrings.WINDOW_TITLE)
        self.resize(650, 450)

        main_layout = QHBoxLayout()
        main_layout.addWidget(self._create_list_widget(), 1)
        main_layout.addLayout(self._create_right_panel(), 2)

        self.setLayout(main_layout)

    def _create_list_widget(self) -> QListWidget:
        """Создать и настроить виджет списка заметок."""
        list_widget = QListWidget()
        list_widget.itemClicked.connect(self.load_note_text)
        self.list_widget = list_widget
        return list_widget

    def _create_right_panel(self) -> QVBoxLayout:
        """Создать правую панель с текстовым полем и кнопками."""
        right_layout = QVBoxLayout()

        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText(UIStrings.PLACEHOLDER_TEXT)
        right_layout.addWidget(self.text_edit)

        right_layout.addLayout(self._create_button_layout())
        return right_layout

    def _create_button_layout(self) -> QVBoxLayout:
        """Создать макет с кнопками управления."""
        button_layout = QVBoxLayout()

        buttons = [
            (UIStrings.BTN_CREATE, self.create_note),
            (UIStrings.BTN_SAVE, self.save_note),
            (UIStrings.BTN_DELETE, self.delete_note),
        ]

        for button_text, callback in buttons:
            btn = QPushButton(button_text)
            btn.clicked.connect(callback)
            button_layout.addWidget(btn)

        return button_layout

    def _find_and_select_note(self, title: str) -> None:
        """Найти и выбрать заметку в списке по названию."""
        for i in range(self.list_widget.count()):
            if self.list_widget.item(i).text() == title:
                self.list_widget.setCurrentRow(i)
                break

    def load_notes_to_list(self) -> None:
        """Обновить список заметок в интерфейсе."""
        self.list_widget.clear()
        notes: Dict[str, str] = note_manager.load_notes()
        self.list_widget.addItems(notes.keys())
        self.text_edit.clear()

    def load_note_text(self, item) -> None:
        """Загрузить текст выбранной заметки."""
        notes: Dict[str, str] = note_manager.load_notes()
        title = item.text()
        self.text_edit.setText(notes.get(title, ""))

    def create_note(self) -> None:
        """Создать новую заметку через диалоговое окно."""
        title, ok = QInputDialog.getText(
            self, UIStrings.DIALOG_NEW_NOTE, UIStrings.DIALOG_NEW_NOTE_PROMPT
        )
        if ok and title.strip():
            try:
                note_manager.add_note(title.strip(), "")
                self.load_notes_to_list()
                self._find_and_select_note(title.strip())
            except ValueError as e:
                QMessageBox.warning(self, UIStrings.DIALOG_ERROR, str(e))

    def save_note(self) -> None:
        """Сохранить изменения текущей заметки."""
        current_item = self.list_widget.currentItem()
        if not current_item:
            QMessageBox.warning(self, UIStrings.DIALOG_ERROR, UIStrings.MSG_SELECT_SAVE)
            return

        title = current_item.text()
        text = self.text_edit.toPlainText()
        try:
            note_manager.update_note(title, text)
            QMessageBox.information(
                self, UIStrings.DIALOG_SUCCESS, f"Заметка '{title}' {UIStrings.MSG_SAVED}"
            )
        except KeyError as e:
            QMessageBox.warning(self, UIStrings.DIALOG_ERROR, str(e))

    def delete_note(self) -> None:
        """Удалить выбранную заметку."""
        current_item = self.list_widget.currentItem()
        if not current_item:
            QMessageBox.warning(self, UIStrings.DIALOG_ERROR, UIStrings.MSG_SELECT_DELETE)
            return

        title = current_item.text()
        reply = QMessageBox.question(
            self,
            UIStrings.DIALOG_DELETE,
            f"{UIStrings.MSG_CONFIRM_DELETE} '{title}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            try:
                note_manager.delete_note(title)
                self.load_notes_to_list()
            except KeyError as e:
                QMessageBox.warning(self, UIStrings.DIALOG_ERROR, str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NotesApp()
    window.show()
    sys.exit(app.exec_())