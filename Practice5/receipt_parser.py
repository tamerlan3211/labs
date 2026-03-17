import re
import json
import os

# Функция для чтения файла чека
def read_receipt(file_name):
    current_directory = os.path.dirname(__file__)
    file_path = os.path.join(current_directory, file_name)
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()

# Функция для извлечения всех цен
def extract_prices(text):
    # Ищем числа с запятой, пробелами в тысячах
    price_pattern = r"(\d[\d\s]*,\d{2})" 
    prices = re.findall(price_pattern, text)
    cleaned_prices = []
    for p in prices:
        # Убираем все пробелы и переносы строк, заменяем запятую на точку
        number = p.replace(" ", "").replace("\n", "").replace(",", ".")
        try:
            cleaned_prices.append(float(number))
        except ValueError:
            # если что-то не удалось преобразовать, пропускаем
            continue
    return cleaned_prices

# Функция для извлечения названий товаров
def extract_products(text):
    # Ищем все строки перед ценой, допускаем русские, латиницу, цифры и спецсимволы
    product_pattern = r"([A-Za-zА-Яа-я0-9\[\]%\-–,.() ]+)\s+\d[\d\s]*,\d{2}"
    products = re.findall(product_pattern, text)
    products = [p.strip() for p in products]
    return products

# Функция для извлечения даты
def extract_date(text):
    # Ищем дату формата DD.MM.YYYY
    date_pattern = r"\d{2}\.\d{2}\.\d{4}"
    match = re.search(date_pattern, text)
    return match.group() if match else None

# Функция для извлечения времени
def extract_time(text):
    # Время формата HH:MM:SS
    time_pattern = r"\d{2}:\d{2}:\d{2}"
    match = re.search(time_pattern, text)
    return match.group() if match else None

# Функция для извлечения способа оплаты
def extract_payment_method(text):
    # Ищем строки "Банковская карта" или "Наличные"
    if "Банковская карта" in text:
        return "Банковская карта"
    elif "Наличные" in text:
        return "Наличные"
    else:
        return None

# Функция для подсчёта общей суммы
def calculate_total(prices):
    return sum(prices)

def main():
    receipt_text = read_receipt("raw.txt")
    prices = extract_prices(receipt_text)
    products = extract_products(receipt_text)
    date = extract_date(receipt_text)
    time = extract_time(receipt_text)
    payment_method = extract_payment_method(receipt_text)
    total = calculate_total(prices)

    receipt_data = {
        "date": date,
        "time": time,
        "products": products,
        "prices": prices,
        "total": total,
        "payment_method": payment_method
    }

    print(json.dumps(receipt_data, indent=4, ensure_ascii=False))  # ensure_ascii=False для русских букв

if __name__ == "__main__":
    main()