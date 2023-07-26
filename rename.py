import os
import sys
import hashlib
import json
import argparse

def hash_file(file_path: str, hash_method: str) -> str:
    if os.path.isdir(file_path):
        return "dir"

    file_bin = open(file_path, 'rb')
    hash_string = ""
    if hash_method == "sha1":
        hash_string = hashlib.sha1(file_bin.read()).hexdigest()
    elif hash_method == "sha224":
        hash_string = hashlib.sha224(file_bin.read()).hexdigest()
    elif hash_method == "sha256":
        hash_string = hashlib.sha256(file_bin.read()).hexdigest()
    elif hash_method == "sha384":
        hash_string = hashlib.sha384(file_bin.read()).hexdigest()
    elif hash_method == "sha512":
        hash_string = hashlib.sha512(file_bin.read()).hexdigest()
    else: # md5
        hash_string = hashlib.md5(file_bin.read()).hexdigest()
    file_bin.close()
    return hash_string

def valid_hash(string):
    hashs = ["sha1", "sha224", "sha256", "sha384", "sha512", "md5"]
    if string in hashs:
        return string
    raise ValueError


def is_path(string):
    abs_arg = os.path.abspath(string)
    if os.path.isfile(abs_arg) or os.path.isdir(abs_arg):
        return abs_arg
    print('No such file or directory: ' + string)
    sys.exit(2)


def is_folder(string):
    abs_arg = os.path.abspath(string)
    if os.path.isdir(abs_arg):
        return abs_arg
    print('Not a valid directory: ' + string)
    sys.exit(2)


def can_be_saved(string):
    abs_arg = os.path.abspath(string)
    if os.path.isdir(abs_arg):
        print('Not a valid filename: ' + string)
        sys.exit(2)
    elif os.path.isfile(abs_arg):
        print('File already exists: ' + string)
        sys.exit(2)
    elif not os.path.exists(abs_arg) and os.path.isdir(os.path.dirname(abs_arg)):
        return abs_arg
    else:
        print('Not a valid path: ' + string)
        sys.exit(2)


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

    use_hash = argsp.hash
    input_folder = ''
    output_folder = ''  # output is not None = path // else output = input folder
    filelist = ''
    preserve = argsp.preserve is not None
    preserve_folder = ''  # preserve is not None = path
    dry_run = argsp.dry_run
    use_json = argsp.json is not None
    json_path = ""  # json is not None = path
    json_opt = []
    json_args = {}
    json_data = []

    # dry_run
    if dry_run:
        json_opt.append("--dry-run")

    # Hash
    json_args["hash"] = use_hash

    # Input
    # this part of code runs anyway because if user does not define
    # a input folder it have a default value
    # check if $input is a valid dir path for input files
    if os.path.isdir(argsp.input):
        input_folder = argsp.input
    # if user is hasing only a file, add it only on $filelist
    elif os.path.isfile(argsp.input):
        input_folder = os.path.dirname(argsp.input)
        filelist = [os.path.basename(argsp.input)]
    json_args["input_path"] = argsp.input

    # json
    # with argparse argsp.json already is a valid path to be saved:
    if use_json:
        json_path = argsp.json
        json_opt.append("-j")
        json_args["json_path"] = json_path

    if argsp.output is None:
        output_folder = input_folder
    else:
        output_folder = argsp.output
    json_args["output_path"] = output_folder

    print(vars(argsp))

    if preserve:
        preserve_folder = argsp.preserve
        if preserve_folder == output_folder:
            parser.error("Preseve folder can't be the same as output folder")
        json_opt.append("-p")
        json_args["preserve_path"] = preserve_folder

    if not filelist:
        unsorted = os.listdir(input_folder)
        filelist = sorted(unsorted, key=len)

    for file in filelist:
        if not (file) == "rename.py":
            json_temp = {}

            file_extension = os.path.splitext((input_folder + "/" + file))[1]

            hash_out = hash_file(input_folder + "/" + file, use_hash)

            print("Trying to rename: " + file)

            if os.path.isfile(output_folder + "/" + hash_out + file_extension):
                print("file " + hash_out + file_extension + " already exists")
                if not os.path.samefile(input_folder + "/" + file,
                                        output_folder + "/" + hash_out + file_extension):
                    if preserve:
                        if not dry_run:
                            print("Moving: " + file + " because it is a duplicate")
                            os.rename(input_folder + "/" + file, preserve_folder + "/" + file)
                        else:
                            print("(dry-run) Moving: " + file + " because it is a duplicate")
                        json_temp["origin_path"] = input_folder + "/" + file
                        json_temp["dest_path"] = preserve_folder + "/" + file
                        json_temp["hash"] = hash_out
                        json_temp["action"] = "duplicate-moved"
                    else:
                        if not dry_run:
                            print("Removing: " + file + " because it is a duplicate")
                            os.remove(input_folder + "/" + file)
                        else:
                            print("(dry-run) Removing: " + file + " because it is a duplicate")
                        json_temp["origin_path"] = input_folder + "/" + file
                        json_temp["hash"] = hash_out
                        json_temp["action"] = "duplicate-removed"
                else:
                    json_temp["origin_path"] = input_folder + "/" + file
                    json_temp["hash"] = hash_out
                    json_temp["action"] = "already-hashed"

            elif not hash_out == "dir":
                if not dry_run:
                    print(file + ' --> ' + hash_out + file_extension)
                    os.rename(input_folder + "/" + file,
                              output_folder + "/" + hash_out + file_extension)
                else:
                    print('(dry-run) ' + file + ' --> ' + hash_out + file_extension)
                json_temp["origin_path"] = input_folder + "/" + file
                json_temp["dest_path"] = output_folder + "/" + hash_out + file_extension
                json_temp["hash"] = hash_out
                json_temp["action"] = "renamed"
            else:
                print("Skipping directory " + file)
                continue

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
