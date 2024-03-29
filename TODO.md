# TODO

These options can be implemented, but in my use case, they are not relevant

- Colision related
  - `--inputs`: Add multiple folders, usualy I prefer `--recursive`
  - `--delete`: As now, due to hash colision, duplicated files are not deleted
  - `--confirm`: Use another hash to compare duplicated files
  - `--preserve`: Location to move and preserve duplicated files
- `--json`: save logs/every action with json
- DEBUG: Create tests
- Rewrite in Rust to utilize native implementation of blake3
- Logging to file (noob friendly/revert)
- Ask for user input in warnings
    - `--confirm` Continue/Stop/Ignore All
        - no extension file
        - in git repo
- TOML config file
    - hash, lenght, uppercase, verbose
    - ignore_warnings
- Check windows file name Limit
- Check permissions to rename files
- Arch Install MAKEPKG
