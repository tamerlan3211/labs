import shutil
import os

# копирование файла
shutil.copy("sample.txt", "sample_copy.txt")
print("Файл скопирован")

# удаление файла
if os.path.exists("sample_copy.txt"):
    os.remove("sample_copy.txt")
    print("Копия удалена")
else:
    print("Файл не найден")







# open("file", "mode")
# открывает файл

# режимы:
# "w" → создаёт файл и перезаписывает
# "r" → читает файл
# "a" → добавляет в конец

# file.write("text")
# записывает текст в файл

# file.read()
# читает весь файл

# shutil.copy(src, dst)
# копирует файл

# os.remove("file")
# удаляет файл

# os.path.exists("file")
# проверяет существует ли файл