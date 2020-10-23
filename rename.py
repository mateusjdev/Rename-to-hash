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
    print('  -H HASH      Hash that will be used: [md5/sha1/sha224/sha256/sha384/sha512]')
    print('  -i DIR/FILE  Files that will be hashed')
    print('  -o DIR       (Soon) Location were hashed files will be stored')
    print('  -r           (Soon) Recursive')
    print('  -s FILE      (Soon) Saves a log in .json format')

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
        opts, args = getopt.getopt(argv, "hH:i:", ["hash=", "ifile="])
    except getopt.GetoptError:
        help_inv('')
        sys.exit(1)

    use_hash = ''
    use_folder='./'
    filelist = ''

    for opt, arg in opts:
        if opt == "-h":
            help()
            sys.exit(1)
        elif opt in ("-H", "--hash"):
            if(arg == "sha1" or arg == "sha224" or arg == "sha256" or arg == "sha384" or arg == "sha512" or arg == "md5"):
                use_hash = arg
            else:
                help_inv("-H " + arg)
                sys.exit(1)
        elif opt in ("-i", "--ifile"):
            if os.path.isdir(arg):
                use_folder = arg
            elif(os.path.isfile(arg)):
                use_folder = os.path.dirname(arg)
                filelist = [os.path.basename(arg)]
            else:
                print("rename.py: Unable to find \"" + arg + "\": No such file or directory")
                sys.exit(2)

    if not filelist:
        unsorted = os.listdir(use_folder)
        filelist = sorted(unsorted, key=len)

    for file in filelist:
        if not (file) == "rename.py":
            filename, file_extension = os.path.splitext((use_folder + "/" + file))

            sum = hash(use_folder + "/" + file, use_hash)

            try:
                print("Trying to rename: " + file)

                if os.path.isfile(use_folder + "/" + sum + file_extension):
                    print("file " + sum + file_extension + " already exists")
                    if not (use_folder + "/" + file) == (use_folder + "/" + sum + file_extension):
                        print("Removing: " + file + " because it is a duplicate")
                        os.remove(use_folder + "/" + file)
                elif not sum == "dir":
                    os.rename(use_folder + "/" + file, use_folder + "/" + sum + file_extension)
                    print(file + ' --> ' + sum + file_extension)
                else:
                    print("Skipping directory " + file)

            except Exception as e:
                print("Error displaying file name.")

        print("")

if __name__ == "__main__":
    main(sys.argv[1:])
