class Company:
    def __init__(self, id, name, linked_db=None):
        self.id = id
        self.name = name
        self.data = {}          # year-CompanyData pairs
        self.changed = False
        self.linked_db = linked_db

    def get_period_data(self, year):
        if year in self.data:
            return self.data[year]
        self.linked_db.get_company_data(self, year)
        try:
            return self.data[year]
        except KeyError:
            return None

    def get_is_changed_and_reset(self):
        if self.changed:
            self.changed = False
            return True
        return False

