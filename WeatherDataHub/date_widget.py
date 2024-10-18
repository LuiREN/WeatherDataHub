from PyQt6.QtWidgets import QHBoxLayout, QLineEdit, QPushButton, QVBoxLayout, QWidget

class DateDataWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        
        date_layout = QHBoxLayout()
        self.date_input = QLineEdit()
        self.date_input.setPlaceholderText("ГГГГ-ММ-ДД")
        self.get_data_button = QPushButton("Получить данные")
        date_layout.addWidget(self.date_input)
        date_layout.addWidget(self.get_data_button)
        
        self.layout.addLayout(date_layout)
        self.setLayout(self.layout)
