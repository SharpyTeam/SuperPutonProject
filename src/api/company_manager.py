import numpy
from typing import Tuple, List, NoReturn, Optional, Callable

from .models.company import Company
from .db import DBWrapper


class CompanyManager:
    def __init__(self, db_wrapper: Optional[DBWrapper]):
        self.companies = {}
        self.db_wrapper = db_wrapper

    def get_company(self, company_id) -> Optional[Company]:
        return self.companies[company_id] if company_id in self.companies else None

    def get_companies(self, ids: Tuple = None) -> List[Company]:
        if ids is not None:
            return [self.companies[c_id] for c_id in ids if c_id in self.companies]
        else:
            return list(self.companies.values())

    def get_company_diagram_for_periods(self, column: int, company_id: int, periods: Optional[List[str]] = None):
        if periods is None:
            periods = self.db_wrapper.get_all_periods()
        company = self.get_company(company_id)
        return [company.get_period_data_summed(period)[column] for period in periods
                if company.get_period_data_summed(period) is not None]

    def get_companies_diagram_for_period(self, column, period: str, companies_ids: Optional[List[str]] = None):
        companies = self.get_companies(companies_ids)
        return [company.get_period_data_summed(period)[column] for company in companies
                if company.get_period_data_summed(period) is not None]

    def get_company_standard_deviation_for_periods(self, column: int, company_id: int, periods: Optional[List[str]] = None):
        return list(numpy.std(self.get_company_diagram_for_periods(column, company_id, periods)))

    def get_companies_standard_deviation_for_period(self, column, period: str, companies_ids: Optional[List[str]] = None):
        return list(numpy.std(self.get_companies_diagram_for_period(column, period, companies_ids)))

    def load_from_db(self, callback: Optional[Callable[[], None]]) -> NoReturn:
        self.db_wrapper.start()

        def loaded(companies: List[Company]):
            self.companies = {company.id: company for company in companies}
            if callback is not None:
                callback()

        self.db_wrapper.get_all_companies_names_async(loaded)
