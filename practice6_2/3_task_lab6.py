from functools import reduce


# 1. map() — квадрат чисел
def use_map():
    numbers = [1, 2, 3, 4, 5]
    squares = list(map(lambda x: x**2, numbers))
    print("Квадраты:", squares)


# 2. filter() — только чётные
def use_filter():
    numbers = [1, 2, 3, 4, 5, 6]
    evens = list(filter(lambda x: x % 2 == 0, numbers))
    print("Чётные:", evens)


# 3. reduce() — сумма
def use_reduce():
    numbers = [1, 2, 3, 4]
    total = reduce(lambda x, y: x + y, numbers)
    print("Сумма:", total)


# 4. enumerate()
def use_enumerate():
    words = ["apple", "banana", "cherry"]
    for i, word in enumerate(words):
        print(f"{i}: {word}")


# 5. zip()
def use_zip():
    names = ["A", "B", "C"]
    scores = [90, 85, 88]

    for name, score in zip(names, scores):
        print(name, score)


# 6. Проверка типов и преобразование
def type_conversion():
    x = "123"

    print("Тип:", type(x))
    x = int(x)
    print("После преобразования:", x, type(x))


def main():
    use_map()
    use_filter()
    use_reduce()
    use_enumerate()
    use_zip()
    type_conversion()


if __name__ == "__main__":
    main()