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


sensor_data = None
app = Flask(__name__)
#app.debug = True

@app.route("/")
def dashboard():
    return render_template('dashboard.html', data=sensor_data.latest, labels=SENSOR_LABELS)

def start(data):
    global sensor_data
    sensor_data = data
    app.run(host='0.0.0.0')
