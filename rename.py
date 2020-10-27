import os
import sys
import hashlib
import getopt

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
    print('  -d           dry run, doesn\'t rename or delete files')

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
            sys.exit(1)

    try:
        opts, args = getopt.getopt(argv, "dhH:i:o:",["hash=", "ipath=","o_file"])
    except getopt.GetoptError:
        help_inv('')
        sys.exit(1)

    use_hash = ''
    input_folder='./'
    output_folder=''
    filelist = ''
    dry_run = False

    # todo: replace getop with argparse
    for opt, arg in opts:
        if opt == "-h":
            help()
            sys.exit(1)
        elif opt == "-d":
            dry_run = True
        elif opt in ("-H", "--hash"):
            if(arg == "sha1" or arg == "sha224" or arg == "sha256" or
            arg == "sha384" or arg == "sha512" or arg == "md5"):
                use_hash = arg
            else:
                help_inv("-H " + arg)
                sys.exit(1)
        elif opt in ("-i", "--ipath"):
            if os.path.isdir(arg):
                input_folder = arg
            elif(os.path.isfile(arg)):
                input_folder = os.path.dirname(arg)
                filelist = [os.path.basename(arg)]
            else:
                print("rename.py: Unable to find \"" + arg +
                "\": No such file or directory")
                sys.exit(2)
        elif opt in ("-o","o_file"):
            if os.path.isdir(arg):
                output_folder = arg
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

    if output_folder == '':
        output_folder = input_folder

    if not filelist:
        unsorted = os.listdir(input_folder)
        filelist = sorted(unsorted, key=len)

    for file in filelist:
        if not (file) == "rename.py":
            filename, file_extension = os.path.splitext((input_folder + "/" + file))

            sum = hash(input_folder + "/" + file, use_hash)

            try:
                print("Trying to rename: " + file)

                if os.path.isfile(output_folder + "/" + sum + file_extension):
                    print("file " + sum + file_extension + " already exists")
                    if not os.path.samefile(input_folder + "/" + file,
                    output_folder + "/" + sum + file_extension):
                        if not dry_run:
                            print("Removing: " + file + " because it is a duplicate")
                            os.remove(input_folder + "/" + file)
                        else:
                            print("(dry-run) Removing: " + file + " because it is a duplicate")

                elif not sum == "dir":
                    if not dry_run:
                        print(file + ' --> ' + sum + file_extension)
                        os.rename(input_folder + "/" + file, output_folder +
                        "/" + sum + file_extension)
                    else:
                        print('(dry-run) ' + file + ' --> ' + sum + file_extension)
                else:
                    print("Skipping directory " + file)

            except Exception as e:
                print("Error displaying file name.")

        print("")

if __name__ == "__main__":
    main(sys.argv[1:])
