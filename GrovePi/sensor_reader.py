import datetime
import time
import threading
import grovepi
import atexit
from fractions import gcd
import sys
import grove_rgb_lcd
import serial

class SensorLooper(object):

    reader_intervals = []
    reader_sleeps = []
    reader_loops = []
    looper_interval = 0
    readers = []
    observers = []

    def addReader(self, reader, interval=5):
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
            data = {}
            now = datetime.datetime.now()
            for i, reader in enumerate(self.readers):
                self.reader_loops[i] += 1
                if self.reader_loops[i] == self.reader_sleeps[i]:
                    self.reader_loops[i] = 0
                    try:
                        val = reader.read()
                        if val:
                            if 'value' in val:
                                # single value
                                val['time'] = now
                                data[reader.key] = val
                            elif len(val) > 0:
                                # multiple values found
                                for k,v in val.iteritems():
                                    v['time'] = now
                                    data[k] = v
                    except:
                        print sys.exc_info()[0]
            for observer in self.observers:
                try:
                    observer.notify(data)
                except:
                    print sys.exc_info()[0]
            time.sleep(self.looper_interval)
    
    def start(self):
        t = threading.Thread(target=self.run)
        t.daemon = True
        t.start()
    

class SensorReader(object):
    
    def __init__(self, key, pin=None):
        self.key = key
        self.pin = pin
    
    def read(self):
        return {}


class PlantowerPmReader(SensorReader):

    port = None
    raw_data = None

    def __init__(self, key):
        super(PlantowerPmReader, self).__init__(key)
        self.port = serial.Serial("/dev/ttyAMA0", baudrate = 9600, timeout = 2)
        
    def parse_field(self, pos):
          return 0x100 * ord(self.raw_data[pos]) + ord(self.raw_data[pos + 1])

    def read(self):
        self.raw_data = self.port.read(24)
        return {
                'pm1.0': {'value': self.parse_field(10)},
                'pm2.5': {'value': self.parse_field(12)},
                'pm10': {'value': self.parse_field(14)},
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

    def __init__(self, key, pin=None, factor=1):
        super(GroveAnalogReader, self).__init__(key, pin)
        self.factor = factor

    def read(self):
        return {
                'value': float(grovepi.analogRead(self.pin)) * self.factor
            }


class GroveDustReader(SensorReader):

    def __init__(self, key):
        super(GroveDustReader, self).__init__(key)
        atexit.register(grovepi.dust_sensor_dis)
        grovepi.dust_sensor_en()

    def read(self):
        [new_val, lpo] = grovepi.dustSensorRead()
        if new_val:
            return {
                    'value': lpo
                }
        else:
            return None


class GroveDhtReader(SensorReader):
    
    mode_type = 1
    
    def __init__(self, key, pin, mod_type=1):
        super(GroveDhtReader, self).__init__(key, pin)
        self.mod_type=mod_type

    def read(self):
        [temperature,humidity] = grovepi.dht(self.pin, self.mod_type)
        return {
                'temp': {'value': temperature},
                'humi': {'value': humidity},
            }


class SensorObserver(object):

    def notify(self, data):
        pass


class ConsoleSensorObserver(SensorObserver):

    def notify(self, data):
        print data


class MemorySensorObserver(SensorObserver):
    
    latest = {}
    
    def notify(self, data):
        self.latest.update(data)


class GroveLcdObserver(MemorySensorObserver):
    
    def notify(self, data):
        super(GroveLcdObserver, self).notify(data)
        txt = []
        for key, val in self.latest.iteritems():
            txt += ['{k}:{v}'.format(k=key.upper(),v=int(val['value']))]
        txt = sorted(txt, key=lambda x: len(x))
        grove_rgb_lcd.setText(txt[-1] + ' ' + txt[0] + '\n' + ' '.join(txt[1:-1]))
        grove_rgb_lcd.setRGB(0, 255, 0)


class GroveRgbLedObserver(MemorySensorObserver):
    
    def notify(self, data):
        super(GroveLcdObserver, self).notify(data)
