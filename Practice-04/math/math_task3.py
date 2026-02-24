import math

n = int(input("Input number of sides: "))
side = float(input("Input the length of a side: "))

# Формула площади правильного многоугольника:
# S = (n * side^2) / (4 * tan(π / n))
area = (n * math.pow(side, 2)) / (4 * math.tan(math.pi / n))

print("The area of the polygon is:", area)