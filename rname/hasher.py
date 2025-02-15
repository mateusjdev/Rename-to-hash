import abc
import hashlib
import os
import string
from blake3 import blake3
from random import choices

from .clog import Log, ReturnCode as RetCode


class RenameAlgorithm:
    """List of Hashing Algorithms"""

    NOTSET = "NOTSET"
    SHA512 = "sha512"
    SHA384 = "sha384"
    SHA256 = "sha256"
    SHA224 = "sha224"
    SHA1 = "sha1"
    MD5 = "md5"
    BLAKE3 = "blake3"
    BLAKE2B = "blake2"
    FUZZY = "fuzzy"


log = Log()


class RenameHelper(metaclass=abc.ABCMeta):
    """Move files / renaming"""

    def __init__(self, dry_run_: bool, recursive_: bool, verbose_):
        self.__dry_run = dry_run_
        self.__recursive = recursive_
        self.__verbose = verbose_

    def __move(self, source: str, destination: str):
        """Move file / Rename"""

        if not self.__dry_run:
            os.rename(source, destination)

        if not self.__verbose:
            source = os.path.relpath(source)
            destination = os.path.relpath(destination)
        else:
            log.debug(f"CWD INP: {os.path.relpath(source)}")
            log.debug(f"CWD OUT: {os.path.relpath(destination)}")

        if self.__dry_run:
            log.info(f"(dry-run) {source} --> {destination}")
        else:
            log.info(f"{source} --> {destination}")

    def _check(self, source: str, destination: str) -> int:
        """Check if possible to rename/move, if True move"""

        # source exists?
        if not os.path.isfile(source):
            log.fatal("Cannot move dir", RetCode.CODE_ERROR)

        # destination path exists?
        destination_dir = os.path.dirname(destination)
        if not os.path.isdir(destination_dir):
            log.fatal(f"Cannot move to dir'{destination_dir}'", RetCode.CODE_ERROR)

        # filename with future source name exists?
        # if not move and return OK
        if not os.path.exists(destination):
            self.__move(source, destination)
            return 0

        # are source and destination the same?
        # if yes do nothing and return OK
        if os.path.samefile(source, destination):
            if self.__verbose:
                log.info(f"file {source} already hashed")
                return 0

            source = os.path.relpath(source)
            log.info(f"file {source} already hashed")
            return 0

        # dir ok to move file, but a equal filename already exists
        # FileExistsError: [Errno 17]
        return 17

    # @abc.abstractmethod
    # def name_generator(self):
    #    raise NotImplementedError("name_generator() method not implemented")

    @abc.abstractmethod
    def rename(self, source_file_path: str, dest_dir_path: str):
        raise NotImplementedError("rename() method not implemented")

    def enqueue_dir(self, input_dir_path: str, output_dir_path):
        input_dir_path = os.path.normpath(input_dir_path)
        output_dir_path = os.path.normpath(output_dir_path)

        # TODO: check behavior on links (folders, files, symlinks...)
        if not os.path.isdir(input_dir_path):
            log.fatal(f"Not a dir: '{input_dir_path}'", RetCode.CODE_ERROR)

        if not os.path.isdir(output_dir_path):
            log.fatal(f"Not a dir: '{output_dir_path}'", RetCode.CODE_ERROR)

        input_file_list = os.listdir(input_dir_path)

        # for input_file_name in os.listdir(input_dir_path):
        for input_file_name in input_file_list:
            # "/in/" + "input.txt" -> "/in/input.txt"
            input_file_path = os.path.join(input_dir_path, input_file_name)
            log.debug(f"Queued INP path: {input_file_path}")
            log.debug(f"Queued OUT path: {output_dir_path}")

            if os.path.isdir(input_file_path):
                if not self.__recursive:
                    log.debug(f"Skipping directory {input_file_name}")
                    continue

                log.debug(f"Enqueing directory {input_file_path}")
                self.enqueue_dir(input_file_path, input_file_path)
                continue

            # @DEPRECATED
            # This has no use since the script is supposed to be installed by pip

            # TODO: check if input_file_name == argv[0]
            # argv[0] == 'python rename.py' || './renamy.py' || ...
            if input_file_name == "rname.py":
                log.info(f"Skipping source file {input_file_name}")
                continue

            # TODO: remove duplicated checks
            if not os.path.isfile(input_file_path):
                log.fatal("Not file or dir", RetCode.CODE_ERROR)
                break

            log.debug(f"Trying to rename: {input_file_name}")

            self.rename(input_file_path, output_dir_path)

    # TODO: use os.walk()
    def enqueue_path(self, input_path: str, output_path: str):
        # TODO: remove duplicated checks
        input_path = os.path.normpath(input_path)
        output_path = os.path.normpath(output_path)

        if not os.path.isdir(output_path):
            log.fatal(f"Not a dir: '{output_path}'", RetCode.CODE_ERROR)

        if os.path.isdir(input_path):
            self.enqueue_dir(input_path, output_path)
            return

        if os.path.isfile(input_path):
            # TODO: check if input_file_name == argv[0]
            # argv[0] == 'python rename.py' || './renamy.py' || ...
            if input_path == "rename.py":
                log.info(f"Skipping source file {input_path}")
                return

            self.rename(input_path, output_path)
            return

        log.fatal(f"Not a file/dir: '{input_path}'", RetCode.CODE_ERROR)


