# ------------------------
# Code Author: Avery Leber
# Purpose: run_failure.py is composed of the two ways a run can fail:
#           1. timed_out() - The current run exceeds the step limit.
#           2. is_stuck() - The LLM is stuck turning.
#           Each function returns a Boolean that determines whether a failure condition was triggered 
#           and if the current run should end. 
# ------------------------
import config
import initialize_run
import robot_setup

import time

def timed_out():
    # Failure: Run Timed Out   
    if (len(initialize_run.actionSequence) > config.STEP_LIMIT):
        # Immediate stop
        robot_setup.left_motor.setVelocity(0.0)
        robot_setup.right_motor.setVelocity(0.0)
        print("Robot stopped")

        # Stop Timer
        endTime = time.time()
        timeToComplete = None

        if (config.COLLECT_DATA):
            # Write to File
            with open(config.FILE_NAME, "a", encoding="utf-8") as f:
                f.write(f"False, {timeToComplete}, {len(initialize_run.actionSequence)}, {initialize_run.actionSequence}\n")

        # Reset simulation
        robot_setup.supervisor.simulationReset()
        robot_setup.supervisor.step(robot_setup.timestep)
        return True         # End run
    else: return False      # Continue run

# Failure Condition: Stuck
def is_stuck(): 
    # Extract just the action character (the first letter) from each history entry
    action_history = [entry[0] for entry in initialize_run.history if entry]
    history_string = "".join(action_history)
    
    # Subcondition 1: All moves are identical (e.g., repeating 'L' or 'R')
    is_spinning = len(set(action_history)) == 1 and action_history[0] in ('L', 'R')
    
    # Subcondition 2: Oscillating back and forth continuously
    is_oscillating = "LRLRLRLRLR" in history_string or "RLRLRLRLRL" in history_string

    # Trigger failure behavior if either condition is met
    if len(history_string) > 5 and is_spinning or is_oscillating:
        # Immediate stop
        robot_setup.left_motor.setVelocity(0.0)
        robot_setup.right_motor.setVelocity(0.0)

        # Stop Timer
        endTime = time.time()
        timeToComplete = None

        # Write to File
        if (config.COLLECT_DATA):
            with open(config.FILE_NAME, "a", encoding="utf-8") as f:
                f.write(f"False, {timeToComplete}, {len(initialize_run.actionSequence)}, {initialize_run.actionSequence}\n")

        # Reset simulation
        robot_setup.supervisor.simulationReset()
        robot_setup.supervisor.step(robot_setup.timestep)
        return True         # End run
    else: return False      # Continue run
