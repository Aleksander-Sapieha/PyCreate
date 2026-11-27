#
#   !!! USE THIS IF NOT USING PYCREATE !!!
#
#   Create/build-old.sh
#
#   Creator: Aleksander Sapieha (sourceguy68@gmail.com)
#
#   Contributors:
#   Aleksander Sapieha (sourceguy68@gmail.com)
#

echo "Starting Build"

pyinstaller src/pycreate.py src/commands.py src/lexer.py src/evaluator.py src/parser.py src/errors.py --onefile

echo "Build Finished!"