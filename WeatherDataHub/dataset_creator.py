from PyQt6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QComboBox

class DatasetCreatorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Создание нового датасета")
        self.setGeometry(150, 150, 300, 200)

        layout = QVBoxLayout()

        self.dataset_type = QComboBox()
        self.dataset_type.addItems(["Собрать данные с сайта", "Разделить по неделям", "Разделить по годам", "Другое"])
        layout.addWidget(self.dataset_type)

        self.create_button = QPushButton("Создать")
        self.create_button.clicked.connect(self.create_dataset)
        layout.addWidget(self.create_button)

        self.setLayout(layout)

    def create_dataset(self):
        selected_type = self.dataset_type.currentText()
        print(f"Создание датасета типа: {selected_type}")
        # Здесь будет логика создания датасета
        self.accept()

def show_dataset_creator_dialog(parent):
    dialog = DatasetCreatorDialog(parent)
    dialog.exec()
