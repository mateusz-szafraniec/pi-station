import datetime
import time
import threading
import grovepi
import atexit
from fractions import gcd
import sys

class SensorLooper(object):

    reader_intervals = []
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
        while True:
            #TODO: support different intervals
            data = {}
            now = datetime.datetime.now()
            for reader in self.readers:
                val = reader.read()
                if val:
                    val['time'] = now
                    data[reader.key] = val
            for observer in self.observers:
                observer.notify(data)
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
        try:
            [new_val, lpo] = grovepi.dustSensorRead()
            if new_val:
                return {
                        'value': lpo
                    }
            else:
                return None
        except:
            return None

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
