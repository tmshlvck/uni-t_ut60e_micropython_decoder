# UNI-T UT60E serial output decoder for MicroPython@ESP32

## Introduction

This multimeter uses quite funny protocol and the opto-isolation cable is known
for not working with most USB-Serial convertors because the cable is abusing old
tricks to power the circuitry for amplifying the singal from the opto-coupler.

However, it is easy to connect the opto-coupler to ESP32, power it directly from
3.3V rail and use ESP32's function to invert the RXD signal to avoid extra HW.

The protocol is described here https://sigrok.org/wiki/Multimeter_ICs#Fortune_Semiconductor_FS9721_LP3

## Tested HW

* works with UNI-T UT60E / Voltcraft VC840 - see https://sigrok.org/wiki/UNI-T_UT60E
* tested only with the original cable - see https://sigrok.org/wiki/Device_cables#UNI-T_UT-D02

## HW connection from the opto-coupler cable to ESP32

* connect DB-9 pins 5,7 (GND, RTS) to ESP32 GND
* connect DB-9 pin 4 (DTR) to ESP32 3.3V rail
* connect DB-9 pin 2 (RXD) to ESP32 GPIO 16