class HashRenameHelper(RenameHelper):
    """Rename files using file hashsum"""

    # blake3 default lenght is 32, but to avoid long file names in windows I
    # recomend setting this to 16
    # obs: in blake2b (64 as default) setting this as 16 will generate a totally
    # diferent hash
    # https://learn.microsoft.com/windows/win32/fileio/maximum-file-path-limitation
    __blake_digest_size = 16

    def __init__(
        self,
        dry_run_: bool,
        recursive_: bool,
        verbose_: bool,
        hash_algorithm: str,
        _lenght: int,
        _uppercase: bool,
    ):
        super().__init__(dry_run_, recursive_, verbose_)

        if _lenght:
            self.__blake_digest_size = _lenght

        self._uppercase = _uppercase

        if hash_algorithm == RenameAlgorithm.NOTSET:
            self.__hash_algorithm = RenameAlgorithm.BLAKE3
            log.warning("Hash Algorithm: defaulting to blake3!")
            return

        self.__hash_algorithm = hash_algorithm
        log.debug(f"Hash Algorithm: {self.__hash_algorithm}")

    def __name_generator(self, file_path: str) -> str:
        """Generate a string of characters based on file and hash algorithm given as param"""

        if not os.path.isfile(file_path):
            log.fatal(f"Not a valid file: '{file_path}'", RetCode.USER_ERROR)

        dict_algorithm = {
            RenameAlgorithm.MD5: hashlib.md5(),
            RenameAlgorithm.SHA1: hashlib.sha1(),
            RenameAlgorithm.SHA224: hashlib.sha224(),
            RenameAlgorithm.SHA256: hashlib.sha256(),
            RenameAlgorithm.SHA384: hashlib.sha384(),
            RenameAlgorithm.SHA512: hashlib.sha512(),
            RenameAlgorithm.BLAKE2B: hashlib.blake2b(
                digest_size=self.__blake_digest_size
            ),
            RenameAlgorithm.BLAKE3: blake3(),
        }

        try:
            hashing = dict_algorithm[self.__hash_algorithm]
        except KeyError:
            log.fatal("Error while chosing algorithm", RetCode.CODE_ERROR)

        with open(file_path, "rb") as file_bin:
            for block in iter(lambda: file_bin.read(4096), b""):
                hashing.update(block)

        if self.__hash_algorithm == RenameAlgorithm.BLAKE3:
            return hashing.hexdigest(length=self.__blake_digest_size)

        return hashing.hexdigest()

    def rename(self, source_file_path: str, dest_dir_path: str):
        if not os.path.isfile(source_file_path):
            log.fatal(f"Not a file: '{source_file_path}'", RetCode.CODE_ERROR)

        if not os.path.isdir(dest_dir_path):
            log.fatal(f"Not a folder: '{dest_dir_path}'", RetCode.CODE_ERROR)

        file_name = (
            self.__name_generator(source_file_path).upper()
            if self._uppercase
            else self.__name_generator(source_file_path)
        )
        file_extension = os.path.splitext(source_file_path)[1].lower()

        # return 0 = return
        # return >0 = continue
        if not super()._check(
            source_file_path, os.path.join(dest_dir_path, file_name + file_extension)
        ):
            return

        # 17 FileExistsError
        iterator = 1
        # Limit maybe? for i in range(1,1000)?
        while True:
            # return 0 = return
            string()
            file_postfix = f"_{iterator}"
            if not super()._check(
                source_file_path,
                os.path.join(dest_dir_path, file_name + file_postfix + file_extension),
            ):
                return
            # return >0 = continue
            iterator = iterator + 1
            continue


class RandomRenameHelper(RenameHelper):
    """Rename files using random characters"""

    # 62^16 - setting this very low can cause problems
    # __DICTIONARY = string.digits + string.ascii_letters
    __filename_size = 16

    def __init__(
        self,
        dry_run_: bool,
        recursive_: bool,
        verbose_: bool,
        _lenght: int,
        _uppercase: bool,
    ):
        super().__init__(dry_run_, recursive_, verbose_)

        if _lenght:
            self.__filename_size = _lenght

        self.__dictionary = (
            string.ascii_uppercase + string.digits
            if _uppercase
            else string.digits + string.ascii_letters
        )

    def __name_generator(self) -> str:
        return "".join(choices(self.__dictionary, k=self.__filename_size))

    def rename(self, source_file_path: str, dest_dir_path: str):
        if not os.path.isfile(source_file_path):
            log.fatal(f"Not a file: '{source_file_path}'", RetCode.CODE_ERROR)

        if not os.path.isdir(dest_dir_path):
            log.fatal(f"Not a folder: '{dest_dir_path}'", RetCode.CODE_ERROR)

        file_extension = os.path.splitext(source_file_path)[1].lower()

        # Limit maybe? for i in range(1,1000)?
        while True:
            file_name = self.__name_generator()
            # return 0 = return
            if not super()._check(
                source_file_path,
                os.path.join(dest_dir_path, file_name + file_extension),
            ):
                return
            # return >0 = continue
            # 17 FileExistsError
            continue
