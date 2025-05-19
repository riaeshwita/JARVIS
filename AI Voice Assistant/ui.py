import sys
import threading
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLabel
)
from PyQt5.QtCore import Qt
from va import start_assistant_logic

class AssistantUI(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.assistant_thread = None
        self.stop_signal = threading.Event()

    def init_ui(self):
        self.setWindowTitle("AI Voice Assistant")
        self.setGeometry(100, 100, 600, 400)

        self.layout = QVBoxLayout()

        self.label = QLabel("Assistant Log:")
        self.layout.addWidget(self.label)

        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.layout.addWidget(self.log_area)

        self.start_button = QPushButton("Start Assistant")
        self.start_button.clicked.connect(self.start_assistant)
        self.layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Assistant")
        self.stop_button.clicked.connect(self.stop_assistant)
        self.layout.addWidget(self.stop_button)

        self.exit_button = QPushButton("Exit")
        self.exit_button.clicked.connect(self.close)
        self.layout.addWidget(self.exit_button)

        self.setLayout(self.layout)

    def log_message(self, message, is_assistant_response=True):
        if is_assistant_response:
            self.log_area.append(f"<b>Assistant:</b> {message}")
        else:
            self.log_area.append(f"<b>User:</b> {message}")

    def start_assistant(self):
        if self.assistant_thread is None or not self.assistant_thread.is_alive():
            self.stop_signal.clear()
            self.assistant_thread = threading.Thread(
                target=start_assistant_logic,
                args=(self.log_message, self.stop_signal),
                daemon=True
            )
            self.assistant_thread.start()
            self.log_message("Assistant started.")
        else:
            self.log_message("Assistant is already running.")

    def stop_assistant(self):
        if self.assistant_thread and self.assistant_thread.is_alive():
            self.stop_signal.set()
            self.assistant_thread.join(timeout=1)
            self.log_message("Assistant stopped.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    assistant_ui = AssistantUI()
    assistant_ui.show()
    sys.exit(app.exec_())
