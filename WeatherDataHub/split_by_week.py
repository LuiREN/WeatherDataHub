import pandas as pd
import os
from typing import Optional

def split_by_week(input_file: str) -> None:
    """
    Разделяет исходный CSV файл на отдельные файлы по неделям.
    
    Args:
        input_file (str): Путь к исходному CSV файлу.
    """
    if not os.path.exists(input_file):
        print(f"Файл {input_file} не найден.")
        return

    df: pd.DataFrame = pd.read_csv(input_file, parse_dates=['Дата'])
    df['Week'] = df['Дата'].dt.to_period('W')
    grouped: pd.DataFrameGroupBy = df.groupby('Week')

    file_name: str = os.path.splitext(os.path.basename(input_file))[0]
    output_folder: str = os.path.join('dataset', 'weekly_data', file_name)
    os.makedirs(output_folder, exist_ok=True)

    for week, group in grouped:
        start_date: str = group['Дата'].min().strftime('%Y%m%d')
        end_date: str = group['Дата'].max().strftime('%Y%m%d')
        filename: str = f'{start_date}_{end_date}.csv'
        filepath: str = os.path.join(output_folder, filename)
        group.drop('Week', axis=1).to_csv(filepath, index=False)
        print(f"Создан файл: {filename}")

    print(f"Файлы по неделям созданы в папке {output_folder}.")

if __name__ == "__main__":
    input_file: str = input("Введите путь к исходному CSV файлу: ")
    split_by_week(input_file)