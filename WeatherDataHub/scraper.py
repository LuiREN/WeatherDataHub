import requests
from bs4 import BeautifulSoup
import csv
import os
from datetime import datetime, timedelta

CLOUDINESS = {
    'sun.png': 'Ясно',
    'sunc.png': 'Малооблачно',
    'suncl.png': 'Переменная облачность',
    'dull.png': 'Пасмурно'
}

class WeatherScraper:
    def get_weather_data(self, year, month):
        url = f"https://www.gismeteo.ru/diary/4618/{year}/{month:02d}/"
        headers = {"User-Agent": "Mozilla/5.0"}
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Ошибка при запросе URL {url}: {e}")
            return []

        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find('table', attrs={"align": "center", "valign": "top", "border": "0"})

        if not table:
            print(f"Таблица с данными не найдена на странице {url}")
            return []

        data = []
        rows = table.find_all('tr')[2:]
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 11:
                date = f"{year}-{month:02d}-{cols[0].text.strip()}"
                temp_day = cols[1].text.strip()
                pressure_day = cols[2].text.strip()
                cloudiness_day = self.get_cloudiness(cols[3])
                wind_day = cols[5].text.strip().split('\n')[-1]
                temp_evening = cols[6].text.strip()
                pressure_evening = cols[7].text.strip()
                cloudiness_evening = self.get_cloudiness(cols[8])
                wind_evening = cols[10].text.strip().split('\n')[-1]
                data.append([
                    date, temp_day, pressure_day, cloudiness_day, wind_day,
                    temp_evening, pressure_evening, cloudiness_evening, wind_evening
                ])

        return data

    def get_cloudiness(self, cell):
        img = cell.find('img', class_='screen_icon')
        if img and 'src' in img.attrs:
            src = img['src'].split('/')[-1]
            return CLOUDINESS.get(src, 'Неизвестно')
        return 'Нет данных'

    def run(self, start_date, end_date, progress_callback, status_callback):
        start_date = datetime.strptime(start_date, "%m.%Y")
        end_date = datetime.strptime(end_date, "%m.%Y")
        
        all_data = []
        current_date = start_date
        total_months = (end_date.year - start_date.year) * 12 + end_date.month - start_date.month + 1
        processed_months = 0

        while current_date <= end_date:
            year = current_date.year
            month = current_date.month
            status_callback.emit(f"Получение данных за {month:02d}.{year}")
            month_data = self.get_weather_data(year, month)
            all_data.extend(month_data)
            current_date += timedelta(days=32)
            current_date = current_date.replace(day=1)
            
            processed_months += 1
            progress = int((processed_months / total_months) * 100)
            progress_callback.emit(progress)

        filename = f'samara_weather_{start_date.strftime("%Y%m")}-{end_date.strftime("%Y%m")}.csv'
        self.save_to_csv(all_data, filename)
        return filename

    def save_to_csv(self, data, filename):
        dataset_folder = 'dataset'
        if not os.path.exists(dataset_folder):
            os.makedirs(dataset_folder)
        
        filepath = os.path.join(dataset_folder, filename)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                'Дата', 'Температура (день)', 'Давление (день)', 'Облачность (день)', 'Ветер (день)',
                'Температура (вечер)', 'Давление (вечер)', 'Облачность (вечер)', 'Ветер (вечер)'
            ])
            writer.writerows(data)