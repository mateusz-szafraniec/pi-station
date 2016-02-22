import datetime
import time
import threading
import grovepi
import atexit
from fractions import gcd
import sys
import grove_rgb_lcd
import serial
from collections import OrderedDict
import math

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

    def run(self):
        for reader_interval in self.reader_intervals:
            self.reader_sleeps += [reader_interval/self.looper_interval]
            self.reader_loops += [0]
        while True:
            data = OrderedDict()
            for i, reader in enumerate(self.readers):
                self.reader_loops[i] += 1
                if self.reader_loops[i] == self.reader_sleeps[i]:
                    self.reader_loops[i] = 0
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
                        print 'Reader error: '
                        print sys.exc_info()
            for observer in self.observers:
                try:
                    observer.notify(data)
                except:
                    print 'Observer error: '
                    print sys.exc_info()
            time.sleep(self.looper_interval)
    
    def start(self):
        t = threading.Thread(target=self.run)
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


class PlantowerPmReader(SensorReader):

    port = None
    raw_data = None
    pm1_levels = OrderedDict([('good', 0), ('low', 10), ('medium', 20), ('high', 30), ('sever', 50)])
    pm25_levels = OrderedDict([('good', 0), ('low', 20), ('medium', 35), ('high', 70), ('sever', 100)])
    pm10_levels = OrderedDict([('good', 0), ('low', 50), ('medium', 150), ('high', 350), ('sever', 420)])

    def __init__(self, key):
        super(PlantowerPmReader, self).__init__(key)
        self.port = serial.Serial("/dev/ttyAMA0", baudrate = 9600, timeout = 2)
        
    def parse_field(self, pos):
          return 0x100 * ord(self.raw_data[pos]) + ord(self.raw_data[pos + 1])

    def parse_fields(self):
          return self.parse_field(10), self.parse_field(12), self.parse_field(14)

    def read(self):
        self.raw_data = self.port.read(24)
        pm1, pm25, pm10 = self.parse_fields()
        return {
                'pm1.0': {'value': pm1, 'level': self.get_level(pm1, self.pm1_levels)},
                'pm2.5': {'value': pm25, 'level': self.get_level(pm25, self.pm25_levels)},
                'pm10': {'value': pm10, 'level': self.get_level(pm10, self.pm10_levels)},
            }

class GroveSensorReader(SensorReader):

    def __init__(self, key, pin=None):
        super(GroveSensorReader, self).__init__(key, pin)
        grovepi.pinMode(pin, "INPUT")


class GroveDigitalReader(GroveSensorReader):

    def read(self):
        return {
                'value': grovepi.digitalRead(self.pin)
            }


class GroveAnalogReader(GroveSensorReader):

    levels = OrderedDict([('good', 0), ('low', 100), ('medium', 300), ('high', 500), ('sever', 700)])

    def __init__(self, key, pin=None, factor=1):
        super(GroveAnalogReader, self).__init__(key, pin)
        self.factor = factor

    def read(self):
        v = float(grovepi.analogRead(self.pin)) * self.factor
        return {
                'value': v,
                'level': self.get_level(v, self.levels),
            }


class GroveDustReader(SensorReader):

    levels = OrderedDict([('good', 0), ('low', 3000), ('medium', 6000), ('high', 10000), ('sever', 20000)])

    def __init__(self, key):
        super(GroveDustReader, self).__init__(key)
        atexit.register(grovepi.dust_sensor_dis)
        grovepi.dust_sensor_en()

    def read(self):
        [new_val, lpo] = grovepi.dustSensorRead()
        if new_val:
            return {
                    'value': lpo,
                    'level': self.get_level(lpo, self.levels),
                }
        else:
            return None


class GroveDhtReader(SensorReader):
    
    temp_levels = OrderedDict([('cold', -273), ('comfortable', 18), ('hot', 28)])
    humi_levels = OrderedDict([('dry', 0), ('comfortable', 30), ('humid', 60)])
    mode_type = 1
    
    def __init__(self, key, pin, mod_type=1):
        super(GroveDhtReader, self).__init__(key, pin)
        self.mod_type=mod_type

    def read(self):
        [temperature,humidity] = grovepi.dht(self.pin, self.mod_type)
        result = {}
        if not math.isnan(temperature):
            result['temp'] = {
                'value': temperature, 
                'level': self.get_level(temperature, self.temp_levels)
            }
        if not math.isnan(humidity):
            result['humi'] = {
                'value': humidity, 
                'level': self.get_level(humidity, self.humi_levels)
            }

        return result


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


class GroveLcdObserver(MemorySensorObserver):
    
    index = 0
    
    def notify(self, data):
        super(GroveLcdObserver, self).notify(data)
        txt = []
        items = self.latest.items()[self.index : self.index + 4]
        print items
        self.index = 0 if self.index + 4 >= len(self.latest) else self.index + 4
        for key, val in items:
            txt += ['{k}:{v}'.format(k=key.upper(),v=int(val['value']))]
        if len(txt) > 1:
            txt = sorted(txt, key=lambda x: len(x))
            grove_rgb_lcd.setText(txt[-1] + ' ' + txt[0] + '\n' + ' '.join(txt[1:-1]))
        else:
            grove_rgb_lcd.setText(txt[0])
        rgb = self.get_level_color(self.get_highest_level(self.latest))
        grove_rgb_lcd.setRGB(*rgb)


class GroveChainableRgbLedObserver(MemorySensorObserver):
    
    def notify(self, data):
        super(GroveLcdObserver, self).notify(data)
        rgb = self.get_level_color(self.get_highest_level(self.latest))
        #TODO: control RGB Led
