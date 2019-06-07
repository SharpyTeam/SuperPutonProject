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

    def load_from_db(self, callback: Optional[Callable[[], None]]) -> NoReturn:
        self.db_wrapper.start()

        def loaded(companies: List[Company]):
            self.companies = {company.id: company for company in companies}
            if callback is not None:
                callback()

        self.db_wrapper.get_all_companies_names_async(loaded)
