import json

import requests as requests
from requests.exceptions import HTTPError


# запрашиваем и парсим JSON по ссылке вида https://egrul.itsoft.ru/2466010203.json
# возвращаем три значения {причина ликвидации}, {КОД ОКВЭД}, {расшифровка ОКВЭДа}
# референс: https://habr.com/ru/post/650291/
def parse_inn(inn):
    #default values for expetions
    name_for_liquidation = "смотри выписку ЕГРЮЛ egrul.nalog.ru"
    code_for_okved = 0
    name_for_okved = "смотри выписку ЕГРЮЛ egrul.nalog.ru"

    if len(inn) != 10:
        print(f'Неверный формат ИНН: {inn}')
        return name_for_liquidation, code_for_okved, name_for_okved

    url_string = "https://egrul.itsoft.ru/{0}.json".format(inn)
    # print(f'     Trying to access {url_string}... ', end=' ')
    try:
        response = requests.get(url_string)
        # если ответ успешен, исключения задействованы не будут
        response.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')  # Python 3.6
        return name_for_liquidation, code_for_okved, name_for_okved
    except Exception as err:
        print(f'Other error occurred: {err}')  # Python 3.6
        return name_for_liquidation, code_for_okved, name_for_okved
    else:
        # print('Success!')
        pass

    json_data = json.loads(response.text)
    if json_data != False:
        if "СвЮЛ" in json_data:
            json_sv_ul = json_data["СвЮЛ"]
            if "СвПрекрЮЛ" in json_sv_ul:
                if "СпПрекрЮЛ" in json_sv_ul["СвПрекрЮЛ"]:
                    if "@attributes" in json_sv_ul["СвПрекрЮЛ"]["СпПрекрЮЛ"]:
                        if "НаимСпПрекрЮЛ" in json_sv_ul["СвПрекрЮЛ"]["СпПрекрЮЛ"]["@attributes"]:
                            name_for_liquidation = json_sv_ul["СвПрекрЮЛ"]["СпПрекрЮЛ"]["@attributes"]["НаимСпПрекрЮЛ"]

            if "СвОКВЭД" in json_sv_ul:
                if "СвОКВЭДОсн" in json_sv_ul["СвОКВЭД"]:
                    if "@attributes" in json_sv_ul["СвОКВЭД"]["СвОКВЭДОсн"]:
                        if "КодОКВЭД" in json_sv_ul["СвОКВЭД"]["СвОКВЭДОсн"]["@attributes"]:
                            code_for_okved = json_sv_ul["СвОКВЭД"]["СвОКВЭДОсн"]["@attributes"]["КодОКВЭД"]
                        if "НаимОКВЭД" in json_sv_ul["СвОКВЭД"]["СвОКВЭДОсн"]["@attributes"]:
                            name_for_okved = json_sv_ul["СвОКВЭД"]["СвОКВЭДОсн"]["@attributes"]["НаимОКВЭД"]

    return name_for_liquidation, code_for_okved, name_for_okved
