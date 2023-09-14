import math
import random
import collections

import pygame
from pygame.locals import (K_ESCAPE, KEYDOWN)

SIMULATION_NAME = 'Multi-Agent Courier-Order System'
SIMULATION_EXPERIMENT = 'Predator Prey Relationship / Example 01'

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600


class Time:
    def __init__(self, h=9, m=0):
        self.hours = h
        self.minutes = m

    def update(self):
        """
        Changes time on 1 minute
        :return: time in simulation
        """
        self.minutes = (self.minutes + 1) % 60
        self.hours += (self.minutes + 1) // 60
        self.__str__()

    def __str__(self):
        """
        :return: time in simulation
        """
        if self.minutes < 10:
            return '{}:0{}'.format(self.hours, self.minutes)
        else:
            return '{}:{}'.format(self.hours, self.minutes)

    def __add__(self, other):
        """
        summaries time
        :param other: list [hours, minutes]
        :return: list [hours, minutes]
        """
        h = self.hours + other[0] + (self.minutes + other[1]) // 60
        m = (self.minutes + other[1]) % 60
        return [h, m]

    def __lt__(self, other):
        """
        compares time
        :param other: list [hours, minutes]
        :return: bool
        """
        if self.hours < other[0] or (self.hours == other[0] and self.minutes < other[1]):
            return True
        else:
            return False

    def __gt__(self, other):
        """
        compares time
        :param other: list [hours, minutes]
        :return: bool
        """
        if self.hours > other[0] or (self.hours == other[0] and self.minutes > other[1]):
            return True
        else:
            return False

    def actual_time(self):
        return [self.hours, self.minutes]


time = Time()


class Agent(pygame.sprite.Sprite):
    def __init__(self, size, color, x=None, y=None):
        super().__init__()
        self.num = None
        self.partner = None if self.__class__.__name__ == 'Order' else {}
        self.income = 0
        self.free = time

        # draw agent
        self.surf = pygame.Surface((2 * size, 2 * size), pygame.SRCALPHA, 32)
        pygame.draw.circle(self.surf, color, (size, size), size)
        self.rect = self.surf.get_rect()

        # self.vmax = 0.0

        # initial position
        self.x = x
        self.y = y

        # if self.__class__.__name__ == 'Courier':
        # default values for Courier
        # self.vmax = 2.0

        # initial velocity for Courier
        # self.dx = 0
        # self.dy = 0

        # move agent on screen
        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)

    def connect(self, other, st=0):
        """
        :param other: Order object
        :param st: default
        :return: None
        """
        if st == 0:
            self.free = Time(self.interim_time[0], self.interim_time[1])
            self.partner.update([(other, self.interim_time)])
            self.income = self.count(other)
            other.connect(self, st=1)
        else:
            self.partner = other

    def count(self, other):
        """
        :param other: Order object
        :return: int (income)
        """
        if self.partner:
            [last_order] = collections.deque(self.partner, maxlen=1)  # Достаем последний заказ
            pos = last_order.pos2
        else:
            pos = self.pos
        dst = self.dist_count(pos, other.pos1) + self.dist_count(other.pos1, other.pos2)
        income = other.price - self.price * dst / 10
        return income

    def last_order_count(self):
        if self.partner:
            [last_order] = collections.deque(self.partner, maxlen=1)  # Достаем последний заказ
            return self.count(last_order)
        else:
            return 0

    def clear(self, st=0, delivered=False):
        """
        :param st: default
        :param delivered: bool (status of Order if it was delivered or not)
        :return: None if delivered, Order if not delivered
        """
        if not delivered:
            if st == 0:
                [last_order] = collections.deque(self.partner, maxlen=1)  # Достаем последний заказ
                buf = last_order
                last_order.clear(st=1, delivered=False)  # чтобы заменить его на новый
                self.partner.pop(last_order)
                if self.partner:
                    [last_order] = collections.deque(self.partner, maxlen=1)
                    self.free = Time(self.partner[last_order][0], self.partner[last_order][1])
                else:
                    self.free = time
                return buf
            else:
                self.partner = None
        else:
            if st == 0:
                first_order = next(iter(self.partner))
                first_order.clear(st=1, delivered=True)
                self.partner.pop(first_order)
                self.free = time
            else:
                self.partner = None

    @staticmethod
    def dist_count(dot1, dot2):
        """
        :param dot1: list (coordinates)
        :param dot2: list (coordinates)
        :return: list (result coordinates)
        """
        return math.sqrt((dot1[0] - dot2[0]) ** 2 + (dot1[1] - dot2[1]) ** 2)


