"""!
@file serial_test.py
This file is used to test the functionality of a serial connection. The user 
inputs a desired setpoint and Kp value and sends it to the connected device. The 
device returns the motor position data which is then processed and plotted. 
"""

import serial
from matplotlib import pyplot as plt

def plotter():
    x = []
    y = []
    i = 0
    with serial.Serial('COM4', 115200, timeout=10) as ser:
        while True:
            try:
                data = ser.readline().strip(b'\r\n').split(b',')
                #print(line,'\r\n')]
                #print(data[0],data[1])
                x.append(int(data[0]))
                y.append(int(data[1]))
                #print(x[i])
                i+=1
                if x[len(x) - 1] >= 3000:
                    print('we made it!')
                    break
            except:
                pass

    plt.plot(x, y, linestyle='-')
    plt.xlabel('Time [msec]')
    plt.ylabel('Motor Position [Encoder Ticks]')
    # plt.scatter(x, y)
    plt.show()

if __name__ == "__main__":
    plotter()


















