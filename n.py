import random

s1 = random.randint(0, 11)
s2 = random.randint(90, 101)
s3 = random.randint(1, 11)

x = []
while len(x) < 9:
    dot = random.randrange(s1, s2, s3)
    if dot not in x:
        x.append(dot)

s1 = random.randint(0, 11)
s2 = random.randint(90, 101)
s3 = random.randint(1, 11)

y = []
while len(y) < 9:
    dot = random.randrange(s1, s2, s3)
    if dot not in y:
        y.append(dot)

shops = list(zip(x, y))
print(shops)

