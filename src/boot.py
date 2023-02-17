"""! @file boot.py
    This file sets up the Nucleo to use USB serial ports by disabling the REPL 
    on UART2. 
"""

import pyb                  # Turn off the REPL on UART2
pyb.repl_uart(None)
