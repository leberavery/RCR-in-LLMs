# ------------------------
# Code Author: Avery Leber
# Purpose: sensor_data.py is composed of a list of functions that obtains and contextualizes data from the robot's sensors.
#          Functions include:
#          1. identify_goal()
#          2. goal_found()
#          3. collision_detection()
#          4. get_cardinal_heading()
#          5. update_coordinates()
#          6. check_neighbors()
#          7. get_neighbor_info()
#          8. get_forward_coordinate()
#          9. get_path_ahead()
#          10. get_sensor_warning()
# ------------------------
import config
import robot_setup
import initialize_run

import math
import time

# IDENTIFY GOAL - Goal is in Sight
def identify_goal():
    objects = robot_setup.recognition_cam.getRecognitionObjects()
    
    farthest_exit = None
    max_distance = -1.0
    
    for obj in objects:
        model = obj.getModel().lower()
        pos = obj.getPosition() 
        # Z is depth/forward distance
        distance = pos[2] 
        
        if "exit" in model and obj.getColors()[1] > 0.8:
            if distance > max_distance:
                max_distance = distance
                farthest_exit = obj

    if farthest_exit:
        pos = farthest_exit.getPosition()
        
        # Use pos[2] for centering and pos[0] for distance
        x_offset_raw = pos[2]  
        distance_raw = pos[0]  
        
        dist_mm = int(abs(distance_raw) * 1000) 
        offset_mm = int(x_offset_raw * 1000)

        # ALIGNMENT CHECK: 
        if -250 <= offset_mm <= 250:
            direction = "STRAIGHT AHEAD"
            print(f"GOAL LOCKED: {direction} ({dist_mm}mm away)")
            return f"GREEN EXIT VISIBLE {direction} ({dist_mm}mm away)"
        else:
            side = "LEFT" if offset_mm < 0 else "RIGHT"
            print(f"Goal detected at {side} (Offset: {offset_mm}mm)")
            return "NOT IN SIGHT"
    return "NOT IN SIGHT" 

# GOAL FOUND - Goal is Found
def goal_found():
    laser_val = collision_detection()
    goal_status = identify_goal()
    if "STRAIGHT AHEAD" in goal_status and laser_val > 900:
        print(f"!!! TARGET REACHED: EXIT SECURED !!!")
        print(f"Final Laser Value: {laser_val:.2f} | Goal Status: {goal_status}")
        
        # Immediate stop
        robot_setup.left_motor.setVelocity(0.0)
        robot_setup.right_motor.setVelocity(0.0)

        # Stop Timer
        endTime = time.time()
        timeToComplete = '%.3f'%(endTime - initialize_run.startTime)
        print(f"Time to Complete: {timeToComplete} seconds")

        # Action Sequence
        print(initialize_run.actionSequence)

        # Write to file
        if (config.COLLECT_DATA):
            with open(config.FILE_NAME, "a", encoding="utf-8") as f:
                f.write(f"True, {timeToComplete}, {len(initialize_run.actionSequence)}, {initialize_run.actionSequence}\n")

        # Reset simulation
        robot_setup.supervisor.simulationReset()
        robot_setup.supervisor.step(robot_setup.timestep)

        return True     # End run
    return False        # Continue run
          
# COLLISION DETECTION
    # With a 0-2m range returning 0-1000:
    # 500 means there is a wall 1 meter away.
    # 800 means there is a wall 0.4 meters away.
def collision_detection():
    global path_ahead
    robot_setup.supervisor.step(robot_setup.timestep)
    
    val = robot_setup.distanceSensor.getValue()

    if (val > 900):
        status = "BLOCKED PATH: Cannot Move Forward. Try Turning."
    else:
        status = "CLEAR PATH."
    
    #print(f"Laser Value: {val:.2f} | Status: {status}")
    
    return status, val

# CARDINAL HEADING 
    # The cardinal direction that the robot is facing
def get_cardinal_heading():
    """Converts IMU yaw to the nearest cardinal direction."""
    yaw = robot_setup.imu.getRollPitchYaw()[2] # Get Z-axis rotation
    
    # Normalize yaw to 0 - 2pi
    if yaw < 0:
        yaw += 2 * math.pi
        
    # Map radians to cardinal directions
    # North: ~1.57 rad, West: ~3.14 rad, South: ~4.71 rad, East: ~0 or 6.28 rad
    if 0.785 <= yaw < 2.355:
        return "NORTH"
    elif 2.355 <= yaw < 3.925:
        return "WEST"
    elif 3.925 <= yaw < 5.495:
        return "SOUTH"
    else:
        return "EAST"

# UPDATE COORDINATES 
    # A helper function that keeps track of the coordinate position the robot currently is
