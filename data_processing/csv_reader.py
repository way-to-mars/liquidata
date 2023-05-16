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
            raise ValueError(f'Missing some necessary keys in {head_string}')

        self.__size = len(keys)
        self.__start_indexes: list[int] = [0] * self.__size
        self.__end_indexes: list[int] = [0] * self.__size
        self.__str_ptr: str = head_string

    def read_line(self, line: str) -> bool:
        self.__str_ptr = line
        founded = 0
        index_start = 0
        index = 0
        for c in line:
            if c == self.CHAR_DELIMITER:
                self.__start_indexes[founded] = index_start
                self.__end_indexes[founded] = index
                index_start = index + 1
                founded += 1
                if founded >= self.__size:
                    print(f"Too many elements in {str}")
                    return False
            index += 1

        # when EOL is reached (actually there's no \n in our line) add a last element
        if founded is not self.__size - 1:
            print(f"Not enough elements in {str}")
            return False
        self.__start_indexes[founded] = index_start
        self.__end_indexes[founded] = len(line)
        return True

    def get_all(self):
        result = []
        for i in range(0, self.__size):
            result.append(self.__get_by_index(i))
        return result

    def __get_by_index(self, index: int):
        return self.__str_ptr[self.__start_indexes[index]: self.__end_indexes[index]]

    def inn(self):
        return self.__get_by_index(self.__inn)

    def kpp(self):
        return self.__get_by_index(self.__kpp)

    def name_full(self):
        return self.__get_by_index(self.__name_full)

    def name_short(self):
        return self.__get_by_index(self.__name_short)

    def status_id(self) -> int:
        try:
            return int(self.__get_by_index(self.__status_id))
        except ValueError:
            return 0

    def date_closed(self):
        return self.__get_by_index(self.__date_closed)

    def okato(self):
        return self.__get_by_index(self.__okato)

    def region_name(self):
        return self.__get_by_index(self.__region_name)


if __name__ == "__main__":
    str1 = "INN\tOGRN\tKPP\tNAMEP\tNAMES\tSTATUS_LIQUIDATION_INNER_ID\tDTSTART\tDATAPREKRUL\tOKATO\t" \
           "INDEKS\tREGION_NAME\tRAION_NAME\tGOROD_NAME\tNASPUNKT_NAME\tSTREET_NAME\tDOM\tKORP\tKVART"

    reader = CsvReader(str1)
    reader.read_line(str1)
    inn = reader.inn()
    kpp = reader.kpp()
    idd = reader.status_id()

    pass
