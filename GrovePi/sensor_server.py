from sensor_reader import *
from flask import Flask, render_template, url_for

SENSOR_LABELS = {
        'dust': "Dust",
        'aq': "Air Quality",
        'gas': "Gas",
        'hcho': "HCHO"
    }

loop = SensorLooper()
loop.addReader(GroveDustReader("dust"))
loop.addReader(GroveAnalogReader("aq", 0))
loop.addReader(GroveAnalogReader("gas", 1))
loop.addReader(GroveAnalogReader("hcho", 2))
loop.addObserver(ConsoleSensorObserver())
mem_sensors = MemorySensorObserver()
loop.addObserver(mem_sensors)
loop.start()


app = Flask(__name__)
app.debug = True

@app.route("/")
def dashboard():
    return render_template('dashboard.html', data=mem_sensors.latest, labels=SENSOR_LABELS)

if __name__ == "__main__":
    app.run(host='0.0.0.0')
