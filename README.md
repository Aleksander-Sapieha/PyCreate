# PyCreate - A tool to simplify PyInstaller

## Usage

1. Download the binary from the newest release
2. run "pycreate <script.pym>"

## Building from source

Run either build-old.sh or build.pym

## Scripting

### Available functions

1. pycreate_init() - Resets the configuration to default.
2. set_script(path) - Adds a script to the final executable. To add multiple, run this function multiple times.
3. add_file(path) - Adds a non-python file to the executable. Can be run multiple times.
4. set_name(value) - Sets the name of the executable.
5. set_onefile(value) - Toggles the --onefile argument. If true, the final executable will be a single file.
6. set_console(value) - Enables/diables the console. If false, the console won't appear. Useful for apps with graphics.
7. build() - Creates the command and runs it. Required for the script to execute.

### All text that starts with # will be a comment, and doesn't impact your script.

## Requirements

1. pyinstaller
