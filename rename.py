import os
import sys
import hashlib
import argparse
from blake3 import blake3

USER_ERROR = 3
CODE_ERROR = 4
SOFT_ERROR = 5

VERSION = "v2.2"

# blake3 default lenght is 32, but to avoid long file names in windows I
# recomend setting this to 16
# https://learn.microsoft.com/windows/win32/fileio/maximum-file-path-limitation
BLAKE3_LENGTH = 16


def exit_with_error(error: str, err_nu: int):
    print("ERROR: " + error)
    sys.exit(err_nu)


def hash_file(file_path: str, algorithm: str) -> str:
    if not os.path.isfile(file_path):
        exit_with_error("Not a valid file:" + file_path, USER_ERROR)

    hashlib.md5().hexdigest()

    dict_algorithm = {
        "md5": hashlib.md5,
        "blake3": blake3,
        "sha1": hashlib.sha1,
        "sha224": hashlib.sha224,
        "sha256": hashlib.sha256,
        "sha384": hashlib.sha384,
        "sha512": hashlib.sha512
    }

    try:
        hashing = dict_algorithm[algorithm]()
    except KeyError:
        exit_with_error("Error while chosing algorithm", CODE_ERROR)

    with open(file_path, 'rb') as file_bin:
        for block in iter(lambda: file_bin.read(4096), b''):
            hashing.update(block)

    if algorithm == "blake3":
        return hashing.hexdigest(length=BLAKE3_LENGTH)

    return hashing.hexdigest()


def is_path(path: str):
    abs_path = os.path.abspath(path)
    if os.path.isfile(abs_path) or os.path.isdir(abs_path):
        return abs_path

    exit_with_error('No such file or directory: ' + path, USER_ERROR)


def is_dir(path: str):
    abs_path = os.path.abspath(path)
    if os.path.isdir(abs_path):
        return abs_path

    exit_with_error('Not a valid directory: ' + path, USER_ERROR)


def action_move(source: str, destination: str, dry_run: bool):
    if dry_run:
        print('(dry-run) ' + source + ' --> ' + destination)
    else:
        os.rename(source, destination)
        print(source + ' --> ' + destination)


def try_move(source: str, destination: str, dry_run: bool):

    if not os.path.isfile(source):
        exit_with_error("Cannot move dir", CODE_ERROR)

    if os.path.isdir(destination):
        destination = destination + "/" + os.path.basename(source)
        try_move(source, destination, dry_run)
        return

    if not os.path.exists(destination):
        action_move(source, destination, dry_run)
        return

    if os.path.samefile(source, destination):
        print("file " + source + " already hashed")
        return

    iterator = 1
    prefix_path = os.path.splitext(destination)[0] + "_"
    postfix_path = os.path.splitext(destination)[1]
    while True:
        new_destination = prefix_path + str(iterator) + postfix_path
        if os.path.exists(new_destination):
            if os.path.samefile(source, new_destination):
                print("file " + source + " already hashed")
                return
            iterator = iterator + 1
        else:
            action_move(source, new_destination, dry_run)
            return

def main():
    parser = argparse.ArgumentParser(
        description="Single python file to rename all files in a directory to \
            their hash sums.")

    parser.add_argument('-d',
                        '--dry-run',
                        action='store_true',
                        help='dry run, doesn\'t rename or delete files')

    parser.add_argument('-H',
                        '--hash',
                        default='blake3',
                        choices=["md5", "blake3", "sha1", "sha224", "sha256",
                                 "sha384", "sha512"],
                        metavar="HASH",
                        help='hash that will be used: \
                        [md5/blake3/sha1/sha224/sha256/sha384/sha512')

    parser.add_argument('-i',
                        '--input',
                        metavar='DIR/FILE',
                        type=is_path,
                        default=os.path.abspath('./'),
                        action='store',
                        help='Files that will be hashed')

    parser.add_argument('-o',
                        '--output',
                        metavar='DIR',
                        type=is_dir,
                        action='store',
                        help='Location were hashed files will be stored')

    parser.add_argument('-v',
                        '--version',
                        action='version',
                        version=VERSION)

    argsp = parser.parse_args()

    dry_run = argsp.dry_run
    use_hash = argsp.hash

    # Input
    # this part of code runs anyway because if user does not define
    # a input folder it have a default value
    # check if $input is a valid dir path for input files
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

    output_folder = input_folder if argsp.output is None else argsp.output

    if dry_run:
        print(vars(argsp))

    # input_file_path		= /in/input.txt
    # input_file_basepath	= /in/
    # input_file_name       = input.txt
    # input_file_name_only	= input
    # input_file_extension	= txt
    # output_file_path		= /out/output.txt
    # output_file_basepath	= /out/
    # output_file_name      = output.txt
    # output_file_name_only	= output
    # preserve_file_path    = /pre/input.txt
    # input_file_list       = input1.txt, input2.txt
    output_file_basepath = output_folder + "/"
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

        # only hash_string without path, name or extensions
        # return("01234567890abcdef01234567890abcd")
        output_file_name_only = hash_file(input_file_path, use_hash)
        # output_file_name = "01234567890abcdef01234567890abcd" + ".txt"
        output_file_name = output_file_name_only + \
            os.path.splitext(input_file_path)[1].lower()
        output_file_path = output_file_basepath + output_file_name

        try_move(input_file_path, output_file_path, dry_run)


if __name__ == "__main__":
    main()
