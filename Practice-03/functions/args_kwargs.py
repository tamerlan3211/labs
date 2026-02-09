def show_numbers(*args):
    for num in args:
        print(num)

show_numbers(1, 2, 3, 4)


def show_profile(**kwargs):
    for key, value in kwargs.items():
        print(f"{key}: {value}")

show_profile(name="Alex", age=20, city="Almaty")
