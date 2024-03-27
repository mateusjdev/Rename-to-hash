import os
import sys
import hashlib
import argparse
import logging


class HashAlgorithm:
    """List of Hashing Algorithms"""
    SHA512 = "sha512"
    SHA384 = "sha384"
    SHA256 = "sha256"
    SHA224 = "sha224"
    SHA1  = "sha1"
    MD5 = "md5"
    BLAKE3 = "blake3"
    BLAKE2B = "blake2"

class ErrorExitCode:
    """List of Error Exit Codes"""
    USER_ERROR = 3
    CODE_ERROR = 4
    SOFT_ERROR = 5

DEFAULT_ALGORITHM = HashAlgorithm.BLAKE3

# blake3 not available on aarch64
# https://github.com/oconnor663/blake3-py/issues/28
try:
    from blake3 import blake3
except ModuleNotFoundError:
    DEFAULT_ALGORITHM = HashAlgorithm.MD5

VERSION = "v2.3.2"

# blake3 default lenght is 32, but to avoid long file names in windows I
# recomend setting this to 16
# obs: in blake2b (64 as default) setting this as 16 will generate a totally
# diferent hash
# https://learn.microsoft.com/windows/win32/fileio/maximum-file-path-limitation
BLAKE_DIGEST_SIZE = 16

# TODO: better format for logging (https://stackoverflow.com/q/384076)
LOGGING_FORMAT = 'rename.py: %(message)s'

logger = logging.getLogger(__name__)

# TODO: raise Exception
def exit_with_error(error: str, err_nu: int):
    logger.critical("ERROR: %s", error)
    sys.exit(err_nu)

class NameGenerator:
    """Generate a string based on method/param"""

    @staticmethod
    def from_file_hash(file_path: str, algorithm: str) -> str:
        if not os.path.isfile(file_path):
            exit_with_error("Not a valid file:" + file_path, ErrorExitCode.USER_ERROR)

        dict_algorithm = {
            HashAlgorithm.MD5: hashlib.md5(),
            HashAlgorithm.SHA1: hashlib.sha1(),
            HashAlgorithm.SHA224: hashlib.sha224(),
            HashAlgorithm.SHA256: hashlib.sha256(),
            HashAlgorithm.SHA384: hashlib.sha384(),
            HashAlgorithm.SHA512: hashlib.sha512(),
            HashAlgorithm.BLAKE2B: hashlib.blake2b(digest_size=BLAKE_DIGEST_SIZE)
        }

        if "blake3" in sys.modules:
            # pylint: disable=E1102
            dict_algorithm[HashAlgorithm.BLAKE3] = blake3()

        try:
            hashing = dict_algorithm[algorithm]
        except KeyError:
            exit_with_error("Error while chosing algorithm", ErrorExitCode.CODE_ERROR)

        with open(file_path, 'rb') as file_bin:
            for block in iter(lambda: file_bin.read(4096), b''):
                hashing.update(block)

        if algorithm == HashAlgorithm.BLAKE3:
            return hashing.hexdigest(length=BLAKE_DIGEST_SIZE)

        return hashing.hexdigest()

    # TODO: merge fuzzy_renamer.py
    # @staticmethod
    # def from_random() -> str:

def is_path(path: str):
    abs_path = os.path.abspath(path)
    if os.path.isfile(abs_path) or os.path.isdir(abs_path):
        return abs_path

    exit_with_error('No such file or directory: ' + path, ErrorExitCode.USER_ERROR)


def is_dir(path: str):
    abs_path = os.path.abspath(path)
    if os.path.isdir(abs_path):
        return abs_path

    exit_with_error('Not a valid directory: ' + path, ErrorExitCode.USER_ERROR)

