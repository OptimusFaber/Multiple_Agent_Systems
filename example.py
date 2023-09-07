from agents import *
import matplotlib.pyplot as plt
import random
import warnings
import imageio

warnings.simplefilter("ignore")

orders = Order_parse(choice='random', num=10).ords

couriers = []
for i in range(16):
    couriers.append(Courier(num=i))

deliver = greedy_algorithm3(orders, couriers)

t = 1
frames = []
size = 200

while any(list(map(lambda x: x.partner, couriers))):
    for c in couriers:
        plt.plot([c.pos[0]], [c.pos[1]], marker='o', color='green')
        c.update()

    for o in orders:

        plt.plot([o.pos2[0]], [o.pos2[1]], marker='o', color='red')
        plt.plot([o.pos1[0]], [o.pos1[1]], marker='o', color='yellow')

    plt.xlim([0, 100])
    plt.xlabel('x', fontsize=14)
    plt.ylim([0, 100])

    plt.title('Time is {}'.format(time), fontsize=14)
    plt.savefig(f'./img/img_{t}.png', transparent=False, facecolor='white')
    frames.append(imageio.imread(f'./img/img_{t}.png'))
    plt.close()
    t+=1

    print('-----------------')
    time.update()

imageio.mimsave('./example.gif',
                frames,
                duration=100)
