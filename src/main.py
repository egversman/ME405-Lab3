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
    
    @param shares A list holding the share and queue used by this task
    """
    # Create motor1 objects.
    motor_dvr1 = motor_driver.MotorDriver()
    motor_dvr1.enable()
    encoder1 = encoder_reader.EncoderReader()
    controller1 = clp_controller.CLPController()
    
    controller1.set_Kp(0.2)
    
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
    
    @param shares A list holding the share and queue used by this task
    """
    # Create motor2 objects.
    motor_dvr2 = motor_driver.MotorDriver(pyb.Pin.board.PC1, pyb.Pin.board.PA0, pyb.Pin.board.PA1, 5)
    motor_dvr2.enable()
    encoder2 = encoder_reader.EncoderReader(pyb.Pin.board.PB6, pyb.Pin.board.PB7, 4)
    controller2 = clp_controller.CLPController()
    
    controller2.set_Kp(0.1)
    
    # Get references to the share and queue which have been passed to this task.
    setpoint_m2, position_m2 = shares

    while True:
        new_setpoint = setpoint_m2.get()
        controller2.set_setpoint(new_setpoint)
        motor_dvr2.set_duty_cycle(
            controller2.run(new_setpoint, encoder2.read())
            )
        position_m2.put(len(controller2.motor_positions)-1) # encoder starting to read now when changing the position
        yield 0

def task_step_response(shares):
    """!
    
    @param shares A list holding the share and queue used by this task
    """
    setpoint_m1, position_m1, setpoint_m2, position_m2 = shares
    
    #setpoint_m1.put(20000)
    #setpoint_m2.put(10000)
    # print value of setpoint in diff locations
    u2 = pyb.UART(2, baudrate=115200)
    start_time = utime.ticks_ms()
    time = 0

    data = []
    
    while time < 3000:
        time = utime.ticks_ms() - start_time
        data.append(array.array('b',[time,position_m1.get(),position_m2.get()]))
        print([time,position_m1.get(),position_m2.get()])
        yield 0
    
    for line in data:
        u2.write(f'{line[0]},{line[1]}\r\n')
    u2.write(b"Done!\r\n")
    yield 0


# The file main...
if __name__ == "__main__":
    print("Testing ME405 stuff in cotask.py and task_share.py\r\n"
          "Press Ctrl-C to stop and show diagnostics.")

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
    # goal of debugging is to gather as much information as possible
    
    # Create the tasks.
    task1 = cotask.Task(
        task_motor1, name="Task_1", priority=1, period=10, 
        profile=True, trace=True, shares=(
            share_m1_setpoint, share_m1_position
            )
        )
    task2 = cotask.Task(
        task_motor2, name="Task_2", priority=1, period=20,
        profile=True, trace=True, shares=(
            share_m2_setpoint, share_m2_position
            )
        )
    task3 = cotask.Task(
        task_step_response, name="Task_3", priority=2, period=100,
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

    # Print a table of task data and a table of shared information data
    print('\n' + str (cotask.task_list))
    print(task_share.show_all())
    print(task1.get_trace())
    print('')

    # call code to disable motor
    motor_dvr1.disable()
    motor_dvr2.disable()
    

#write an enable and disable method