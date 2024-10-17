import pandas as pd
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QDialog, QVBoxLayout

def show_data_preview(file_path):
    df = pd.read_csv(file_path)
    
    dialog = QDialog()
    dialog.setWindowTitle("Предварительный просмотр данных")
    dialog.setGeometry(100, 100, 800, 600)
    
    layout = QVBoxLayout()
    table = QTableWidget()
    layout.addWidget(table)
    
    table.setColumnCount(len(df.columns))
    table.setRowCount(len(df))
    
    table.setHorizontalHeaderLabels(df.columns)
    
    for i in range(len(df)):
        for j in range(len(df.columns)):
            table.setItem(i, j, QTableWidgetItem(str(df.iloc[i, j])))
    
    dialog.setLayout(layout)
    dialog.exec()
