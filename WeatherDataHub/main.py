import os
from typing import Optional, Tuple
from datetime import datetime
from scraper import WeatherScraper
from split_csv import split_csv,split_by_year,split_by_week
from data_retrieval import (
    get_data_by_date_original,
    get_data_by_date_split,
    get_data_by_date_yearly,
    get_data_by_date_weekly,
    WeatherIterator
)
def get_csv_file(folder: str = 'dataset') -> Optional[str]:
    """Запрашивает у пользователя выбор CSV файла из указанной папки."""
    if not os.path.exists(folder):
        print(f"Папка {folder} не найдена.")
        return None

    files = [f for f in os.listdir(folder) if f.endswith('.csv')]

    if not files:
        print(f"В папке {folder} нет CSV файлов.")
        return None

    print("Доступные CSV файлы:")
    for i, file in enumerate(files, 1):
        print(f"{i}. {file}")

    while True:
        try:
            choice = int(input("Выберите номер файла для обработки: ")) - 1
            if 0 <= choice < len(files):
                return os.path.join(folder, files[choice])
            print("Неверный номер. Попробуйте еще раз.")
        except ValueError:
            print("Пожалуйста, введите число.")


def get_subfolder(base_folder: str) -> Optional[str]:
    """Запрашивает у пользователя выбор подпапки из указанной папки."""
    if not os.path.exists(base_folder):
        print(f"Папка {base_folder} не найдена.")
        return None

    subfolders = [f for f in os.listdir(base_folder)
                  if os.path.isdir(os.path.join(base_folder, f))]
    if not subfolders:
        print("Нет подпапок с файлами.")
        return None

    print("Доступные подпапки:")
    for i, folder in enumerate(subfolders, 1):
        print(f"{i}. {folder}")

    while True:
        try:
            choice = int(input("Выберите номер подпапки: ")) - 1
            if 0 <= choice < len(subfolders):
                return os.path.join(base_folder, subfolders[choice])
            print("Неверный номер. Попробуйте еще раз.")
        except ValueError:
            print("Пожалуйста, введите число.")


def main() -> None:
    """Основная функция программы."""
    while True:
        print("\nМеню:")
        print("1. Запустить сбор данных")
        print("2. Разделить файл на X.csv и Y.csv")
        print("3. Разделить файл по годам")
        print("4. Разделить файл по неделям")
        print("5. Получить данные по дате")
        print("6. Использовать итератор")
        print("7. Выход")

        choice: str = input("Выберите действие: ")

        if choice == '1':
            scraper: WeatherScraper = WeatherScraper()
            scraper.run()
        elif choice in ['2', '3', '4']:
            input_file: Optional[str] = get_csv_file()
            if input_file:
                if choice == '2':
                    split_csv(input_file)
                elif choice == '3':
                    split_by_year(input_file)
                else:
                    split_by_week(input_file)
        elif choice == '5':
            print("Выберите тип входных данных:")
            print("1. Оригинальный CSV")
            print("2. X.csv и Y.csv")
            print("3. Годовые файлы")
            print("4. Недельные файлы")

            data_type = input("Ваш выбор: ")

            if data_type == '1':
                file_path = get_csv_file()
            elif data_type == '2':
                split_folder = os.path.join('dataset', 'split_csv')
                subfolder = get_subfolder(split_folder)
                if subfolder:
                    x_file = os.path.join(subfolder, 'X.csv')
                    y_file = os.path.join(subfolder, 'Y.csv')
                    if os.path.exists(x_file) and os.path.exists(y_file):
                        file_path = (x_file, y_file)
                    else:
                        print("Файлы X.csv и Y.csv не найдены в выбранной подпапке.")
                        continue
                else:
                    continue
            elif data_type in ['3', '4']:
                folder = os.path.join('dataset', 'yearly_data' if data_type == '3' else 'weekly_data')
                subfolder = get_subfolder(folder)
                if not subfolder:
                    continue
                file_path = subfolder
            else:
                print("Неверный выбор типа данных")
                continue

            date_str = input("Введите дату в формате YYYY-MM-DD: ")
            try:
                date = datetime.strptime(date_str, "%Y-%m-%d").date()

                if data_type == '1':
                    data = get_data_by_date_original(date, file_path)
                elif data_type == '2':
                    data = get_data_by_date_split(date, file_path[0], file_path[1])
                elif data_type == '3':
                    data = get_data_by_date_yearly(date, file_path)
                elif data_type == '4':
                    data = get_data_by_date_weekly(date, file_path)

                if data:
                    print(f"Данные на {data['Дата']}:")
                    for key, value in data.items():
                        print(f"{key}: {value}")
                else:
                    print("Данные не найдены")
            except ValueError as e:
                print(f"Ошибка: {e}")
        elif choice == '6':
            input_file: Optional[str] = get_csv_file()
            if input_file:
                iterator = WeatherIterator(input_file)
                while True:
                    try:
                        date, data = next(iterator)
                        print(f"Дата: {date}")
                        for key, value in data.items():
                            if key != 'Дата':
                                print(f"{key}: {value}")
                        if input("Нажмите Enter для следующей записи или 'q' для выхода: ").lower() == 'q':
                            break
                    except StopIteration:
                        print("Достигнут конец данных")
                        break
        elif choice == '7':
            print("Выход из программы.")
            return
        else:
            print("Неверный выбор. Попробуйте еще раз.")


if __name__ == "__main__":
    main()