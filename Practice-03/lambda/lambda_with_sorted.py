students = [
    ("Alex", 85),
    ("Maria", 92),
    ("John", 78)
]

sorted_students = sorted(students, key=lambda x: x[1])

print(sorted_students)
