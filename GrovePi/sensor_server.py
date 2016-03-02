from sensor_reader import *
from flask import Flask, render_template, url_for

SENSOR_LABELS = {
        'pm1.0': "PM1.0",
        'pm2.5': "PM2.5",
        'pm10': "PM10",
        'dust': "Dust",
        'aq': "Air Quality",
        'gas': "Gas",
        'hcho': "HCHO",
        'temp': "Temperature",
        'humi': "Humidity",
        'so2': "SO2",
        'no2': "NO2",
        'o3': "O3",
    }

loop = SensorLooper()
loop.addReader(GroveDhtReader("dht", 4))
#loop.addReader(GroveDustReader("dust"))
loop.addReader(PlantowerPmReader('pm'))
#loop.addReader(GroveAnalogReader("so2", 0))
#loop.addReader(GroveAnalogReader("no2", 1))
#loop.addReader(GroveAnalogReader("o3", 2))
#loop.addReader(GroveAnalogReader("aq", 0))
#loop.addReader(GroveAnalogReader("gas", 1))
#loop.addReader(GroveAnalogReader("hcho", 2))

loop.addObserver(ConsoleSensorObserver())
#mem_sensors = MemorySensorObserver()
mem_sensors = GroveLcdObserver()
loop.addObserver(GroveChainableRgbLedObserver(7))
loop.addObserver(mem_sensors)

loop.start()


app = Flask(__name__)
# app.debug = True

@app.route("/")
def dashboard():
    return render_template('dashboard.html', data=mem_sensors.latest, labels=SENSOR_LABELS)

if __name__ == "__main__":
    app.run(host='0.0.0.0')
