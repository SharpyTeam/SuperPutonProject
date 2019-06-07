from api.config import RuntimeConfig
from typing import Tuple, Optional
from .company_data import CompanyData


class Company:
    def __init__(self, id, name, linked_db=None):
        self.id = id
        self.name = name
        self.data = {}  # year-CompanyData pairs
        self.linked_db = linked_db

    def get_period_data(self, year: str) -> Optional[CompanyData]:
        if year in self.data:
            return self.data[year]
        self.linked_db.get_company_data(self, year)
        try:
            return self.data[year]
        except KeyError:
            return None

    def get_period_data_summed(self, year: str) -> Optional[Tuple]:
        period = self.get_period_data(year)
        if period is None:
            return None
        summed = []
        for index in RuntimeConfig.rows_indices_to_sum:
            data_row = list(period.data_frame.loc[index])
            if len(summed) == 0:
                summed = data_row
            for i in range(len(summed)):
                summed[i] += data_row[i]
        return tuple(summed) if len(summed) > 0 else None
