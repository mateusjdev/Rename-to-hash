# Algorithm Benchmarks

In version 2.2, with the implementation of the blake3 algorithm, several algorithms were benchmarked:

**Dataset:** Total of 4161 image files, 10KB to 4MB per file and 609MB total

**System:** linux (ramdisk)

**Command:**

```shell
hyperfine --export-markdown ../result.md --runs 20 \
--prepare 'fuzzy_rename.py -i .' 'rename.py -i . -H md5' \
--prepare 'fuzzy_rename.py -i .' 'rename.py -i . -H blake3' \
--prepare 'fuzzy_rename.py -i .' 'rename.py -i . -H sha1' \
--prepare 'fuzzy_rename.py -i .' 'rename.py -i . -H sha224' \
--prepare 'fuzzy_rename.py -i .' 'rename.py -i . -H sha256' \
--prepare 'fuzzy_rename.py -i .' 'rename.py -i . -H sha384' \
--prepare 'fuzzy_rename.py -i .' 'rename.py -i . -H sha512'
```

## Result

| Command | Mean [s]      | Min [s] | Max [s] | Relative    |
| :---    | :--:          | :--:    | :--:    | :--:        |
| sha1    | 0.815 ± 0.010 | 0.799   | 0.836   | 1.00        |
| sha256  | 0.833 ± 0.012 | 0.822   | 0.867   | 1.02 ± 0.02 |
| sha224  | 0.855 ± 0.014 | 0.835   | 0.883   | 1.05 ± 0.02 |
| blake3  | 0.955 ± 0.014 | 0.932   | 0.980   | 1.17 ± 0.02 |
| md5     | 1.347 ± 0.013 | 1.323   | 1.370   | 1.65 ± 0.03 |
| sha512  | 1.432 ± 0.018 | 1.409   | 1.473   | 1.76 ± 0.03 |
| sha384  | 1.441 ± 0.018 | 1.414   | 1.491   | 1.77 ± 0.03 |

## TODO

- Benchmark on windows
- Use normal file system
- Try on a bigger dataset
- Merge fuzzy_rename.py with rename.py
