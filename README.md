# dslog2csv
Convert FRC DSLog files to CSV file

usage: dslog2csv.py [-h] [--one-output-per-file] [--output OUTPUT] [--event]
                    [--add-match-info] [--matches-only]
                    files [files ...]

DSLog to CSV file

positional arguments:
  files                 Input files

optional arguments:
  -h, --help            show this help message and exit
  --one-output-per-file
                        Output one CSV per DSLog file
  --output OUTPUT, -o OUTPUT
                        Output filename (stdout otherwise)
  --event               Input files are EVENT files
  --add-match-info      Look for EVENT files matching DSLOG files and pull
                        info
  --matches-only        Ignore files which have no match info. Imples add-
                        match-info


# Reference Sources:
  https://www.chiefdelphi.com/forums/showthread.php?p=1556451

Particularly:
  https://www.chiefdelphi.com/forums/showpost.php?p=1556451&postcount=11
  
Program: https://github.com/orangelight/DSLOG-Reader

However, DSLog-Reader does not seem to be fully correct:
* It unpacks the "packet loss" value as a *signed* integer. Unsigned gives more sensible answers (https://github.com/orangelight/DSLOG-Reader/issues/3)
* There is a bug in FormMain::BoolNameToValue(): wrong string for "Robo Tele" and "Watchdog" returns the Brownout value. (https://github.com/orangelight/DSLOG-Reader/issues/2)
* It does not reverse the PDP values, as indicated in the Chief Delphi post (but I don't have another reference).
