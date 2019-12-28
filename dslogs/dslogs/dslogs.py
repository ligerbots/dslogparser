#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# builtins
import collections
from pathlib import Path

# not builtins
import arrow
import dslogparser


def default_log(time):
    return {
        'time': time,
        'round_trip_time': 0,
        'packet_loss': 0,
        'voltage': 255,
        'rio_cpu': 0,
        'can_usage': 0,
        'wifi_db': 0,
        'bandwidth': 0,
        'robot_disabled': False,
        'robot_auto': False,
        'robot_tele': False,
        'ds_disabled': False,
        'ds_auto': False,
        'ds_tele': False,
        'watchdog': False,
        'brownout': False,
        'pdp_id': 0,
        'pdp_currents': 16 * [0, ],
        'pdp_resistance': 0,
        'pdp_voltage': 0,
        'pdp_temp': 0,
        'pdp_total_current': 0,
        }


class DSlogs():
    def __init__(self, dslog_path, dsevent_path):
        self.logpath = Path(dslog_path)
        self.eventpath = Path(dsevent_path)

    @property
    def _log_parser(self):
        return dslogparser.DSLogParser(str(self.logpath))

    @property
    def _event_parser(self):
        return dslogparser.DSEventParser(str(self.eventpath))

    @staticmethod
    def _continuous(gen):
        last_item = None
        for item in gen:
            last_item = item
            yield item
        while True:
            last_item['time'] = arrow.get(last_item['time']).shift(seconds=dslogparser.DSLOG_TIMESTEP).datetime
            yield last_item

    @staticmethod
    def _fix_time(gen):
        for item in gen:
            item['time'] = arrow.get(item['time'])
            yield item

    def _slice(self, gen, start=None, end=None):
        if not start:
            start = arrow.get(0)
        if not end:
            end = arrow.get()
        for item in gen:
            if item['time'].is_between(start, end, '[]'):
                yield item
            elif end < item['time']:
                break

    def _window(self, gen, start, end, items_per_window):
        if not items_per_window:
            raise ValueError('Must provide a window size')
        if not start:
            start = arrow.get(0)
        if not end:
            end = arrow.get()
        window = collections.deque(maxlen=items_per_window)
        middle_index = items_per_window // 2  # left of center if even, else absolute center
        for item in gen:
            window.append(item)
            if (len(window) < items_per_window):
                continue
            if not window[middle_index]['time'].is_between(start, end, '[]'):
                continue
            yield window

    def _items(self, gen, start=None, end=None, window=None, continuous=False):
        if continuous:
            gen = self._continuous(gen)
        gen = self._fix_time(gen)
        if window:
            gen = self._window(gen, start=start, end=end, items_per_window=window)
            for item in gen:
                yield item

        elif not start and not end:
            for item in gen:
                yield item
        else:
            gen = self._slice(gen, start, end)
            for item in gen:
                yield item

    def logs(self, start=None, end=None, window=None, continuous=False):
        return self._items(self._log_parser.read_records(), start, end, window, continuous)

    def events(self, start=None, end=None, window=None, continuous=False):
        return self._items(self._event_parser.read_records(), start, end, window, continuous)

    def match_info(self):
        match_data = self._event_parser.find_match_info(str(self.eventpath))
        field_time = arrow.get(match_data['field_time'])
        match = match_data['match_name']
        start_time = None
        for log in self.logs(start=field_time):
            if log['ds_auto']:
                start_time = log['time']
                break

        return start_time, match
