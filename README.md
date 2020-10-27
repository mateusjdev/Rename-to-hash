# Rename-Files-To-Hash
#### Single python file to rename all files in a directory to their hash sums.

---

### Run the file
The file is written in the language `python` which means you have to have `python` installed.
If not: Do so [here](https://www.python.org/).

To run the script open a command prompt/shell and type in: `python rename.py`
This will rename all files to the selected hashing algorithm (`md5` is default).

#### Supported hashes
```
md5 / sha1 / sha224 / sha256 / sha384 / sha512
```

> :warning: **Hashsum libraries can have collisions**: Some hashed files can be diferent and have the same checksum causing one of them to be deleted. You can learn an example of MD5 collision [here](https://www.mscs.dal.ca/~selinger/md5collision/).

#### Usage
```
Usage: rename.py [OPTIONS]

Options:
  -h            Print this help text and exit
  -H HASH       Hash that will be used: [md5/sha1/sha224/sha256/sha384/sha512]
  -i DIR/FILE   Files that will be hashed
  -o DIR        Location were hashed files will be stored
  -r            (Soon) Recursive
  -s FILE       (Soon) Saves a log in .json format
  -l            (Soon) log only, doesn't rename or delete files
```
