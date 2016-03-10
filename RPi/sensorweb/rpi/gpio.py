from . import SensorReader
import serial
from collections import OrderedDict


class PlantowerPmReader(SensorReader):

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

