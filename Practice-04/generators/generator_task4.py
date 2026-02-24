# Генератор квадратов чисел в диапазоне от a до b

def squares(a, b):
    
    for i in range(a, b + 1):
        yield i * i

a = int(input("Enter a: "))
b = int(input("Enter b: "))

# Проверка через цикл for
for value in squares(a, b):
    print(value)