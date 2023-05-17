class CsvReader:
    CHAR_DELIMITER = "\t"

    def __init__(self,
                 index_inn: int,
                 index_kpp: int,
                 index_name_full: int,
                 index_name_short: int,
                 index_status_id: int,
                 index_date_closed: int,
                 index_okato: int,
                 index_region_name: int,
                 key_list_size: int,
                 ):
        self.__inn = index_inn
        self.__kpp = index_kpp
        self.__name_full = index_name_full
        self.__name_short = index_name_short
        self.__status_id = index_status_id
        self.__date_closed = index_date_closed
        self.__okato = index_okato
        self.__region_name = index_region_name

        self.__size = key_list_size
        self.__start_indexes: list[int] = [0] * self.__size
        self.__end_indexes: list[int] = [0] * self.__size
        self.__str_ptr: str = ''

    # this is a fabric method to create an object from csv-string containing headers
    @staticmethod
    def from_str(line: str):
        keys = line.split(CsvReader.CHAR_DELIMITER)
        try:
            _inn = keys.index("INN")
            _kpp = keys.index("KPP")
            _name_full = keys.index("NAMEP")
            _name_short = keys.index("NAMES")
            _status_id = keys.index("STATUS_LIQUIDATION_INNER_ID")
            _date_closed = keys.index("DATAPREKRUL")
            _okato = keys.index("OKATO")
            _region_name = keys.index("REGION_NAME")
        except ValueError:
            return None

        return CsvReader(
            index_inn=_inn,
            index_kpp=_kpp,
            index_okato=_okato,
            index_name_full=_name_full,
            index_name_short=_name_short,
            index_region_name=_region_name,
            index_status_id=_status_id,
            index_date_closed=_date_closed,
            key_list_size=len(keys),
        )

    # returns True only if {line} has exactly {self.__size} substrings
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

    reader = CsvReader.from_str(str1)
    reader.read_line(str1)
    inn = reader.inn()
    kpp = reader.kpp()
    idd = reader.status_id()


