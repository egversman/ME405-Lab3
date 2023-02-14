"""! @file motor_driver.py
   This file contains an implementation of a motor driver class. This includes a
   test in the file main to make sure it works properly.
"""
import pyb

class MotorDriver:
    """! 
    This class implements a motor driver for an ME405 kit. 
    """

    def __init__ (
                  self, en_pin = pyb.Pin.board.PA10, in1pin = pyb.Pin.board.PB4, 
                  in2pin = pyb.Pin.board.PB5, tim_num: int = 3
                  ):
        """! 
        Initializes selected pins and timer appropriately. Turns the motor off 
        for safety. 
        @param en_pin Motor driver enable pin. Set high to enable the motor.
        @param in1pin First directional pin. Set this pin high and send it a PWM
               signal (with in2pin set low) to power the motor CW (?).
        @param in2pin Second directional pin. Set this pin high and send it a 
               PWM signal (with in1pin set low) to power the motor CCW (?).
        @param timer Motor driver timer which generates PWM signals whose 
               frequency determines the motor speed.
        """
        self.en_pin = pyb.Pin(en_pin, pyb.Pin.OUT_OD, pyb.Pin.PULL_UP)
        self.in1pin = pyb.Pin(in1pin, pyb.Pin.OUT_PP)
        self.in2pin = pyb.Pin(in2pin, pyb.Pin.OUT_PP)
        self.timer = pyb.Timer(tim_num, prescaler = 0, period = 0xFFFF)
        
        # Turn the motor off for safety
        self.en_pin.low()
        
    def __repr__(self):
        return f"MotorDriver(en_pin={self.en_pin}, in1pin={self.in1pin}, in2pin={self.in2pin}, tim_num={self.timer.tim_num})"
    
    def __str__(self):
        return f"MotorDriver:\n\ten_pin={self.en_pin},\n\tin1pin={self.in1pin},\n\tin2pin={self.in2pin}, and\n\ttim_num={self.timer.tim_num}"
        
    def set_duty_cycle (self, level):
        """!
        This method sets the duty cycle to be sent to the motor to the given 
        level. Positive values cause torque in one direction, negative values in 
        the opposite direction.
        @param level A signed integer holding the duty cycle of the voltage sent 
               to the motor 
        """
        ch1 = self.timer.channel(1, pyb.Timer.PWM, pin=self.in1pin) 
        ch2 = self.timer.channel(2, pyb.Timer.PWM, pin=self.in2pin)
        
        self.en_pin.high() #enable motor
        
        # set the timer according to the specified PWM duty cycle 'level'
        if abs(level) >= 99:
            level = 99
        if level >= 0:
            ch1.pulse_width_percent(abs(level)) #IN1A low
            ch2.pulse_width_percent(0) #PWM signal to IN2A
        else:
            ch1.pulse_width_percent(0) #IN1A low
            ch2.pulse_width_percent(abs(level)) #PWM signal to IN2A
        
        # print (f"Setting duty cycle to {level}")

        
if __name__ == "__main__":
    '''
    Test motor driver class: Send a range of duty cycles, both positive and 
    negative, and check that the motor moves both ways. Make sure to check “edge 
    cases” such as the maximum and minimum possible duty cycles for proper 
    operation.
    '''
    # MotorDriver test
    moe = MotorDriver (
        pyb.Pin.board.PA10, pyb.Pin.board.PB4, pyb.Pin.board.PB5, 3
        )
    moe.set_duty_cycle (100) # only abs 20-99 plz

