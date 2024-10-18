import pandas as pd
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem
from PyQt6.QtCore import Qt

class OptimizedTableWidget(QTableWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.chunk_size = 1000
        self.current_chunk = 0
        self.total_rows = 0
        self.df = None

    def load_data(self, file_path_or_df):
        if isinstance(file_path_or_df, str):
            self.df = pd.read_csv(file_path_or_df)
        else:
            self.df = file_path_or_df
        self.total_rows = len(self.df)
        self.setRowCount(self.total_rows)
        self.setColumnCount(len(self.df.columns))
        self.setHorizontalHeaderLabels(self.df.columns)
        self.load_chunk()

    def load_chunk(self):
        start = self.current_chunk * self.chunk_size
        end = min(start + self.chunk_size, self.total_rows)
        chunk = self.df.iloc[start:end]
        
        for row in range(start, end):
            for col in range(len(self.df.columns)):
                item = QTableWidgetItem(str(chunk.iloc[row - start, col]))
                self.setItem(row, col, item)
        
        self.current_chunk += 1

    def scrollContentsBy(self, dx, dy):
        super().scrollContentsBy(dx, dy)
        if self.verticalScrollBar().value() == self.verticalScrollBar().maximum():
            if self.current_chunk * self.chunk_size < self.total_rows:
                self.load_chunk()
