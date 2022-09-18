# Doctool 2

An extension on the original _live doc_, but this version implements django at the root, to simplify aggregation and indexing of discovered files.

1. Read a dir
2. index all files


## Run

A user should be able to present:

+ A single file
+ A directory

A single file may be:

+ A target .md file
+ A Config file

When given a directory, it should be tested for a config file, else the directory
is used with a blank config.