class RenameHelper:
    """Move files / renaming"""

    def __init__(self, dry_run: bool, _logger):
        self.__dry_run = dry_run
        self.__logger = _logger

    def __move(self, source: str, destination: str):
        """Move file / Rename"""
        if self.__dry_run:
            self.__logger.info("(dry-run)%s --> %s", source, destination)
        else:
            os.rename(source, destination)
            self.__logger.info("%s --> %s", source, destination)

    def move(self, source: str, destination: str):
        """Check if possible to rename/move, if True move"""

        if not os.path.isfile(source):
            exit_with_error("Cannot move dir", ErrorExitCode.CODE_ERROR)

        if os.path.isdir(destination):
            destination = destination + "/" + os.path.basename(source)
            self.move(source, destination)
            return

        if not os.path.exists(destination):
            self.__move(source, destination)
            return

        if os.path.samefile(source, destination):
            self.__logger.info("file %s already hashed", source)
            return

        iterator = 1
        prefix_path = os.path.splitext(destination)[0] + "_"
        postfix_path = os.path.splitext(destination)[1]
        while True:
            new_destination = prefix_path + str(iterator) + postfix_path
            if os.path.exists(new_destination):
                if os.path.samefile(source, new_destination):
                    self.__logger.info("file %s already hashed", source)
                    return
                iterator = iterator + 1
            else:
                self.__move(source, new_destination)
                return

def main():
    parser = argparse.ArgumentParser(
        description="Single python file to rename all files in a directory to \
            their hash sums.", add_help=True, allow_abbrev=False)

    parser.add_argument('-d',
                        '--dry-run',
                        default=False,
                        action='store_true',
                        help='dry run, doesn\'t rename or delete files')

    parser.add_argument('--debug',
                        default=False,
                        action='store_true',
                        help='Print debug logs')

    parser.add_argument('--silent',
                        default=False,
                        action='store_true',
                        help='SHHHHHHH!')

    parser.add_argument('-H',
                        '--hash',
                        default=DEFAULT_ALGORITHM,
                        choices=[HashAlgorithm.BLAKE3, HashAlgorithm.BLAKE2B,
                                 HashAlgorithm.MD5, HashAlgorithm.SHA1,
                                HashAlgorithm.SHA224, HashAlgorithm.SHA256,
                                HashAlgorithm.SHA384, HashAlgorithm.SHA512],
                        metavar="HASH",
                        help='hash that will be used: \
                        [md5/blake3/blake2/sha1/sha224/sha256/sha384/sha512')

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

    logging.basicConfig(format=LOGGING_FORMAT, level=logging.INFO)

    debug = argsp.debug

    if debug:
        logger.setLevel(logging.DEBUG)

    if argsp.silent:
        if argsp.debug:
            exit_with_error("Both --silent and --debug flags can not be" +
                            "declared together", ErrorExitCode.USER_ERROR)
        logger.setLevel(logging.WARNING)

    dry_run = argsp.dry_run

    if dry_run or debug:
        logger.info(vars(argsp))

    use_hash = argsp.hash

    if use_hash == HashAlgorithm.BLAKE3 and "blake3" not in sys.modules:
        exit_with_error("blake3 not found", ErrorExitCode.USER_ERROR)

    if DEFAULT_ALGORITHM == HashAlgorithm.MD5:
        logger.warning("blake3 not found, defaulting to md5!")

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
            exit_with_error("Input path is git repo!", ErrorExitCode.SOFT_ERROR)

        input_file_list = os.listdir(input_folder)

    elif os.path.isfile(argsp.input):
        input_folder = os.path.dirname(argsp.input)
        input_file_list = [os.path.basename(argsp.input)]

    output_folder = input_folder if argsp.output is None else argsp.output

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

    rename_helper = RenameHelper(dry_run, logger)

    for input_file_name in input_file_list:

        # "/in/" + "input.txt" -> "/in/input.txt"
        input_file_path = input_file_basepath + input_file_name

        # TODO: check if input_file_name == argv[0]
        # argv[0] == 'python rename.py' || './renamy.py' || ...
        if input_file_name == "rename.py":
            logger.info("Skipping source file %s", input_file_name)
            continue

        if os.path.isdir(input_file_path):
            logger.info("Skipping directory %s", input_file_name)
            continue

        if not os.path.isfile(input_file_path):
            exit_with_error("Not file or dir", ErrorExitCode.CODE_ERROR)
            break

        logger.debug("Trying to rename: %s", input_file_name)

        # only hash_string without path, name or extensions
        # return("01234567890abcdef01234567890abcd")
        output_file_name_only = NameGenerator.from_file_hash(input_file_path, use_hash)
        # output_file_name = "01234567890abcdef01234567890abcd" + ".txt"
        output_file_name = output_file_name_only + \
            os.path.splitext(input_file_path)[1].lower()
        output_file_path = output_file_basepath + output_file_name

        rename_helper.move(input_file_path, output_file_path)


if __name__ == "__main__":
    main()
