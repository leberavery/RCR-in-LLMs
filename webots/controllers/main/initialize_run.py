import robot_setup

import time

def initializeRun():
    global startTime
    global prompt_time
    global current_pos
    global current_heading
    global visited_coords
    global actionSequence
    global step_data
    global path_ahead
    global history
    global history_string
    global action_history
    

    startTime = time.time()
    current_pos = [0, 0]
    current_heading = "NORTH"
    visited_coords = []
    actionSequence = []
    step_data = []
    path_ahead = ()
    history = []
    history_string = ""
    sensor_warning = ""
    action_history = []

    robot_setup.left_motor.setPosition(float('inf'))
    robot_setup.right_motor.setPosition(float('inf'))
    robot_setup.left_motor.setVelocity(0.0)
    robot_setup.right_motor.setVelocity(0.0)
    print("Run Initialized.")