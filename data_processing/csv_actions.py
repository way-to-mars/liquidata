import csv
import datetime
import os

from globals import APP_DATA_DIR

NEEDED_COLUMNS = ['INN', 'NAMEP', 'NAMES', 'OKATO', 'KPP', 'STATUS_LIQUIDATION_INNER_ID', 'DATAPREKRUL', 'REGION_NAME']

REGIONS_DICTIONARY_INTERNAL = {
    'РЕСПУБЛИКА АДЫГЕЯ': ('01', '79', 'АДЫГЕЯ'),
    'РЕСПУБЛИКА БАШКОРТОСТАН': ('02', '80', 'БАШКОРТОСТАН'),
    'РЕСПУБЛИКА БУРЯТИЯ': ('03', '81', 'БУРЯТИЯ'),
    'РЕСПУБЛИКА АЛТАЙ': ('04', '84', 'АЛТАЙ'),
    'РЕСПУБЛИКА ДАГЕСТАН': ('05', '82', 'ДАГЕСТАН'),
    'РЕСПУБЛИКА ИНГУШЕТИЯ': ('06', '26', 'ИНГУШЕТИЯ'),
    'РЕСПУБЛИКА КАБАРДИНО-БАЛКАРИЯ': ('07', '83', 'КАБАРДИНО-БАЛКАР'),
    'РЕСПУБЛИКА КАЛМЫКИЯ': ('08', '85', 'КАЛМЫКИЯ'),
    'КАРАЧАЕВО-ЧЕРКЕССКАЯ РЕСПУБЛИКА': ('09', '91', 'КАРАЧАЕВО-ЧЕРКЕССКАЯ'),
    'РЕСПУБЛИКА КАРЕЛИЯ': ('10', '86', 'КАРЕЛИЯ'),
    'РЕСПУБЛИКА КОМИ': ('11', '87', 'КОМИ'),
    'РЕСПУБЛИКА МАРИЙ ЭЛ': ('12', '88', 'МАРИЙ'),
    'РЕСПУБЛИКА МОРДОВИЯ': ('13', '89', 'МОРДОВИЯ'),
    'РЕСПУБЛИКА САХА (ЯКУТИЯ)': ('14', '98', 'САХА'),
    'РЕСПУБЛИКА СЕВЕРНАЯ ОСЕТИЯ-АЛАНИЯ': ('15', '90', 'ОСЕТИЯ-АЛАНИЯ'),
    'РЕСПУБЛИКА ТАТАРСТАН': ('16', '92', 'ТАТАРСТАН'),
    'РЕСПУБЛИКА ТЫВА': ('17', '93', 'ТЫВА'),
    'УДМУРТСКАЯ РЕСПУБЛИКА': ('18', '94', 'УДМУРТСКАЯ'),
    'РЕСПУБЛИКА ХАКАСИЯ': ('19', '95', 'ХАКАСИЯ'),
    'ЧЕЧЕНСКАЯ РЕСПУБЛИКА': ('20', '96', 'ЧЕЧЕНСКАЯ'),
    'ЧУВАШСКАЯ РЕСПУБЛИКА': ('21', '97', 'ЧУВАШСКАЯ'),
    'АЛТАЙСКИЙ КРАЙ': ('22', '01', 'АЛТАЙСКИЙ'),
    'КРАСНОДАРСКИЙ КРАЙ': ('23', '03', 'КРАСНОДАРСКИЙ'),
    'КРАСНОЯРСКИЙ КРАЙ': ('24', '04', 'КРАСНОЯРСКИЙ'),
    'ПРИМОРСКИЙ КРАЙ': ('25', '05', 'ПРИМОРСКИЙ'),
    'СТАВРОПОЛЬСКИЙ КРАЙ': ('26', '07', 'СТАВРОПОЛЬСКИЙ'),
    'ХАБАРОВСКИЙ КРАЙ': ('27', '08', 'ХАБАРОВСКИЙ'),
    'АМУРСКАЯ ОБЛАСТЬ': ('28', '10', 'АМУРСКАЯ'),
    'АРХАНГЕЛЬСКАЯ ОБЛАСТЬ И НЕНЕЦКИЙ АВТОНОМНЫЙ ОКРУГ': ('29', '11', 'АРХАНГЕЛЬСКАЯ'),
    'АСТРАХАНСКАЯ ОБЛАСТЬ': ('30', '12', 'АСТРАХАНСКАЯ'),
    'БЕЛГОРОДСКАЯ ОБЛАСТЬ': ('31', '14', 'БЕЛГОРОДСКАЯ'),
    'БРЯНСКАЯ ОБЛАСТЬ': ('32', '15', 'БРЯНСКАЯ'),
    'ВЛАДИМИРСКАЯ ОБЛАСТЬ': ('33', '17', 'ВЛАДИМИРСКАЯ'),
    'ВОЛГОГРАДСКАЯ ОБЛАСТЬ': ('34', '18', 'ВОЛГОГРАДСКАЯ'),
    'ВОЛОГОДСКАЯ ОБЛАСТЬ': ('35', '19', 'ВОЛОГОДСКАЯ'),
    'ВОРОНЕЖСКАЯ ОБЛАСТЬ': ('36', '20', 'ВОРОНЕЖСКАЯ'),
    'ИВАНОВСКАЯ ОБЛАСТЬ': ('37', '24', 'ИВАНОВСКАЯ'),
    'ИРКУТСКАЯ ОБЛАСТЬ': ('38', '25', 'ИРКУТСКАЯ'),
    'КАЛИНИНГРАДСКАЯ ОБЛАСТЬ': ('39', '27', 'КАЛИНИГРАДСКАЯ'),
    'КАЛУЖСКАЯ ОБЛАСТЬ': ('40', '29', 'КАЛУЖСКАЯ'),
    'КАМЧАТСКИЙ КРАЙ': ('41', '30', 'КАМЧАТСКИЙ'),
    'КЕМЕРОВСКАЯ ОБЛАСТЬ': ('42', '32', 'КЕМЕРОВСКАЯ'),
    'КИРОВСКАЯ ОБЛАСТЬ': ('43', '33', 'КИРОВСКАЯ'),
    'КОСТРОМСКАЯ ОБЛАСТЬ': ('44', '34', 'КОСТРОМСКАЯ'),
    'КУРГАНСКАЯ ОБЛАСТЬ': ('45', '37', 'КУРГАНСКАЯ'),
    'КУРСКАЯ ОБЛАСТЬ': ('46', '38', 'КУРСКАЯ'),
    'ЛЕНИНГРАДСКАЯ ОБЛАСТЬ': ('47', '41', 'ЛЕНИНГРАДСКАЯ'),
    'ЛИПЕЦКАЯ ОБЛАСТЬ': ('48', '42', 'ЛИПЕЦКАЯ'),
    'МАГАДАНСКАЯ ОБЛАСТЬ': ('49', '44', 'МАГАДНСКАЯ'),
    'МОСКОВСКАЯ ОБЛАСТЬ': ('50', '46', 'МОСКОВСКАЯ'),
    'МУРМАНСКАЯ ОБЛАСТЬ ': ('51', '47', 'МУРМАНСКАЯ'),
    'НИЖЕГОРОДСКАЯ ОБЛАСТЬ': ('52', '22', 'НИЖЕГОРОДСКАЯ'),
    'НОВГОРОДСКАЯ ОБЛАСТЬ': ('53', '49', 'НОВГОРОДСКАЯ'),
    'НОВОСИБИРСКАЯ ОБЛАСТЬ': ('54', '50', 'НОВОСИБИРСКАЯ'),
    'ОМСКАЯ ОБЛАСТЬ': ('55', '52', 'ОМСКАЯ'),
    'ОРЕНБУРГСКАЯ ОБЛАСТЬ': ('56', '53', 'ОРЕНБУРГСКАЯ'),
    'ОРЛОВСКАЯ ОБЛАСТЬ': ('57', '54', 'ОРЛОВСКАЯ'),
    'ПЕНЗЕНСКАЯ ОБЛАСТЬ': ('58', '56', 'ПЕНЗЕНСКАЯ'),
    'ПЕРМСКИЙ КРАЙ': ('59', '57', 'ПЕРМСКИЙ'),
    'ПСКОВСКАЯ ОБЛАСТЬ': ('60', '58', 'ПСКОВСКАЯ'),
    'РОСТОВСКАЯ ОБЛАСТЬ': ('61', '60', 'РОСТОВСКАЯ'),
    'РЯЗАНСКАЯ ОБЛАСТЬ': ('62', '61', 'РЯЗАНСКАЯ'),
    'САМАРСКАЯ ОБЛАСТЬ': ('63', '36', 'САМАРСКАЯ'),
    'САРАТОВСКАЯ ОБЛАСТЬ': ('64', '63', 'САРАТОВСКАЯ'),
    'САХАЛИНСКАЯ ОБЛАСТЬ': ('65', '64', 'САХАЛИНСКАЯ'),
    'СВЕРДЛОВСКАЯ ОБЛАСТЬ': ('66', '65', 'СВЕРДЛОВСКАЯ'),
    'СМОЛЕНСКАЯ ОБЛАСТЬ': ('67', '66', 'СМОЛЕНСКАЯ'),
    'ТАМБОВСКАЯ ОБЛАСТЬ': ('68', '68', 'ТАМБОВСКАЯ'),
    'ТВЕРСКАЯ ОБЛАСТЬ': ('69', '28', 'ТВЕРСКАЯ'),
    'ТОМСКАЯ ОБЛАСТЬ': ('70', '69', 'ТОМСКАЯ'),
    'ТУЛЬСКАЯ ОБЛАСТЬ': ('71', '70', 'ТУЛЬСКАЯ'),
    'ТЮМЕНСКАЯ ОБЛАСТЬ': ('72', '71', 'ТЮМЕНСКАЯ'),
    'УЛЬЯНОВСКАЯ ОБЛАСТЬ': ('73', '73', 'УЛЬЯНОВСКАЯ'),
    'ЧЕЛЯБИНСКАЯ ОБЛАСТЬ': ('74', '75', 'ЧЕЛЯБИНСКАЯ'),
    'ЗАБАЙКАЛЬСКИЙ КРАЙ': ('75', '76', 'ЗАБАЙКАЛЬСКИЙ'),
    'ЯРОСЛАВСКАЯ ОБЛАСТЬ': ('76', '78', 'ЯРОСЛАВСКАЯ'),
    'Г. МОСКВА': ('77', '45', 'МОСКВА'),
    'Г. САНКТ-ПЕТЕРБУРГ': ('78', '40', 'САНКТ-ПЕТЕРБУРГ'),
    'ЕВРЕЙСКАЯ АВТОНОМНАЯ ОБЛАСТЬ': ('79', '99', 'ЕВРЕЙСКАЯ'),
    'ЧУКОТСКИЙ АВТОНОМНЫЙ ОКРУГ': ('87', '77', 'ЧУКОТСКИЙ'),
    'РЕСПУБЛИКА КРЫМ': ('91', '35', 'КРЫМ'),
    'Г.СЕВАСТОПОЛЬ': ('92', '67', 'СЕВАСТОПОЛЬ')
}

