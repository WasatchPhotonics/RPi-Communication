# RPi-Communication

This repository is the program that allows a raspberry pi connected to a spectrometer via usb to communicate over different protocols including:
  -USB
  -BLE
  -Wi-Fi
  -Ethernet

pybleno determines the name advertised that shows up in the app, but to change the name of the device read by ble communication the pi needs a new file called [/etc/machine-info](https://stackoverflow.com/questions/26299053/changing-raspberry-pi-bluetooth-device-name)

pybleno determines the MTU based on what the central device requests. This means the device that connects to the pi must request an MTU of at least 256 or else reading spectra will not work.

In the Socket folder, exampleClient.py and exampleClientGUI.py provide a CLI and GUI interface for connecting to the RPi, respectively.

# Dependencies

- [Wasatch.PY](https://github.com/WasatchPhotonics/Wasatch.PY) for spectrometer interface
- [pybleno](https://github.com/Adam-Langley/pybleno) for BLE interface
- [bleno](https://github.com/noble/bleno)

Follow the [bleno prerequisites](https://github.com/noble/bleno#prerequisites) to setup the raspberry pi initially. 

# Methodology

The application starts in the gatewayController.py file. This sets up the logger, the standard message handler function, and the priority queues that handle the various communication interfaces. Once the gateway starts, it first instantiates a deviceManger object. This object is the gatekeeper through which all messaging must pass, and it is the worker that handles processing messages between the Pi and spectrometer. The first thing the devivceManger does is check if a spectrometer is connected. If there is no spectrometer, the application quits, so there must be a spectrometer connected for it to function. After it finds a spectrometer it creates a worker thread that keeps checking the various priority queues and processes a message when it finds one in the queue. After the device manager is created it creates managers for the different communications types (BLE, eth, wifi). The general overview of these managers is they receive a command and a value. This is passed into the shared message handler that bundles the information into the same format and passes it into the respective queue. Since eth and wifi both use socket communication they share a queue. Once, a response is processed the shared message handler returns the response to the manager, and it will return the result via that connection.

# Spectrometer Errors

If the spectrometer is disconnected or needs to be hot-plugged, it will reconnect after a few queries. If you have an error, unplug then plug the spectrometer back in. Send a few requests to the Pi. The spectrometer should be reconnected and functional after approximately 3 queries and you can resume your operation.

# Supported Commands

- 'EEPROM',
- 'HAS_BATTERY',
- 'BATTERY'(gives percentage),
- 'GET_GAIN',
- 'SET_GAIN',
- 'SET_INT_TIME',
- 'GET_INT_TIME',
- 'GET_SPECTRA',
- 'GET_ROI',
- 'SET_ROI',
- 'SET_LASER',
- 'SET_WATCHDOG',
- 'SET_RAMAN_DELAY',
- 'GET_LASER_STATE',
- 'GET_WATCHDOG_DELAY',
- 'GET_RAMAN_DELAY',
- 'GET_RAMAN_MODE'

# Future possible features
- multiple spectrometer support
- additional commands
- http web page view

# Invocation

Run the BLE service:

    $ sudo python3 -u gatewayController.py

(Sudo required because pybleno [uses raw sockets](https://github.com/Adam-Langley/pybleno/issues/12#issuecomment-386927390)).
