import math
import random


class Time:
    def __init__(self):
        self.hours = 9
        self.minutes = 0

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


time = Time()


class Agent:
    def __init__(self):
        self.num = None
        self.partner = None
        self.income = 0

    def connect(self, other, st=0):
        """
        :param other: Order object
        :param st: default
        :return: None
        """
        self.partner = other
        if st == 0:
            other.connect(self, st=1)

    def count(self, other):
        """
        :param other: Order object
        :return: int (income)
        """
        dst = dist_count(self.pos, other.pos1) + dist_count(other.pos1, other.pos2)
        self.income = other.price - self.price * dst / 10
        return self.income

    def clear(self, st=0, delivered=False):
        """
        :param st: default
        :param delivered: bool (status of Order if it was delivered or not)
        :return: None if delivered Order if not delivered
        """
        buf = self.other

        if delivered:
            if self.partner:
                del self.partner
                self.partner = None
        else:
            if self.partner:
                if st == 0:
                    self.partner.clear(st=1)
                self.partner = None
            return buf

    @staticmethod
    def dist_count(dot1, dot2):
        """
        :param dot1: list (coordinates)
        :param dot2: list (coordinates)
        :return: list (result coordinates)
        """
        return math.sqrt((dot1[0] - dot2[0]) ** 2 + (dot1[1] - dot2[1]) ** 2)


class Courier(Agent):
    def __init__(self, ln, wd, num=0):
        super().__init__()
        self.pos = [random.randint(0, wd), random.randint(0, ln)]
        self.price = random.randint(25, 40)
        self.start_time = [random.randint(8, 9), random.randint(0, 50)]
        self.end_time = [self.start_time[0] + 12, self.start_time[1]]
        self.start_work = self.start_time < time  # Проверяем вышел ли Курьер на работу
        self.end_work = self.end_time < time  # Проверяем закончил ли Курьер работу
        self.status = self.start_work and not self.end_work
        if not self.end_work and not self.start_work:  # Смотрим через сколько Курьер выйдет на работу
            self.wait = [self.start_time[0] - time.hours, self.start_time[1] - time.minutes]
        else:
            self.wait = [0, 0]
        self.num = num
        self.vector = None
        self.k = None
        self.b = None

    def route(self, pt=0):
        """
        finds k and h parameters for route-graph y=kx+b
        :param pt: destination 1 or 2
        :return: None
        """
        if self.partner:
            if pt == 0:
                self.k = (self.pos[1] - self.partner.pos1[1]) / (self.pos[0] - self.partner.pos1[0])
                self.b = self.pos[1] - self.k * self.pos[0]
            elif pt == 1:
                self.k = (self.partner.pos2[1] - self.partner.pos1[1]) / (self.partner.pos2[0] - self.partner.pos1[0])
                self.b = self.partner.pos1[1] - k * self.partner.pos1[0]

    def calculate_position(
            self):  # Обновлять позицию будем каждую секунду (минуту) => он будет проходить 1 клетку в секунду
        """
        We have equation:
        x1^2 * (1+k^2) - x1 * (2*x0 + 2*y0*k - 2*k*b) + (x0^2 + y0^2 - 2*y0*b + b^2 - s^2) = 0
        where x1 is unknown
        Calculates the next coordinates of Courier and updates the old ones
        :return: None
        """
        a = 1 + self.k ** 2
        b = 2 * self.pos[0] + 2 * self.pos[1] * self.k - 2 * self.k * self.b
        c = self.pos[0] ** 2 + self.pos[1] ** 2 - 2 * self.pos[1] * self.b + self.b ** 2 - 10 ** 2
        D = b ** 2 - 4 * a * c
        if self.pos[1] < self.partner.pos1[1]:
            x = max((b + math.sqrt(D)) / (2 * a), (b - math.sqrt(D)) / (2 * a))
        else:
            x = min((b + math.sqrt(D)) / (2 * a), (b - math.sqrt(D)) / (2 * a))
        y = self.k * x + self.b
        self.pos = [x, y]  # Обновляем позицию

    def time_count(self, other):
        """
        Checks if Courier will be able to deliver at the time
        :param other: Order object
        :return: bool
        """
        dist = self.dist_count(self.pos, other.pos1) + self.dist_count(other.pos1, other.pos2)
        timing = [(dist / 10) // 6, (
                dist / 10) % 6 / 6 * 60]  # Делаем подсчёт времени для доставки Курьером продукта, если он скоро выйдет

        delivery_time = time + timing + self.wait
        if other.timing > delivery_time:
            return True
        else:
            return False

    def update(self):
        """
        Method to update the position and the status of Courier
        :return: None
        """
        self.start_work = self.start_time < time  # Проверяем вышел ли Курьер на работу
        self.end_work = self.end_time < time  # Проверяем закончил ли Курьер работу
        self.status = self.start_work and not self.end_work
        if self.partner:
            self.route()
            self.calculate_position()

    def __str__(self):
        return 'Courier-{} took order number {}'.format(self.num, self.partner.num)


class Order(Agent):
    def __init__(self, pos1, pos2, price, t, num):
        super().__init__()
        self.pos1 = pos1
        self.pos2 = pos2
        self.price = price
        self.timing = [t[0], t[1]]
        self.num = num

    def __gt__(self, other):
        """
        compares time
        :param other: list [hours, minutes]
        :return:
        """
        if self.timing[0] > other[0] or (self.timing[0] == other[0] and self.timing[1] > other[1]):
            return True
        else:
            return False

    def __str__(self):
        return 'Order number {}'.format(self.num)


class Order_parse:
    """
    For generating or reading coordinates of order
    """
    def __init__(self, choice='random', num=None, filename=None):
        if choice == 'random':
            self.ords = self.random_generate(num)
        else:
            self.ords = self.file_parse(filename)

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

    @staticmethod
    def random_generate(num):
        """
        Randomly generates 9 shop places and then specific number of Orders
        :param num: int (number of Orders)
        :return: list of Order objects
        """
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

        raf = []
        for i in range(num):
            posx = random.randint(1, 100)
            posy = random.randint(1, 100)

            shopx = 0
            shopy = 0

            dst = 1000
            for s in shops:
                if dst > math.sqrt((posx - s[0]) ** 2 + (posy - s[1]) ** 2):
                    shopx = s[0]
                    shopy = s[1]
                    dst = math.sqrt((posx - s[0]) ** 2 + (posy - s[1]) ** 2)

            price = random.randint(40, 55) * (dst // 10 + 12)
            tme = [random.randint(9, 13), random.randrange(0, 61, 5)]

            raf.append(Order([shopx, shopy], [posx, posy], price, tme, i))
        return raf


def greedy_algorithm3(ordr, work):
    received_orders = []
    for i in range(len(ordr)):
        maxi = 0
        obj = None
        for j in range(len(work)):
            if work[j].count(ordr[i]) > maxi and not work[j].end_work and work[j].time_count(
                    ordr[i]):  # Теперь мы учитываем и тех Курьеров, которые скоро могут выйти
                if not work[j].partner and not ordr[i].partner:
                    maxi = work[j].count(ordr[i])
                    obj = work[j]
                else:
                    if work[j].income < work[j].count(ordr[i]):
                        ordr = work[j].clear()
                        maxi = work[j].count(ordr[i])
                        obj = work[j]
                        received_ordeers.remove(ordr)  # Убираем заказ из списка принятых и продолжаем искать варианты
        if obj:
            ordr[i].update(obj)
            received_orders.append(ordr[i])  # Добавляем заказ в список принятых

    return received_orders

