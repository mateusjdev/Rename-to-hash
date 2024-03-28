import os
import sys
import hashlib
import argparse
import logging
import string
import random

class RenameAlgorithm:
    """List of Hashing Algorithms"""
    NOTSET = "NOTSET"
    SHA512 = "sha512"
    SHA384 = "sha384"
    SHA256 = "sha256"
    SHA224 = "sha224"
    SHA1  = "sha1"
    MD5 = "md5"
    BLAKE3 = "blake3"
    BLAKE2B = "blake2"
    FUZZY = "fuzzy"

class ErrorExitCode:
    """List of Error Exit Codes"""
    USER_ERROR = 3
    CODE_ERROR = 4
    SOFT_ERROR = 5

# blake3 not available on aarch64
# https://github.com/oconnor663/blake3-py/issues/28
try:
    from blake3 import blake3
except ModuleNotFoundError:
    pass

VERSION = "v2.4"

# TODO: better format for logging (https://stackoverflow.com/q/384076)
LOGGING_FORMAT = 'rename.py: %(message)s'

logger = logging.getLogger(__name__)

# TODO: raise Exception
# TODO: use kwargs
def exit_with_error(error: str, err_nu: int):
    logger.critical("ERROR: %s", error)
    sys.exit(err_nu)

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

    def getLogger(self):
        return self.__logger

    def _check(self, source: str, destination: str) -> int:
        """Check if possible to rename/move, if True move"""

        # source exists?
        if not os.path.isfile(source):
            exit_with_error("Cannot move dir", ErrorExitCode.CODE_ERROR)

        # destination path exists?
        destination_dir = os.path.dirname(destination)
        if not os.path.isdir(destination_dir):
            exit_with_error("Cannot move to dir" + destination_dir, ErrorExitCode.CODE_ERROR)

        # filename with future source name exists?
        # if not move and return OK
        if not os.path.exists(destination):
            self.__move(source, destination)
            return 0

        # are source and destination the same?
        # if yes do nothing and return OK
        if os.path.samefile(source, destination):
            self.__logger.info("file %s already hashed", source)
            return 0

        # dir ok to move file, but a equal filename already exists
        # FileExistsError: [Errno 17]
        return 17

