REM
REM   !!! USE THIS IF NOT USING PYCREATE !!!
REM
REM   Create/build-old.cmd
REM
REM   Creator: Aleksander Sapieha (sourceguy68@gmail.com)
REM
REM   Contributors:
REM   Aleksander Sapieha (sourceguy68@gmail.com)
REM

@echo off

echo Starting build...

pyinstaller src/pycreate.py src/commands.py src/lexer.py src/evaluator.py src/parser.py src/errors.py --onefile

echo Build finished!