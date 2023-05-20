import json
import time

import requests as requests
from requests.exceptions import HTTPError


# запрашиваем и парсим JSON по ссылке вида https://egrul.itsoft.ru/2466010203.json
# возвращаем три значения {причина ликвидации}, {КОД ОКВЭД}, {расшифровка ОКВЭДа}
# референс: https://habr.com/ru/post/650291/
def parse_inn(inn):
    default_result = (None, None)

    if len(inn) != 10:
        print(f'Неверный формат ИНН: {inn}')
        return default_result

    url_string = "https://egrul.itsoft.ru/{0}.json".format(inn)
    print(f"Загружаем данные из {url_string}", end="")
    start_time = time.time_ns()
    try:
        response = requests.get(url_string)
        response.raise_for_status()  # если ответ успешен, исключения задействованы не будут
    except HTTPError as http_err:
        print(f' HTTP error occurred: {http_err}')  # Python 3.6
        return default_result
    except Exception as err:
        print(f' Other error occurred: {err}')  # Python 3.6
        return default_result
    response_time = int((time.time_ns() - start_time) / 1_000_000)  # convert ns to ms
    print(f" ✔{response_time}мс", end="")

    json_data = json.loads(response.text)

    okved_list = get_okved_list(json_data)
    name_for_main_okved = get_or_default(json_data,
                                         ["СвЮЛ", "СвОКВЭД", "СвОКВЭДОсн", "@attributes", "НаимОКВЭД"],
                                         "нет данных")
    return okved_list, name_for_main_okved


def get_okved_list(json_data):
    result = []
    okved = get_or_default(json_data, ["СвЮЛ", "СвОКВЭД", "СвОКВЭДОсн", "@attributes", "КодОКВЭД"], None)

    if okved is None:  # there must be the main okved
        return None
    result.append(okved)

    okved_list = get_or_default(json_data, ["СвЮЛ", "СвОКВЭД", "СвОКВЭДДоп"], None)
    if okved_list is None:
        return None

    for json_block in okved_list:
        okved = get_or_default(json_block, ["@attributes", "КодОКВЭД"], None)
        if okved is not None:
            result.append(okved)

    return result


def get_or_default(json_data, path: list[str], default=None):
    try:
        for item in path:
            json_data = json_data[item]
        return json_data
    except (KeyError, TypeError, IndexError):
        return default
