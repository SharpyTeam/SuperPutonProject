class Company:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.data = {}          # year-CompanyData pairs
        self.changed = False

    def get_is_changed_and_reset(self):
        if self.changed:
            self.changed = False
            return True
        return False

