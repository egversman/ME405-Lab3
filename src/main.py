"""!
@file basic_tasks.py
    This file contains a demonstration program that runs some tasks, an
    inter-task shared variable, and a queue. The tasks don't really @b do
    anything; the example just shows how these elements are created and run.

@author JR Ridgely
@date   2021-Dec-15 JRR Created from the remains of previous example
@copyright (c) 2015-2021 by JR Ridgely and released under the GNU
    Public License, Version 2. 
"""

import gc
import pyb
import cotask
import task_share
import motor_driver
import encoder_reader
import clp_controller
import utime
import array


def task_motor1(shares):
    """!
    This task creates the motor one objects, sets its proportional control gain,
    and updates its position based on encoder readings.
    @param shares A list holding the shares used by this task, the setpoint and 
    position of motor one.
    """
    # Create motor1 objects.
    motor_dvr1 = motor_driver.MotorDriver()
    motor_dvr1.enable()
    encoder1 = encoder_reader.EncoderReader()
    controller1 = clp_controller.CLPController()
    
    controller1.set_Kp(.2) # IMPORTANT: set this to around .01
    
    # Get references to the share and queue which have been passed to this task.
    setpoint_m1, position_m1 = shares
    
    while True:
        new_setpoint = setpoint_m1.get()
        controller1.set_setpoint(new_setpoint)
        motor_dvr1.set_duty_cycle(
            controller1.run(new_setpoint, encoder1.read())
            )
        position_m1.put(
            controller1.motor_positions[len(controller1.motor_positions)-1]
            )
        yield 0


def task_motor2(shares):
    """!
    This task creates the motor two objects, sets its proportional control gain,
    and updates its position based on encoder readings.
    @param shares A list holding the shares used by this task, the setpoint and 
    position of motor one.
    """
    # Create motor2 objects.
    motor_dvr2 = motor_driver.MotorDriver(
        pyb.Pin.board.PC1, pyb.Pin.board.PA0, pyb.Pin.board.PA1, 5
        )
    motor_dvr2.enable()
    encoder2 = encoder_reader.EncoderReader(
        pyb.Pin.board.PB6, pyb.Pin.board.PB7, 4
        )
    controller2 = clp_controller.CLPController()
    
    controller2.set_Kp(0.02)
    
    # Get references to the share and queue which have been passed to this task.
    setpoint_m2, position_m2 = shares

    while True:
        new_setpoint = setpoint_m2.get()
        controller2.set_setpoint(new_setpoint)
        motor_dvr2.set_duty_cycle(
            controller2.run(new_setpoint, encoder2.read())
            )
        position_m2.put(
            controller2.motor_positions[len(controller2.motor_positions)-1]
            ) # encoder starting to read now when changing the position
        yield 0

def task_step_response(shares):
    """!
    This task writes the position data of both motors to the serial port.
    @param shares A list holding the shares used by this task, the setpoints and 
    positions of motors one and two.
    """
    setpoint_m1, position_m1, setpoint_m2, position_m2 = shares
    
    u2 = pyb.UART(2, baudrate=115200)
    start_time = utime.ticks_ms()
    time = 0
    
    m1_positions = []
    m2_positions = []
    times = []
    data = []
    some_flag = 0
    while True:
        #if setpoint reached
        if time < 3000:
            
            time = utime.ticks_ms() - start_time
            curr_pos_m1 = position_m1.get()
            curr_pos_m2 = position_m2.get()

            data.append(array.array('i',[time, curr_pos_m1, curr_pos_m2]))
            print([time, curr_pos_m1, curr_pos_m2])
            yield 0
            
        if time>= 3000:
            for i in data:
                u2.write(f'{i[0]},{i[1]}\r\n')
            u2.write(b"Done!\r\n")
            
        yield 0


if __name__ == "__main__":
    # Create shares.
    share_m1_setpoint = task_share.Share(
        'l', thread_protect=False, name="Share m1 setpt"
        )
    share_m1_position = task_share.Share(
        'l', thread_protect=False, name="Share m1 pos"
        )
    share_m2_setpoint = task_share.Share(
        'l', thread_protect=False, name="Share m2 setpt"
        )
    share_m2_position = task_share.Share(
        'l', thread_protect=False, name="Share m2 pos")
    
    share_m1_setpoint.put(20000)
    share_m2_setpoint.put(10000)
    
    # Create the tasks.
    task1 = cotask.Task(
        task_motor1, name="Task_1", priority=1, period=20, #change the period here
        profile=True, trace=True, shares=(
            share_m1_setpoint, share_m1_position
            )
        )
    task2 = cotask.Task(
        task_motor2, name="Task_2", priority=1, period=50,
        profile=True, trace=True, shares=(
            share_m2_setpoint, share_m2_position
            )
        )
    task3 = cotask.Task(
        task_step_response, name="Task_3", priority=2, period=10,
        profile=True, trace=True, shares=(
            share_m1_setpoint, share_m1_position, 
            share_m2_setpoint, share_m2_position
            )
        )
    
    cotask.task_list.append(task1)
    cotask.task_list.append(task2)
    cotask.task_list.append(task3)

    # Run the memory garbage collector.
    gc.collect()

    # Run the scheduler with the chosen scheduling algorithm. Quit if ^C pressed
    while True:
        try:
            cotask.task_list.pri_sched()
        except KeyboardInterrupt:
            break
