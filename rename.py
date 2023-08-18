import os
import sys
import hashlib
import argparse

# 2 -> USER ERROR
# 3 -> CODE ERROR

def exit_with_error(error: str, err_nu:int):
    print("ERROR: " + error)
    sys.exit(err_nu)

def hash_file(file_path: str, hash_method: str) -> str:
    if os.path.isdir(file_path):
        exit_with_error("Not a valid file:" + file_path, 2)

    file_bin = open(file_path, 'rb')
    hash_string = ""
    if hash_method == "md5":
        hash_string = hashlib.md5(file_bin.read()).hexdigest()
    elif hash_method == "sha1":
        hash_string = hashlib.sha1(file_bin.read()).hexdigest()
    elif hash_method == "sha224":
        hash_string = hashlib.sha224(file_bin.read()).hexdigest()
    elif hash_method == "sha256":
        hash_string = hashlib.sha256(file_bin.read()).hexdigest()
    elif hash_method == "sha384":
        hash_string = hashlib.sha384(file_bin.read()).hexdigest()
    elif hash_method == "sha512":
        hash_string = hashlib.sha512(file_bin.read()).hexdigest()
    file_bin.close()
    if hash_string == "":
        exit_with_error("Could't compute file hash from" + file_path, 3)
    return hash_string

def valid_hash(string):
    hashs = ["sha1", "sha224", "sha256", "sha384", "sha512", "md5"]
    if string in hashs:
        return string
    exit_with_error("Not a valid hash algorithm" + string, 2)


def is_path(string):
    abs_arg = os.path.abspath(string)
    if os.path.isfile(abs_arg) or os.path.isdir(abs_arg):
        return abs_arg
    exit_with_error('No such file or directory: ' + string, 2)


def is_folder(string):
    abs_arg = os.path.abspath(string)
    if os.path.isdir(abs_arg):
        return abs_arg
    exit_with_error('Not a valid directory: ' + string, 2)


def can_be_saved(string):
    abs_arg = os.path.abspath(string)
    if os.path.isdir(abs_arg):
        exit_with_error('Not a valid filename: ' + string, 2)
    elif os.path.isfile(abs_arg):
        exit_with_error('File already exists: ' + string, 2)
    elif not os.path.exists(abs_arg) and os.path.isdir(os.path.dirname(abs_arg)):
        return abs_arg
    else:
        exit_with_error('Not a valid path: ' + string, 2)

def _action_move(source: str, destination: str, dry_run: bool):
    # todo: get common base path from source and destination
    #   if commom path, show input.txt -> output.txt
    # todo: check if source and destination are valid
    if dry_run:
        print('(dry-run) ' + source + ' --> ' + destination)
    else:
        os.rename(source, destination)
        print(source + ' --> ' + destination)

def action_move(source: str, destination: str, dry_run: bool):

    if not os.path.isfile(source):
        exit_with_error("Cannot move dir", 3)

    if os.path.isdir(destination):
        destination = destination + "/" + os.path.basename(source)
        action_move(source, destination, dry_run)
        return

    if not os.path.exists(destination):
        _action_move(source, destination, dry_run)
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
            _action_move(source, new_destination, dry_run)
            return

def main():
    parser = argparse.ArgumentParser(
        description="Single python file to rename all files in a directory to their hash sums.")

    parser.add_argument('-d',
                        '--dry-run',
                        action='store_true',
                        help='dry run, doesn\'t rename or delete files')

    parser.add_argument('-H',
                        '--hash',
                        type=valid_hash,
                        default='md5',
                        help='hash that will be used: [md5/sha1/sha224/sha256/sha384/sha512]')

    parser.add_argument('-i',
                        '--input',
                        metavar='DIR/FILE',
                        type=is_path,
                        default=os.path.abspath('./'),
                        action='store',
                        help='Files that will be hashed')

    # if defined a filename here, show to user that -d can be used to only show name of variables
    parser.add_argument('-o',
                        '--output',
                        metavar='DIR',
                        type=is_folder,
                        action='store',
                        help='Location were hashed files will be stored')

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
        input_file_list = sorted(os.listdir(input_folder), key=len)
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
    # input_file_list       = input1.txt
    #                         input2.txt
    output_file_basepath = output_folder + "/"
    input_file_basepath = input_folder + "/"

    for input_file_name in input_file_list:

        # "/in/" + "input.txt" -> "/in/input.txt"
        input_file_path = input_file_basepath + input_file_name

        if input_file_name == "rename.py": # todo: sys.argv[0]
            print("Skipping source file " + input_file_name)
            continue

        if os.path.isdir(input_file_path):
            print("Skipping directory " + input_file_name)
            continue

        if not os.path.isfile(input_file_path):
            exit_with_error("Not file or dir",3)
            break

        print("Trying to rename: " + input_file_name)

        # only hash_string without path, name or extensions
        # return("01234567890abcdef01234567890abcd")
        output_file_name_only = hash_file(input_file_path, use_hash)
        # output_file_name = "01234567890abcdef01234567890abcd" + "txt" <- "/in/input.txt"
        output_file_name = output_file_name_only + os.path.splitext(input_file_path)[1]
        output_file_path = output_file_basepath + output_file_name

        action_move(input_file_path, output_file_path, dry_run)

if __name__ == "__main__":
    main()
