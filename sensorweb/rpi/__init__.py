import requests
import datetime
import time
import threading
from fractions import gcd
from collections import OrderedDict
import traceback


class SensorLooper(object):

    reader_intervals = []
    reader_sleeps = []
    reader_loops = []
    looper_interval = 0
    readers = []
    observers = []

    def addReader(self, reader, interval=5, group=''):
        self.readers += [reader]
        self.reader_intervals += [interval]
        if 0 == self.looper_interval:
            self.looper_interval = interval
        self.looper_interval = gcd(self.looper_interval, interval)

    def addObserver(self, observer):
        self.observers += [observer]

    def _calculateIntervals(self):
        self.reader_sleeps = []
        self.reader_loops = []
        for reader_interval in self.reader_intervals:
            self.reader_sleeps += [reader_interval/self.looper_interval]
            self.reader_loops += [0]

    def _readerSleeps(self, i):
        self.reader_loops[i] += 1
        if self.reader_loops[i] == self.reader_sleeps[i]:
            self.reader_loops[i] = 0
            return False
        return True


    def _readAllData(self):
        data = OrderedDict()
        for i, reader in enumerate(self.readers):
            if self._readerSleeps(i):
                continue
            try:
                val = reader.read()
                if val:
                    if 'value' in val:
                        # single value
                        data[reader.key] = val
                    elif len(val) > 0:
                        # multiple values found
                        for k,v in val.iteritems():
                            data[k] = v
            except:
                print "Reader error: "
                traceback.print_exc()
        return data

    def _notifyAll(self, data):
        for observer in self.observers:
            try:
                observer.notify(data)
            except:
                print "Observer error: "
                traceback.print_exc()


    def start(self):
        self._calculateIntervals()
        while True:
            data = self._readAllData()
            self._notifyAll(data)
            time.sleep(self.looper_interval)
    
    def startInBackground(self):
        t = threading.Thread(target=self.start)
        t.daemon = True
        t.start()
    

class SensorReader(object):
    
    def __init__(self, key, pin=None):
        self.key = key
        self.pin = pin
    
    def get_level(self, value, levels):
        if len(levels) > 0:
            prev = levels.items()[0][0]
            for level, threshold in levels.iteritems():
                if threshold > value:
                    return prev
                prev = level
            return prev
        return None
        
    def read(self):
        return {}


class SensorObserver(object):

    warning_levels = ['good', 'low', 'medium', 'high', 'sever']
    level_colors = {
        'good': (0, 255, 0),
        'low': (255, 255, 0),
        'medium': (255, 128, 0),
        'high': (255, 0, 0),
        'sever': (128, 0, 128),
    }

    def get_highest_level(self, data):
        highest_level = 'good'
        for d in data.values():
            if not 'level' in d:
                continue
            if d['level'] in self.warning_levels and self.warning_levels.index(d['level']) > self.warning_levels.index(highest_level):
                highest_level = d['level']
        return highest_level

    def get_level_color(self, level):
        if level in self.level_colors:
            return self.level_colors[level]
        return (0, 255, 0)

    def notify(self, data):
        pass


class ConsoleSensorObserver(SensorObserver):

    def notify(self, data):
        print data


class MemorySensorObserver(SensorObserver):
    
    latest = OrderedDict()

    def notify(self, data):
        now = datetime.datetime.now()
        for k, v in data.iteritems():
            v['time'] = now
        self.latest.update(data)

class SensorWebObserver(MemorySensorObserver):

    def __init__(self, config):
        self.config = config

    def notify(self, data):
        super(SensorWebObserver, self).notify(data)
	requests.post('http://api.sensorweb.io/sensors/' + self.config.SENSOR_ID + '/data', data = {'pm2_5': self.latest['pm2_5'], 'api_key': self.config.API_KEY})
