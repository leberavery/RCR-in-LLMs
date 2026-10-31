from controller import Supervisor, DistanceSensor

supervisor = Supervisor()
timestep = int(supervisor.getBasicTimeStep())
print("Robot Initialized... (1/7)")

# Initialize Motors
left_motor = supervisor.getDevice("left wheel motor")
right_motor = supervisor.getDevice("right wheel motor")
# Set Motors to Velocity Control Mode
left_motor.setPosition(float("inf"))
right_motor.setPosition(float("inf"))
# Set Initial Motor Speed to Zero
left_motor.setVelocity(0.0)
right_motor.setVelocity(0.0)
print("Motors Initialized... (2/7)")

# Initialize Wheel Encoders
left_sensor = supervisor.getDevice("left wheel sensor")
right_sensor = supervisor.getDevice("right wheel sensor")
left_sensor.enable(timestep)
right_sensor.enable(timestep)
print("Encoders Initialized... (3/7)")

# Initialize Inertial Measurement Unit (IMU)
imu = supervisor.getDevice("inertial unit")
imu.enable(timestep)
print("IMU Initialized... (4/7)")

# Initialize Camera
camera = supervisor.getDevice("camera(1)")
camera.enable(timestep)
print("Camera Initialized...(5/7)")

# Enable Camera Recognition
recognition_cam = supervisor.getDevice("camera(1)")
recognition_cam.enable(timestep)
recognition_cam.recognitionEnable(timestep)
print("Recognition Enabled... (6/7)")

# Initialize Distance Sensors
distanceSensor = supervisor.getDevice("distance sensor")
distanceSensor.enable(timestep)
print("Distance Sensors Initialized... (7/7)")