regions_dictionary = {}


# Проверяем, что дата "прекращения" существует и её значение от {date_min} до {date_max}
def check_date(date_in, date_min, date_max):
    if len(date_in) == 0:
        return False
    date = datetime.datetime.strptime(date_in, '%d.%m.%Y').date()
    if date_min <= date <= date_max:
        return True
    return False


# Если имя {name} содержит в себе запрещенный фрагмент {forbidden_list} то возвращаем False
def check_forbidden_names(name, forbidden_list):
    upper_fname = str.upper(name)
    for f in forbidden_list:
        if f in upper_fname:
            return True
    return False


# Проверка региона
# Если аргумент {name} содержит один из ключевых фрагментов {regions_list}, то возвращаем True
def check_region(name, regions_list):
    upper_name = str.upper(name)
    if len(regions_list) == 0:  # для пустого фильтра вернем true
        return True
    for r in regions_list:
        if r in upper_name:
            return True
    return False


# Проверка региона
# Если список {region_list} пустой, то возвращаем (True, 0)
#
# Вычисляем рейтинг соответствия (в случае успеха от 0 до 3)
def triple_check_region(region_name, regions_list, kpp="", okato=""):
    if regions_list is None:
        return True, -1
    if len(regions_list) == 0:  # для пустого фильтра вернем true
        return True, 0

    upper_name = str.upper(region_name)
    # check if somehow this dictionary (map) is empty
    if not regions_dictionary:
        load_regions_data()
    rating = 0
    for region in regions_list:
        dict_rec = regions_dictionary[region]
        if dict_rec is None:
            print(f'Ошибка наименования региона. "{region}" отсутствует в справочнике регионов')
            return False, -2

        if kpp.startswith(dict_rec[0]):
            rating += 1

        if okato.startswith(dict_rec[1]):
            rating += 1

        short_name_upper = str.upper(dict_rec[2])
        for each_word in upper_name.split():
            if each_word == short_name_upper:
                rating += 1
                break

        if rating > 0:
            return True, rating

    return False, -3


