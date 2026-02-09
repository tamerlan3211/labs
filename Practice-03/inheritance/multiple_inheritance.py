class Flyable:
    def fly(self):
        print("I can fly")

class Swimable:
    def swim(self):
        print("I can swim")

class Duck(Flyable, Swimable):
    pass

duck = Duck()
duck.fly()
duck.swim()
