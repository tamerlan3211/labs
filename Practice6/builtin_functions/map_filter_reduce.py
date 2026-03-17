from functools import reduce

numbers = [1, 2, 3, 4, 5]

# map → применяет функцию к каждому элементу
squared = list(map(lambda x: x**2, numbers))
print("Квадраты:", squared)

# filter → оставляет только элементы по условию
even = list(filter(lambda x: x % 2 == 0, numbers))
print("Чётные:", even)

# reduce → сворачивает список в одно значение
sum_all = reduce(lambda x, y: x + y, numbers)
print("Сумма:", sum_all)