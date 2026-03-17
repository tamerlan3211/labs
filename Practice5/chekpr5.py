import re
camel_text = "helloWorldTest"

# Добавляем "_" перед заглавными буквами
snake_case = re.sub(r"([A-Z])", r"_\1", camel_text).lower()

print(snake_case)
