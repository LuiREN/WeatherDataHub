import pandas as pd
import csv

def create_annotation_file(file_path, output_path):
    df = pd.read_csv(file_path)
    
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
        writer.writerow(["Параметр", "Значение"])
        writer.writerow(["Имя файла", file_path.split("/")[-1]])
        writer.writerow(["Количество строк", len(df)])
        writer.writerow(["Количество столбцов", len(df.columns)])
        writer.writerow(["Начальная дата", df['Дата'].min()])
        writer.writerow(["Конечная дата", df['Дата'].max()])
        writer.writerow(["Информация о столбцах", ""])
        
        for col in df.columns:
            writer.writerow([
                col,
                f"Тип: {df[col].dtype}, Уникальных значений: {df[col].nunique()}, Примеры: {', '.join(map(str, df[col].sample(min(5, df[col].nunique())).tolist()))}"
            ])

def read_annotation_file(file_path):
    return pd.read_csv(file_path, encoding='utf-8')