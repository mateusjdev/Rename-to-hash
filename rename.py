import os
import sys
import hashlib
import getopt
import json

def help_inv(inv_arg):
    if inv_arg:
        print("rename.py: invalid option \"" + inv_arg + "\"\n")
    else:
        print("rename.py: invalid options\n")
    help()

def help():
    print('Usage: rename.py [OPTIONS]\n')
    print('Options:')
    print('  -h           Print this help text and exit')
    print('  -H HASH      Hash that will be used: [md5/sha1/sha224/sha256'
    + '/sha384/sha512]')
    print('  -i DIR/FILE  Files that will be hashed')
    print('  -o DIR       Location were hashed files will be stored')
    print('  -j FILE      Saves a log in .json format')
    print('  -d           dry run, doesn\'t rename or delete files')
    sys.exit(2)

def hash(file, method):
    if not os.path.isdir(file):
        f = open(file, 'rb')
        sum = ""
        if method == "sha1":
            sum = hashlib.sha1(f.read()).hexdigest()
        elif method == "sha224":
            sum = hashlib.sha224(f.read()).hexdigest()
        elif method == "sha256":
            sum = hashlib.sha256(f.read()).hexdigest()
        elif method == "sha384":
            sum = hashlib.sha384(f.read()).hexdigest()
        elif method == "sha512":
            sum = hashlib.sha512(f.read()).hexdigest()
        else:  # md5
            sum = hashlib.md5(f.read()).hexdigest()
        f.close()
        return sum
    else:
        return "dir"

def main(argv):

    if argv:
        if(argv[0][0] != '-' or len(argv[0]) == 1):
            help_inv(argv[0])

    try:
        opts, args = getopt.getopt(argv, "dhH:i:j:o:",["hash", "jfile", "ipath","opath"])
    except getopt.GetoptError:
        help_inv('')

    use_hash = ''
    input_folder = os.path.abspath("./")
    output_folder=''
    filelist = ''
    dry_run = False
    use_json = False
    json_path = ""
    json_opt = []
    json_args = {}
    json_data = []

    # todo: replace getop with argparse
    for opt, arg in opts:
        if opt == "-h":
            help()
        elif opt == "-d":
            dry_run = True
            json_opt.append("-d")

        elif opt in ("-H", "--hash"):
            if(arg == "sha1" or arg == "sha224" or arg == "sha256" or
            arg == "sha384" or arg == "sha512" or arg == "md5"):
                use_hash = arg
            else:
                help_inv("-H " + arg)

            json_opt.append("-h")
            json_args["hash"] = arg

        elif opt in ("-j","--jfile"):
            use_json = True
            abs_arg = os.path.abspath(arg)
            if os.path.isdir(abs_arg):
                help_inv('-j ' + arg)
            elif os.path.isfile(abs_arg):
                j_path, j_ext = os.path.splitext(arg)
                json_path = abs_arg
                out_json = os.path.basename(j_path)
                it = 1
                while os.path.isfile(json_path):
                    if j_ext != ".json":
                        json_path = j_path + "\\" + out_json + "-"  + it + j_ext + ".json"
                    else:
                        json_path = j_path + "\\" + out_json + "-"  + it + ".json"
                    it += 1
                print('File \"' + abs_arg + '\"already exists, saving as \"' + json_path + "\"." )
            else:
                json_dir = os.path.dirname(abs_arg)
                if os.path.isdir(json_dir):
                    out_json = os.path.basename(abs_arg)
                    if not out_json.endswith(".json"):
                        out_json = out_json + ".json"
                    json_path = json_dir + "\\" + out_json
                else:
                    print("rename.py: \"" + json_dir +
                    "\": Is not a valid directory")
                    sys.exit(2)

            json_opt.append("-j")
            json_args["jfile"] = json_path

        elif opt in ("-i", "--ipath"):
            if os.path.isdir(arg):
                input_folder = os.path.abspath(arg)
            elif(os.path.isfile(arg)):
                input_folder = os.path.abspath(arg)
                filelist = [os.path.basename(arg)]
            else:
                print("rename.py: Unable to find \"" + arg +
                "\": No such file or directory")
                sys.exit(2)

            json_opt.append("-i")
            json_args["ipath"] = input_folder

        elif opt in ("-o","--opath"):
            if os.path.isdir(arg):
                output_folder = os.path.abspath(arg)
            else:
                o_folder, o_file = os.path.splitext(arg)
                if os.path.isdir(o_folder):
                    if len(filelist) == 1:
                        output_folder = o_folder
                        if os.path.isfile(arg):
                            help_inv('-o')
                    else:
                        help_inv('-o ' + arg)
                else:
                    print("rename.py: \"" + o_folder +
                    "\": Is not a valid directory")
                    sys.exit(2)

            json_opt.append("-o")
            json_args["opath"] = output_folder

    if output_folder == '':
        output_folder = input_folder

    if not filelist:
        unsorted = os.listdir(input_folder)
        filelist = sorted(unsorted, key=len)

    for file in filelist:
        if not (file) == "rename.py":
            json_temp = {}

            filename, file_extension = os.path.splitext((input_folder + "\\"
            + file))

            sum = hash(input_folder + "\\" + file, use_hash)

            try:
                print("Trying to rename: " + file)

                if os.path.isfile(output_folder + "\\" + sum + file_extension):
                    print("file " + sum + file_extension + " already exists")
                    if not os.path.samefile(input_folder + "\\" + file,
                    output_folder + "\\" + sum + file_extension):
                        if not dry_run:
                            print("Removing: " + file +
                            " because it is a duplicate")
                            os.remove(input_folder + "\\" + file)
                        else:
                            print("(dry-run) Removing: " + file +
                            " because it is a duplicate")
                        json_temp["origin_path"] = (input_folder + "\\" + file)
                        json_temp["hash"] = sum
                        json_temp["action"] = "duplicate-removed"
                    else:
                        json_temp["origin_path"] = (input_folder + "\\" + file)
                        json_temp["hash"] = sum
                        json_temp["action"] = "nothing"

                elif not sum == "dir":
                    if not dry_run:
                        print(file + ' --> ' + sum + file_extension)
                        os.rename(input_folder + "\\" + file, output_folder +
                        "\\" + sum + file_extension)
                    else:
                        print('(dry-run) ' + file + ' --> ' + sum +
                         file_extension)
                    json_temp["origin_path"] = (input_folder + "\\" + file)
                    json_temp["dest_path"] = (output_folder +
                    "\\" + sum + file_extension)
                    json_temp["hash"] = "remove"
                    json_temp["action"] = "renamed"
                else:
                    print("Skipping directory " + file)
                    continue

            except Exception as e:
                print("Error displaying file name.")

            json_data.append(json_temp)

            print("")

    if use_json:
        json_args['options'] = json_opt
        json_args['data'] = json_data

        with open(json_path,'w') as f:
            json.dump(json_args,f,indent=4)

        print('.json log saved as \"' + json_path + '\"\n')



if __name__ == "__main__":
    main(sys.argv[1:])
