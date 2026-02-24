# Генератор чисел от 0 до n,
# которые делятся и на 3, и на 4

def divisible(n):
    for i in range(n + 1):
        # Число должно делиться на 3 И на 4
        if i % 3 == 0 and i % 4 == 0:
            yield i


n = int(input("Enter n: "))

# Перебираем и печатаем каждое найденное число
for num in divisible(n):
    print(num)