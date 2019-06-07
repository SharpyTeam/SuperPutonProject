from api.company_manager import CompanyManager
from api.db import DBWrapper


class Runtime:
    db_wrapper = DBWrapper()
    company_manager = CompanyManager(db_wrapper)

