import sys
import os
from typing import Union, Optional
from datetime import datetime
import pandas as pd
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout,
    QWidget, QFileDialog, QLabel, QFrame, QProgressBar, QMessageBox,
    QTableWidgetItem, QLineEdit
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
from data_preprocessing import preprocess_data
from scraper import WeatherScraper
from split_csv import split_csv, split_by_year, split_by_week
from optimized_table import OptimizedTableWidget
from annotation import create_annotation_file, read_annotation_file
from date_widget import DateDataWidget


class ScraperThread(QThread):
    update_progress = pyqtSignal(int)
    update_status = pyqtSignal(str)
    scraping_finished = pyqtSignal(str)

    def __init__(self, start_date: str, end_date: str):
        super().__init__()
        self.start_date = start_date
        self.end_date = end_date

    def run(self) -> None:
        """Запускает поток скрапера."""
        scraper = WeatherScraper()
        filename = scraper.run(self.start_date, self.end_date, self.update_progress, self.update_status)
        self.scraping_finished.emit(filename)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.current_file: Optional[str] = None
        self.preprocessed_data: Optional[pd.DataFrame] = None
        self.load_styles()

    def init_ui(self) -> None:
        """Инициализирует пользовательский интерфейс."""
        self.setWindowTitle("WeatherDataHub")
        self.setGeometry(100, 100, 1200, 800)

        central_widget = QWidget()
        main_layout = QHBoxLayout()

        left_panel = self.create_left_panel()
        right_panel = self.create_right_panel()

        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel)

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def create_left_panel(self) -> QWidget:
        """Создает левую панель с кнопками."""
        left_panel = QVBoxLayout()
        left_panel.setAlignment(Qt.AlignmentFlag.AlignTop)

        button_width = 220
        buttons = [
            ("Выбрать файл", self.select_file),
            ("Предобработка данных", self.preprocess_data),
            ("Создать новый датасет", self.show_scraper_dialog),
            ("Разделить по неделям", self.split_by_week),
            ("Разделить по годам", self.split_by_year),
            ("Разделить на X и Y", self.split_csv),
            ("Создать аннотацию", self.create_annotation)
        ]

        for text, callback in buttons:
            button = self.create_button(text, callback, button_width)
            left_panel.addWidget(button)

        left_panel_widget = QWidget()
        left_panel_widget.setLayout(left_panel)
        left_panel_widget.setFixedWidth(240)

        return left_panel_widget

    def create_right_panel(self) -> QWidget:
        """Создает правую панель для отображения информации."""
        right_panel = QVBoxLayout()

        self.info_label = QLabel("Выберите файл для начала работы")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setFont(QFont("Arial", 12))
        right_panel.addWidget(self.info_label)

        self.data_preview = OptimizedTableWidget()
        right_panel.addWidget(self.data_preview)

        self.date_input = QLineEdit()
        self.date_input.setPlaceholderText("ГГГГ-ММ-ДД")
        right_panel.addWidget(self.date_input)

        self.get_data_button = QPushButton("Получить данные")
        self.get_data_button.clicked.connect(self.get_data_for_date)
        right_panel.addWidget(self.get_data_button)

        right_panel_widget = QWidget()
        right_panel_widget.setLayout(right_panel)

        return right_panel_widget

    def create_button(self, text: str, callback, width: int) -> QPushButton:
        """Создает кнопку с заданными параметрами."""
        button = QPushButton(text)
        button.clicked.connect(callback)
        button.setFixedWidth(width)
        return button

    def load_styles(self) -> None:
        """Загружает стили из файла QSS."""
        with open('styles.qss', 'r') as f:
            self.setStyleSheet(f.read())

    def select_file(self) -> None:
        """Открывает диалоговое окно для выбора CSV файла."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите файл CSV", "", "CSV Files (*.csv)")
        if file_path:
            self.current_file = file_path
            self.info_label.setText(f"Выбран файл: {self.current_file}")
            self.load_data(self.current_file)

    def preprocess_data(self) -> None:
        """Предобрабатывает выбранный файл данных."""
        if self.current_file:
            self.preprocessed_data = preprocess_data(self.current_file)
            self.info_label.setText("Данные предобработаны")
            self.load_data(self.preprocessed_data)
            self.save_preprocessed_data()
        else:
            self.info_label.setText("Сначала выберите файл")

    def save_preprocessed_data(self) -> None:
        """Сохраняет предобработанные данные в CSV файл."""
        save_path, _ = QFileDialog.getSaveFileName(self, "Сохранить предобработанные данные", "", "CSV Files (*.csv)")
        if save_path and self.preprocessed_data is not None:
            self.preprocessed_data.to_csv(save_path, index=False)
            self.info_label.setText(f"Предобработанные данные сохранены в {save_path}")

    def load_data(self, data: Union[str, pd.DataFrame]) -> None:
        """Загружает данные в таблицу предварительного просмотра."""
        if isinstance(data, str):
            try:
                df = pd.read_csv(data)
            except Exception as e:
                self.info_label.setText(f"Ошибка при чтении файла: {str(e)}")
                return
        elif isinstance(data, pd.DataFrame):
            df = data
        else:
            self.info_label.setText("Неподдерживаемый тип данных")
            return

        self.data_preview.load_data(df)

    def create_annotation(self) -> None:
        """Создает файл аннотации для текущего набора данных."""
        if self.current_file:
            output_path = self.current_file.rsplit('.', 1)[0] + '_annotation.csv'
            create_annotation_file(self.current_file, output_path)
            self.info_label.setText(f"Файл аннотации создан: {output_path}")
            self.show_annotation(output_path)
        else:
            self.info_label.setText("Сначала выберите файл")

    def show_annotation(self, annotation_file: str) -> None:
        """Отображает содержимое файла аннотации."""
        try:
            annotation_data = read_annotation_file(annotation_file)
            self.load_data(annotation_data)
            self.info_label.setText("Просмотр аннотации")
        except Exception as e:
            self.info_label.setText(f"Ошибка при чтении файла аннотации: {str(e)}")

    def get_data_for_date(self) -> None:
        """Извлекает и отображает данные для конкретной даты."""
        if not self.current_file:
            self.info_label.setText("Сначала выберите файл")
            return

        date_str = self.date_input.text()
        try:
            input_date = pd.to_datetime(date_str).normalize()
            df = pd.read_csv(self.current_file, parse_dates=['Дата'])
            df['Дата'] = pd.to_datetime(df['Дата']).dt.normalize()

            if input_date < df['Дата'].min() or input_date > df['Дата'].max():
                self.info_label.setText(f"Дата {date_str} находится вне диапазона данных ({df['Дата'].min().date()} - {df['Дата'].max().date()})")
                self.data_preview.clear()
                return

            data = df[df['Дата'] == input_date]

            if not data.empty:
                self.load_data(data)
                self.info_label.setText(f"Данные на {date_str}")
            else:
                self.info_label.setText(f"Нет данных на {date_str}")
                self.data_preview.clear()

        except ValueError as e:
            self.info_label.setText(f"Ошибка в формате даты: {str(e)}. Используйте формат ГГГГ-ММ-ДД")
        except Exception as e:
            self.info_label.setText(f"Ошибка при получении данных: {str(e)}")

    def show_scraper_dialog(self) -> None:
        """Показывает диалоговое окно для сбора данных."""
        self.scraper_dialog = QWidget()
        self.scraper_dialog.setWindowTitle("Сбор данных с сайта")
        self.scraper_dialog.setGeometry(200, 200, 400, 200)

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

        self.scraper_dialog.setLayout(layout)
        self.scraper_dialog.show()

    def start_scraping(self) -> None:
        """Запускает процесс сбора данных."""
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

    def update_progress_bar(self, value: int) -> None:
        """Обновляет значение индикатора выполнения."""
        self.progress_bar.setValue(value)

    def update_status_label(self, status: str) -> None:
        """Обновляет текст метки статуса."""
        self.status_label.setText(status)

    def scraping_finished(self, filename: str) -> None:
        """Обрабатывает завершение процесса сбора данных."""
        if filename:
            full_path = os.path.join(os.getcwd(), 'dataset', filename)
            QMessageBox.information(self, "Сбор данных завершен", f"Данные сохранены в файл:\n{full_path}")
            self.scraper_dialog.close()
            self.current_file = full_path
            self.load_data(self.current_file)  
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось собрать данные. Проверьте подключение к интернету и попробуйте снова.")

    def split_by_week(self) -> None:
        """Разделяет данные текущего файла по неделям."""
        if self.current_file:
            output_folder = split_by_week(self.current_file)
            self.info_label.setText(f"Данные разделены по неделям. Результаты сохранены в {output_folder}")
        else:
            self.info_label.setText("Сначала выберите файл")

    def split_by_year(self) -> None:
        """Разделяет данные текущего файла по годам."""
        if self.current_file:
            output_folder = split_by_year(self.current_file)
            self.info_label.setText(f"Данные разделены по годам. Результаты сохранены в {output_folder}")
        else:
            self.info_label.setText("Сначала выберите файл")

    def split_csv(self) -> None:
        """Разделяет текущий файл на части X и Y."""
        if self.current_file:
            output_folder = split_csv(self.current_file)
            self.info_label.setText(f"Данные разделены на X и Y. Результаты сохранены в {output_folder}")
        else:
            self.info_label.setText("Сначала выберите файл")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())