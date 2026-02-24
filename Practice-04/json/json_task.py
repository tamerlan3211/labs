import json

# Открываем и читаем JSON файл
with open("Json_task_for.json") as f:
    data = json.load(f)

# Заголовок таблицы
print("Interface Status")
print("=" * 80)
print(f"{'DN':<50} {'Description':<20} {'Speed':<6} {'MTU':<6}")
print("-" * 50, "-" * 20, "-" * 6, "-" * 6)

# Предположим, что в JSON есть список интерфейсов
# Структура может быть типа:
# data['imdata'] = [
#   {"l1PhysIf": {"attributes": {"dn": "...", "descr": "...", "speed": "...", "mtu": "..."}}}, ...
# ]
for interface in data['imdata']:
    attrs = interface['l1PhysIf']['attributes']
    dn = attrs.get('dn', '')             # полный путь интерфейса
    descr = attrs.get('descr', 'inherit') # описание, если пустое → inherit
    speed = attrs.get('speed', 'inherit') # скорость, если пустая → inherit
    mtu = attrs.get('mtu', '')           # mtu

    # Выводим красиво в столбцах
    print(f"{dn:<50} {descr:<20} {speed:<6} {mtu:<6}")