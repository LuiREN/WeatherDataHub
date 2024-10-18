import pandas as pd
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem
from PyQt6.QtCore import Qt

class OptimizedTableWidget(QTableWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.chunk_size = 100
        self.current_chunk = 0
        self.total_rows = 0
        self.df = None

    def load_data(self, df):
        self.df = df
        self.total_rows = len(df)
        self.setRowCount(self.total_rows)
        self.setColumnCount(len(df.columns))
        self.setHorizontalHeaderLabels(df.columns)
        self.current_chunk = 0
        self.load_chunk()

    def load_chunk(self):
        start = self.current_chunk * self.chunk_size
        end = min(start + self.chunk_size, self.total_rows)
        
        for row in range(start, end):
            for col in range(len(self.df.columns)):
                item = QTableWidgetItem(str(self.df.iloc[row, col]))
                self.setItem(row, col, item)
        
        self.current_chunk += 1

    def clear(self):
        self.setRowCount(0)
        self.setColumnCount(0)
        self.df = None
        self.total_rows = 0
        self.current_chunk = 0

    def scrollContentsBy(self, dx, dy):
        super().scrollContentsBy(dx, dy)
        if self.verticalScrollBar().value() == self.verticalScrollBar().maximum():
            if self.current_chunk * self.chunk_size < self.total_rows:
                self.load_chunk()