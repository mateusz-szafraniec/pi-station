from sensorweb.rpi import *
from sensorweb.rpi.gpio import *
#from sensorweb.rpi.grovepi import *
import sensor_dashboard


loop = SensorLooper()

#######################
# Sensor Readers      #
# uncomment to enable #
#######################
loop.addReader(PlantowerPmReader('pm'))
#loop.addReader(GroveDhtReader("dht", 4))
#loop.addReader(GroveDustReader("dust"))
#loop.addReader(GroveAnalogReader("so2", 0))
#loop.addReader(GroveAnalogReader("no2", 1))
#loop.addReader(GroveAnalogReader("o3", 2))
#loop.addReader(GroveAnalogReader("aq", 0))
#loop.addReader(GroveAnalogReader("gas", 1))
#loop.addReader(GroveAnalogReader("hcho", 2))


#######################
# Sensor Observers    #
# uncomment to enable #
#######################
loop.addObserver(ConsoleSensorObserver())
mem_sensors = MemorySensorObserver()
#mem_sensors = GroveLcdObserver()
#loop.addObserver(GroveChainableRgbLedObserver(7))
loop.addObserver(mem_sensors)


##########################################
# Start Looper                           #
# Use loop.start() if dashboard disabled #
##########################################
#loop.start()
loop.startInBackground()
sensor_dashboard.start(mem_sensors)
