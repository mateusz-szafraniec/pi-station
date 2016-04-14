Raspberry Pi Sensor Station
==============
Sensor Station software for Raspberry Pi.
Since our first initiative is to build a PM2.5 sensor network, we will demostrate below how to setup the station with PM sensor connected.

## Hardware Requirements:

* Raspberry Pi (currently only tested with Pi 2)
* At least 4G SD Card
* Plantower PM Sensor (currently only tested with PMS3003) with Cable

## Setup Steps

### Step 1. Prepare OS

[Install Raspbian on your SDCard.](https://www.raspberrypi.org/documentation/installation/installing-images/)

Insert the SDCard to your Raspberry Pi when done.

### Step 2. Connect Sensor

You only need to connect 4 pins of the PM Sensor, others should be left unconnected.

PM Sensor Pins| RPi Pins
---------- | ----------
VCC (PIN1) | +5V (PIN2)
GND (PIN2) | GND (PIN6)
RXD (PIN4) | TXD (PIN8)
TXD (PIN5) | RXD (PIN10)


### Step 3. Access and Configure Raspberry Pi

Power on your Raspberry Pi and get access to it. 

It would be easier if you have screen/mouse/keyboard to access GUI. But if you prefer command line access, you can use a [USB to TTL cable](https://learn.adafruit.com/adafruits-raspberry-pi-lesson-5-using-a-console-cable) or [SSH](https://learn.adafruit.com/adafruits-raspberry-pi-lesson-6-using-ssh) when you got it's IP address. Note that USB to TTL cable uses serial pins, so you might need to unplug serial sensors first.

In order to read data from serial PM sensor, you'll have to disable serial console access first.  
```
sudo raspi-config
```
Select 'Advanced Options' -> 'Serial' -> 'No'

### Step 4. Setup and Run

Firstly, clone sensor station repository into your Raspberry Pi:  
```
git clone https://github.com/sensor-web/pi-station.git
```

Change to the pi-station directory:  
```
cd pi-station
```

Install dependencies:  
```
sudo pip install -r requirements.txt
```

Copy config.py.sample to config.py
```
cp config.py.sample config.py
```

Add your `sensor_id` and `api_key` to config.py so it look like:
```
API_KEY='znergjcd6hghvq5x2paf'
SENSOR_ID='f61xy1xkkft509j49qao'
```

Start the server, you'll see console output if it runs correctly:  
```
sudo python sensor_daemon.py
```

Access the sensor dashboard in Raspberry Pi's browser with following URL:  
http://localhost:5000

If your Raspberry Pi have an IP, you can access it on other devices via IP.  

### Step 5. Make It Run at Startup
You can leverage crontab to run the script at startup.
```
sudo crontab -e
```

Add following line to start sensor daemon each time when system starts.
```
@reboot /usr/bin/python /home/pi/pi-station/sensor_daemon.py &
```


If your Raspberry Pi is usually connected to a screen,  
you can consider making it a kiosk by installing [iceweasel](https://wiki.debian.org/Iceweasel) with [R-kiosk](https://addons.mozilla.org/firefox/addon/r-kiosk/) add-on.

Setting ```http://localhost:5000``` as the browser homepage,  
add ```@iceweasel``` in ```/home/pi/.config/lxsession/LXDE/autostart``` to make it auto start on desktop login.

This way you'll have a air quality kiosk in your place.

## More Supported Modules

You may need to [install GrovePi](http://www.dexterindustries.com/GrovePi/get-started-with-the-grovepi/setting-software/) in order to use Grove Modules.

### Connect More Sensors

Currently supported sensors are:

* Plantower PM Sensor
* Grove Dust Sensor
* Grove Temperature & Humidity Sensor Pro
* Grove Barometer Sensor
* Generic Grove Analog Sensors

Connect your sensor, uncomment and edit corresponding code in ```senser_daemon.py``` to use them.

### More Output Options

Currently supported output method:

* Console output
* Grove LCD RGB Backlight
* Grove Chainable RGB LED  

Connect your module, uncomment and edit corresponding code in ```senser_daemon.py``` to use them.

## Next Steps

* Try different Raspberry Pi versions
* Store data offline and sync when online
* Basic offline charts/analytics
* Support GPS modules/dongles (serial pins are occupied by PM sensor, cannot use grove GPS at the same time.)

## Maintainers
* [Eddie Lin](https://github.com/yshlin)

