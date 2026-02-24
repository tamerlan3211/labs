import datetime

# Получаем текущее время с микросекундами
now = datetime.datetime.now()

# replace() позволяет изменить отдельные части даты
# Здесь мы заменяем microsecond на 0
without_microseconds = now.replace(microsecond=0)

# Вывод
print("With microseconds:", now)
print("Without microseconds:", without_microseconds)