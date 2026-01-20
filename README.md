# Wifi_controlled_LEDs_Display
A small project done using, ESP-32 and ESP-01 module using the WIFI-NOW feature to connect them together to create background for a display event in our college annual function. 
*** 
# Follow the Given steps:
***
# Step-1:
Upload the reciever code to the ESP-01 module( select board type as 'Generic ESP8266 Module'), the connect the module's GIOP-2 to the digital pin of the RGB-strip, here make sure you put a 10 kΩ resistor in between the EN pin and power of the ESP-01 to pull the pin up so no issues are there while the ESP-01 recieves data.
***
# Step-2:
Now take the reciver code and upload it to the ESP-32 module(remember to change select board type), then just plug it into you pc and use the python code to do as you wish..., add new song or just remove the song and just play with patterns or just add more patterns as you like.
***
# Prerequsites:
> The ESP-01 module only supports 3.3V power, so remember that while powering it.
> If the range is not enough you can just create a couple of repeaters to relay the signal better,well that for you to explore👌.
> Just enjoy this project!!!!
