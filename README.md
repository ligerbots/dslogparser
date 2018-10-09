# dslog2csv
Convert FRC DSLog files to CSV file

WARNING: the 8 status values (ds tele, robot tele, etc) should not be trusted, yet.

# Reference Sources:
  https://www.chiefdelphi.com/forums/showthread.php?p=1556451

Particularly:
  https://www.chiefdelphi.com/forums/showpost.php?p=1556451&postcount=11
  
Program: https://github.com/orangelight/DSLOG-Reader

However, DSLog-Reader does not seem to be fully correct:
* It unpacks the "packet loss" value as a *signed* integer. Unsigned gives more sensible answers (https://github.com/orangelight/DSLOG-Reader/issues/3)
* There is a bug in FormMain::BoolNameToValue(): wrong string for "Robo Tele" and "Watchdog" returns the Brownout value. (https://github.com/orangelight/DSLOG-Reader/issues/2)
* It does not reverse the PDP values, as indicated in the Chief Delphi post (but I don't have another reference).
