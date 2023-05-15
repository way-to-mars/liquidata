import json
from json import JSONDecodeError

from globals import APP_DATA_DIR
from os.path import join


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

        def apply_filter(self, okved: str) -> bool:
            if okved in self.exact_values:
                return True
            for it in self.mask_values:
                if okved.startswith(it):
                    return True
            return False

    def __init__(self, json_filename: str):
        self.filters: list[OkvedFilters.OkvedFilter] = []

        with open(json_filename, mode="r", encoding="UTF-8") as json_file:
            try:
                json_data = json.loads(json_file.read())
            except JSONDecodeError:
                print("Wrong okved_filer.json format!")
                return
        filter_id = 0
        for each_filter in json_data:
            try:
                name = each_filter['name']
                filters_list = each_filter['list']
            except JSONDecodeError:
                print("Wrong okved_filer.json format!")
                return
            new_filter = OkvedFilters.OkvedFilter(filter_id, name, filters_list)
            filter_id += 1
            self.filters.append(new_filter)

    def get_filter_func(self, filter_id):
        # id = 0..infinity
        return self.filters[filter_id].apply_filter

    def get_list(self) -> list[str]:
        result = []
        for it in self.filters:
            result.append(it.name)
        return result

    


if __name__ == "__main__":
    fullname = join(APP_DATA_DIR, "okved_filter.json")
    filters = OkvedFilters(fullname)

    print(filters.get_list())
