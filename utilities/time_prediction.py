"""
    Задача этого класса рассчитывать время до завершения процесса

    линейная аппроксимация по {dimension = 2..100} точкам

    точки в виде кортежей (время, процент выполнения)
        время = time.time()
        процент выполнения = 0.0 - 1.0 (дробное число от 0 до 1)
"""

import time


class TimePrediction:
    sequence = []
    MAX_DIMENSION = 100

    def __init__(self, level):
        if level > self.MAX_DIMENSION:
            level = self.MAX_DIMENSION
        elif level < 2:
            level = 2
        self.dimension = level  # количество точек для аппроксимации
        self.create_time = time.time()  # время создания объекта класса (для упрощения расчетов)

    def add_point(self, time_now, percentage):
        if len(self.sequence) >= self.dimension:
            del self.sequence[0]
        # на входе получаем системное время, но сохраняем только интервал времени от {self.create_time}
        # для упрощения вычислений
        self.sequence.append((time_now - self.create_time, percentage))

    def seek_time(self):
        sumx = 0
        sumy = 0
        sumxy = 0
        sumxx = 0

        n = len(self.sequence)
        if n < 2:
            return 0
        for point in self.sequence:
            sumx += point[0]
            sumy += point[1]
            sumxy += point[0] * point[1]
            sumxx += point[0] * point[0]

        a = (n * sumxy - sumx * sumy) / (n * sumxx - sumx * sumx)
        b = (sumy - a * sumx) / n

        finish_time = (1 - b) / a
        estimated_time = finish_time - self.sequence[-1][0]

        return estimated_time
