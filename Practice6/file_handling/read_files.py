# читаем файл и выводим содержимое

with open("sample.txt", "r", encoding="utf-8") as file:
    content = file.read()

print("Содержимое файла:")
print(content)