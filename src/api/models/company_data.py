import numpy as np
import pandas

from .company import Company


class CompanyData:
    def __init__(self, company: Company, year: str, data_frame: pandas.DataFrame):
        self.company = company
        self.year = year
        self.data_frame = data_frame
        self.changed = False

    def __getitem__(self, key):
        return self.data_frame.iloc[key[0], key[1]]

    def __setitem__(self, key, value):
        if self.data_frame.iloc[key[0], key[1]] != value:
            self.data_frame.iloc[key[0], key[1]] = value
            self.changed = True

    def __iter__(self):
        self.index = -1
        return self

    def __next__(self):
        self.index += 1
        if self.index == self.data_frame.shape[0]:
            raise StopIteration
        return self.data_frame.index[self.index], np.asarray(self.data_frame.iloc[self.index])

    def copy(self):
        return CompanyData(self.company, self.year, self.data_frame.copy())

    def copy_for_commit(self):
        self.changed = False
        return self.copy()
