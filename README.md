# Rename Files to Hash

Single python file to rename all files in a directory to their hash sums

## Usage

Requirements:

- [python](https://www.python.org/)
- [blake3](https://pypi.org/project/blake3/)

To run the script open a command prompt/shell and type in: `python rename.py -i PATH/TO/DIR`
This will rename all files to the selected hashing algorithm (`blake3` is default, `md5` is fallback).

> [!warning]
> **Hashsum libraries can have collisions**: Some hashed files can be diferent and have the same checksum causing one of them to be deleted. You can learn an example of MD5 collision [here](https://www.mscs.dal.ca/~selinger/md5collision/).

## Options

```txt
-h, --help            show this help message and exit
-d, --dry-run         dry run, doesn't rename or delete files
--debug               Print debug logs
--silent              SHHHHHHH! Doesn't print to stdout, way faster!
-H HASH, --hash HASH  hash that will be used: [md5/blake3/blake2/sha1/sha224/sha256/sha384/sha512/fuzzy]
-i DIR/FILE, --input DIR/FILE
                      Files that will be hashed
-o DIR, --output DIR  Location were hashed files will be stored
-v, --version         show program's version number and exit
-l LENGHT, --lenght LENGHT
                      Lenght used in filename for blake3 and fuzzy algorithms
-u, --uppercase       Convert characters to UPPERCASE when possible
-r, --recursive       Recurse DIRs, when enabled, will not accept output folder
-V, --verbose         Show full path
```

**Supported hashes:** `md5 / blake3 / blake2 / sha1 / sha224 / sha256 / sha384 / sha512 / fuzzy`

---

[Algorithm Benchmarks](docs/README.md)

[TODO: Possible improvements](docsTODO.md)
