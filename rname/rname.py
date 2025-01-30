import argparse
import cfs
import os
from clog import LogLevel, Log, ReturnCode as RetCode
from hasher import RenameAlgorithm, HashRenameHelper, RandomRenameHelper

VERSION = "v3.1"

log = Log()


def main():
    parser = argparse.ArgumentParser(
        description="Single python file to rename all files in a directory to their hash sums.",
        add_help=True,
        allow_abbrev=False,
    )

    parser.add_argument(
        "-d",
        "--dry-run",
        default=False,
        action="store_true",
        help="dry run, doesn't rename or delete files",
    )

    parser.add_argument(
        "--debug", default=False, action="store_true", help="Print debug logs"
    )

    parser.add_argument(
        "--silent",
        default=False,
        action="store_true",
        help="SHHHHHHH! Doesn't print to stdout (runs way faster!) ",
    )

    parser.add_argument(
        "-H",
        "--hash",
        default=RenameAlgorithm.NOTSET,
        choices=[
            RenameAlgorithm.BLAKE3,
            RenameAlgorithm.BLAKE2B,
            RenameAlgorithm.MD5,
            RenameAlgorithm.SHA1,
            RenameAlgorithm.SHA224,
            RenameAlgorithm.SHA256,
            RenameAlgorithm.SHA384,
            RenameAlgorithm.SHA512,
            RenameAlgorithm.FUZZY,
        ],
        metavar="HASH",
        help="hash that will be used: \
                        [md5/blake3/blake2/sha1/sha224/sha256/sha384/sha512/fuzzy]",
    )

    parser.add_argument(
        "-i",
        "--input",
        metavar="DIR/FILE",
        type=cfs.is_path,
        default=os.getcwd(),
        action="store",
        help="Files that will be hashed",
    )

    parser.add_argument(
        "-o",
        "--output",
        metavar="DIR",
        type=cfs.is_dir,
        action="store",
        help="Location were hashed files will be stored",
    )

    parser.add_argument("-v", "--version", action="version", version=VERSION)

    parser.add_argument(
        "-l",
        "--lenght",
        type=int,
        default=0,
        action="store",
        help="Lenght used in filename for blake3 and fuzzy algorithms",
    )

    parser.add_argument(
        "-u",
        "--uppercase",
        default=False,
        action="store_true",
        help="Convert characters to UPPERCASE when possible",
    )

    parser.add_argument(
        "-r",
        "--recursive",
        default=False,
        action="store_true",
        help="Recurse DIRs, when enabled, will not accept output folder",
    )

    parser.add_argument(
        "-V", "--verbose", default=False, action="store_true", help="Show full path"
    )

    argsp = parser.parse_args()

    if argsp.debug:
        log.setLevel(LogLevel.DEBUG)

    if argsp.silent:
        if argsp.debug:
            log.fatal(
                "Both --silent and --debug flags can not be declared together",
                RetCode.USER_ERROR,
            )
        log.setLevel(LogLevel.WARNING)

    if argsp.dry_run or argsp.debug:
        log.info(vars(argsp))

    if cfs.is_git_dir(argsp.input) and not argsp.debug:
        log.fatal("Input path is git repo!", RetCode.SOFT_ERROR)

    rename_helper = (
        RandomRenameHelper(
            argsp.dry_run,
            argsp.recursive,
            argsp.verbose,
            argsp.lenght,
            argsp.uppercase,
        )
        if argsp.hash == RenameAlgorithm.FUZZY
        else HashRenameHelper(
            argsp.dry_run,
            argsp.recursive,
            argsp.verbose,
            argsp.hash,
            argsp.lenght,
            argsp.uppercase,
        )
    )

    # if --recursive and --output be declared together, all diferent folders traversed will be
    # renamed to the same output folder
    if argsp.recursive and argsp.output:
        log.fatal(
            "--recursive and --output cannot be declared together!",
            RetCode.SOFT_ERROR,
        )

    rename_helper.enqueue_path(
        argsp.input, argsp.input if argsp.output is None else argsp.output
    )


if __name__ == "__main__":
    main()
