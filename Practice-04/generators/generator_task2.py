# Генератор, который возвращает только чётные числа от 0 до n

def even_numbers(n):
    for i in range(n + 1):
        # Проверяем, делится ли число на 2 без остатка
        if i % 2 == 0:
            yield i


n = int(input("Enter n: "))

# .join() работает только со строками,
# поэтому каждое число преобразуем в str()
result = ",".join(str(num) for num in even_numbers(n))

# Выводим в формате: 0,2,4,6...
print(result)