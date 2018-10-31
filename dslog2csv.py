#!/usr/bin/env python3

# Note: should work correctly with either Python 2 or 3

from __future__ import print_function

# Parse the FRC drive station logs which are packed binary data

# Notes on comparison to DSLog-Parse:
# D-P has packet_loss as a *signed* integer, which makes no sense. Unsigned looks sensible.
# D-P did not reverse the PDP values as was indicated in the CD post

import sys
import os
import struct
import csv
import bitstring


class DSLogParser():
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

    def __init__(self, input_file):
        self.strm = open(input_file, 'rb')

        self.record_num = 0
        self.record_time_offset = 20.0

        self.read_header()
        return

    def read_records(self):
        if self.version != 3:
            raise Exception("Unknown file version number {}".format(self.version))

        while True:
            r = self.read_record_v3()
            if r is None:
                break
            yield r
        return

    def read_header(self):
        self.version = struct.unpack('>i', self.strm.read(4))[0]
        if self.version != 3:
            raise Exception("Unknown file version number {}".format(self.version))

        # for now, ignore the file timestamp
        self.strm.read(16)
        return

    def read_record_v3(self):
        data_bytes = self.strm.read(10)
        if not data_bytes or len(data_bytes) < 10:
            return None
        pdp_bytes = self.strm.read(25)
        if not pdp_bytes or len(pdp_bytes) < 25:
            # should not happen!!
            print('ERROR: no data for PDP. Unexpected end of file. Quitting', file=sys.stderr)
            return None

        res = {'time': self.record_num * self.record_time_offset}
        res.update(self.parse_data_v3(data_bytes))
        res.update(self.parse_pdp_v3(pdp_bytes))
        self.record_num += 1

        return res

    @staticmethod
    def shifted_float(raw_value, shift_right):
        return raw_value / (2.0**shift_right)

    @staticmethod
    def unpack_bits(raw_value):
        '''Unpack and invert the bits in a byte'''

        status_bits = bitstring.Bits(bytes=raw_value)
        # invert them all
        return [not b for b in status_bits]

    def parse_data_v3(self, data_bytes):
        raw_values = struct.unpack('>BBHBcBBH', data_bytes)
        status_bits = self.unpack_bits(raw_values[4])
        # print('bits', self.record_num, raw_values[4], int.from_bytes(raw_values[4], byteorder='big'), status_bits)

        res = {
            'round_trip_time': self.shifted_float(raw_values[0], 1),
            'packet_loss': 0.04 * raw_values[1],             # not shifted
            'voltage': self.shifted_float(raw_values[2], 8),
            'rio_cpu': 0.01 * self.shifted_float(raw_values[3], 1),
            'can_usage': 0.01 * self.shifted_float(raw_values[5], 1),
            'wifi_db': self.shifted_float(raw_values[6], 1),
            'bandwidth': self.shifted_float(raw_values[7], 8),

            'robot_disabled': status_bits[7],
            'robot_auto': status_bits[6],
            'robot_tele': status_bits[5],
            'ds_disabled': status_bits[4],
            'ds_auto': status_bits[3],
            'ds_tele': status_bits[2],
            'watchdog': status_bits[1],
            'brownout': status_bits[0],
        }

        return res

    def parse_pdp_v3(self, pdp_bytes):
        # from CD post https://www.chiefdelphi.com/forums/showpost.php?p=1556451&postcount=11
        # pdp_offsets = (8, 18, 28, 38, 52, 62, 72, 82, 92, 102, 116, 126, 136, 146, 156, 166)

        # from DSLog-Reader
        # these make more sense in terms of defining a packing scheme, so stick with them
        # looks like this is a 64-bit int holding 6 10-bit numbers and they ignore the extra 4 bits
        pdp_offsets = (8, 18, 28, 38, 48, 58,
                       72, 82, 92, 102, 112, 122,
                       136, 146, 156, 166)

        bits = bitstring.Bits(bytes=pdp_bytes)

        vals = []
        for offset in pdp_offsets:
            vals.append(self.shifted_float(bits[offset:offset+10].uint, 3))

        # values are 15 through 0, so reverse the list
        # note: DSLog-Reader did not reverse these. Don't know who to believe.
        vals.reverse()

        total_i = 0.0
        for i in vals:
            total_i += i

        # the scaling on R, V and T are almost certainly not correct
        # need to find a reference for those values
        res = {
            'pdp_id': bits[0:8].uint,
            'pdp_currents': vals,
            'pdp_resistance': bits[176:184].uint,
            'pdp_voltage': bits[184:192].uint,
            'pdp_temp': bits[192:200].uint,
            'pdp_total_current': total_i,
        }

        return res


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='DSLog to CSV file')
    parser.add_argument('--output', '-o', help='Output filename (stdout otherwise)')
    parser.add_argument('files', nargs='+', help='Input files')

    args = parser.parse_args()

    if sys.platform == "win32":
        import glob
        import msvcrt

        # csv.writer requires binary output file
        msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)

        # do glob expanding on Windows. Linux/Mac does this automatically.
        newfiles = []
        for a in args.files:
            newfiles.extend(glob.glob(a))
        args.files = newfiles

    col = ['inputfile', ]
    col.extend(DSLogParser.OUTPUT_COLUMNS)
    if args.output:
        outstrm = open(args.output, 'wb')
    else:
        outstrm = sys.stdout
    outcsv = csv.DictWriter(outstrm, fieldnames=col, extrasaction='ignore')
    outcsv.writeheader()

    for fn in args.files:
        dsparser = DSLogParser(fn)
        for rec in dsparser.read_records():
            rec['inputfile'] = fn

            # unpack the PDP currents to go into columns more easily
            for i in range(16):
                rec['pdp_{}'.format(i)] = rec['pdp_currents'][i]

            outcsv.writerow(rec)

    if args.output:
        outstrm.close()
