import os.path as path
import src.config as c


def make_tmp_path():
    return path.join(c.DATA_DIR, c.TMP_DIR)


def make_data_abs_path(p):
    return path.join(p, c.DATA_DIR)


def make_tmp_abs_path(p):
    return path.join(p, make_tmp_path())
