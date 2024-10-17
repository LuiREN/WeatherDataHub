import sys
import os
import pandas as pd
from datetime import datetime
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QFileDialog, QTableWidget, QTableWidgetItem, QLabel, QFrame, QLineEdit, QProgressBar, QMessageBox
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
from data_preprocessing import preprocess_data
from data_viewer import show_data_preview
from dataset_creator import show_dataset_creator_dialog
from scraper import WeatherScraper
from split_by_week import split_by_week
from split_by_year import split_by_year
from split_csv import split_csv

class ScraperThread(QThread):
    update_progress = pyqtSignal(int)
    update_status = pyqtSignal(str)
    scraping_finished = pyqtSignal(str)

    def __init__(self, start_date, end_date):
        QThread.__init__(self)
        self.start_date = start_date
        self.end_date = end_date

    def run(self):
        scraper = WeatherScraper()
        filename = scraper.run(self.start_date, self.end_date, self.update_progress, self.update_status)
        self.scraping_finished.emit(filename)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WeatherDataHub")
        self.setGeometry(100, 100, 1000, 600)

        central_widget = QWidget()
        main_layout = QHBoxLayout()
        
        # Левая панель с кнопками
        left_panel = QVBoxLayout()
        left_panel.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.select_file_button = self.create_button("Выбрать файл", self.select_file)
        left_panel.addWidget(self.select_file_button)
        
        self.preprocess_button = self.create_button("Предобработка данных", self.preprocess_data)
        left_panel.addWidget(self.preprocess_button)
        
        self.preview_button = self.create_button("Предварительный просмотр", self.show_preview)
        left_panel.addWidget(self.preview_button)
        
        self.create_dataset_button = self.create_button("Создать новый датасет", self.show_dataset_creator)
        left_panel.addWidget(self.create_dataset_button)
        
        self.scrape_data_button = self.create_button("Собрать данные с сайта", self.show_scraper_dialog)
        left_panel.addWidget(self.scrape_data_button)
        
        self.split_by_week_button = self.create_button("Разделить по неделям", self.split_by_week)
        left_panel.addWidget(self.split_by_week_button)
        
        self.split_by_year_button = self.create_button("Разделить по годам", self.split_by_year)
        left_panel.addWidget(self.split_by_year_button)
        
        self.split_csv_button = self.create_button("Разделить на X и Y", self.split_csv)
        left_panel.addWidget(self.split_csv_button)

        # Правая панель для отображения информации
        right_panel = QVBoxLayout()
        self.info_label = QLabel("Выберите файл для начала работы")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setFont(QFont("Arial", 12))
        right_panel.addWidget(self.info_label)
        
        self.data_preview = QTableWidget()
        right_panel.addWidget(self.data_preview)

        # Добавляем панели в главный layout
        left_panel_widget = QWidget()
        left_panel_widget.setLayout(left_panel)
        left_panel_widget.setFixedWidth(200)
        
        right_panel_widget = QWidget()
        right_panel_widget.setLayout(right_panel)
        
        main_layout.addWidget(left_panel_widget)
        main_layout.addWidget(right_panel_widget)

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.current_file = None
        self.preprocessed_data = None

        # Загрузка стилей
        self.load_styles()

    def create_button(self, text, callback):
        button = QPushButton(text)
        button.clicked.connect(callback)
        return button

    def load_styles(self):
        with open('styles.qss', 'r') as f:
            self.setStyleSheet(f.read())

    def select_file(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Выберите файл CSV", "", "CSV Files (*.csv)")
        if file_path:
            self.current_file = file_path
            self.info_label.setText(f"Выбран файл: {self.current_file}")
            self.show_preview()

    def preprocess_data(self):
        if self.current_file:
            self.preprocessed_data = preprocess_data(self.current_file)
            self.info_label.setText("Данные предобработаны")
            self.show_data_in_table(self.preprocessed_data)
            # Сохранение предобработанных данных
            save_path, _ = QFileDialog.getSaveFileName(self, "Сохранить предобработанные данные", "", "CSV Files (*.csv)")
            if save_path:
                self.preprocessed_data.to_csv(save_path, index=False)
                self.info_label.setText(f"Предобработанные данные сохранены в {save_path}")
        else:
            self.info_label.setText("Сначала выберите файл")

    def show_preview(self):
        if self.current_file:
            df = pd.read_csv(self.current_file)
            self.show_data_in_table(df)
        else:
            self.info_label.setText("Сначала выберите файл")

    def show_data_in_table(self, df):
        self.data_preview.setColumnCount(len(df.columns))
        self.data_preview.setRowCount(len(df))
        self.data_preview.setHorizontalHeaderLabels(df.columns)
        for i in range(len(df)):
            for j in range(len(df.columns)):
                self.data_preview.setItem(i, j, QTableWidgetItem(str(df.iloc[i, j])))
        self.data_preview.resizeColumnsToContents()

    def show_dataset_creator(self):
        show_dataset_creator_dialog(self)

    def show_scraper_dialog(self):
        dialog = QWidget()
        dialog.setWindowTitle("Сбор данных с сайта")
        dialog.setGeometry(200, 200, 400, 200)
        
        layout = QVBoxLayout()
        
        start_date_label = QLabel("Начальная дата (ММ.ГГГГ):")
        self.start_date_input = QLineEdit()
        layout.addWidget(start_date_label)
        layout.addWidget(self.start_date_input)
        
        end_date_label = QLabel("Конечная дата (ММ.ГГГГ):")
        self.end_date_input = QLineEdit()
        layout.addWidget(end_date_label)
        layout.addWidget(self.end_date_input)
        
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Готов к сбору данных")
        layout.addWidget(self.status_label)
        
        start_button = QPushButton("Начать сбор данных")
        start_button.clicked.connect(self.start_scraping)
        layout.addWidget(start_button)
        
        dialog.setLayout(layout)
        dialog.show()
        
        self.scraper_dialog = dialog

    def start_scraping(self):
        start_date = self.start_date_input.text()
        end_date = self.end_date_input.text()
        
        try:
            start_datetime = datetime.strptime(start_date, "%m.%Y")
            end_datetime = datetime.strptime(end_date, "%m.%Y")
            
            if start_datetime > end_datetime:
                raise ValueError("Начальная дата не может быть позже конечной даты.")
            
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", f"Неверный формат даты или диапазон дат: {str(e)}\nИспользуйте формат ММ.ГГГГ")
            return
        
        self.scraper_thread = ScraperThread(start_date, end_date)
        self.scraper_thread.update_progress.connect(self.update_progress_bar)
        self.scraper_thread.update_status.connect(self.update_status_label)
        self.scraper_thread.scraping_finished.connect(self.scraping_finished)
        self.scraper_thread.start()
        
        self.status_label.setText("Начинается сбор данных...")
        self.progress_bar.setValue(0)

    def update_progress_bar(self, value):
        self.progress_bar.setValue(value)

    def update_status_label(self, status):
        self.status_label.setText(status)

    def scraping_finished(self, filename):
        if filename:
            QMessageBox.information(self, "Сбор данных завершен", f"Данные сохранены в файл: {filename}")
            self.scraper_dialog.close()
            self.current_file = os.path.join('dataset', filename)
            self.show_preview()
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось собрать данные. Проверьте подключение к интернету и попробуйте снова.")

    def split_by_week(self):
        if self.current_file:
            split_by_week(self.current_file)
            self.info_label.setText("Данные разделены по неделям")
        else:
            self.info_label.setText("Сначала выберите файл")

    def split_by_year(self):
        if self.current_file:
            split_by_year(self.current_file)
            self.info_label.setText("Данные разделены по годам")
        else:
            self.info_label.setText("Сначала выберите файл")

    def split_csv(self):
        if self.current_file:
            split_csv(self.current_file)
            self.info_label.setText("Данные разделены на X и Y")
        else:
            self.info_label.setText("Сначала выберите файл")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())