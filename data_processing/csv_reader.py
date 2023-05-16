class CsvReader:
    CHAR_DELIMITER = "\t"

    def __init__(self, head_string: str):
        keys = head_string.split(self.CHAR_DELIMITER)

        try:
            self.__inn = keys.index("INN")
            self.__kpp = keys.index("KPP")
            self.__name_full = keys.index("NAMEP")
            self.__name_short = keys.index("NAMES")
            self.__status_id = keys.index("STATUS_LIQUIDATION_INNER_ID")
            self.__date_closed = keys.index("DATAPREKRUL")
            self.__okato = keys.index("OKATO")
            self.__region_name = keys.index("REGION_NAME")
        except ValueError:
            raise ValueError('В строке инициализации отсутствует один или несколько заголовков!')

        self.__start_indexes = []
        self.__end_indexes = []

    def read_line(self, line: str):
        self.__start_indexes[0] = 0
        founded = 0
        index_start = 0
        index = 0
        for c in line:
            if c == self.CHAR_DELIMITER:
                self.__start_indexes[founded] = index_start
                self.__end_indexes[founded] = index-1 if index > 0 else 0
                index_start = index + 1
                founded += 1
            index += 1
