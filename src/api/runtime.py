from api.company_manager import CompanyManager
from api.db import DBWrapper


class Runtime:
    company_manager = CompanyManager(DBWrapper())

