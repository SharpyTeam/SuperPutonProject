from typing import List

from api.company_manager import CompanyManager
from api.db import DBWrapper


class Runtime:
    company_manager = CompanyManager(DBWrapper())


class Config:
    rows_indices_to_sum: List[int] = []