class HashRenameHelper(RenameHelper):
    """Rename files using file hashsum"""

    # blake3 default lenght is 32, but to avoid long file names in windows I
    # recomend setting this to 16
    # obs: in blake2b (64 as default) setting this as 16 will generate a totally
    # diferent hash
    # https://learn.microsoft.com/windows/win32/fileio/maximum-file-path-limitation
    __BLAKE_DIGEST_SIZE = 16
    __IMPORTED_BLAKE3 = "blake3" in sys.modules

    def __init__(self, dry_run: bool, _logger, hash_algorithm: str):
        if hash_algorithm == RenameAlgorithm.BLAKE3 and not self.__IMPORTED_BLAKE3:
            exit_with_error("blake3 not found, please run 'pip install blake3' or choose another" +
                            "algorithm", ErrorExitCode.USER_ERROR)

        super().__init__(dry_run, _logger)

        if hash_algorithm == RenameAlgorithm.NOTSET and not self.__IMPORTED_BLAKE3:
            super().getLogger().warning("blake3 not found, defaulting to md5!")
            self.__hash_algorithm = RenameAlgorithm.MD5
            return

        self.__hash_algorithm = RenameAlgorithm.BLAKE3 if hash_algorithm == RenameAlgorithm.NOTSET \
            else hash_algorithm

        super().getLogger().debug("Hash Algorithm: %s", self.__hash_algorithm)

    def __name_generator(self, file_path: str) -> str:
        """Generate a string of characters based on file and hash algorithm given as param"""

        if not os.path.isfile(file_path):
            exit_with_error("Not a valid file:" + file_path, ErrorExitCode.USER_ERROR)

        dict_algorithm = {
            RenameAlgorithm.MD5: hashlib.md5(),
            RenameAlgorithm.SHA1: hashlib.sha1(),
            RenameAlgorithm.SHA224: hashlib.sha224(),
            RenameAlgorithm.SHA256: hashlib.sha256(),
            RenameAlgorithm.SHA384: hashlib.sha384(),
            RenameAlgorithm.SHA512: hashlib.sha512(),
            RenameAlgorithm.BLAKE2B: hashlib.blake2b(digest_size=self.__BLAKE_DIGEST_SIZE)
        }

        if self.__IMPORTED_BLAKE3:
            # pylint: disable=E1102
            dict_algorithm[RenameAlgorithm.BLAKE3] = blake3()

        try:
            hashing = dict_algorithm[self.__hash_algorithm]
        except KeyError:
            exit_with_error("Error while chosing algorithm", ErrorExitCode.CODE_ERROR)

        with open(file_path, 'rb') as file_bin:
            for block in iter(lambda: file_bin.read(4096), b''):
                hashing.update(block)

        if self.__hash_algorithm == RenameAlgorithm.BLAKE3:
            return hashing.hexdigest(length=self.__BLAKE_DIGEST_SIZE)

        return hashing.hexdigest()

    def rename(self, source_file_path: str, dest_dir_path: str):
        if not os.path.isfile(source_file_path):
            exit_with_error(f"Not a file: '{source_file_path}'", ErrorExitCode.CODE_ERROR)

        if not os.path.isdir(dest_dir_path):
            exit_with_error(f"Not a folder: '{dest_dir_path}'", ErrorExitCode.CODE_ERROR)

        file_name = self.__name_generator(source_file_path)
        file_extension = os.path.splitext(source_file_path)[1].lower()

        # return 0 = return
        # return >0 = continue
        if not super()._check(source_file_path, dest_dir_path +  file_name + file_extension):
            return

        # 17 FileExistsError
        iterator = 1
        # Limit maybe? for i in range(1,1000)?
        while True:
            # return 0 = return
            file_postfix = "_" + str(iterator)
            if not super()._check(source_file_path, dest_dir_path +  file_name +
                            file_postfix + file_extension):
                return
            # return >0 = continue
            iterator = iterator + 1
            continue


class RandomRenameHelper(RenameHelper):
    """Rename files using random characters"""

    # 62^16 - setting this very low can cause problems
    __DICTIONARY = string.digits + string.ascii_letters
    __FILENAME_SIZE = 16

    def __name_generator(self) -> str:
        return ''.join(random.choices(self.__DICTIONARY, k=self.__FILENAME_SIZE))

    # TODO: Add atributte 'LENGHT'
    def rename(self, source_file_path: str, dest_dir_path: str):
        if not os.path.isfile(source_file_path):
            exit_with_error(f"Not a file: '{source_file_path}'", ErrorExitCode.CODE_ERROR)

        if not os.path.isdir(dest_dir_path):
            exit_with_error(f"Not a folder: '{dest_dir_path}'", ErrorExitCode.CODE_ERROR)

        file_extension = os.path.splitext(source_file_path)[1].lower()

        # Limit maybe? for i in range(1,1000)?
        while True:
            file_name = self.__name_generator()
            # return 0 = return
            if not super()._check(source_file_path, dest_dir_path +  file_name + file_extension):
                return
            # return >0 = continue
            # 17 FileExistsError
            continue


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
                        default=RenameAlgorithm.NOTSET,
                        choices=[RenameAlgorithm.BLAKE3, RenameAlgorithm.BLAKE2B,
                                 RenameAlgorithm.MD5, RenameAlgorithm.SHA1,
                                RenameAlgorithm.SHA224, RenameAlgorithm.SHA256,
                                RenameAlgorithm.SHA384, RenameAlgorithm.SHA512,
                                RenameAlgorithm.FUZZY],
                        metavar="HASH",
                        help='hash that will be used: \
                        [md5/blake3/blake2/sha1/sha224/sha256/sha384/sha512/fuzzy]')

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

    if not input_file_list:
        logger.info("No files, nothing to do!")
        return

    rename_helper = RandomRenameHelper(dry_run, logger) if use_hash == RenameAlgorithm.FUZZY \
        else HashRenameHelper(dry_run, logger, use_hash)

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

        rename_helper.rename(input_file_path, output_file_basepath)

if __name__ == "__main__":
    main()
