# ------------------------
# Code Author: Avery Leber
# Purpose: main.py is the starting point for the Supervisor Controller.
#          The general process is as follows:
#           1. Check if the run has exceed the step limit ("Timed Out")
#           2. Check if the LLM has gotten stuck 
#           3. Check if the goal has been found
#           4. Get, read, and execute the LLM's output
#           5. Repeat until the a failure condition is triggered or the goal is found
#
# To enable data collection, set @COLLECT_DATA to True in config.py.
# If data collection is enabled, set @FILE_NAME in config.py to a CSV file of your choice to record data.
# To confire the number of runs the program should do, set @RUN_NUM in config.py to a positive non-zero integer of your choice
# To configure the step limit of the run, set @STEP_LIMIT in config.py to a positive non-zero integer of your choice
# ------------------------

import config
import initialize_run
import robot_setup
import run_failed
import sensor_data
import llm

def main():
    print("Starting Autonomous Navigation...")
    for _ in range(config.RUN_NUM):
            initialize_run.initializeRun()
    
            while robot_setup.supervisor.step(robot_setup.timestep) != -1:
                # 1. Check if Run Failed: Run Timed Out 
                if (run_failed.timed_out()): break
    
                # 2. Check if Run Failed: Stuck
                if (run_failed.is_stuck()): break
    
                # 3. Check if Goal is Found:
                if (sensor_data.goal_found()): break
    
                # 4. Get and Read LLM Output
                output = llm.prompt_llm(sensor_data.collision_detection(), sensor_data.identify_goal(), sensor_data.get_neighbor_info())
                llm.read_llm_output(output)

main()