class Student:
    school = "High School"   # переменная класса

    def __init__(self, name):
        self.name = name     # переменная объекта

s1 = Student("Alex")
s2 = Student("Maria")

print(s1.school)
print(s2.school)
