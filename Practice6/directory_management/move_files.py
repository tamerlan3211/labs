import shutil
import os

# создаём папку если её нет
os.makedirs("destination", exist_ok=True)

# создаём файл для примера
with open("example.txt", "w", encoding="utf-8") as file:
    file.write("Test file")

# перемещаем файл
shutil.move("example.txt", "destination/example.txt")
print("Файл перемещён")

# копируем обратно
shutil.copy("destination/example.txt", "example_copy.txt")
print("Файл скопирован обратно")