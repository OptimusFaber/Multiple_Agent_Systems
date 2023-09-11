from agents_v2 import *
import matplotlib.pyplot as plt
import random
import warnings
import imageio

random.seed(43)

warnings.simplefilter("ignore")

orders = Order_parse(choice='random', num=40).ords

orders.sort(key=lambda x: x.timing)
buf = orders.copy()

couriers = []
for i in range(15):
    couriers.append(Courier(num=i, ln=200, wd=200))

plan = Business()

new_sum2 = 2
new_sum1 = 1
pt = True
for i in range(15):
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

t = 1
frames = []
size = 200
income = 0
while any(list(map(lambda x: x.partner, couriers))):
    for c in couriers:
        plt.plot([c.pos[0]], [c.pos[1]], marker='o', color='green')
        c.update()
    ind = -1
    for o in buf:
        if o.partner:
            plt.plot([o.pos2[0]], [o.pos2[1]], marker='*', color='red')
            plt.plot([o.pos1[0]], [o.pos1[1]], marker='D', color='yellow')
        else:
            income += o.income
            ind = buf.index(o)
    if ind >= 0:
        del buf[ind]

    plt.xlim([0, size])
    plt.xlabel('x', fontsize=14)
    plt.ylim([0, size])

    plt.title('Time is {}     Earnings are {}'.format(time, str(income)), fontsize=14)
    plt.savefig(f'./img/img_{t}.png', transparent=False, facecolor='white')
    frames.append(imageio.imread(f'./img/img_{t}.png'))
    plt.close()
    t+=1

    time.update()

imageio.mimsave('./example2.gif',
                frames,
                loop=1,
                duration=200)


