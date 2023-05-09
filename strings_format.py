import tkinter

"""
example_minutes_one_digit = {
    'минут',  # 0
    'минута',  # 1
    'минуты',  # 2
    'минуты',  # 3
    'минуты',  # 4
    'минут',  # 5
    'минут',  # 6
    'минут',  # 7
    'минут',  # 8
    'минут'  # 0
}
example_minutes_teen_digits = {
    'минут',  # 10
    'минут',  # 11
    'минут',  # 12
    'минут',  # 13
    'минут',  # 14
    'минут',  # 15
    'минут',  # 17
    'минут',  # 18
    'минут'  # 19
}  ### определяем правильный падеж к заданному числу
"""
def name_of_count(input_x, like_5_minut, like_1_minuta, like_2_minutiy):
    x = abs(input_x)

    # смотрим на первые две (младшие) цифры числа, с 5 по 20 написание одинаковое
    first_2_digits = x % 100
    if 5 <= first_2_digits <= 20:
        return like_5_minut

    # в остальных случая падеж записит только от первой (младшей) цифры числа
    first_1_digit = first_2_digits % 10
    if first_1_digit == 0 or first_1_digit >= 5:
        return like_5_minut
    if first_1_digit == 1:
        return like_1_minuta
    return like_2_minutiy

def name_count_hours(x):
    return name_of_count(input_x=x, like_5_minut="часов", like_2_minutiy="часа", like_1_minuta="час")

def name_count_minutes(x):
    return name_of_count(input_x=x, like_5_minut="минут", like_2_minutiy="минуты", like_1_minuta="минута")

def name_count_seconds(x):
    return name_of_count(input_x=x, like_5_minut="секунд", like_2_minutiy="секунды", like_1_minuta="секунда")

def name_count_strings(x):
    return name_of_count(input_x=x, like_5_minut="строк", like_2_minutiy="строки", like_1_minuta="строка")

"""
    list1 - список строк в ВЕРХНЕМ регистре
    string_list - строка из слов, разделенных пробелами

    Добавляем в {list1} неповторные слова из строки {string_list}, приводя их в КАПС-вид
"""
def combine_lists(list1, string_list):
    list1.clear()
    list2 = string_list.split()
    for item in list2:
        item_upper = item.upper()
        if item_upper not in list1:
            if len(item_upper) > 0:
                list1.append(item_upper)
    return list1


def group_digits(number_string, char_delimiter=' '):
    result = '{0:,}'.format(number_string).replace(',', char_delimiter)
    return result


def seconds_to_timestr(sec):
    minutes, seconds = divmod(sec, 60)

    if minutes < 60:
        return f'{minutes: .0f} {name_count_minutes(minutes)}, {seconds: .0f} {name_count_seconds(seconds)}'
    else:
        hours, minutes = divmod(minutes, 60)
        return f'{hours: .0f} {name_count_hours(hours)} {minutes: .0f} {name_count_minutes(minutes)}, {seconds: .0f} {name_count_seconds(seconds)}'


class RedirectText(object):
    def __init__(self, text_ctrl):
        """Constructor"""
        self.output = text_ctrl

    def write(self, string):
        """"""
        self.output.insert(tkinter.END, string)
        self.output.see("end")

    def flush(self):
        pass
