import re
import json
import os  # для работы с путями


# Функция для чтения файла чека
def read_receipt(file_name):
    # Получаем папку, где лежит скрипт
    current_directory = os.path.dirname(__file__)
    # Формируем полный путь к файлу raw.txt
    file_path = os.path.join(current_directory, file_name)

    # Открываем файл в режиме чтения
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()
    return content


# Функция для извлечения всех цен
def extract_prices(text):
    price_pattern = r"\d+\.\d{2}"  # ищем числа с 2 знаками после точки
    prices = re.findall(price_pattern, text)
    prices = [float(p) for p in prices]  # преобразуем в числа
    return prices


# Функция для извлечения названий товаров
def extract_products(text):
    product_pattern = r"([A-Za-z ]+)\s+\d+\.\d{2}"  # название перед ценой
    products = re.findall(product_pattern, text)
    products = [p.strip() for p in products]  # убираем лишние пробелы
    return products


# Функция для извлечения даты
def extract_date(text):
    date_pattern = r"\d{4}-\d{2}-\d{2}"
    match = re.search(date_pattern, text)
    return match.group() if match else None


# Функция для извлечения времени
def extract_time(text):
    time_pattern = r"\d{2}:\d{2}"
    match = re.search(time_pattern, text)
    return match.group() if match else None


# Функция для извлечения способа оплаты
def extract_payment_method(text):
    payment_pattern = r"Payment method:\s*(\w+)"
    match = re.search(payment_pattern, text)
    return match.group(1) if match else None


# Функция для подсчёта общей суммы
def calculate_total(prices):
    return sum(prices)


def main():
    # Читаем текст чека из файла raw.txt
    receipt_text = read_receipt("raw.txt")

    # Извлекаем данные
    prices = extract_prices(receipt_text)
    products = extract_products(receipt_text)
    date = extract_date(receipt_text)
    time = extract_time(receipt_text)
    payment_method = extract_payment_method(receipt_text)
    total = calculate_total(prices)

    # Формируем структурированный словарь
    receipt_data = {
        "date": date,
        "time": time,
        "products": products,
        "prices": prices,
        "total": total,
        "payment_method": payment_method
    }

    # Красивый вывод в формате JSON
    print(json.dumps(receipt_data, indent=4))


# Запуск программы только если файл запускается напрямую
if __name__ == "__main__":
    main()