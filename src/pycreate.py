#
#   Create/src/create.py
#
#   Creator: Aleksander Sapieha (sourceguy68@gmail.com)
#
#   Contributors:
#   Aleksander Sapieha (sourceguy68@gmail.com)
#

import sys
import runpy
import os

import commands

def main():
    if len(sys.argv) < 2:
        print("Usage: pycreate <file.pym>")
        return 1

    path = sys.argv[1]

    if not os.path.isfile(path):
        print(f"Error: File not found: {path}")
        return 1

    if not path.endswith(".pym"):
        print("Error: Expected a .pym file")
        return 1

    try:

        runpy.run_path(
            path,
            run_name="__main__",
            init_globals=vars(commands)
        )
    except Exception as error:
        print(f"PyCreate Error: {error}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
