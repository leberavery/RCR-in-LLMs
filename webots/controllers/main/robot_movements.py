# ------------------------
# Code Author: Avery Leber
# Purpose: robot_movements.py executes the physical movement advised by the LLM.
#          Available actions include:
#           1. Forward
#           2. Backward (not advertised)
#           3. Left
#           4. Right
# ------------------------
import config
import robot_setup
import sensor_data


from controller import Supervisor, DistanceSensor
import math


def forward():      # Move robot forward by one tile
    robot_setup.supervisor.step(robot_setup.timestep)
    print("Moving Forward...")
    target = config.TILE / config.WHEEL_RADIUS
    start = robot_setup.left_sensor.getValue()

    robot_setup.left_motor.setVelocity(config.MAX_SPEED)
    robot_setup.right_motor.setVelocity(config.MAX_SPEED)

    while robot_setup.supervisor.step(robot_setup.timestep) != -1:
        if abs(robot_setup.left_sensor.getValue() - start) >= target:
            break

    robot_setup.left_motor.setVelocity(0)
    robot_setup.right_motor.setVelocity(0)

    robot_setup.supervisor.step(robot_setup.timestep)

    return sensor_data.collision_detection()

def backward():    # Move robot backward by one tile
    robot_setup.supervisor.step(robot_setup.timestep)
    print("Moving Backward...")
    target = config.TILE / config.WHEEL_RADIUS
    start = robot_setup.left_sensor.getValue()

    robot_setup.left_motor.setVelocity(-config.MAX_SPEED)
    robot_setup.right_motor.setVelocity(-config.MAX_SPEED)

    while robot_setup.supervisor.step(robot_setup.timestep) != -1:
        if abs(robot_setup.left_sensor.getValue() - start) >= target:
            break

    robot_setup.left_motor.setVelocity(0)
    robot_setup.right_motor.setVelocity(0)

    robot_setup.supervisor.step(robot_setup.timestep)

    return sensor_data.collision_detection()

def turnRight():    # Turn robot in place 90 degrees
    """
    Move left and right motor in opposite directions until target_rad is reached.
    Args:
        target_rad (float): The rotation the e-puck needs to achieve, in radians.
        start_yaw, last_yaw, final_yaw (float): The value of the epuck2's Z-axis at a given moment.
        kp (float): The Gain that determines how aggressively the robot slows down. 
                    A higher gain stays faster for longer. Recommended 2.0 <= kp <= 5.0
        min_speed (float): The speed that the epuck2 will steadily reduce to as it approaches its target.
        error_rad (float): "How much farther we have to turn."
        calculated_speed (float): As error_rad approaches 0, calculated_speed approaches 0. Ensure "smooth" stop.
        speed (float): Dynamic speed that is dependent on error_rad
        
    """
    robot_setup.supervisor.step(robot_setup.timestep)
    print("Turning Right...")

    # Stabilize
    for _ in range(20):
        robot_setup.supervisor.step(robot_setup.timestep)

    # Get the initial  yaw
    start_yaw = robot_setup.imu.getRollPitchYaw()[2]

    target_rad = math.radians(90)
    kp = 4.5
    min_speed = 0.1
    last_yaw = robot_setup.imu.getRollPitchYaw()[2]

    total_turned_rad = 0.0

    while robot_setup.supervisor.step(robot_setup.timestep) != -1:
        current_yaw = robot_setup.imu.getRollPitchYaw()[2]

        # Calculate the difference in yaw and handle IMU "wrap-around" that occurs when the yaw "jumps" between minimum and maximum values, such as 359° to 0°.
        diff = current_yaw - last_yaw
        if diff > math.pi: 
            diff -= 2 * math.pi
        elif diff < -math.pi:
            diff += 2 * math.pi

        # Sum the absolute change to the total radians turned
        total_turned_rad += abs(diff)
        last_yaw = current_yaw

        # Calculate how much is left to turn
        error_rad = target_rad - total_turned_rad

        # Calculate speed based on error_rad. As error_rad approaches 0, speed approaches 0.
        calculated_speed = error_rad * kp

        # Ensure speed does not exceed MAX or drop below MIN
        speed = max(min_speed, min (calculated_speed, config.ROTATION_SPEED))

        # Turn
        robot_setup.left_motor.setVelocity(speed)
        robot_setup.right_motor.setVelocity(-speed)

        # Exit once target_rotation is reached
        if error_rad <= 0.001:
            break
    
    # Stop
    robot_setup.left_motor.setVelocity(0)
    robot_setup.right_motor.setVelocity(0)

    # Apply stop and update sensors
    robot_setup.supervisor.step(robot_setup.timestep)

    return sensor_data.collision_detection()

def turnLeft():    # Turn robot in place 90 degrees
    """
    Move left and right motor in opposite directions until target_rad is reached.
    Args:
        target_rad (float): The rotation the e-puck needs to achieve, in radians.
        start_yaw, last_yaw, final_yaw (float): The value of the epuck2's Z-axis at a given moment.
        kp (float): The Gain that determines how aggressively the robot slows down. 
                    A higher gain stays faster for longer. Recommended 2.0 <= kp <= 5.0
        min_speed (float): The speed that the epuck2 will steadily reduce to as it approaches its target.
        error_rad (float): "How much farther we have to turn."
        calculated_speed (float): As error_rad approaches 0, calculated_speed approaches 0. Ensure "smooth" stop.
        speed (float): Dynamic speed that is dependent on error_rad
    """
    robot_setup.supervisor.step(robot_setup.timestep)
    print("Turning Left...")

    # Stabilize
    for _ in range(20):
        robot_setup.supervisor.step(robot_setup.timestep)

    # Get the initial  yaw
    start_yaw = robot_setup.imu.getRollPitchYaw()[2]

    target_rad = math.radians(90)
    kp = 4.5
    min_speed = 0.1
    last_yaw = robot_setup.imu.getRollPitchYaw()[2]

    total_turned_rad = 0.0

    while robot_setup.supervisor.step(robot_setup.timestep) != -1:
        current_yaw = robot_setup.imu.getRollPitchYaw()[2]

        # Calculate the difference in yaw and handle IMU "wrap-around" that occurs when the yaw "jumps" between minimum and maximum values, such as 359° to 0°.
        diff = current_yaw - last_yaw
        if diff > math.pi: 
            diff -= 2 * math.pi
        elif diff < -math.pi:
            diff += 2 * math.pi

        # Sum the absolute change to the total radians turned
        total_turned_rad += abs(diff)
        last_yaw = current_yaw

        # Calculate how much is left to turn
        error_rad = target_rad - total_turned_rad

        # Calculate speed based on error_rad. As error_rad approaches 0, speed approaches 0.
        calculated_speed = error_rad * kp

        # Ensure speed does not exceed MAX or drop below MIN
        speed = max(min_speed, min (calculated_speed, config.ROTATION_SPEED))

        # Turn
        robot_setup.left_motor.setVelocity(-speed)
        robot_setup.right_motor.setVelocity(speed)

        # Exit once target_rotation is reached
        if error_rad <= 0.001:
            break
    
    # Stop
    robot_setup.left_motor.setVelocity(0)
    robot_setup.right_motor.setVelocity(0)

    # Apply stop and update sensors
    robot_setup.supervisor.step(robot_setup.timestep)

    return sensor_data.collision_detection()