import pandas as pd
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem
from PyQt6.QtCore import Qt
from typing import Any, Optional


class OptimizedTableWidget(QTableWidget):
    """
    Оптимизированный виджет таблицы для отображения больших объемов данных.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Инициализирует OptimizedTableWidget.

        Args:
            *args: Позиционные аргументы для QTableWidget.
            **kwargs: Именованные аргументы для QTableWidget.
        """
        super().__init__(*args, **kwargs)
        self.chunk_size: int = 100
        self.current_chunk: int = 0
        self.total_rows: int = 0
        self.df: Optional[pd.DataFrame] = None

    def load_data(self, df: pd.DataFrame) -> None:
        """
        Загружает данные в таблицу.

        Args:
            df (pd.DataFrame): DataFrame для отображения.
        """
        self.df = df
        self.total_rows = len(df)
        self.setRowCount(self.total_rows)
        self.setColumnCount(len(df.columns))
        self.setHorizontalHeaderLabels(df.columns)
        self.current_chunk = 0
        self.load_chunk()

    def load_chunk(self) -> None:
        """
        Загружает следующий фрагмент данных в таблицу.
        """
        if self.df is None:
            return

        start: int = self.current_chunk * self.chunk_size
        end: int = min(start + self.chunk_size, self.total_rows)
        
        for row in range(start, end):
            for col in range(len(self.df.columns)):
                item = QTableWidgetItem(str(self.df.iloc[row, col]))
                self.setItem(row, col, item)
        
        self.current_chunk += 1

    def clear(self) -> None:
        """
        Очищает таблицу и сбрасывает все связанные переменные.
        """
        self.setRowCount(0)
        self.setColumnCount(0)
        self.df = None
        self.total_rows = 0
        self.current_chunk = 0

    def scrollContentsBy(self, dx: int, dy: int) -> None:
        """
        Обрабатывает событие прокрутки и загружает новые данные при необходимости.

        Args:
            dx (int): Изменение по горизонтали.
            dy (int): Изменение по вертикали.
        """
        super().scrollContentsBy(dx, dy)
        if self.verticalScrollBar().value() == self.verticalScrollBar().maximum():
            if self.current_chunk * self.chunk_size < self.total_rows:
                self.load_chunk()


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    table = OptimizedTableWidget()
    
    # Пример использования
    df = pd.DataFrame({'A': range(1000), 'B': range(1000, 2000)})
    table.load_data(df)
    table.show()
    
    sys.exit(app.exec())