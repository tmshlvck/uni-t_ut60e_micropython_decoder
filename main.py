# MicroPython on ESP32
# (C) 2023 Tomas Hlavacek (tmshlvck@gmail.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# based on https://sigrok.org/wiki/Multimeter_ICs#Fortune_Semiconductor_FS9721_LP3
# works with UNI-T UT60E / Voltcraft VC840 - see https://sigrok.org/wiki/UNI-T_UT60E
# and the original cable - see https://sigrok.org/wiki/Device_cables#UNI-T_UT-D02
#
# HW connection from the cable to ESP32:
# connect DB-9 pins 5,7 (GND, RTS) to ESP32 GND; DB-9 pin 4 (DTR) to ESP32 3.3V rail
# and DB-9 pin 2 (RXD) to ESP32 GPIO 16


from machine import UART

def decode_byte(ib):
    seq = ib >> 4
    data = (bool(ib & 8), bool(ib & 4), bool(ib & 2), bool(ib & 1))
    return (seq, data)

zero = (True, True, True, True, True, False, True)
one = (False, False, False, False, True, False, True)
two = (True, False, True, True, False, True, True)
three = (False, False, True, True, True, True, True)
four = (False, True, False, False, True, True, True)
five = (False, True, True, True, True, True, False)
six = (True, True, True, True, True, True, False)
seven = (False, False, True, False, True, False, True)
eight = (True, True, True, True, True, True, True)
nine = (False, True, True, True, True, True, True)

empty = (False, False, False, False, False, False, False)
L = (True, True, False, True, False, False, False)

def decode_number(x, y):
    flag, a, b, c = x
    d, e, f, g = y

    if (a, b, c, d, e, f, g) == empty:
        return (flag, 0)
    if (a, b, c, d, e, f, g) == L:
        return (flag, None)

    if (a, b, c, d, e, f, g) == zero:
        return (flag, 0)
    if (a, b, c, d, e, f, g) == one:
        return (flag, 1)
    if (a, b, c, d, e, f, g) == two:
        return (flag, 2)
    if (a, b, c, d, e, f, g) == three:
        return (flag, 3)
    if (a, b, c, d, e, f, g) == four:
        return (flag, 4)
    if (a, b, c, d, e, f, g) == five:
        return (flag, 5)
    if (a, b, c, d, e, f, g) == six:
        return (flag, 6)
    if (a, b, c, d, e, f, g) == seven:
        return (flag, 7)
    if (a, b, c, d, e, f, g) == eight:
        return (flag, 8)
    if (a, b, c, d, e, f, g) == nine:
        return (flag, 9)

    print("Unknown symbol: "+ str([a,b,c,d,e,f,g]))
    return (flag, -1)

def humanize_flags(flags):
    ac, dc, auto, rs232, diode, beep, Hold, Low_Bat = flags

    out = ""
    if ac:
        out += "AC "
    if dc:
        out += "DC "
    if auto:
        out += "auto "
    if rs232:
        out += "rs232 "
    if diode:
        out += "diode "
    if beep:
        out += "beep "
    if Hold:
        out += "Hold "
    if Low_Bat:
        out += "Low_Bat "
    return out.strip()


def decode_buffer(buff):
    ac, dc, auto, rs232 = buff[0]
    neg, num1 = decode_number(buff[1], buff[2])
    dp1, num2 = decode_number(buff[3], buff[4])
    dp2, num3 = decode_number(buff[5], buff[6])
    dp3, num4 = decode_number(buff[7], buff[8])
    u, n, k, diode = buff[9]
    m, percent, M, beep = buff[10]
    Farads, Ohms, Rel, Hold = buff[11]
    A, V, Hz, Low_Bat = buff[12]
    ub3, ub2, ub1, ub0 = buff[13]

    if num1 == None or num2 == None or num3 == None or num4 == None:
        number = None
    else:
        number = num1*1000+num2*100+num3*10+num4
        if dp1:
            number = float(number) / 1000

        if dp2:
            number = float(number) / 100

        if dp3:
            number = float(number) / 10

        if neg:
            number *= -1

    unit = ""
    if u:
        unit = "u"
    if n:
        unit = "n"
    if k:
        unit = "k"
    if m:
        unit = "m"
    if M:
        unit = "M"

    if percent:
        unit = "%"

    if Farads:
        unit += "F"
    if Ohms:
        unit += "Ohms"
    if Hz:
        unit += "Hz"
    if A:
        unit += "A"
    if V:
        unit += "V"

    flags = (ac, dc, auto, rs232, diode, beep, Hold, Low_Bat)

    return (number, unit, humanize_flags(flags))


def main():
    u2 = UART(2, baudrate=2400, tx=17, rx=16)
    u2.init(2400, bits=8, parity=None, stop=1, invert=UART.INV_RX)

    buffer = [(False, False, False, False)]*14
    while True:
        data = u2.read()
        if data:
            #print("DEBUG: " + str([hex(b) for b in data]))
            for b in data:
                i,bits = decode_byte(b)
                if i == 1 or i > 14:
                    expect = 1
                if i == expect:
                    buffer[i-1] = bits
                    expect += 1
                if expect == 15:
                    expect = 1
                    print(str(decode_buffer(buffer)))


if __name__ == '__main__':
    main()
