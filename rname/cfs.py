import os
from clog import Log, ReturnCode as RetCode
from shutil import which
from subprocess import call, DEVNULL

log = Log()


def is_path(path: str) -> str:
    path = os.path.abspath(path)
    if os.path.isfile(path) or os.path.isdir(path):
        return path

    log.fatal(f"No such file or directory: '{path}'", RetCode.USER_ERROR)


def is_dir(path: str) -> str:
    path = os.path.abspath(path)
    if os.path.isdir(path):
        return path

    log.fatal(f"Not a valid directory: '{path}'", RetCode.USER_ERROR)


def is_git_dir(path: str) -> bool:
    # ignore check if --input is a file
    if not is_dir(path):
        return False

    # TODO: Improve .git repo detection
    if which("git"):
        if (
            call(
                ["git", "-C", os.path.normpath(path), "rev-parse"],
                stderr=DEVNULL,
                stdout=DEVNULL,
            )
            == 0
        ):
            return True
    # TODO: walk directory sctructure
    elif os.path.exists(os.path.join(path, ".git")):
        return True

    return False
