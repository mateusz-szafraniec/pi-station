from . import SensorReader
import serial
from collections import OrderedDict


class PlantowerPmReader(SensorReader):

    pm1_levels = OrderedDict([('good', 0), ('low', 10), ('medium', 20), ('high', 30), ('sever', 50)])
    pm25_levels = OrderedDict([('good', 0), ('low', 20), ('medium', 35), ('high', 70), ('sever', 100)])
    pm10_levels = OrderedDict([('good', 0), ('low', 50), ('medium', 150), ('high', 350), ('sever', 420)])

    def __init__(self, key, data_length=24):
        super(PlantowerPmReader, self).__init__(key)
        self.port = serial.Serial("/dev/ttyAMA0", baudrate = 9600, timeout = 2)
        self.data_length = data_length

    def parse_field(self, pos):
          return 0x100 * ord(self.raw_data[pos]) + ord(self.raw_data[pos + 1])

    def parse_fields(self):
          return self.parse_field(10), self.parse_field(12), self.parse_field(14)

    def read(self):
        self.raw_data = self.port.read(self.data_length)
        try:
            head_index = self.raw_data.index('\x42\x4d')
        except:
            # No valid data
            return

        if head_index > 0:
            # Adjust wrong position in serial data
            self.port.read(head_index)
            self.raw_data = self.port.read(self.data_length)

        pm1, pm25, pm10 = self.parse_fields()
        return {
                'pm1.0': {'value': pm1, 'level': self.get_level(pm1, self.pm1_levels)},
                'pm2.5': {'value': pm25, 'level': self.get_level(pm25, self.pm25_levels)},
                'pm10': {'value': pm10, 'level': self.get_level(pm10, self.pm10_levels)},
            }
            