def update_coordinates(action):
    current_heading = get_cardinal_heading()
    visited_coords = [tuple(initialize_run.current_pos)] 

    
    if action == "F":
        if current_heading == "NORTH": initialize_run.current_pos[1] += 1
        elif current_heading == "SOUTH": initialize_run.current_pos[1] -= 1
        elif current_heading == "EAST": initialize_run.current_pos[0] += 1
        elif current_heading == "WEST": initialize_run.current_pos[0] -= 1
    elif action == "B":
        if current_heading == "NORTH": initialize_run.current_pos[1] -= 1
        elif current_heading == "SOUTH": initialize_run.current_pos[1] += 1
        elif current_heading == "EAST": initialize_run.current_pos[0] -= 1
        elif current_heading == "WEST": initialize_run.current_pos[0] += 1

    new_coord = tuple(initialize_run.current_pos)
    if new_coord not in visited_coords:
        visited_coords.append(new_coord)
    return new_coord

# CHECK NEIGHBORS
    # Checks the exploration status of neighboring tilles
    # Status can be NEW or EXPLORED
def check_neighbors(pos, heading, visited):
    x, y = pos
    neighbors = {
        "NORTH": (x, y + 1),
        "SOUTH": (x, y - 1),
        "EAST": (x + 1, y),
        "WEST": (x - 1, y)
    }
    
    status_updates = []
    for dir_key, coord in neighbors.items():
        if coord in visited:
            tag = "(EXPLORED)"
            status_updates.append(f"{dir_key}: {coord} {tag}")
        else:
            status_updates.append(f"{dir_key}: {coord} (NEW)")
    
    return " | ".join(status_updates)

# GET NEIGHBOR INFO
    # Return the robot's current coordinate position, heading, and list of visited coordinates
def get_neighbor_info():
    return check_neighbors(tuple(initialize_run.current_pos), initialize_run.current_heading, initialize_run.visited_coords)

# GET FORWARD COORDINATE
    # Returns the (x, y) coordinate directly in front of the robot.
def get_forward_coordinate(pos, heading):
    x, y = pos
    if heading == "NORTH":
        return (x, y + 1)
    elif heading == "SOUTH":
        return (x, y - 1)
    elif heading == "EAST":
        return (x + 1, y)
    elif heading == "WEST":
        return (x - 1, y)
    return (x, y) # Fallback

# GET PATH AHEAD
    # Determine if path ahead is new, explored, blocked, or a dead end:
    #   @path_ahead is a tuple containing:
    #   1. Value of the laser sensor (higher = closer to object)
    #   2. Sensor Warning (0 = new and clear, 1 = blocked, 2 = explored, 4 = dead end)
def get_path_ahead():
    current_status, laser_val = collision_detection() 
    facing_tile = get_forward_coordinate(tuple(initialize_run.current_pos), initialize_run.current_heading)
    x, y = initialize_run.current_pos
    neighbors = {
                    "NORTH": (x, y + 1),
                    "SOUTH": (x, y - 1),
                    "EAST": (x + 1, y),
                    "WEST": (x - 1, y)
                }
    if laser_val > 900:
        path_ahead = ('%.3f'%(laser_val), 1)
    elif facing_tile in initialize_run.visited_coords:
            unvisited_left = any(coord not in initialize_run.visited_coords for coord in neighbors.values())
            if unvisited_left:
                path_ahead = ('%.3f'%(laser_val), 2)

            else:
                path_ahead = ('%.3f'%(laser_val), 4)
    else:
        path_ahead = ('%.3f'%(laser_val), 0)
    return path_ahead

# GET SENSOR WARNING
    # Returns whether the path ahead is new, explored, blocked, or a dead end
    # @sensor_warning is a String
    # TODO: Is this necessary?
def get_sensor_warning():
    current_status, laser_val = collision_detection() 
    facing_tile = get_forward_coordinate(tuple(initialize_run.current_pos), initialize_run.current_heading)
    x, y = initialize_run.current_pos
    neighbors = {
                    "NORTH": (x, y + 1),
                    "SOUTH": (x, y - 1),
                    "EAST": (x + 1, y),
                    "WEST": (x - 1, y)
                }
    if laser_val > 900:
        sensor_warning = "BLOCKED PATH: Cannot Move Forward. Try Turning."
    elif facing_tile in initialize_run.visited_coords:
            unvisited_left = any(coord not in initialize_run.visited_coords for coord in neighbors.values())
            if unvisited_left:
                sensor_warning = "PRIORITY: You are facing an EXPLORED tile, but there are NEW tiles nearby. Turn to find them."

            else:
                sensor_warning = "DEAD END DETECTED: All surrounding tiles are EXPLORED. You MUST backtrack."
    else:
        sensor_warning = "Facing NEW territory. Safe to proceed F."
    # print(f"Sensor Warning: {sensor_warning}")
    return sensor_warning