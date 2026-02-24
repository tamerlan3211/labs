# Генератор, который возвращает числа от n до 0

def countdown(n):
    # Пока n больше или равно 0
    while n >= 0:
        # Возвращаем текущее значение
        yield n
        # Уменьшаем n на 1
        n -= 1


n = int(input("Enter n: "))

# Перебираем генератор
for num in countdown(n):
    print(num)