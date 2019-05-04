class Company:
    def __init__(self, index, name):
        self.index = index
        self.name = name
        self.data = {}          # year-CompanyData pairs

    def commit_to_db(self):
        changed = []
        for key, value in self.data.items():
            if value.changed:
                changed.append(value.copy_to_commit())
        # TODO commit list of changes to db here

