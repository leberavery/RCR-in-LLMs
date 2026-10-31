import robot_setup

import math

# -----------------------------
# IDENTIFY GOAL
# -----------------------------
def identifyGoal():
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
                
# -----------------------------
# COLLISION DETECTION
# -----------------------------
    # With a 0-2m range returning 0-1000:
    # 500 means there is a wall 1 meter away.
    # 800 means there is a wall 0.4 meters away.
def collisionDetection():
    global path_ahead
    robot_setup.supervisor.step(robot_setup.timestep)
    
    val = robot_setup.distanceSensor.getValue()

    if (val > 900):
        status = "BLOCKED PATH: Cannot Move Forward. Try Turning."
    else:
        status = "CLEAR PATH."
    
    #print(f"Laser Value: {val:.2f} | Status: {status}")
    
    return status, val
# -----------------------------
# COORDINATE HISTORY
# -----------------------------
# Initialize starting state
current_pos = [0, 0]
current_heading = "SOUTH"
visited_coords = [tuple(current_pos)] 

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

def update_coordinates(action):
    global current_pos, current_heading
    current_heading = get_cardinal_heading()
    
    if action == "F":
        if current_heading == "NORTH": current_pos[1] += 1
        elif current_heading == "SOUTH": current_pos[1] -= 1
        elif current_heading == "EAST": current_pos[0] += 1
        elif current_heading == "WEST": current_pos[0] -= 1
    elif action == "B":
        if current_heading == "NORTH": current_pos[1] -= 1
        elif current_heading == "SOUTH": current_pos[1] += 1
        elif current_heading == "EAST": current_pos[0] -= 1
        elif current_heading == "WEST": current_pos[0] += 1

    new_coord = tuple(current_pos)
    if new_coord not in visited_coords:
        visited_coords.append(new_coord)
    return new_coord

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

def get_forward_coordinate(pos, heading):
    """Calculates the (x, y) coordinate directly in front of the robot."""
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