# проверяем, что {name} содержит в себе {necessary_part} == 'ОБЩЕСТВО'
def is_ooo(name, necessary_part):
    if necessary_part in name:
        return True
    return False


# проверяем наличие нужных csv-заголовков
def check_headers(filename_input, code_table, char_delimiter):
    try:
        with open(filename_input, encoding=code_table) as r_file:
            file_reader = csv.DictReader(r_file, delimiter=char_delimiter)
            titles = file_reader.fieldnames
            test = True
            for each in NEEDED_COLUMNS:
                if each not in titles:
                    test = False
            if not test:
                return False, "Не содержит необходимые заголовки csv"
            return True, "Всё ок!"
    except OSError:
        return False, "Неверный формат файла (не .csv или не windows-1251)"


# загружает из csv-базы данные в глобальный словарь {regions_dictionary}
def load_regions_data() -> dict:
    regions_file_name = ""
    result = {}
    try:
        regions_file_name = os.path.join(APP_DATA_DIR, "region_code.csv")

        with open(regions_file_name, encoding="WINDOWS-1251") as r_file:
            if r_file is None:
                return result  # void dict
            file_reader = csv.DictReader(r_file, delimiter='\t')
            if file_reader is None:
                return result  # void dict

            for row in file_reader:
                full_name = str.upper(row['Регион'])
                short_name = str.upper(row['Короткое Имя'])
                kpp_value = row['КПП']
                okato_value = row['ОКАТО']
                result[full_name] = (kpp_value, okato_value, short_name)
    except OSError:
        print(f"Ошибка при открытии базы регионов. Проверьте правильность пути и имени файла:\n"
              f"\t{regions_file_name}")
    return result


# выгружает словарь {regions_dictionary} в текстовый файл
def export_default_regions():
    regions_file_name = ""
    try:
        regions_file_name = os.path.join(APP_DATA_DIR, "region_code.txt")

        with open(regions_file_name, mode="w", encoding="WINDOWS-1251") as w_file:
            for i in REGIONS_DICTIONARY_INTERNAL:
                w_file.write(f"'{i}' : {REGIONS_DICTIONARY_INTERNAL[i]},\n")
                print(f"[{i}] : {REGIONS_DICTIONARY_INTERNAL[i]}")
    except OSError:
        print(f"Ошибка при создании файла списка регионов. Проверьте правильность пути и имени файла:\n"
              f"\t{regions_file_name}")
        return


'''
    initialize global variable "regions_dictionary" either with:
        * a data from "region_code.csv" if load_from_file = True
    or with:
        * the hardcoded dict REGIONS_DICTIONARY_INTERNAL by creatings its copy
    returns a list of all all_regions (key of dict)    
'''


def init_regions_and_get_list(load_from_file: bool) -> list[str]:
    global regions_dictionary
    regions_dictionary = load_regions_data() if load_from_file else REGIONS_DICTIONARY_INTERNAL.copy()
    return list(regions_dictionary.keys())
