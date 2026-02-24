# Импортируем модуль datetime
import datetime

# Получаем сегодняшнюю дату (без времени)
today = datetime.date.today()

# Создаём объект timedelta — разницу во времени (5 дней)
five_days = datetime.timedelta(days=5)

# Вычитаем 5 дней из текущей даты
new_date = today - five_days

# Выводим результат
print("Today:", today)
print("5 days ago:", new_date)