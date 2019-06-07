import pandas
from typing import List, Union


class CompanyData:
    def __init__(self, company, year: str, data: Union[pandas.DataFrame, List[List]] = None):
        self.company = company
        self.year = year
        self.data_frame = data if isinstance(data, pandas.DataFrame) else None

        if self.data_frame is None and data is not None:
            rows_indices = [data_row[0] for data_row in data]
            rows_list = [data_row[1:] for data_row in data]
            self.data_frame = pandas.DataFrame(rows_list, index=rows_indices)

    def __iter__(self):
        self.index = -1
        return self

    def __next__(self):
        self.index += 1
        if self.index == self.data_frame.shape[0]:
            raise StopIteration
        return self.data_frame.index[self.index], list(self.data_frame.iloc[self.index])

    def copy(self):
        return CompanyData(self.company, self.year, self.data_frame.copy())
