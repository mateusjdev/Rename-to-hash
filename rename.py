import os
import sys
import hashlib
import json
import argparse

# 2 -> USER ERROR
# 3 -> CODE ERROR
def exit_with_error(error: str, err_nu:int):
    print(error)
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

    parser.add_argument('-j',
                        '--json',
                        metavar='FILE',
                        type=can_be_saved,
                        action='store',
                        help='Saves a log in .json format')

    parser.add_argument('-p',
                        '--preserve',
                        metavar='DIR',
                        type=is_folder,
                        action='store',
                        help='Location to move and preserve duplicated files')

    argsp = parser.parse_args()

    json_path = ""  # json is not None = path
    json_opt = []
    json_args = {}
    json_data = []

    # JSON
    # todo: json = file path? x folder path
    # todo: if !json doesnot log any
    # with argparse argsp.json already is a valid path to be saved:
    use_json = argsp.json is not None
    if use_json:
        json_path = argsp.json
        json_opt.append("-j")
        json_args["json_path"] = json_path

    # dry_run
    dry_run = argsp.dry_run
    if dry_run:
        json_opt.append("--dry-run")

    # Hash
    use_hash = argsp.hash
    json_args["hash"] = use_hash

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
    json_args["input_path"] = argsp.input

    output_folder = input_folder if argsp.output is None else argsp.output
    json_args["output_path"] = output_folder

    print(vars(argsp))

    preserve = argsp.preserve is not None
    preserve_folder = ''  # preserve is not None = path
    if preserve:
        preserve_folder = argsp.preserve
        if preserve_folder == output_folder:
            parser.error("Preseve folder can't be the same as output folder")
        json_opt.append("-p")
        json_args["preserve_path"] = preserve_folder

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

    # for input_file_name in input_file_list:
    for input_file_name in input_file_list:
        if input_file_name == "rename.py": # todo: sys.argv[0]
            print("Skipping source file " + input_file_name)
            continue

        if os.path.isdir(input_file_name):
            print("Skipping directory " + input_file_name)
            continue

        # "/in/" + "input.txt" -> "/in/input.txt"
        input_file_path = input_file_basepath + input_file_name

        if os.path.isfile(input_file_path) and not os.path.isdir(input_file_path):
            json_temp = {}

            # only hash_string without path, name or extensions
            # return("01234567890abcdef01234567890abcd")
            output_file_name_only = hash_file(input_file_path, use_hash)
            # output_file_name = "01234567890abcdef01234567890abcd" + "txt" <- "/in/input.txt"
            output_file_name = output_file_name_only + os.path.splitext(input_file_path)[1]
            output_file_path = output_file_basepath + output_file_name

            print("Trying to rename: " + input_file_name)

            # if output_file_path exists
            if os.path.isfile(output_file_path):
                print("file " + output_file_name + " already exists")
                # if input_file_path = output_file_path then:
                if os.path.samefile(input_file_path, output_file_path):
                    json_temp["origin_path"] = input_file_path
                    json_temp["hash"] = output_file_name_only
                    json_temp["action"] = "already-hashed"
                # if input_file_path != output_file_path then:
                else:
                    # if (preserve) move (input_file_path) to (preserve_file_path)
                    if preserve:
                        preserve_file_path = preserve_folder + "/" + input_file_name
                        if dry_run:
                            print("(dry-run) " + input_file_name + " is a duplicate")
                        else:
                            print("Moving: " + input_file_name + " because it is a duplicate")
                            os.rename(input_file_path, preserve_file_path)
                        json_temp["origin_path"] = input_file_path
                        json_temp["dest_path"] = preserve_file_path
                        json_temp["hash"] = output_file_name_only
                        json_temp["action"] = "duplicate-moved"
                    # if !(preserve) delete (input_file_path)
                    else:
                        if dry_run:
                            print("(dry-run) " + input_file_name + " is a duplicate")
                        else:
                            print("Removing: " + input_file_name + " because it is a duplicate")
                            os.remove(input_file_path)
                        json_temp["origin_path"] = input_file_path
                        json_temp["hash"] = output_file_name_only
                        json_temp["action"] = "duplicate-removed"
            else:
                if dry_run:
                    print('(dry-run) ' + input_file_name + ' --> ' + output_file_name)
                else:
                    print(input_file_name + ' --> ' + output_file_name)
                    os.rename(input_file_path, output_file_path)
                json_temp["origin_path"] = input_file_path
                json_temp["dest_path"] = output_file_path
                json_temp["hash"] = output_file_name_only
                json_temp["action"] = "renamed"

            json_data.append(json_temp)

            print("")

    if use_json:
        json_args['options'] = json_opt
        json_args['data'] = json_data

        with open(json_path, 'w', encoding="utf-8") as json_file:
            json.dump(json_args, json_file, indent=4)

        print('.json log saved as \"' + json_path + '\"\n')


if __name__ == "__main__":
    main()
