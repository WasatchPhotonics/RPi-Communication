1. Open a terminal and create a directory on the Pi where you will copy the code such as 
    - ```mkdir gatewayDir```
2. Clone the Wasatch.PY repository into that directory in the manner you prefer 
    - ```git clone https://github.com/WasatchPhotonics/Wasatch.PY.git```
<img width="391" alt="image" src="https://user-images.githubusercontent.com/62862738/133320198-3d106c11-f691-43ca-83de-1bab3d705e37.png">

3. Install the python dependencies using pip

    - netifaces
    - pybleno
    
5. Follow the [bleno prerequisites](https://github.com/noble/bleno#prerequisites) to setup the raspberry pi for using BLE
    - OPTIONAL: Create an [/etc/machine-info](https://stackoverflow.com/questions/26299053/changing-raspberry-pi-bluetooth-device-name) in order to change the BLE device name to something other than raspberyy-pi
6. Clone the RPi-Communication repository to the same shared folder as Wasatch.PY and navigatge to RPi-Communication 
    - ```git clone https://github.com/WasatchPhotonics/RPi-Communication.git```
    - ```cd RPi-Communication```
7. Create a [service](https://www.raspberrypi-spy.co.uk/2015/10/how-to-autorun-a-python-script-on-boot-using-systemd/) so that the server starts when the Pi boots up with the following steps:
    - copy the wpGateway.service using ```sudo cp ./wpGateway.service /lib/systemd/system/wpGateway.service```
    - change to the service directory and then change the permissions of the service file ```cd /lib/systemd/system/ && chmod 644 /lib/systemd/system/wpGateway.service```
    - Setup then start the service with the following command ```sudo systemctl daemon-reload && sudo systemctl enable wpGateway.service && sudo systemctl start wpGateway.service```

The gateway should now be running. Use Enlighten Mobile or one of the exampleClients to verify the ability to connect to the Raspberry Pi

