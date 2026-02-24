import datetime

# Получаем сегодняшнюю дату
today = datetime.date.today()

# timedelta на 1 день
one_day = datetime.timedelta(days=1)

# Вычисляем даты
yesterday = today - one_day
tomorrow = today + one_day

# Выводим
print("Yesterday:", yesterday)
print("Today:", today)
print("Tomorrow:", tomorrow)