#!/usr/bin/env python3

# Note: should work correctly with either Python 2 or 3
from __future__ import print_function

# Parse the FRC drive station logs which are packed binary data

import sys
import os
import os.path
import csv
from dslogparser import DSLogParser, DSEventParser

# Python 2 CSV writer wants binary output, but Py3 want regular
_USE_BINARY_OUTPUT = sys.version_info[0] == 2

OUTPUT_COLUMNS = [
    'time', 'round_trip_time', 'packet_loss', 'voltage', 'rio_cpu',
    'robot_disabled', 'robot_auto', 'robot_tele',
    'ds_disabled', 'ds_auto', 'ds_tele',
    'watchdog', 'brownout',
    'can_usage', 'wifi_db', 'bandwidth',
    'pdp_id',
    'pdp_0', 'pdp_1', 'pdp_2', 'pdp_3', 'pdp_4', 'pdp_5', 'pdp_6', 'pdp_7',
    'pdp_8', 'pdp_9', 'pdp_10', 'pdp_11', 'pdp_12', 'pdp_13', 'pdp_14', 'pdp_15',
    'pdp_total_current',
    # don't output these. They are not correct
    # 'pdp_resistance', 'pdp_voltage', 'pdp_temp'
]


def find_event_file(filename):
    evtname = os.path.splitext(filename)[0] + '.dsevents'
    if os.path.exists(evtname):
        return evtname
    return None


if __name__ == '__main__':
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
        if _USE_BINARY_OUTPUT:
            # csv.writer requires binary output file
            import msvcrt
            msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)

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
        col = ['inputfile', ]
        if args.add_match_info:
            col.extend(('match_name', 'field_time'))
        col.extend(OUTPUT_COLUMNS)

        if not args.one_output_per_file:
            if args.output:
                outstrm = open(args.output, 'wb' if _USE_BINARY_OUTPUT else 'w')
            else:
                outstrm = sys.stdout
            outcsv = csv.DictWriter(outstrm, fieldnames=col, extrasaction='ignore')
            outcsv.writeheader()
        else:
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

            if args.one_output_per_file:
                if outstrm:
                    outstrm.close()
                outname, _ = os.path.splitext(os.path.basename(fn))
                outname += '.csv'
                outstrm = open(outname, 'wb' if _USE_BINARY_OUTPUT else 'w')
                outcsv = csv.DictWriter(outstrm, fieldnames=col, extrasaction='ignore')
                outcsv.writeheader()

            dsparser = DSLogParser(fn)
            for rec in dsparser.read_records():
                rec['inputfile'] = fn
                if match_info:
                    rec.update(match_info)

                # unpack the PDP currents to go into columns more easily
                for i in range(16):
                    rec['pdp_{}'.format(i)] = rec['pdp_currents'][i]

                outcsv.writerow(rec)

            dsparser.close()

        if args.output or args.one_output_per_file:
            outstrm.close()
