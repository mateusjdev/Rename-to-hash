import os
import sys
import argparse
import string
import random

USER_ERROR = 3
CODE_ERROR = 4
SOFT_ERROR = 5

VERSION = "v1"

# 62^16 - setting this very low can cause problems
DICTIONARY = string.digits + string.ascii_letters
FILENAME_SIZE = 16

def exit_with_error(error: str, err_nu: int):
    print("ERROR: " + error)
    sys.exit(err_nu)


def random_name() -> str:
    return ''.join(random.choices(DICTIONARY, k=FILENAME_SIZE))


def is_path(path: str):
    abs_path = os.path.abspath(path)
    if os.path.isfile(abs_path) or os.path.isdir(abs_path):
        return abs_path

    return exit_with_error('No such file or directory: ' + path, USER_ERROR)


def action_move(source: str, destination: str):
    os.rename(source, destination)
    print(source + ' --> ' + destination)


def try_move(source: str, destination_folder: str):

    ext = os.path.splitext(source)[1].lower()

    if not os.path.isfile(source):
        exit_with_error("Cannot move dir", CODE_ERROR)

    while True:
        new_destination = destination_folder + random_name() + ext
        if os.path.exists(new_destination):
            continue

        action_move(source, new_destination)
        break


def main():
    parser = argparse.ArgumentParser(
        description="Rename all files to random characters")

    parser.add_argument('-i',
                        '--input',
                        metavar='DIR/FILE',
                        type=is_path,
                        default=os.path.abspath('./'),
                        action='store',
                        help='Files that will be renamed')

    parser.add_argument('-v',
                        '--version',
                        action='version',
                        version=VERSION)

    argsp = parser.parse_args()

    input_folder = ''
    input_file_list = ''
    if os.path.isdir(argsp.input):
        input_folder = argsp.input

        # TODO: Improve .git repo detection
        if os.path.exists(input_folder + "/.git"):
            exit_with_error("Input path is git repo!", SOFT_ERROR)

        input_file_list = os.listdir(input_folder)

    elif os.path.isfile(argsp.input):
        input_folder = os.path.dirname(argsp.input)
        input_file_list = [os.path.basename(argsp.input)]

    input_file_basepath = input_folder + "/"

    for input_file_name in input_file_list:

        # "/in/" + "input.txt" -> "/in/input.txt"
        input_file_path = input_file_basepath + input_file_name

        # TODO: check if input_file_name == argv[0]
        # argv[0] == 'python rename.py' || './renamy.py' || ...
        if input_file_name == "rename.py":
            print("Skipping source file " + input_file_name)
            continue

        if os.path.isdir(input_file_path):
            print("Skipping directory " + input_file_name)
            continue

        if not os.path.isfile(input_file_path):
            exit_with_error("Not file or dir", CODE_ERROR)
            break

        print("Trying to rename: " + input_file_name)

        try_move(input_file_path, input_file_basepath)


if __name__ == "__main__":
    main()