class Courier(Agent):
    def __init__(self, ln=600, wd=600, num=0):
        self.pos = [random.randint(0, wd), random.randint(0, ln)]
        self.price = random.randint(25, 40)
        self.start_time = [random.randint(8, 9), random.randint(0, 50)]
        self.end_time = [self.start_time[0] + 12, self.start_time[1]]
        self.start_work = self.start_time < time  # Проверяем вышел ли Курьер на работу
        self.end_work = self.end_time < time  # Проверяем закончил ли Курьер работу
        self.status = self.start_work and not self.end_work
        self.num = num
        self.vector = None
        self.k = None
        self.b = None
        self.delivery_status = 0
        self.make_route = True
        self.free = Time(self.start_time[0], self.start_time[1]) if self.start_time > time else time
        self.interim_time = None
        super().__init__(size=4, color=(255, 0, 0), x=self.pos[0], y=self.pos[1])

    def route(self, pt=0):
        """
        finds k and h parameters for route-graph y=kx+b
        :param pt: destination 1 or 2
        :return: None
        """
        if self.partner:
            first_order = next(iter(self.partner))
            if pt == 0:
                if self.pos[0] == first_order.pos1[0]:
                    self.k = 0
                    self.b = 0
                else:
                    self.k = (self.pos[1] - first_order.pos1[1]) / (self.pos[0] - first_order.pos1[0])
                    self.b = self.pos[1] - self.k * self.pos[0]
            elif pt == 1:
                if self.pos[0] == first_order.pos2[0]:
                    self.k = 0
                    self.b = 0
                else:
                    self.k = (first_order.pos2[1] - self.pos[1]) / (first_order.pos2[0] - self.pos[0])
                    self.b = self.pos[1] - self.k * self.pos[0]

    def calculate_position(self, st=0):  # Обновляем позицию каждую секунду => он будет проходить 1 клетку в секунду
        """
        We have equation:
        x1^2 * (1+k^2) - x1 * (2*x0 + 2*y0*k - 2*k*b) + (x0^2 + y0^2 - 2*y0*b + b^2 - s^2) = 0
        where x1 is unknown
        Calculates the next coordinates of Courier and updates the old ones
        :return: list - finish position
        """
        if st == 0:
            pos = next(iter(self.partner)).pos1
        else:
            pos = next(iter(self.partner)).pos2
        a = 1 + self.k ** 2
        b = 2 * self.pos[0] + 2 * self.pos[1] * self.k - 2 * self.k * self.b
        c = self.pos[0] ** 2 + self.pos[1] ** 2 - 2 * self.pos[1] * self.b + self.b ** 2 - 1 ** 2
        D = b ** 2 - 4 * a * c
        if self.pos[1] < pos[1] and self.pos[0] < pos[0]:
            x = max((b + math.sqrt(D)) / (2 * a), (b - math.sqrt(D)) / (2 * a))
            y = self.k * x + self.b
        elif self.pos[1] < pos[1] and self.pos[0] > pos[0]:
            x = min((b + math.sqrt(D)) / (2 * a), (b - math.sqrt(D)) / (2 * a))
            y = self.k * x + self.b
        elif self.pos[1] > pos[1] and self.pos[0] < pos[0]:
            x = max((b + math.sqrt(D)) / (2 * a), (b - math.sqrt(D)) / (2 * a))
            y = self.k * x + self.b
        elif self.pos[1] > pos[1] and self.pos[0] > pos[0]:
            x = min((b + math.sqrt(D)) / (2 * a), (b - math.sqrt(D)) / (2 * a))
            y = self.k * x + self.b
        else:
            if self.pos[1] == pos[1] and self.pos[0] < pos[0]:
                y = pos[1]
                x = self.pos[0] + 1
            elif self.pos[1] == pos[1] and self.pos[0] > pos[0]:
                y = pos[1]
                x = self.pos[0] - 1
            elif self.pos[1] > pos[1] and self.pos[0] == pos[0]:
                x = pos[0]
                y = self.pos[1] - 1
            elif self.pos[1] > pos[1] and self.pos[0] == pos[0]:
                x = pos[0]
                y = self.pos[1] + 1
            else:
                self.clear(delivered=True)
                return pos

        self.pos = [x, y]  # Обновляем позицию

        return pos

    def time_count(self, other):
        """
        Checks if Courier will be able to deliver at the time
        :param other: Order object
        :return: bool
        """
        if not self.partner:
            position = self.pos
        else:
            [last_order] = collections.deque(self.partner, maxlen=1)
            position = last_order.pos2
        dist = self.dist_count(position, other.pos1) + self.dist_count(other.pos1, other.pos2)
        timing = [(dist / 10) // 18, (
                dist / 10) % 18 / 18 * 60]  # Делаем подсчёт времени для доставки Курьером продукта, если он скоро выйдет
        delivery_time = self.free + timing  # К времени, когда Курьер закончит - добавляем время на доставку
        self.period = Time(timing[0], timing[1])
        if other.timing > delivery_time:
            self.interim_time = delivery_time
            return True
        else:
            return False

    def update(self, screen):
        """
        Method to update the position and the status of Courier
        :return: None
        """
        self.start_work = self.start_time < time  # Проверяем вышел ли Курьер на работу
        self.end_work = self.end_time < time  # Проверяем закончил ли Курьер работу
        self.status = self.start_work and not self.end_work
        if self.status and self.partner:  # Проверяем есть ли у Курьера заказ и вышел ли он на работу
            if not self.delivery_status:  # рассчитываем ему путь до первой цели и меняем статус
                self.route(self.delivery_status)

            pos = self.calculate_position(self.delivery_status)  # Возвращаем позицию цели

            [last_order] = collections.deque(self.partner, maxlen=1)
            self.free = self.partner[last_order]
            if self.dist_count(self.pos, pos) <= 1:  # Если курьер в минуте от цели, считаем что
                self.delivery_status = (self.delivery_status + 1) % 2  # заказ доставлен
                self.pos = pos
                self.route(self.delivery_status)
                if not self.delivery_status:  # Если статус снова 0, значит заказ доставлен
                    self.clear(delivered=True)

        self.x = self.pos[0]
        self.y = self.pos[1]

        # update graphics
        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)
        screen.blit(self.surf, self.rect)

    def check_if_arrived(self, pos):
        if self.dist_count(self.pos, pos) <= 1:
            self.delivery_status += 1

    def __str__(self):
        return 'Courier-{} took order number {}'.format(self.num, ', '.join(
            list(map(str, (map(lambda x: x.num, list(self.partner.keys())))))))


