#!/usr/bin/env python3

# Note: should work correctly with either Python 2 or 3
from __future__ import print_function

# Parse the FRC drive station logs which are packed binary data

import sys
import os
import os.path
import csv
import re

from dslogparser import DSLogParser, DSEventParser

OUTPUT_COLUMNS = [
    'time', 'file_time', 'round_trip_time', 'packet_loss', 'voltage', 'rio_cpu',
    'robot_disabled', 'robot_auto', 'robot_tele',
    'ds_disabled', 'ds_auto', 'ds_tele',
    'watchdog', 'brownout',
    'can_usage', 'wifi_db', 'bandwidth',
    'pd_id',
    'pd_total_current',
    # don't output these. They are not correct
    # 'pd_resistance', 'pd_voltage', 'pd_temp'
]


def find_event_file(filename):
    evtname = os.path.splitext(filename)[0] + '.dsevents'
    if os.path.exists(evtname):
        return evtname
    return None


def main():
    import argparse
    parser = argparse.ArgumentParser(description='FRC DSLog to CSV file')
    parser.add_argument('--one-output-per-file', action='store_true', help='Output one CSV per DSLog file')
    parser.add_argument('--output', '-o', help='Output filename (stdout otherwise)')
    parser.add_argument('--event', action='store_true', help='Input files are EVENT files')
    parser.add_argument('--add-match-info', action='store_true', help='Look for EVENT files matching DSLOG files and pull info')
    parser.add_argument('--matches-only', action='store_true', help='Ignore files which have no match info. Imples add-match-info')
    parser.add_argument('files', nargs='+', help='Input files')

    args = parser.parse_args()

    if args.matches_only:
        args.add_match_info = True

    if sys.platform == "win32":
        # do glob expanding on Windows. Linux/Mac does this automatically.
        import glob
        newfiles = []
        for a in args.files:
            newfiles.extend(glob.glob(a))
        args.files = newfiles

    if args.event:
        dsparser = DSEventParser(args.files[0])
        for rec in dsparser.read_records():
            print(rec['time'], rec['message'])

    else:
        base_cols = ['inputfile', ]
        if args.add_match_info:
            base_cols.extend(('match_name', 'field_time'))
        base_cols.extend(OUTPUT_COLUMNS)

        outstrm = None
        outcsv = None

        for fn in args.files:
            match_info = None
            if args.add_match_info:
                evtfn = find_event_file(fn)
                if evtfn:
                    match_info = DSEventParser.find_match_info(evtfn)

            if args.matches_only and not match_info:
                continue

            # different PD devices have different numbers of columns
            # so we need to wait on opening the file

            dsparser = DSLogParser(fn)
            for rec in dsparser.read_records():
                rec['inputfile'] = fn
                if match_info:
                    rec.update(match_info)

                # unpack the pd currents to go into columns more easily
                for i in range(len(rec['pd_currents'])):
                    rec['pd_{}'.format(i)] = rec['pd_currents'][i]

                if outstrm is None:
                    cols = base_cols
                    cols.extend( [k for k in rec.keys() if re.match('^pd_[0-9]+$', k)] )
                    outname, _ = os.path.splitext(os.path.basename(fn))
                    outname += '.csv'
                    outstrm = open(outname, 'w')
                    outcsv = csv.DictWriter(outstrm, fieldnames=cols, extrasaction='ignore')
                    outcsv.writeheader()

                outcsv.writerow(rec)

            dsparser.close()
            if not args.one_output_per_file and outstrm:
                outstrm.close()
                outstrm = None

        if outstrm:
            outstrm.close()

main()