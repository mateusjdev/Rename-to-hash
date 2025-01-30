# Rename Files to Hash

Single python file to rename all files in a directory to their hash sums

## Install & Usage

Requirements:

- [python](https://python.org/)
- [blake3](https://pypi.org/project/blake3/) - Installed through pip/pipx/uv

The best way to run the script is using tools like  `pipx`/`uv` to install to the path:

```shell
git clone https://github.com/mateusjdev/rename-files-to-hash
cd rename-files-to-hash
pipx install ./

# or with uv (prefered)
uv tool install ./

# run from any path
rname --help
```

Another way is executing from a command prompt/shell:

```shell
python rname/rname.py -i PATH/TO/DIR
```

This will rename all files to the selected hashing algorithm (`blake3` is the default).

> [!warning]
> **Hashsum libraries can have collisions**: Some hashed files can be diferent and have the same checksum causing one of them to be deleted. You can learn an example of MD5 collision [here](https://www.mscs.dal.ca/~selinger/md5collision/).

## Options

```txt
-h, --help            show this help message and exit
-d, --dry-run         dry run, doesn't rename or delete files
--debug               Print debug logs
--silent              SHHHHHHH! Doesn't print to stdout, way faster!
-H HASH, --hash HASH  hash that will be used: [md5/blake3/blake2/sha1/sha224/sha256/sha384/sha512/fuzzy]
-i DIR/FILE, --input DIR/FILE [default="./"]
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
