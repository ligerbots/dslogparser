# dslogparser
Parse FIRST FRC Driver Station log files.

This repository hosts 2 PyPI packages:
* dslogparser includes the basic parsing library, plus a command line script to output CSV files
* dslogs contains the DSlogs class which is useful for streaming log entries to "real time" application.

# Reference Sources:
  https://www.chiefdelphi.com/forums/showthread.php?p=1556451

Particularly:
  https://www.chiefdelphi.com/forums/showpost.php?p=1556451&postcount=11
  
Program: https://github.com/orangelight/DSLOG-Reader

However, DSLog-Reader does not seem to be fully correct:
* It unpacks the "packet loss" value as a *signed* integer. Unsigned gives more sensible answers (https://github.com/orangelight/DSLOG-Reader/issues/3)
* There is a bug in FormMain::BoolNameToValue(): wrong string for "Robo Tele" and "Watchdog" returns the Brownout value. (https://github.com/orangelight/DSLOG-Reader/issues/2)
