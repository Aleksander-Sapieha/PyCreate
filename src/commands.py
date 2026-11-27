#
#   Create/src/commands.py
#
#   Creator: Aleksander Sapieha (sourceguy68@gmail.com)
#
#   Contributors:
#   Aleksander Sapieha (sourceguy68@gmail.com)
#

import subprocess
import sys
import os

files = []
py_files = []
name = None
onefile = False
console = True
separator = ";" if os.name == "nt" else ":"

def pycreate_init():
    global files,  py_files
    files = []
    py_files = []

def set_script(path):
    global py_files
    py_files.append(path)

def add_file(path, target):
    global files, separator
    files.append(f"{path}{separator}{target}")

def set_name(value):
    global name
    name = value

def set_onefile(value):
    global onefile
    onefile = value

def set_console(value):
    global console
    console = value

def build():
    if py_files == []:
        print("Error: No entry script specified!")
        return

    command = ["pyinstaller"]

    if onefile:
        command.append("--onefile")

    if not console:
        command.append("--noconsole")

    if name:
        command.extend(["--name", name])

    for file in files:
        command.extend(["--add-data", f"{file}."])

    for py_file in py_files:
        command.append(py_file)

    print("Executing:", subprocess.list2cmdline(command))
    subprocess.run(command, check=True)
