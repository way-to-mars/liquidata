import tkinter.scrolledtext
import time

import globals
from data_processing.csv_actions import *
from data_processing.excel_export import create_excel
from utilities.time_prediction import TimePrediction
from utilities.strings_format import *
from data_processing.json_actions import parse_inn
from view_model import Frame3


def big_search(
        parent_frame: Frame3,
        start_date,
        end_date,
        regions_to_use,
        input_file_name,
        input_encoding,
        output_csv_file,
        output_xlsx_file,
        char_delimiter,
        total_lines,
):
    necessary_part_of_name = 'ОБЩЕСТВО'
    forbidden_grocery_names = ['НЕФТЕГАЗ', 'КЛИНИНГОВ', 'КОММУНАЛЬН', 'РЕМОНТН', 'ГЕОХИМ', 'ЮРИДИЧЕСК', 'СТРОИТЕЛЬН',
                               'ТЕПЛОСНАБ', 'ПРОИЗВОДСТВЕНН', 'ТЕХСТРОЙ', 'ЖИЛСТРОЙ', 'СИБСТРОЙ', 'СТРОЙСЕРВИС',
                               'ГАЗСТРОЙ',
                               'ПРОМТОРГ', 'САНТЕХ', 'ЖИЛСЕРВИС', 'ПРОМРЕСУРС', 'ПРОМБЕТОН', 'МЕДИЦИНСК', 'ТЕХКОМПЛЕКТ',
                               'СТРОЙМОНТАЖ', 'СНАБСЕРВИС', 'ДИАГНОСТ', 'ТРАНСПОРТ', 'ФАРМАЦЕВТ', 'ИНЖИНИРИНГ',
                               'ТУРИСТИЧ',
                               'МОНТАЖЭНЕРГО', 'ЭНЕРГОРЕМОНТ', 'ЭЛЕКТРОМОНТАЖ', 'ПРОМХОЗ', 'ЛЕССТРОЙ', 'КАДАСТР']

    if len(regions_to_use) == 0:
        print("Ищем во всех регионах!")
    else:
        print(f"Ищем в следующих регионах:")
        for item in regions_to_use:
            print(f" • {item}")
    print(f"В диапазоне дат от {start_date} до {end_date}")

    with open(input_file_name, encoding=input_encoding) as r_file:
        with open(output_csv_file, mode="w", encoding='WINDOWS-1251') as w_file:
            fieldnames = ['ИНН', 'Дата прекращения', 'Код', 'Причина прекращения', 'Наименование (краткое)',
                          'Основной ОКВЭД', 'Расшифровка ОКВЭД']
            # write headers
            w_file.write(f"{char_delimiter.join(fieldnames)}\n")

            file_reader = csv.DictReader(r_file, delimiter=char_delimiter)

            total_write = 0
            total_read = 0

            mp = TimePrediction(25)  # "Предсказатель" оставшегося времени выполнения по {arg} точкам
            digit_delimiter = "'"  # разделитель групп разрядов

            # Считывание данных из CSV файла
            for row in file_reader:
                total_read += 1
                x_name_long = row['NAMEP']
                x_date = row['DATAPREKRUL']
                x_region = row['REGION_NAME']
                x_kpp = row['KPP']
                x_okato = row['OKATO']
                x_inner_id = row['STATUS_LIQUIDATION_INNER_ID']

                flag_date = check_date(x_date, start_date, end_date)
                flag_obshestvo = is_ooo(x_name_long, necessary_part_of_name)
                flag_region, rating_regions = triple_check_region(region_name=x_region,
                                                                  regions_list=regions_to_use,
                                                                  kpp=x_kpp,
                                                                  okato=x_okato)

                if flag_date & flag_obshestvo & flag_region:
                    if check_forbidden_names(x_name_long, forbidden_grocery_names):
                        print(f'[{total_read / total_lines:.2%}] Отклонено! Непрофильное название: {x_name_long}')
                    else:
                        total_write += 1
                        parent_frame.search_founded.delete(0, tkinter.END)
                        parent_frame.search_founded.insert(0, f"Найдено: {total_write}")
                        percentage = total_read / total_lines
                        parent_frame.search_progressbar.set(percentage)
                        mp.add_point(time.time(), percentage)
                        x_inn = row['INN']
                        x_name_short = row['NAMES']
                        x_reason, x_okved, x_okved_name = parse_inn(x_inn)
                        print(f'[{percentage:.1%}] {group_digits(total_write, digit_delimiter)}: ИНН {x_inn}\t'
                              f'{x_name_short}\tдата прекращения: {x_date}\tпричина: {x_reason}\n'
                              f'\t\tОКВЭД {x_okved} {x_okved_name}')

                        w_file.write(f'{x_inn}{char_delimiter}'
                                     f'{x_date}{char_delimiter}'
                                     f'{(int(x_inner_id), rating_regions)}{char_delimiter}'
                                     f'{x_reason}{char_delimiter}'
                                     f'{x_name_short}{char_delimiter}'
                                     f'{x_okved}{char_delimiter}'
                                     f'{x_okved_name}\n')

                # раз в --- шагов обновляем индикатор прогресса
                if (total_read % 10000) == 9999:
                    percentage = total_read / total_lines
                    parent_frame.search_progressbar.set(percentage)
                    mp.add_point(time.time(), percentage)
                    parent_frame.elapsed_time_text.configure(
                        text=f'{seconds_to_time_string(mp.seek_time())}')

                # self.break_button.event_generate("<<DoExcel>>", when="tail")

                # ограничим количество строк для записи значением {limit_output}
                if total_write >= 65_535:
                    print(f'Достигнут предел количества искомых строк')
                    break
                if globals.globals_user_break:
                    print(f'Пользователь прервал поиск')
                    break

    print(
        f'Прочитано {total_read} {name_count_strings(total_read)},'
        f' найдено {total_write} {name_count_strings(total_write)}')
    parent_frame.basement_frame.grid_forget()
    print("Выгружаем результат в Excel...", end="")
    create_excel(output_csv_file, output_xlsx_file)
    print("- готово.")
    parent_frame.search_text.configure(
        text=f'Программа завершила свою работу. В открывшемся окне Excel можно насладиться результатами )))')
