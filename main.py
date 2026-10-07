from collections import defaultdict
from dataclasses import dataclass
import json
import os
import urllib.parse
import urllib.request


# Модель данных WeatherData
@dataclass
class WeatherData:
  city: str
  temp_c: int
  country: str


def get_weather_data(city_query: str) -> WeatherData:
  """Запрашивает данные о погоде через wttr.in API без сторонних библиотек."""
  # Кодируем название города для использования в URL (например, для пробелов)
  encoded_city = urllib.parse.quote(city_query.strip())
  url = f"https://wttr.in/{encoded_city}?format=j1"

  # Указываем User-Agent, чтобы избежать блокировок по умолчанию
  req = urllib.request.Request(
      url, headers={"User-Agent": "Python-Weather-Script/1.0"}
  )

  with urllib.request.urlopen(req) as response:
    raw_json = response.read().decode("utf-8")
    data = json.loads(raw_json)

    # Извлечение текущей температуры в градусах Цельсия
    current_temp = int(data["current_condition"][0]["temp_C"])

    # Извлечение страны
    try:
      country = data["nearest_area"][0]["country"][0]["value"]
    except (KeyError, IndexError):
      country = "Unknown"

    # Извлечение каноничного названия города из ответа API (или используем исходное)
    try:
      city_name = data["nearest_area"][0]["areaName"][0]["value"]
    except (KeyError, IndexError):
      city_name = city_query.strip()

    return WeatherData(
        city=city_name, temp_c=current_temp, country=country
    )


def format_temp(temp: float) -> str:
  """Форматирует температуру с знаком '+' для положительных значений."""
  rounded_temp = round(temp)
  return f"+{rounded_temp} °C" if rounded_temp > 0 else f"{rounded_temp} °C"


def main():
  file_path = "cities.txt"

  if not os.path.exists(file_path):
    print(
        f"Ошибка: Файл '{file_path}' не найден! Создайте файл со списком"
        " городов."
    )
    return

  # Загрузка списка городов из файла в память и фильтрация дубликатов
  with open(file_path, "r", encoding="utf-8") as f:
    raw_cities = [line.strip() for line in f if line.strip()]
    # Сохраняем уникальные города с сохранением порядка появления
    unique_cities = list(dict.fromkeys(raw_cities))

  print(f"Загружено уникальных городов: {len(unique_cities)}\n")

  weather_results: list[WeatherData] = []

  # Получение данных и вывод информации по каждому городу
  print("=== Погода по городам ===")
  for city in unique_cities:
    try:
      weather = get_weather_data(city)
      weather_results.append(weather)
      print(f"{weather.city}, {weather.country} {format_temp(weather.temp_c)}")
    except Exception as e:
      print(f"Не удалось получить данные для города '{city}': {e}")

  # Группировка по странам и вычисление агрегированных показателей
  print("\n=== Статистика по странам ===")
  country_groups = defaultdict(list)

  for weather in weather_results:
    country_groups[weather.country].append(weather.temp_c)

  for country, temps in country_groups.items():
    count = len(temps)
    avg_temp = sum(temps) / count
    min_temp = min(temps)
    max_temp = max(temps)

    city_word = "city" if count == 1 else "cities"

    print(
        f"{country} — {count} {city_word}, "
        f"avg: {format_temp(avg_temp)}, "
        f"min: {format_temp(min_temp)}, "
        f"max: {format_temp(max_temp)}"
    )


if __name__ == "__main__":
  main()