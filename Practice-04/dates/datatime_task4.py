import datetime

# Ввод двух дат вручную (пример фиксированных дат)
date1 = datetime.datetime(2026, 2, 24, 12, 0, 0)
date2 = datetime.datetime(2026, 2, 25, 12, 0, 0)

# Вычисляем разницу
difference = date2 - date1

# total_seconds() возвращает разницу в секундах
seconds = difference.total_seconds()

print("Difference in seconds:", seconds)