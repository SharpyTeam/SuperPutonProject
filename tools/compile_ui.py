import os
import subprocess

os.chdir(os.path.dirname(os.path.dirname(__file__)))

UI_SRC_DIR = "ui_src"
COMPILED_UI_DIR = os.path.join("src", "ui", "gui")
COMPILED_UI_SUFFIX = "_design"

print("-= UI Compiler =-", end='\n\n')

for the_file in os.listdir(os.path.join(os.getcwd(), UI_SRC_DIR)):
    file_path = os.path.join(os.getcwd(), UI_SRC_DIR, the_file)
    try:
        if os.path.isfile(file_path):
            compiled_name = str(the_file.split('.')[0]) + COMPILED_UI_SUFFIX + ".py"
            compiled_path = os.path.join(os.getcwd(), COMPILED_UI_DIR, compiled_name)
            os.unlink(compiled_path)
            subprocess.run(["pyuic5", file_path, "-o", compiled_path])
            print("Successfully compiled %s" % the_file)
    except IOError as e:
        pass
