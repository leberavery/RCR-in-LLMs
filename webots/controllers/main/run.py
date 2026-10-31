import constants
import robot_setup
import initialize_run
import sensor_data
import prompt_llm
import robot_movements

import time

######################
# Collect 35 runs
######################
def run(collect_data, runNum):
    for run in range(runNum):
        initialize_run.initializeRun()

        while robot_setup.supervisor.step(robot_setup.timestep) != -1:
            # Failure: Run Timed Out   
            if (len(constants.actionSequence) > 150):
                # Immediate stop
                robot_setup.left_motor.setVelocity(0.0)
                robot_setup.right_motor.setVelocity(0.0)

                # Stop Timer
                endTime = time.time()
                timeToComplete = None

                if (collect_data):
                    # Write to File
                    with open("ollama-gemma4-12b-maze3-data.csv", "a", encoding="utf-8") as f:
                        f.write(f"False, {timeToComplete}, {len(constants.actionSequence)}, {constants.actionSequence}\n")

                # Reset simulation
                robot_setup.supervisor.simulationReset()
                robot_setup.supervisor.step(robot_setup.timestep)

                break

            # Failure: Stuck 
            # Extract just the action character (the first letter) from each history entry
            action_history = [entry[0] for entry in initialize_run.history if entry]
            history_string = "".join(action_history)
            
            # Condition 1: All moves are identical (e.g., repeating 'L' or 'R')
            is_spinning = len(set(action_history)) == 1 and action_history[0] in ('L', 'R')
            
            # Condition 2: Oscillating back and forth continuously
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
                if (collect_data):
                    with open("ollama-gemma4-12b-maze3-data.csv", "a", encoding="utf-8") as f:
                        f.write(f"False, {timeToComplete}, {len(constants.actionSequence)}, {constants.actionSequence}\n")

                # Reset simulation
                robot_setup.supervisor.simulationReset()
                robot_setup.supervisor.step(robot_setup.timestep)

                break

            # 1. Get the current physical proximity (Laser) and visual status (Camera)
            current_status, laser_val = sensor_data.collisionDetection() 
            goal_status = sensor_data.identifyGoal()
            x, y = initialize_run.current_pos
            neighbors = {
                "NORTH": (x, y + 1),
                "SOUTH": (x, y - 1),
                "EAST": (x + 1, y),
                "WEST": (x - 1, y)
            }
            neighbor_info = sensor_data.check_neighbors(tuple(initialize_run.current_pos), initialize_run.current_heading, initialize_run.visited_coords)
            
            # Goal is in sight:
            if "STRAIGHT AHEAD" in goal_status and laser_val > 900:
                print(f"!!! TARGET REACHED: EXIT SECURED !!!")
                print(f"Final Laser Value: {laser_val:.2f} | Goal Status: {goal_status}")
                
                # Immediate stop
                robot_setup.left_motor.setVelocity(0.0)
                robot_setup.right_motor.setVelocity(0.0)

                # Stop Timer
                endTime = time.time()
                timeToComplete = '%.3f'%(endTime - constants.startTime)
                print(f"Time to Complete: {timeToComplete} seconds")

                # Action Sequence
                print(constants.actionSequence)

                # Write to file
                if (collect_data):
                    with open("ollama-gemma4-12b-maze3-data.csv", "a", encoding="utf-8") as f:
                        f.write(f"True, {timeToComplete}, {len(constants.actionSequence)}, {constants.actionSequence}\n")

                # Reset simulation
                robot_setup.supervisor.simulationReset()
                robot_setup.supervisor.step(robot_setup.timestep)
                
                # Break the loop to end the program
                break 

            facing_tile = sensor_data.get_forward_coordinate(tuple(initialize_run.current_pos), initialize_run.current_heading)
            
            # Determine if path ahead is new, explored, blocked, or a dead end:
            ''' 
                path_ahead is a tuple containing:
                1. Value of the laser sensor (higher = closer to object)
                2. Sensor Warning (0 = new and clear, 1 = blocked, 2 = explored, 4 = dead end)
            '''
            if laser_val > 900:
                initialize_run.sensor_warning = "BLOCKED PATH: Cannot Move Forward. Try Turning."
                path_ahead = ('%.3f'%(laser_val), 1)
            elif facing_tile in initialize_run.visited_coords:
                    unvisited_left = any(coord not in initialize_run.visited_coords for coord in neighbors.values())
                    if unvisited_left:
                        initialize_run.sensor_warning = "PRIORITY: You are facing an EXPLORED tile, but there are NEW tiles nearby. Turn to find them."
                        path_ahead = ('%.3f'%(laser_val), 2)

                    else:
                        initialize_run.sensor_warning = "DEAD END DETECTED: All surrounding tiles are EXPLORED. You MUST backtrack."
                        path_ahead = ('%.3f'%(laser_val), 4)

            else:
                initialize_run.sensor_warning = "Facing NEW territory. Safe to proceed F."
                path_ahead = ('%.3f'%(laser_val), 0)

            # print(f"Sensor Warning: {sensor_warning}")

            # 3. If the goal isn't reached, ask the LLM for the next navigational move
            action = prompt_llm.getNextStep(current_status, goal_status, neighbor_info)

            if action:
                print(f"LLM Decided Action: {action}")
                
                if action == "F":
                    robot_movements.forward()
                elif action == "B":
                    robot_movements.backward()
                elif action == "L":
                    robot_movements.turnLeft()
                elif action == "R":
                    robot_movements.turnRight()
                new_loc = sensor_data.update_coordinates(action)

                # Add data to step_data
                initialize_run.step_data.append(f"[{action}")
                initialize_run.step_data.append(prompt_llm.prompt_time)
                initialize_run.step_data.append(new_loc)
                initialize_run.step_data.append(f"{path_ahead}]")
                

                constants.actionSequence.append(initialize_run.step_data)

                facing_coord = sensor_data.get_forward_coordinate(new_loc, initialize_run.current_heading)
                # print(f"Robot now at: {new_loc} | Facing Tile: {facing_coord} ({current_heading})")
                # print(f"Neighbor Info: {neighbor_info}")
                    
            else:
                # Failsafe: stop if the LLM output is garbled
                robot_setup.left_motor.setVelocity(0.0)
                robot_setup.right_motor.setVelocity(0.0)
                print("Waiting for valid LLM command...")