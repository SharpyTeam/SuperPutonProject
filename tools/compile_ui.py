import os
import subprocess
from typing import NoReturn


def get_parent_directory(directory: str, levels: int = 1) -> str:
    for _ in range(levels):
        directory = os.path.dirname(directory)
    return directory


def chdir(main_file_path: str) -> NoReturn:
    if os.path.isabs(main_file_path):
        os.chdir(get_parent_directory(os.path.normpath(main_file_path), levels=2))
    else:
        os.chdir(get_parent_directory(os.path.normpath(os.path.join(os.getcwd(), main_file_path)), levels=2))


chdir(__file__)

UI_SRC_DIR = "ui_src"
COMPILED_UI_DIR = os.path.join("src", "ui", "gui", "design")
COMPILED_UI_SUFFIX = "_design"

print("-= UI Compiler =-", end='\n\n')

for the_file in os.listdir(os.path.join(os.getcwd(), UI_SRC_DIR)):
    file_path = os.path.join(os.getcwd(), UI_SRC_DIR, the_file)
    try:
        if os.path.isfile(file_path):
            compiled_name = str(the_file.split('.')[0]) + COMPILED_UI_SUFFIX + ".py"
            compiled_path = os.path.join(os.getcwd(), COMPILED_UI_DIR, compiled_name)
            subprocess.run(["pyuic5", file_path, "-o", compiled_path])
            print("Successfully compiled %s" % the_file)
    except IOError as e:
        print(e)
