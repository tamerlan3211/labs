import os
import shutil


# 1. Создание файла и запись данных
def create_file():
    with open("sample.txt", "w", encoding="utf-8") as file:
        file.write("Hello\n")
        file.write("This is a sample file\n")
        file.write("Python is great\n")


# 2. Чтение файла
def read_file():
    with open("sample.txt", "r", encoding="utf-8") as file:
        content = file.read()
        print("Содержимое файла:")
        print(content)


# 3. Добавление строк
def append_file():
    with open("sample.txt", "a", encoding="utf-8") as file:
        file.write("New line added\n")

    print("После добавления:")
    read_file()


# 4. Копирование файла
def copy_file():
    shutil.copy("sample.txt", "sample_copy.txt")
    print("Файл скопирован как sample_copy.txt")


# 5. Удаление файла
def delete_file():
    file_name = "sample_copy.txt"

    if os.path.exists(file_name):
        os.remove(file_name)
        print(f"{file_name} удалён")
    else:
        print("Файл не найден")


def main():
    create_file()
    read_file()
    append_file()
    copy_file()
    delete_file()


if __name__ == "__main__":
    main()