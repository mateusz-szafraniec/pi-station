from . import SensorReader, MemorySensorObserver
import grovepi
import atexit
import grove_rgb_lcd
from collections import OrderedDict
import math


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
        result = OrderedDict()
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


class GroveLcdObserver(MemorySensorObserver):
    
    index = 0
    
    def notify(self, data):
        super(GroveLcdObserver, self).notify(data)
        txt = []
        items = self.latest.items()[self.index : self.index + 4]
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
    
    def __init__(self, pin):
        self.pin = pin
        grovepi.pinMode(self.pin,"OUTPUT")
        grovepi.chainableRgbLed_init(self.pin, 1)
        grovepi.storeColor(0, 255, 0)
        
    def notify(self, data):
        super(GroveChainableRgbLedObserver, self).notify(data)
        rgb = self.get_level_color(self.get_highest_level(self.latest))
        grovepi.chainableRgbLed_pattern(self.pin, 0, 0)
        grovepi.storeColor(*rgb)
 
