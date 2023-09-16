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
        if self.hours == 24:
            self.hours = 0
            self.minutes = 0
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
    def __init__(self, size, color, x=None, y=None, num=None):
        super().__init__()
        self.num = num  # Номер нашего Агента
        self.partner = None if self.__class__.__name__ == 'Order' else {}   # Связь Агента
        self.income = 0     # Доход, который он мне приносит
        self.free = time

        # Рисуем Агента
        self.surf = pygame.Surface((2 * size, 2 * size), pygame.SRCALPHA, 32)
        pygame.draw.circle(self.surf, color, (size, size), size)
        self.rect = self.surf.get_rect()

        self.x = x
        self.y = y

        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)

    def connect(self, other, timing=None):
        """
        :param other: Order object
        :param timing: at what time the Order will be delivered by Courier
        :return: None
        """
        if self.__class__.__name__ == 'Courier':
            self.partner.update([(other, timing)])
            self.income = round(self.count(other))
            self.free = Time(timing[0], timing[1])
            other.connect(self)
        else:
            self.partner = other
            self.income = round(other.income)

    def count(self, other):
        """
        Our income
        :param other: Order object
        :return: int (income)
        """
        if self.partner:
            [last_order] = collections.deque(self.partner, maxlen=1)  # Достаем последний заказ
            pos = last_order.pos2
        else:
            pos = self.pos
        dst = self.dist_count(pos, other.pos1) + self.dist_count(other.pos1, other.pos2)
        income = round(other.price - self.price * dst / 60)
        return income

    def clear(self, st=0, delivered=False):
        """
        Destrou cprevious connection Order-Courier
        :param st: default
        :param delivered: bool (status of Order if it was delivered or not)
        :return: None if delivered, Order if not delivered
        """
        if not delivered:   # Разрушаем связь, хоть Заказ еще не был доставлен
            if st == 0:
                [last_order] = collections.deque(self.partner, maxlen=1)  # Достаем последний заказ
                buf = last_order
                last_order.clear(st=1, delivered=False)  # чтобы заменить его на новый
                self.partner.pop(last_order)
                return buf
            else:
                self.partner = None
                self.income = 0
        else:   # Разрушаем связь и удаляем заказ, когда тот доставлен
            if st == 0:
                first_order = next(iter(self.partner))
                first_order.clear(st=1, delivered=True)
                self.partner.pop(first_order)
            else:
                self.partner = None

    @staticmethod
    def dist_count(dot1, dot2):
        """
        Counts destination between Order and Courier
        :param dot1: list (coordinates)
        :param dot2: list (coordinates)
        :return: list (result coordinates)
        """
        return math.sqrt((dot1[0] - dot2[0]) ** 2 + (dot1[1] - dot2[1]) ** 2)


