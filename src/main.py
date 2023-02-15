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


def task_motor1(shares):
    """!
    
    @param shares A list holding the share and queue used by this task
    """
    # Create motor1 objects.
    motor_dvr1 = motor_driver.MotorDriver()
    encoder1 = encoder_reader.EncoderReader()
    controller1 = clp_controller.CLPController()
    
    # Get references to the share and queue which have been passed to this task.
    setpoint_m1, position_m1 = shares
    
    while True:
        new_setpoint = setpoint_m1.get()
        controller1.set_setpoint(new_setpoint)
        motor_dvr1.set_duty_cycle(
            controller1.run(new_setpoint, encoder1.read())
            )
        position_m1.put(controller1.motor_positions[0])
        yield 0


def task_motor2(shares):
    """!
    
    @param shares A list holding the share and queue used by this task
    """
    # Create motor1 objects.
    motor_dvr2 = motor_driver.MotorDriver("enter appropriate pins")
    encoder2 = encoder_reader.EncoderReader("enter appropriate pins")
    controller2 = clp_controller.CLPController("enter appropriate pins")
    
    # Get references to the share and queue which have been passed to this task.
    setpoint_m2, position_m2 = shares
    
    while True:
        new_setpoint = setpoint_m2.get()
        controller2.set_setpoint(new_setpoint)
        motor_dvr2.set_duty_cycle(
            controller2.run(new_setpoint, encoder2.read())
            )
        position_m2.put(controller2.motor_positions[0])
        yield 0

def task_step_response(shares):
    """!
    
    @param shares A list holding the share and queue used by this task
    """
    #
    u2 = pyb.UART(2, baudrate=115200)
    
    # Get references to the share and queue which have been passed to this task.
    setpoint_m1, position_m1, setpoint_m2, position_m2 = shares
    
    setpoint_m1.put("motor1 setpoint")
    setpoint_m2.put("motor2 setpoint")
    
    while True:
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
    
    # Create the tasks.
    task1 = cotask.Task(
        task_motor1, name="Task_1", priority=1, period=20, 
        profile=False, trace=False, shares=(
            share_m1_setpoint, share_m1_position
            )
        )
    task2 = cotask.Task(
        task_motor2, name="Task_2", priority=1, period=20,
        profile=False, trace=False, shares=(
            share_m2_setpoint, share_m2_position
            )
        )
    task3 = cotask.Task(
        task_step_response, name="Task_2", priority=1, period=20,
        profile=False, trace=False, shares=(
            share_m2_setpoint, share_m2_position
            )
        )
    
    cotask.task_list.append(task1)
    cotask.task_list.append(task2)

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
