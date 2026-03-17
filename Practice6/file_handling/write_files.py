# создаём и записываем данные в файл

with open("sample.txt", "w", encoding="utf-8") as file:
    file.write("Hello\n")
    file.write("This is a sample file\n")
    file.write("Python is easy\n")

print("Файл создан и данные записаны")