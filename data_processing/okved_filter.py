import json
from json import JSONDecodeError


class OkvedFilters:
    class OkvedFilter:
        def __init__(self, filter_id: int, name: str, unsorted_values: list[str]):
            self.id = filter_id
            self.name = name
            self.exact_values: list[str] = []
            self.mask_values: list[str] = []
            for it in unsorted_values:
                if it.endswith('.'):
                    self.mask_values.append(it)
                else:
                    self.exact_values.append(it)
            pass

        def apply_filter_to_first_element(self, okveds: list[str]) -> bool:
            print(f"Invoked filter ({self.id}) {self.name}:")
            print(f"\texact values = {self.exact_values}")
            print(f"\tmask values = {self.mask_values}")
            print(f"\tinput {type(okveds)} = {okveds}")
            okved = okveds[0]
            if okved in self.exact_values:
                return True
            for mask in self.mask_values:
                if okved.startswith(mask):
                    return True
            return False

        def apply_filter_to_list(self, okveds: list[str]) -> bool:
            print(f"Invoked filter ({self.id}) {self.name}:")
            print(f"\texact values = {self.exact_values}")
            print(f"\tmask values = {self.mask_values}")
            print(f"\tinput {type(okveds)} = {okveds}")
            for okved in okveds:
                if okved in self.exact_values:
                    return True
                for mask in self.mask_values:
                    if okved.startswith(mask):
                        return True
            return False

    def __init__(self, list_of_filters: list[OkvedFilter]):
        self.filters = list_of_filters

    @staticmethod
    def from_json_file(json_filename: str):
        with open(json_filename, mode="r", encoding="UTF-8") as json_file:
            try:
                json_data = json.loads(json_file.read())
            except JSONDecodeError:
                print("Wrong okved_filter.json format!")
                return None
        _filter_id = 0
        _filters: list[OkvedFilters.OkvedFilter] = []
        for each_filter in json_data:
            try:
                name = each_filter['name']
                filters_list = each_filter['list']
            except JSONDecodeError:
                print("Wrong okved_filter.json format!")
                return None
            new_filter = OkvedFilters.OkvedFilter(_filter_id, name, filters_list)
            _filter_id += 1
            _filters.append(new_filter)
        return OkvedFilters(_filters)

    # Returns a filter-function
    def get_filter_func(self, filter_id, only_main: bool):
        if only_main:
            return self.filters[filter_id].apply_filter_to_first_element
        else:
            return self.filters[filter_id].apply_filter_to_list

    def get_list(self) -> list[str]:
        result = []
        for it in self.filters:
            result.append(f'({it.id}) {it.name}')
        return result
