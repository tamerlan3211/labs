import os

# создаём вложенные папки
os.makedirs("test_dir/sub_dir", exist_ok=True)
print("Папки созданы")

# выводим список файлов и папок
print("\nСодержимое текущей директории:")
items = os.listdir("test_dir")

for item in items:
    print(item)