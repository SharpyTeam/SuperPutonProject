import os


class Runtime:
    app_path = None

    @staticmethod
    def get_app_path():
        return Runtime.app_path

    @staticmethod
    def set_app_path(path):
        if os.path.exists(path):
            Runtime.app_path = path

    @staticmethod
    def init(file):
        Runtime.set_app_path(os.path.dirname(file)
                             .replace('/', os.sep)
                             .replace('\\', os.sep))