class Order(Agent):
    def __init__(self, pos1, pos2, price, t, num):
        self.pos1 = pos1
        self.pos2 = pos2
        self.price = price
        self.timing = [t[0], t[1]]
        self.num = num
        super().__init__(size=3, color=(255, 255, 255), x=self.pos2[0], y=self.pos2[1])

    def __gt__(self, other):
        """
        compares time
        :param other: list [hours, minutes]
        :return:
        """
        if self.__class__.__name__ == 'Order':
            if self.timing[0] > other.timing[0] or (
                    self.timing[0] == other.timing[0] and self.timing.timing[1] > other.timing[1]):
                return True
            else:
                return False
        else:
            if self.timing[0] > other[0] or (self.timing[0] == other[0] and self.timing[1] > other[1]):
                return True
            else:
                return False

    def update(self, screen):
        screen.blit(self.surf, self.rect)
        return

    def __str__(self):
        return 'Order number {}'.format(self.num)


class Shops(Agent):
    def __init__(self, chords):
        self.pos = chords
        super().__init__(size=3, color=(255, 255, 0), x=self.pos[0], y=self.pos[1])

    def update(self, screen):
        screen.blit(self.surf, self.rect)
        return


class Order_parse:
    """
    For generating or reading coordinates of order
    """

    def __init__(self, choice='random', num=None, filename=None, size=600, shops_num=9, gen_shops=False):
        """
        :param choice: default: random, for reading from .txt: file, for one random order: order
        :param num: for random choice - number of random orders
        :param filename: for file choice - name of .txt file
        :param size: size of field
        :param shops_num: number of shop points
        """
        self.shops = None
        self.num = 0
        if choice == 'random':
            if not self.shops:
                self.point_generator(size=size, num=shops_num)
            self.ords = self.random_generate(num, size)
        elif choice == 'file':
            self.ords = self.file_parse(filename)
        elif choice == 'order':
            if not self.shops:
                self.point_generator(size=size, num=shops_num, )
            self.ords = self.random_time_generate(size)

    @staticmethod
    def file_parse(file_name):
        """
        Parse file for Order information - pos1, pos2, price, time
        :param file_name: str (file name .txt)
        :return: list of Order objects
        """
        raf = []
        file = open(file_name).readlines()
        for i in range(len(file)):
            buf = file[i].split(' ')
            buf[0] = list(map(int, buf[0].replace('(', '').replace(')', '').split(',')))
            buf[1] = list(map(int, buf[1].replace('(', '').replace(')', '').split(',')))
            buf[2] = int(buf[2])
            buf[3] = list(map(int, buf[3].split(':')))
            raf.append(Order(buf[0], buf[1], buf[2], buf[3], i))
        return raf

    def random_generate(self, num, size):
        """
        Randomly generates 9 shop places and then specific number of Orders
        :param size: size of field
        :param num: int (number of Orders)
        :return: list of Order objects
        """
        ordrs = []
        for i in range(self.num, self.num + num):
            posx = random.randint(1, size)
            posy = random.randint(1, size)
            shopx, shopy = 0, 0
            dst = 1000
            for s in self.shops:
                if dst > math.sqrt((posx - s.pos[0]) ** 2 + (posy - s.pos[1]) ** 2):
                    shopx = s.pos[0]
                    shopy = s.pos[1]
                    dst = math.sqrt((posx - s.pos[0]) ** 2 + (posy - s.pos[1]) ** 2)

            price = random.randint(40, 55) * (dst // 10 + 12)
            tme = [random.randint(9, 13), random.randrange(0, 61, 5)]

            ordrs.append(Order([shopx, shopy], [posx, posy], price, tme, i))
        self.num = num
        return ordrs

    def random_time_generate(self, size=600):
        """
        Generates a random Order somewhere on map
        :param size: size of field
        :return:
        """
        self.num += 1
        required_time = random.randrange(40, 76, 5)
        timing = time + [0, required_time]
        posx = random.randint(1, size)
        posy = random.randint(1, size)
        shopx, shopy = 0, 0
        dst = 1000
        for s in self.shops:
            if dst > math.sqrt((posx - s.pos[0]) ** 2 + (posy - s.pos[1]) ** 2):
                shopx = s.pos[0]
                shopy = s.pos[1]
                dst = math.sqrt((posx - s.pos[0]) ** 2 + (posy - s.pos[1]) ** 2)

        price = random.randint(40, 55) * (dst // 10 + 12)

        ordr = Order([shopx, shopy], [posx, posy], price, timing, self.num)

        return ordr

    def point_generator(self, size=100, num=9):
        s1 = random.randint(1, size // 10)
        s2 = random.randint(size // 2, size)
        s3 = random.randint(6, 11)
        x = []
        while len(x) < num:
            dot = random.randrange(s1, s2, s3)
            if dot not in x:
                x.append(dot)
        s1 = random.randint(1, size // 10)
        s2 = random.randint(size // 2, size)
        s3 = random.randint(6, 11)
        y = []
        while len(y) < num:
            dot = random.randrange(s1, s2, s3)
            if dot not in y:
                y.append(dot)

        shops = list(zip(x, y))
        self.shops = [Shops(pos) for pos in shops]


class Algorithm:
    def __init__(self):
        self.earnings = 0

    def greedy_algorithm3(self, ordr, wrkrs):
        list_orders = []
        declined_orders = []
        for i in range(len(ordr)):
            maxi = 0  # Максимальная сумма, которую можем получить с этой сделки
            obj = None  # Курьер, который доставит заказ
            pt = None
            for j in range(len(wrkrs)):
                if not wrkrs[j].end_work:  # Проверяем, работает ли наш курьер
                    if wrkrs[j].time_count(ordr[i]) and wrkrs[j].count(
                            ordr[i]) > maxi:  # Проверяем, успеет ли Курьер доставить заказ
                        maxi = wrkrs[j].count(ordr[i])
                        obj = wrkrs[j]
                        pt = 0
                    elif (not wrkrs[j].time_count(ordr[i]) and wrkrs[j].partner) or (
                            wrkrs[j].time_count(ordr[i]) and not wrkrs[j].count(
                        ordr[i]) > maxi):  # Если не успеет, то попробуем вытащить его последний заказ
                        if wrkrs[j].last_order_count() < wrkrs[j].count(ordr[i]):
                            maxi = wrkrs[j].count(ordr[i])
                            obj = wrkrs[j]
                            pt = 1
            if obj:  # Если Курьер был найден, то соединяем его с заказом
                if pt and obj.partner:
                    buf = obj.clear()
                    self.earnings -= obj.count(buf)
                    buf.income = 0
                    declined_orders.append(buf)  # Убираем заказ из списка принятых и продолжаем искать варианты
                obj.connect(ordr[i])
                ordr[i].income = obj.count(ordr[i])
                self.earnings += obj.count(ordr[i])
                list_orders.append(ordr[i])  # Добавляем заказ в список принятых

        for o in list_orders:
            if o in ordr:
                ordr.remove(o)
        ordr.extend(declined_orders)
        return ordr

    def higgle_algorithm(self, ordr, wrkrs):  # На случай если остались заказы, которые некуда рассовать
        list_orders = []
        for i in range(len(ordr)):
            t_maxi = [9, 0]  # Максимальное время доставки
            obj = None  # Курьер, который доставит заказ
            income = None
            for j in range(len(wrkrs)):
                wrkrs[j].time_count(ordr[i])
                if not wrkrs[j].end_work and wrkrs[
                    j].period < t_maxi:  # Ищем курьера, который быстрее всего доставит заказ
                    t_maxi = wrkrs[j].period.actual_time()
                    income = wrkrs[j].count(ordr[i])
                    obj = wrkrs[j]
            if obj:
                income -= ordr[i].price * 0.1  # Мы делаем скидку в 10% за задержку заказа
                self.earnings += income
                obj.connect(ordr[i])
                ordr[i].income = obj.count(ordr[i])
                self.earnings += obj.count(ordr[i])
                list_orders.append(ordr[i])

        for o in list_orders:
            if o in ordr:
                ordr.remove(o)

        return ordr


def main():
    # Import and initialize the pygame library
    pygame.init()
    clock = pygame.time.Clock()

    # white = (255, 255, 255)
    green = (0, 255, 0)
    black = (0, 0, 0)

    font = pygame.font.Font('freesansbold.ttf', 12)
    t = ':'.join(map(str, time.actual_time()))
    text = font.render(t, True, green, black)
    textRect = text.get_rect()
    textRect.center = (600-20, 20)
    # Create the screen object
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(f'Simulation')

    # create initial agents
    targets = Order_parse(choice='random', num=20)
    shops = targets.shops
    orders_buf = targets.ords
    orders_buf.sort(key=lambda x: x.timing)
    orders = orders_buf.copy()
    couriers = [Courier(num=i, ln=600, wd=600) for i in range(15)]
    alg = Algorithm()
    new_sum1, new_sum2 = 1, 2
    pt = True
    for i in range(15):
        orders_buf = alg.greedy_algorithm3(orders_buf, couriers)
        if pt:
            new_sum1 = alg.earnings
            pt = False
        else:
            new_sum2 = alg.earnings
            pt = True
        if new_sum1 == new_sum2:
            break
    if orders_buf:
        alg.higgle_algorithm(orders_buf, couriers)

    # Run until the user asks to quit
    running = True
    print(len(orders))
    t = 0
    while running:
        ti = ':'.join(map(str, time.actual_time()))
        text = font.render(ti, True, green, black)
        textRect = text.get_rect()
        textRect.center = (600 - 20, 20)

        # check user input events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False

        # Fill the background
        screen.fill((11, 11, 11))

        # update all agents
        # print(len(orders))
        [o.update(screen) for o in orders]
        [c.update(screen) for c in couriers]
        [s.update(screen) for s in shops]
        if t == 24:
            time.update()
            t = 0
            if time.actual_time()[1] % 4 == 0:
                ordr = targets.random_time_generate()
                orders.append(ordr)
                ordr = alg.greedy_algorithm3([ordr], couriers)
                if ordr:
                    alg.higgle_algorithm(ordr, couriers)
                print(orders)

        orders = [o for o in orders if o.partner]

        screen.blit(text, textRect)

        # draw all changes to the screen
        pygame.display.flip()
        clock.tick(24)  # wait until next frame (at 60 FPS)
        t += 1
        # print(len(orders))

    # Done! Time to quit.
    pygame.quit()


if __name__ == "__main__":
    main()
