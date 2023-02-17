"""!
@file serial_test.py
This file is used to test the functionality of a serial connection. The user 
inputs a desired setpoint and Kp value and sends it to the connected device. The 
device returns the motor position data which is then processed and plotted. 
"""

import serial
from matplotlib import pyplot as plt

"""!
Splits the input line into two parts and returns them as a list. 
@param line: line of data to be split
@return: list of two values split from the line
"""
split = lambda line: line.strip().split(b',')[:3]


def to_float(num: str):
    """!
    Converts a string to a float, or returns False if it is not possible.
    @param num string to be converted to float
    @return float value of the string, or False if the conversion is not
    possible
    """
    try:
        return float(num)
    except:
        return False


def process_data():
    """!
    Reads motor position data from the serial connection and returns the time
    and position values as two separate lists.
    @return tuple of two lists, the first being time values and the second being
            motor position values
    """
    x = []
    y1 = []
    y2 = []
    data = []
    with serial.Serial('COM4', 115200, timeout=10) as ser:

        while True:
            line = ser.readline()

            if b"done" in line.lower():
                break

            data = split(line)

            if False in {data[0], data[1], data[2]}:
                print(b"problem, idiot!")
            else:
                x.append(float(data[0]))
                y1.append(float(data[1]))
                y2.append(float(data[2]))

    return x, y1, y2

def generate_plots(x: list, y1: list, y2: list):
    """!
    Generates a plot of motor position vs. time based on the input data.
    @param x list of time values
    @param y list of motor position values
    """
    plt.plot(x, y1, 'r-')
    plt.xlabel('Time [msec]')
    plt.ylabel('Motor Position [Encoder Ticks]')
    #plt.scatter(x, y)
    plt.show()

    plt.plot(x, y2, 'b-')
    plt.xlabel('Time [msec]')
    plt.ylabel('Motor Position [Encoder Ticks]')
    # plt.scatter(x, y)
    plt.show()

if __name__ == "__main__":
    x, y1, y2 = process_data()
    generate_plots(x, y1, y2)






















