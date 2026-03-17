import os
import shutil


# 1. Создание вложенных папок
def create_directories():
    os.makedirs("test_dir/sub_dir", exist_ok=True)
    print("Папки созданы")


# 2. Список файлов и папок
def list_files():
    print("Содержимое test_dir:")
    for item in os.listdir("test_dir"):
        print(item)


# 3. Поиск файлов по расширению
def find_txt_files():
    print("TXT файлы:")
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".txt"):
                print(os.path.join(root, file))


# 4. Перемещение файла
def move_file():
    if os.path.exists("sample.txt"):
        shutil.move("sample.txt", "test_dir/sample.txt")
        print("Файл перемещён")


# 5. Копирование файла
def copy_file():
    if os.path.exists("test_dir/sample.txt"):
        shutil.copy("test_dir/sample.txt", "test_dir/sub_dir/sample_copy.txt")
        print("Файл скопирован в sub_dir")


def main():
    create_directories()
    list_files()
    find_txt_files()
    move_file()
    copy_file()


if __name__ == "__main__":
    main()