# headphones_code
From installing the back-up:
- enable SPI in raspi-config
- repair home directory permission with sudo chown myname:myname /home/myname
- install Adafruit LEd Animation, Blinka and NeoPixel_SPI library

If this pi is for BLE
- make sure bluez tools are installed
- change machine name to bhpble if this pi, 

If this pi is for bluetooth audio:
- follow instructions on https://forums.raspberrypi.com/viewtopic.php?t=235519
- change machine name to bliss-headphones if this pi is bluetooth audio
