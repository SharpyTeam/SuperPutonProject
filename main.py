import os
import sys

import src.config as c
import src.api.dl as d
import src.api.parsing as p
import src.api.utils as u


def c_(bytes, file_name, counter, total):
    # print(str(bytes) + " downloaded. File " + str(counter)
    #      + "/" + str(total) + " - " + file_name)
    pass


d.dl_archive_files(p.parse_annual_page(d.get_page('http://cbr.ru/finmarket/fcsm/publication/insurers/2017-12-31/')),
                   u.make_tmp_abs_path(os.path.dirname(__file__)))

print("Done")
