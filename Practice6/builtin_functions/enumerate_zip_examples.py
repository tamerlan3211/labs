names = ["Alice", "Bob", "Charlie"]
scores = [85, 90, 78]

# enumerate → даёт индекс + значение
print("Список с индексами:")
for index, name in enumerate(names):
    print(index, name)

# zip → объединяет списки
print("\nОбъединённые данные:")
for name, score in zip(names, scores):
    print(name, score)