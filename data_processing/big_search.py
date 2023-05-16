import time

import globals
from data_processing.csv_actions import *
from data_processing.excel_export import create_excel
from data_processing.csv_reader import CsvReader
from utilities.time_prediction import TimePrediction
from utilities.strings_format import *
from data_processing.json_actions import parse_inn


def big_search(
        start_date,
        end_date,
        regions_to_use,
        input_file_name,
        input_encoding,
        output_csv_file,
        output_xlsx_file,
        char_delimiter,
        total_lines,
        func_callback_progress,
        func_callback_on_finish,
):
    STATUS_LIQUIDATION_ID = {
        51: "ЛИКВИДАЦИЯ ЮРИДИЧЕСКОГО ЛИЦА #301",
        42: "ЛИКВИДАЦИЯ ЮЛ #201",
        43: "ЛИКВИДАЦИЯ ЮРИДИЧЕСКОГО ЛИЦА #201",
        44: "ЛИКВИДИРОВАНО #201",
        84: "ЛИКВИДАЦИЯ ЮРИДИЧЕСКОГО ЛИЦА #314",
        85: "ЛИКВИДАЦИЯ ЮРИДИЧЕСКОГО ЛИЦА #320",
        152: "ЛИКВИДАЦИЯ ЮРИДИЧЕСКОГО ЛИЦА #313",
        138: "ЛИКВИДАЦИЯ ЮРИДИЧЕСКОГО ЛИЦА #414",
        139: "ИСКЛЮЧЕНИЕ ИЗ ЕГРЮЛ ЮРИДИЧЕСКОГО ЛИЦА В СВЯЗИ НАЛИЧИЕМ В ЕГРЮЛ СВЕДЕНИЙ О НЕМ,"
             " В ОТНОШЕНИИ КОТОРЫХ ВНЕСЕНА ЗАПИСЬ О НЕДОСТОВЕРНОСТИ #415",
        140: "ЛИКВИДАЦИЯ ЮРИДИЧЕСКОГО ЛИЦА #415",
        142: "ЛИКВИДАЦИЯ ЮРИДИЧЕСКОГО ЛИЦА #501",
    }

    # forbidden_grocery_names = ['НЕФТЕГАЗ', 'КЛИНИНГОВ', 'КОММУНАЛЬН', 'РЕМОНТН', 'ГЕОХИМ', 'ЮРИДИЧЕСК', 'СТРОИТЕЛЬН',
    #                            'ТЕПЛОСНАБ', 'ПРОИЗВОДСТВЕНН', 'ТЕХСТРОЙ', 'ЖИЛСТРОЙ', 'СИБСТРОЙ', 'СТРОЙСЕРВИС',
    #                            'ГАЗСТРОЙ',
    #                            'ПРОМТОРГ', 'САНТЕХ', 'ЖИЛСЕРВИС', 'ПРОМРЕСУРС', 'ПРОМБЕТОН', 'МЕДИЦИНСК',
    #                            'ТЕХКОМПЛЕКТ',
    #                            'СТРОЙМОНТАЖ', 'СНАБСЕРВИС', 'ДИАГНОСТ', 'ТРАНСПОРТ', 'ФАРМАЦЕВТ', 'ИНЖИНИРИНГ',
    #                            'ТУРИСТИЧ',
    #                            'МОНТАЖЭНЕРГО', 'ЭНЕРГОРЕМОНТ', 'ЭЛЕКТРОМОНТАЖ', 'ПРОМХОЗ', 'ЛЕССТРОЙ', 'КАДАСТР']

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

            head_line = r_file.readline()

            csvreader = CsvReader(head_line)

            new_line = r_file.readline()

            csvreader.read_line(new_line)

            file_reader = csv.DictReader(r_file, delimiter=char_delimiter)

            total_write = 0
            total_read = 0

            mp = TimePrediction(25)  # "Предсказатель" оставшегося времени выполнения по {arg} точкам
            digit_delimiter = "'"  # разделитель групп разрядов
            status_liquidations_ids = list(STATUS_LIQUIDATION_ID.keys())

            # Считывание данных из CSV файла
            for row in file_reader:
                total_read += 1

                # раз в --- шагов обновляем индикатор прогресса
                if (total_read % 10000) == 9999:
                    percentage = total_read / total_lines
                    mp.add_point(time.time(), percentage)
                    # invoke callback function on UI
                    func_callback_progress(percentage, mp.seek_time(), total_write)

                # ограничим количество строк для записи значением {limit_output}
                if total_write >= 65_535:
                    print(f'Достигнут предел количества искомых строк')
                    break
                if globals.globals_user_break:
                    print(f'Пользователь прервал поиск')
                    break

                x_name_long = row['NAMEP']
                x_date = row['DATAPREKRUL']
                x_region = row['REGION_NAME']
                x_kpp = row['KPP']
                x_okato = row['OKATO']
                x_inner_id_str = row['STATUS_LIQUIDATION_INNER_ID']
                try:
                    x_inner_id = int(x_inner_id_str)
                except (TypeError, ValueError):
                    print(x_inner_id_str)
                    continue

                if x_inner_id not in status_liquidations_ids:
                    continue

                if 'ОБЩЕСТВО' not in x_name_long.upper():
                    continue

                if not check_date(x_date, start_date, end_date):
                    continue

                flag_region, rating_regions = triple_check_region(region_name=x_region,
                                                                  regions_list=regions_to_use,
                                                                  kpp=x_kpp,
                                                                  okato=x_okato)
                if not flag_region:
                    continue

                x_inn = row['INN']
                x_name_short = row['NAMES']

                x_okved_list, x_okved_name = parse_inn(x_inn)
                if x_okved_list is None:
                    continue

                # the following sections works only if every check-up is passed
                x_reason = STATUS_LIQUIDATION_ID[x_inner_id]
                x_okved = x_okved_list[0]
                total_write += 1
                percentage = total_read / total_lines
                mp.add_point(time.time(), percentage)
                # invoke callback function on UI
                func_callback_progress(percentage, mp.seek_time(), total_write)

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

    print(f'Прочитано {total_read} {name_count_strings(total_read)},'
          f' найдено {total_write} {name_count_strings(total_write)}')
    print("Выгружаем результат в Excel...", end="")
    create_excel(output_csv_file, output_xlsx_file)
    print("- готово.")
    func_callback_on_finish()
