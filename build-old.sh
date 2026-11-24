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

pyinstaller src/pycreate.py src/commands.py --onefile

echo "Build Finished!"