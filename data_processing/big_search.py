import time

import globals
from data_processing.csv_actions import *
from data_processing.excel_export import create_excel
from data_processing.csv_reader import CsvReader
from data_processing.okved_filter import OkvedFilters
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
    status_liquidation_id_dict = {
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

    if len(regions_to_use) == 0:
        print("Ищем во всех регионах!")
    else:
        print(f"Ищем в следующих регионах:")
        for item in regions_to_use:
            print(f" • {item}")
    print(f"В диапазоне дат от {start_date} до {end_date}")

    with open(input_file_name, encoding=input_encoding) as r_file:
        with open(output_csv_file, mode="w", encoding='WINDOWS-1251') as w_file:
            fieldnames = ['ИНН', 'Дата прекращения', 'Код', 'Причина прекращения', 'Наименование',
                          'Основной ОКВЭД', 'Расшифровка ОКВЭД']
            # write headers
            w_file.write(f"{char_delimiter.join(fieldnames)}\n")

            head_line = r_file.readline()
            csv_reader = CsvReader.from_str(head_line)
            okved_filters = OkvedFilters.from_json_file(os.path.join(APP_DATA_DIR, "okved_filter.json"))
            if csv_reader is None or okved_filters is None:
                func_callback_on_finish(False)

            total_write = 0
            total_read = 0

            mp = TimePrediction(25)  # "Предсказатель" оставшегося времени выполнения по {arg} точкам
            digit_delimiter = "'"  # разделитель групп разрядов
            status_liquidations_ids = list(status_liquidation_id_dict.keys())

            filter_func = okved_filters.get_filter_func(2, False)

            for line in r_file:
                total_read += 1

                # раз в --- шагов обновляем индикатор прогресса
                if (total_read % 10_000) == 9_999:
                    percentage = total_read / total_lines
                    mp.add_point(time.time(), percentage)
                    # invoke callback function on UI
                    func_callback_progress(percentage, mp.seek_time(), total_write)

                # xls table has a limit of 65536 lines
                if total_write >= 65_530:
                    print(f'Достигнут предел количества искомых строк')
                    break
                if globals.globals_user_break:
                    print(f'Пользователь прервал поиск')
                    break

                # trying to read elements from a line
                if not csv_reader.read_line(line):
                    continue

                # check the STATUS_LIQUIDATION_INNER_ID at first because it is a light-weight integer
                line_id = csv_reader.status_id()
                if line_id not in status_liquidations_ids:
                    continue

                line_name_full = csv_reader.name_full()
                if 'ОБЩЕСТВО' not in line_name_full.upper():
                    continue

                line_date = csv_reader.date_closed()
                if not check_date(line_date, start_date, end_date):
                    continue

                line_region = csv_reader.region_name()
                line_kpp = csv_reader.kpp()
                line_okato = csv_reader.okato()

                flag_region, _ = triple_check_region(region_name=line_region,
                                                     regions_list=regions_to_use,
                                                     kpp=line_kpp,
                                                     okato=line_okato)
                if not flag_region:
                    continue

                line_inn = csv_reader.inn()

                # fetching a list of okved codes: ["Основной Оквэд", "Доп1", "Доп2", ...]
                line_okved_list, line_main_okved_name = parse_inn(line_inn)
                if line_okved_list is None:
                    continue

                # comparing okved codes
                if not filter_func(line_okved_list):
                    continue

                # the following sections works only if every check-up is passed
                line_name_short = csv_reader.name_short()
                if len(line_name_short) == 0:
                    line_name_short = line_name_full  # some firms have no short name
                line_reason = status_liquidation_id_dict[line_id]
                line_main_okved = line_okved_list[0]

                total_write += 1
                percentage = total_read / total_lines
                mp.add_point(time.time(), percentage)
                # invoke callback function on UI
                func_callback_progress(percentage, mp.seek_time(), total_write)

                print(f'[{percentage:.1%}] {group_digits(total_write, digit_delimiter)}: ИНН {line_inn}\t'
                      f'{line_name_short}\tдата прекращения: {line_date}\tпричина: {line_reason}\n'
                      f'\t\tОКВЭД {line_main_okved} {line_main_okved_name}')

                w_file.write(f'{line_inn}{char_delimiter}'
                             f'{line_date}{char_delimiter}'
                             f'{line_reason}{char_delimiter}'
                             f'{line_name_short}{char_delimiter}'
                             f'{line_main_okved} - {line_main_okved_name}{char_delimiter}'
                             f'{" ".join(line_okved_list[1:])}\n')  # put all the elements except 1st to a string

    print(f'Прочитано {total_read} {name_count_strings(total_read)},'
          f' найдено {total_write} {name_count_strings(total_write)}')
    print("Выгружаем результат в Excel...", end="")
    create_excel(output_csv_file, output_xlsx_file)
    print("- готово.")
    func_callback_on_finish(True)
