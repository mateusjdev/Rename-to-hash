# TODO

These options can be implemented, but in my use case, they are not relevant

- Skip extensions
  - .lnk (Windows Links/Shortcuts)
  - .* (Linux hidden dir/files)

- Colision related
  - `--inputs`: Add multiple folders, usualy I prefer `--recursive`
  - `--delete`: As now, due to hash colision, duplicated files are not deleted
  - `--confirm`: Use another hash to compare duplicated files, differ by size
  - `--preserve`: Location to move and preserve duplicated files
- `--json`: save logs/every action with json
- DEBUG: Create tests/CI
- Rewrite in Rust to utilize native implementation of blake3
- Logging to file (noob friendly/revert)
- Ask for user input in warnings
  - `--confirm` Continue/Stop/Ignore All
    - no extension file
    - in git repo
- TOML config file (~/.config/rename/)
  - hash, lenght, uppercase, verbose
  - ignore_warnings
- Check windows file name Limit
- Check permissions to rename files
- Arch Install MAKEPKG
- Color python logging -> <https://stackoverflow.com/questions/384076/how-can-i-color-python-logging-output>
