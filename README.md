# RPi-Communication

This repository is the program that allows a raspberry pi connected to a spectrometer via usb to communicate over different protocols including:
  -USB
  -BLE
  -Wi-Fi
  -Ethernet

pybleno determines the name advertised that shows up in the app, but to change the name of the device read by ble communication the pi needs a new file called /etc/machine-infohttps://stackoverflow.com/questions/26299053/changing-raspberry-pi-bluetooth-device-name

# Dependencies

- [Wasatch.PY](https://github.com/WasatchPhotonics/Wasatch.PY) for spectrometer interface
- [pybleno](https://github.com/Adam-Langley/pybleno) for BLE interface
- [bleno](https://github.com/noble/bleno)

Follow the [bleno prerequisites](https://github.com/noble/bleno#prerequisites) to setup the raspberry pi initially. 

# Invocation

Run the BLE service:

    $ sudo PYTHONPATH=/path/to/Wasatch.PY python -u main.py

(Sudo required because pybleno [uses raw sockets](https://github.com/Adam-Langley/pybleno/issues/12#issuecomment-386927390)).
