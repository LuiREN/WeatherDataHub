import pandas as pd
from datetime import date
import os
from typing import Dict, Optional, Tuple

def format_date(d: date) -> str:
    """Преобразует дату в строку формата YYYY-MM-DD."""
    return d.strftime("%Y-%m-%d")

def get_data_by_date_original(date: date, file_path: str) -> Optional[Dict[str, str]]:
    """Возвращает данные для указанной даты из оригинального CSV файла."""
    df: pd.DataFrame = pd.read_csv(file_path, parse_dates=['Дата'])
    df['Дата'] = df['Дата'].dt.date
    row: pd.DataFrame = df[df['Дата'] == date]
    if row.empty:
        return None
    data = row.iloc[0].to_dict()
    data['Дата'] = format_date(data['Дата'])
    return data

def get_data_by_date_split(date: date, x_file: str, y_file: str) -> Optional[Dict[str, str]]:
    """Возвращает данные для указанной даты из разделенных X.csv и Y.csv файлов."""
    x_df: pd.DataFrame = pd.read_csv(x_file, parse_dates=['Date'])
    x_df['Date'] = x_df['Date'].dt.date
    y_df: pd.DataFrame = pd.read_csv(y_file)

    row_index = x_df.index[x_df['Date'] == date]
    if row_index.empty:
        return None

    y_row = y_df.iloc[row_index[0]]
    return {'Дата': format_date(date), **y_row.to_dict()}

def get_data_by_date_yearly(date: date, folder: str) -> Optional[Dict[str, str]]:
    """Возвращает данные для указанной даты из годовых файлов."""
    year_file = os.path.join(folder, f"{date.year}0101_{date.year}1231.csv")
    if not os.path.exists(year_file):
        print(f"Файл для {date.year} года не найден.")
        return None

    df: pd.DataFrame = pd.read_csv(year_file, parse_dates=['Дата'])
    df['Дата'] = df['Дата'].dt.date
    row: pd.DataFrame = df[df['Дата'] == date]
    if row.empty:
        return None
    data = row.iloc[0].to_dict()
    data['Дата'] = format_date(data['Дата'])
    return data

def get_data_by_date_weekly(date: date, folder: str) -> Optional[Dict[str, str]]:
    """Возвращает данные для указанной даты из недельных файлов."""
    files = [f for f in os.listdir(folder) if f.endswith('.csv')]
    for file in files:
        start_date, end_date = file.split('_')
        start_date = pd.to_datetime(start_date).date()
        end_date = pd.to_datetime(end_date.split('.')[0]).date()
        if start_date <= date <= end_date:
            file_path = os.path.join(folder, file)
            df: pd.DataFrame = pd.read_csv(file_path, parse_dates=['Дата'])
            df['Дата'] = df['Дата'].dt.date
            row: pd.DataFrame = df[df['Дата'] == date]
            if not row.empty:
                data = row.iloc[0].to_dict()
                data['Дата'] = format_date(data['Дата'])
                return data

    print(f"Данные для даты {format_date(date)} не найдены.")
    return None


class WeatherIterator:
    """Итератор для перебора данных о погоде."""

    def __init__(self, input_file: str):
        self.df: pd.DataFrame = pd.read_csv(input_file, parse_dates=['Дата'])
        self.df['Дата'] = self.df['Дата'].dt.date
        self.df = self.df.sort_values('Дата')
        self.index: int = 0

    def __iter__(self) -> 'WeatherIterator':
        return self

    def __next__(self) -> Tuple[str, Dict[str, str]]:
        if self.index >= len(self.df):
            raise StopIteration
        row: pd.Series = self.df.iloc[self.index]
        self.index += 1
        data = row.to_dict()
        data['Дата'] = format_date(data['Дата'])
        return data['Дата'], data