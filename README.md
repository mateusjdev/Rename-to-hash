# Rename Files to Hash

Single python file to rename all files in a directory to their hash sums

## Usage

The file is written in the language `python` which means you have to have `python` installed. If not, do so [here](https://www.python.org/).

To run the script open a command prompt/shell and type in: `python rename.py`
This will rename all files to the selected hashing algorithm (`md5` is default).

> :warning: **Hashsum libraries can have collisions**: Some hashed files can be diferent and have the same checksum causing one of them to be deleted. You can learn an example of MD5 collision [here](https://www.mscs.dal.ca/~selinger/md5collision/).

## Options

```txt
-h            Print this help text and exit
-d            Dry run, doesn't rename files
-H HASH       Hash that will be used: [md5/sha1/sha224/sha256/sha384/sha512]
-i DIR/FILE   Files that will be hashed
-o DIR        Location were hashed files will be stored
```

**Supported hashes:** `md5 / sha1 / sha224 / sha256 / sha384 / sha512`

## TODO
- Print only common path to logs
- Add -r/--recursive
- Add multiple -i/--inputs || Fix multiple -i/--inputs
- Normalize file extensions (.MP4 -> .mp4)
- Check if in .git repo
- Add blake2b and blake3
- Remove sha1, sha224, sha384

## Possible Improvements

These options can be implemented easily, but in my use case, they are not relevant

- Colision related
  - "--delete": As now, due to hash colision, duplicated files are not deleted
  - "--confirm": Use another hash to compare duplicated files
  - "--preserve": Location to move and preserve duplicated files
- "--json": save logs/every action with json
- DEBUG: Create tests
