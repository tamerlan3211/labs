age = 20
has_ticket = True

# and
can_enter = age >= 18 and has_ticket
print("Can enter:", can_enter)

# or
is_weekend = False
is_holiday = True
print("Free day:", is_weekend or is_holiday)

# not
is_raining = False
print("Not raining:", not is_raining)

# Combined example
temperature = 25
is_sunny = True

good_weather = temperature > 20 and is_sunny
print("Good weather:", good_weather)