class Courier(Agent):
    def __init__(self, ln=600, wd=600, num=0):
        self.pos = [random.randint(0, wd), random.randint(0, ln)]   # Положение курьера (координаты)
        self.price = random.randint(25, 35)         # Цена доставки курьера в руб за км
        self.start_time = [random.randint(8, 9), random.randint(0, 50)]     # Начало работы Курьера
        self.end_time = [self.start_time[0] + 12, self.start_time[1]]   # Окончание работы Курьера
        self.status = self.start_time < time < self.end_time    # Статус Курьера - работает он или нет
        self.num = num      # Рабочий номер Курьера
        self.k = None           # Параметр k для построения прямой пути Курьера
        self.b = None           # Параметр b для построения прямой пути Курьера
        self.delivery_status = 0    # Статус заказа 0 - нужно построить путь до магазина, 1 - путь до цели
        self.make_route = True      # Параметр для строительства маршрута
        self.free = Time(self.start_time[0], self.start_time[1]) if self.start_time > time else time    # Время, когда Курьер будет доступен для принятия нового заказа
        super().__init__(size=4, color=(255, 0, 0), x=self.pos[0], y=self.pos[1], num=self.num)   # Рисуем Курьера на экране

    def route(self, pt=0):
        """
        finds k and h parameters for route-graph y=kx+b
        :param pt: destination 1 or 2
        :return: None
        """
        if self.partner:
            first_order = next(iter(self.partner))
            if pt == 0:     # pt это пункт назначения (pt = 0 это магазин, pt = 1 это заказчик)
                if self.pos[0] == first_order.pos1[0] or self.pos[1] == first_order.pos1[1]:
                    self.k = 0
                    self.b = 0
                else:
                    self.k = (self.pos[1] - first_order.pos1[1]) / (self.pos[0] - first_order.pos1[0])
                    self.b = self.pos[1] - self.k * self.pos[0]
            elif pt == 1:
                if self.pos[0] == first_order.pos2[0] or self.pos[1] == first_order.pos2[1]:
                    self.k = 0
                    self.b = 0
                else:
                    self.k = (first_order.pos2[1] - self.pos[1]) / (first_order.pos2[0] - self.pos[0])
                    self.b = self.pos[1] - self.k * self.pos[0]

    def calculate_position(self, pt=0):  # Обновляем позицию каждую секунду => он будет проходить 1 клетку в секунду
        """
        We have equation:
        x1^2 * (1+k^2) - x1 * (2*x0 + 2*y0*k - 2*k*b) + (x0^2 + y0^2 - 2*y0*b + b^2 - s^2) = 0
        where x1 is unknown
        Calculates the next coordinates of Courier and updates the old ones
        :return: list - finish position
        """
        if pt == 0:     # Как и в прошлом методе, pt = 0 это магазин, а pt = 1 это заказчик
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
            elif self.pos[1] < pos[1] and self.pos[0] == pos[0]:
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
        if not self.partner:    # Если у Курьера нет иных заказов, то считаем точкой отсчёта его начальную позицию
            position = self.pos
        else:
            [last_order] = collections.deque(self.partner, maxlen=1)
            position = last_order.pos2      # Если в очереди есть заказы, то считаем точкой отсчета координаты последнего заказа

        dist = self.dist_count(position, other.pos1) + self.dist_count(other.pos1, other.pos2)
        self.delay = [(dist / 60) // 5, (dist / 60) % 5 / 5 * 60]  # Делаем подсчёт времени для доставки Курьером продукта, его скорость 5 км/ч
        self.delivery_time = self.free + self.delay  # Ко времени, когда Курьер закончит - добавляем время на доставку
        if other.timing > self.delivery_time and self.delivery_time < self.end_time:    # Проверяем, успеет ли Курьер всё доставить
            return True
        else:
            return False

    def check_if_swap(self, other):
        """
        Checks if Courier can swap new Order with last one if new is more profitable
        :param other: Order object
        :return: bool
        """
        last_order = list(self.partner.keys())[-1]
        if len(self.partner) > 1:
            pre_last_order_time = self.partner[list(self.partner.keys())[-2]]
            pos = list(self.partner.keys())[-2].pos2
        else:
            if self.delivery_status == 1:
                return False    # Курьер уже забрал продукты, обратно мы его не повернем
            pre_last_order_time = time.actual_time()
            pos = self.pos
        # Тут нужно узнать, будет ли Курьеру выгодна данная операция, поэтому сравним текущий последний заказ и новый
        dist1 = self.dist_count(pos, other.pos1) + self.dist_count(other.pos1, other.pos2)  # Дистанция до нового заказа
        dist2 = self.dist_count(pos, last_order.pos1) + self.dist_count(last_order.pos1, last_order.pos2)   # Дистанция до старого заказа
        delay = Time((dist1 / 60) // 5, (dist1 / 60) % 5 / 5 * 60)  # Время за которое доставят новый заказ
        delivery_time = delay + pre_last_order_time     # К какому времени прийдет новый заказ

        if delivery_time < other.timing and (last_order.price - self.price*dist2) < (other.price - self.price*dist1):
        # Сравниваем время доставки первого и второго + цену доставки
            return True
        else:
            return False

    def update(self, screen):
        """
        Method to update the position and the status of Courier
        :return: None
        """
        self.status = self.start_time < time < self.end_time
        if self.status and self.partner:  # Проверяем есть ли у Курьера заказ и вышел ли он на работу    
            self.route(self.delivery_status)    # рассчитываем ему путь до цели (self.delivery_status = 0 это магазин, self.delivery_status = 1 это Заказчик)
            pos = self.calculate_position(self.delivery_status)  # Возвращаем позицию цели, к которой пойдет Курьер

            [last_order] = collections.deque(self.partner, maxlen=1)
            self.free = Time(self.partner[last_order][0], self.partner[last_order][1])  # Обновляем время освобождения Курьера

            if self.dist_count(self.pos, pos) <= 1:  # Если курьер в минуте от цели, считаем что заказ доставлен
                self.delivery_status = (self.delivery_status + 1) % 2   # Меняем пункт доставки на Заказчика
                self.pos = pos  # Обновляем положение Курьера
                self.route(self.delivery_status)    # Заново строим машрут до цели
                if not self.delivery_status:  # Если статус снова 0, значит заказ доставлен
                    self.clear(delivered=True)  # Уничтожаем связь Курьер-Заказ и уничтожаем заказ
        elif self.status and not self.partner:
            self.free = time    # Обновляем время освобождения ждущего Курьера на текущие

        # Обновляем графику
        self.x = self.pos[0]
        self.y = self.pos[1]

        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)
        screen.blit(self.surf, self.rect)

        # Рисуем номер Курьера
        font = pygame.font.Font('freesansbold.ttf', 12)
        t = str(self.num)
        text = font.render(t, True, (255, 255, 255), None)
        textRect = text.get_rect()
        textRect.center = (self.pos[0], self.pos[1])
        screen.blit(text, textRect)

    def __str__(self):
        """
        Returns info about Orders which Courier took
        """
        return 'Courier-{} took order number {}'.format(self.num, ', '.join(
            list(map(str, (map(lambda x: x.num, list(self.partner.keys())))))))


class Order(Agent):
    def __init__(self, pos1, pos2, price, t, num):
        self.pos1 = pos1    # Координаты магазина
        self.pos2 = pos2    # Координаты Заказчика
        self.price = price  # Цена, которую платит Курьер
        self.timing = [t[0], t[1]]  # Время к которому ожидается заказ
        self.num = num  # Номер закащза (нужен для дебага)
        super().__init__(size=3, color=(0, 255, 0), x=self.pos2[0], y=self.pos2[1], num=self.num)

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
        """
        Draws Order object on map
        :param Pygame screen
        """
        screen.blit(self.surf, self.rect)
        return

    def __str__(self):
        return 'Order number {}'.format(self.num)


class Shops(Agent):
    def __init__(self, pos):
        self.pos = pos   # Координаты магазина
        super().__init__(size=3, color=(255, 255, 0), x=self.pos[0], y=self.pos[1])

    def update(self, screen):
        """
        Draws Shop object on map
        :param Pygame screen
        """
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
        :param gen_shops: generate shops for order choice
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
        ords = []
        file = open(file_name).readlines()
        for i in range(len(file)):
            buf = file[i].split(' ')
            buf[0] = list(map(int, buf[0].replace('(', '').replace(')', '').split(',')))
            buf[1] = list(map(int, buf[1].replace('(', '').replace(')', '').split(',')))
            buf[2] = int(buf[2])
            buf[3] = list(map(int, buf[3].split(':')))
            ords.append(Order(buf[0], buf[1], buf[2], buf[3], i))
        return ords

    def random_generate(self, num, size=600):
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

            price = random.randint(40, 48) * (dst // 60 + 4)
            t = random.randint(30, 75)
            tme = time + [0, t]

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

        price = random.randint(40, 48) * (dst // 60 + 4)

        ordr = Order([shopx, shopy], [posx, posy], price, timing, self.num)

        return ordr

    def point_generator(self, size=600, num=9):
        """
        Generates random Shops somewhere on map
        :param size: size of field
        :param num: number of shops
        :return
        """
        s1 = random.randint(1, size // 10)
        s2 = random.randint(size // 2, size)
        s3 = random.randint(size//15, size//5)
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
    """
    Algorithms for distributing Orders among Couriers
    """
    def __init__(self):
        self.earnings = 0   # Моя выручка за всю работу

    def greedy_algorithm3(self, ordr, wrkrs):
        list_orders = []
        declined_orders = []
        for i in range(len(ordr)):
            maxi = 0  # Максимальная сумма, которую можем получить с этой сделки
            obj = None  # Курьер, который доставит заказ
            pt = None   # Какой вариант мы выбрали (pt = 0 это просто добавить заказ, pt = 1 заменить последний)
            timing = None   # Время, к которому Курьер доставит заказ
            mini = 10000
            for j in range(len(wrkrs)):
                if time < wrkrs[j].end_time:  # Проверяем, работает ли наш курьер
                    if wrkrs[j].time_count(ordr[i]) and wrkrs[j].count(ordr[i]) > maxi:  # Проверяем, успеет ли Курьер доставить заказ
                        timing = wrkrs[j].delivery_time
                        maxi = wrkrs[j].count(ordr[i])
                        obj = wrkrs[j]
                        pt = 0
                    elif wrkrs[j].partner:  # Если не успеет, то попробуем вытащить его последний заказ
                        if wrkrs[j].check_if_swap(ordr[i]):
                            timing = wrkrs[j].delivery_time
                            obj = wrkrs[j]
                            pt = 1
                    else:   # На крайний случай спихнем заказ отдыхающему Курьеру
                        if (wrkrs[j].dist_count(wrkrs[j].pos, ordr[i].pos1) + wrkrs[j].dist_count(ordr[i].pos1, ordr[i].pos2)) < mini:
                            timing = wrkrs[j].delivery_time
                            mini = wrkrs[j].dist_count(wrkrs[j].pos, ordr[i].pos1) + wrkrs[j].dist_count(ordr[i].pos1, ordr[i].pos2)
                            obj = wrkrs[j]
                            pt = 0
            if obj:  # Если Курьер был найден, то соединяем его с заказом
                if pt and obj.partner:  # Если мы выбрали вариант замены
                    buf = obj.clear()       # Меняем старый заказ на новый
                    # self.earnings -= round(obj.count(buf))     # Вычитаем деньги из расчета
                    buf.income = 0
                    declined_orders.append(buf)  # Убираем заказ из списка принятых и продолжаем искать варианты
                obj.connect(ordr[i], timing)
                ordr[i].income = round(obj.count(ordr[i]))
                # ordr[i].income = obj.count(ordr[i])
                # self.earnings += round(obj.count(ordr[i]))
                list_orders.append(ordr[i])  # Добавляем заказ в список принятых

        for o in list_orders:   # Обновляем список заказов
            if o in ordr:
                ordr.remove(o)
        ordr.extend(declined_orders)    # Добавляем отклоненные
        return ordr     # Возвращаем остатки

    def higgle_algorithm(self, ordr, wrkrs):  # На случай если остались заказы, которые некуда рассовать
        list_orders = []
        for i in range(len(ordr)):
            t_maxi = [9, 0]  # Максимальное время доставки
            obj = None  # Курьер, который доставит заказ
            income = None   # Моя выручка
            timing = None   # Время на доставку
            for j in range(len(wrkrs)):
                wrkrs[j].time_count(ordr[i])
                if time < wrkrs[j].end_time and wrkrs[j].delay < t_maxi:  # Ищем курьера, который быстрее всего доставит заказ
                    timing = wrkrs[j].delivery_time
                    t_maxi = wrkrs[j].delay
                    income = wrkrs[j].count(ordr[i])
                    obj = wrkrs[j]
            if obj:
                income -= round(ordr[i].price * 0.1)  # Мы делаем скидку в 10% за задержку заказа
                obj.connect(ordr[i], timing)
                ordr[i].income = income
                list_orders.append(ordr[i])

        for o in list_orders:
            if o in ordr:
                ordr.remove(o)

        return ordr


def main():
    size = 600

    pygame.init()
    clock = pygame.time.Clock()

    green = (0, 255, 0)
    black = (0, 0, 0)

    font = pygame.font.Font('freesansbold.ttf', 12)
    t = ':'.join(map(str, time.actual_time()))
    text = font.render(t, True, green, None)
    textRect = text.get_rect()
    textRect.center = (size-15, 10)
 
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(f'Simulation')

    # Создаем наших агентов
    targets = Order_parse(choice='random', num=20)
    shops = targets.shops
    orders_buf = targets.ords
    orders_buf.sort(key=lambda x: x.timing)
    orders = orders_buf.copy()
    couriers = [Courier(num=i, ln=600, wd=600) for i in range(15)]

    # Запускаем Алгоритм распределения заказов
    alg = Algorithm()

    font2 = pygame.font.Font('freesansbold.ttf', 12)
    e = "{} руб.".format(str(alg.earnings))
    text2 = font2.render(e, True, green, black)
    textRect2 = text2.get_rect()
    textRect2.center = (30, 10)

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

    running = True
    print(len(orders))
    t = 0
    while running:
        ti = time.actual_time()
        if ti[1] < 9:
            ti = '{}:{}'.format(str(ti[0]), '0' + str(ti[1]))
        else:
            ti = '{}:{}'.format(str(ti[0]), str(ti[1]))
        text = font.render(ti, True, green, None)
        textRect = text.get_rect()
        textRect.center = (size - 15, 10)

        font2 = pygame.font.Font('freesansbold.ttf', 12)
        e = "{} руб.".format(str(alg.earnings))
        text2 = font2.render(e, True, green, black)
        textRect2 = text2.get_rect()
        textRect2.center = (30, 10)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False

        screen.fill((11, 11, 11))

        # Обновляем всех Агентов
        [o.update(screen) for o in orders]
        [c.update(screen) for c in couriers]
        [s.update(screen) for s in shops]
        if t == 24:
            # Время обновляется раз в секунду (1 реальная секунда = 1 минуте симуляции)
            time.update()
            t = 0
            # Каждые 4 секунды (минуты) добавляем новый заказ
            if time.actual_time()[1] % 1 == 0:
                ordr = targets.random_time_generate()
                orders.append(ordr)
                ordr = alg.greedy_algorithm3([ordr], couriers)
                if ordr:
                    alg.higgle_algorithm(ordr, couriers)

        # Удаляем старые заказы, которые уже доставили
        for o in orders:
            if not o.partner:
                alg.earnings += o.income

        orders = [o for o in orders if o.partner]

        screen.blit(text, textRect)
        screen.blit(text2, textRect2)

        pygame.display.flip()
        clock.tick(24)  # 60 FPS
        t += 1

    pygame.quit()


if __name__ == "__main__":
    main()
