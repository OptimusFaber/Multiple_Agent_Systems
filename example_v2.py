from agents_v2 import *
import matplotlib.pyplot as plt
import random
import warnings
import imageio

# random.seed(43)

warnings.simplefilter("ignore")

orders = Order_parse(choice='random', num=15).ords

orders.sort(key=lambda x: x.timing)

couriers = []
for i in range(8):
    couriers.append(Courier(num=i, ln=100, wd=100))

plan = Business()

new_sum2 = 2
new_sum1 = 1
pt = True
for i in range(10):
    orders = plan.greedy_algorithm3(orders, couriers)
    if pt:
        new_sum1 = plan.earnings
        pt = False
    else:
        new_sum2 = plan.earnings
        pt = True

    if new_sum1 == new_sum2:
        break
print(plan.earnings)
if orders:
    orders = plan.higgle_algorithm(orders, couriers)
print(plan.earnings)
for c in couriers:
    print(c)


