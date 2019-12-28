# dslogparser
Parse FIRST FRC Driver Station log files.

The DSLogParser class can parse FRC .dslog files and extract each entry, which are returned as dictionaries.

The DSEventParser class parses FRC .dsevents, including extracting the match information.

The script dslog2csv.py can read one or many .dslog files to produce CSV file(s).
It can combine .dslog and .dsevents files if the filenames match. See ```dslog2csv.py -h``` for usage information.
