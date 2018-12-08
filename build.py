import os
import sys
import argparse

parser = argparse.ArgumentParser()

parser.add_argument("--onedir", action='store_true', help="Make exe within one directory")
parser.add_argument("--onefile", action='store_true', help="Make exe in a single file")
parser.add_argument("--name", nargs=1, help="Name of output directory and exe")
args = parser.parse_args()

command = 'pyinstaller --windowed --icon=src/univ_icon.ico '
output_dir = 'dist\\'
name = 'py_gui'
# Set output directory option
if args.onedir:
    if args.onefile:
        print('Use only one option among onedir and onefile')
        sys.exit(1)
    command += '--onedir '
    output_dir += 'py_gui'
elif args.onefile:
    command += '--onefile '
else:
    output_dir += 'py_gui'


if args.name:
    name = args.name[0]
    command = command.replace('py_gui', name)
    output_dir = output_dir.replace('py_gui', name)
    command += '--name %s ' % name

# Run the command
command += './py_gui.py'

e = os.system(command)
if not e == 0:
    print(sys.stderr, '실행 중 에러가 났습니다. 에러 코드:', e)
    sys.exit(1)

# # Copy the source directory to output folder
e = os.system('xcopy src\*.* %s\src\ /e /h /k /Y > nul' % output_dir)
if not e == 0:
    print(sys.stderr, '실행 중 에러가 났습니다. 에러 코드:', e)
    sys.exit(1)

print('Make %s.exe is finished successfully' % name)
