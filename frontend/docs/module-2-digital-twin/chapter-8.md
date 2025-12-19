# Chapter 8: Gazebo Simulation Setup for Robotics

## Introduction to Robot Simulation

Physical prototyping of humanoid robots is expensive, time-consuming, and risky. A single hardware failure during bipedal walking tests can cost thousands in repairs. **Gazebo** solves this by providing a high-fidelity 3D robot simulator that accurately models physics, sensors, and actuators—enabling developers to test algorithms safely before deploying to real hardware.

**Gazebo** (formerly Gazebo Simulator, previously named "Ignition Gazebo" in newer versions) is an open-source robotics simulator that integrates seamlessly with ROS 2. It provides:
- **Photorealistic rendering** with GPU-accelerated graphics
- **Accurate physics simulation** using ODE, Bullet, DART, or Simbody engines
- **Sensor models** for cameras, LiDAR, IMU, GPS, force/torque sensors
- **Multi-robot simulations** for swarm robotics and human-robot interaction
- **Cloud-based simulation** for distributed testing

This chapter explores Gazebo's architecture, setup with ROS 2, world creation, robot spawning, and sensor integration—the foundation for digital twin development.

## Why Gazebo for Humanoid Robotics?

### The Cost of Physical Testing

Consider the challenges of developing bipedal walking:
- **Hardware risk**: Falls damage expensive actuators, sensors, and frames
- **Iteration speed**: Mechanical repairs take hours; simulation restarts instantly
- **Dangerous scenarios**: Testing obstacle avoidance with real humans is unsafe
- **Reproducibility**: Physical experiments vary with floor friction, battery charge, temperature

### Simulation Advantages

**1. Safe Failure Modes**:
- Test aggressive behaviors (running, jumping, stumbling) without hardware damage
- Simulate catastrophic failures (motor burnout, sensor loss) safely

**2. Accelerated Development**:
- Run multiple experiments in parallel (10x speedup with cloud simulation)
- Iterate on control algorithms hourly instead of daily
- Automated regression testing for every code change

**3. Scenario Diversity**:
- Test in environments impossible to replicate (stairs, rough terrain, zero gravity)
- Vary parameters systematically (mass, inertia, friction coefficients)
- Inject sensor noise, communication delays, actuator failures

**4. Cost Efficiency**:
- Develop algorithms before hardware arrives
- Reduce prototype iterations with validated designs
- Train multiple developers simultaneously on identical virtual robots

## Gazebo Architecture

### Core Components

Gazebo uses a **client-server architecture** separating physics computation from visualization:

```
┌─────────────────────────────────────────────────────┐
│                   Gazebo Server                      │
│  ┌────────────┐  ┌─────────────┐  ┌──────────────┐ │
│  │ Physics    │  │ Sensor      │  │ Plugin       │ │
│  │ Engine     │→ │ Manager     │→ │ System       │ │
│  │ (ODE/DART) │  │ (Ray, Cam)  │  │ (ROS Bridge) │ │
│  └────────────┘  └─────────────┘  └──────────────┘ │
└──────────────────────┬──────────────────────────────┘
                       │ Transport (Protobuf msgs)
                       ↓
┌─────────────────────────────────────────────────────┐
│                   Gazebo Client                      │
│  ┌────────────┐  ┌─────────────┐  ┌──────────────┐ │
│  │ GUI        │  │ Camera      │  │ Scene        │ │
│  │ Controls   │← │ Viewport    │← │ Renderer     │ │
│  │ (Qt)       │  │ (OGRE)      │  │ (GPU)        │ │
│  └────────────┘  └─────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────┘
```

**Gazebo Server**:
- Runs physics simulation at fixed timestep (default: 1ms` = 1000 Hz)
- Manages world state (entities, joints, collisions)
- Processes sensor data generation
- Executes plugin logic (ROS 2 bridge, custom controllers)

**Gazebo Client (GUI)**:
- Renders 3D scene using OGRE or Ignition Rendering
- Provides interactive controls (pause, reset, camera movement)
- Displays sensor visualizations (camera feeds, LiDAR point clouds)
- Optional: Can run headless (no GUI) for faster simulation

**Communication Layer**:
- Uses Google Protobuf for message serialization
- Asynchronous transport (ZeroMQ or custom implementation)
- Topic-based pub-sub (similar to ROS)

### Physics Engines

Gazebo supports multiple physics backends:

| Engine | Strengths | Use Cases |
|--------|-----------|-----------|
| **ODE** (Open Dynamics Engine) | Fast, stable contact dynamics | Default for most robots, good for wheels/manipulators |
| **Bullet** | Real-time performance, soft bodies | Games, deformable objects, cloth simulation |
| **DART** (Dynamic Animation and Robotics Toolkit) | Precision, numerical stability | Research, humanoid bipedal walking, contact-rich manipulation |
| **Simbody** | Biomechanics accuracy | Human motion simulation, medical applications |

**Choosing a Physics Engine**:
- **ODE**: Best for beginners, stable wheeled robots
- **DART**: Humanoid walking (better constraint resolution)
- **Bullet**: Fast multi-robot simulations (10+ robots)

## Installing Gazebo with ROS 2

### Gazebo Garden/Harmonic (Modern Stack)

ROS 2 Humble/Iron/Rolling use **Gazebo Garden** or **Gazebo Harmonic** (not the older Gazebo Classic 11):

```bash
# Install Gazebo Harmonic (latest stable)
sudo apt-get update
sudo apt-get install gz-harmonic

# Install ROS 2 Gazebo integration
sudo apt-get install ros-humble-ros-gz

# Verify installation
gz sim --version
# Output: Gazebo Sim, version 8.x.x
```

### ROS 2 Gazebo Packages

Install ROS 2 - Gazebo bridge packages:

```bash
sudo apt-get install \
  ros-humble-ros-gz-bridge \
  ros-humble-ros-gz-sim \
  ros-humble-ros-gz-image \
  ros-humble-ros-gz-interfaces
```

**Package purposes**:
- `ros-gz-bridge`: Converts Gazebo topics ↔ ROS 2 topics
- `ros-gz-sim`: Launch Gazebo from ROS 2 launch files
- `ros-gz-image`: Bridges camera/depth sensors to ROS 2 image topics
- `ros-gz-interfaces`: Message type conversions

## Creating Gazebo Worlds

### World File Structure (SDF Format)

Gazebo worlds use **SDF (Simulation Description Format)**, an XML-based specification:

**simple_world.sdf**:
```xml
<?xml version="1.0"?>
<sdf version="1.8">
  <world name="simple_world">

    <!-- Physics settings -->
    <physics name="1ms`" type="ode">
      <max_step_size>0.001</max_step_size>  <!-- 1ms` timestep -->
      <real_time_factor>1.0</real_time_factor>  <!-- Run at real-time speed -->
    </physics>

    <!-- Lighting -->
    <light type="directional" name="sun">
      <cast_shadows>true</cast_shadows>
      <pose>0 0 10 0 0 0</pose>
      <diffuse>1.0 1.0 1.0 1</diffuse>
      <specular>0.2 0.2 0.2 1</specular>
      <attenuation>
        <range>1000</range>
      </attenuation>
      <direction>-0.5 0.1 -0.9</direction>
    </light>

    <!-- Ground plane -->
    <model name="ground_plane">
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry>
            <plane>
              <normal>0 0 1</normal>
              <size>100 100</size>
            </plane>
          </geometry>
          <surface>
            <friction>
              <ode>
                <mu>0.8</mu>   <!-- Friction coefficient -->
                <mu2>0.8</mu2>
              </ode>
            </friction>
          </surface>
        </collision>
        <visual name="visual">
          <geometry>
            <plane>
              <normal>0 0 1</normal>
              <size>100 100</size>
            </plane>
          </geometry>
          <material>
            <ambient>0.8 0.8 0.8 1</ambient>
            <diffuse>0.8 0.8 0.8 1</diffuse>
          </material>
        </visual>
      </link>
    </model>

    <!-- Add obstacles -->
    <model name="box_obstacle">
      <pose>2 0 0.5 0 0 0</pose>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box>
              <size>1 1 1</size>
            </box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box>
              <size>1 1 1</size>
            </box>
          </geometry>
          <material>
            <ambient>1 0 0 1</ambient>
            <diffuse>1 0 0 1</diffuse>
          </material>
        </visual>
      </link>
    </model>

  </world>
</sdf>
```

**Launching the world**:
```bash
gz sim simple_world.sdf
```

### Complex Environments

**Loading pre-built models** from Gazebo Fuel (online model repository):

```xml
<include>
  <uri>https://fuel.gazebosim.org/1.0/OpenRobotics/models/Construction Cone</uri>
  <pose>3 2 0 0 0 0</pose>
</include>
```

**Common Gazebo Fuel models**:
- Construction Cone, Jersey Barrier (obstacles)
- AWS Robomaker Hospital, Office (indoor navigation)
- Moon Surface, Mars Terrain (space robotics)

## Spawning Robots in Gazebo

### Method 1: Include in World File

Add robot directly in SDF world:

```xml
<world name="robot_world">
  <!-- ... physics, lighting ... -->

  <include>
    <uri>model://my_humanoid</uri>  <!-- Path to robot SDF -->
    <pose>0 0 1.0 0 0 0</pose>  <!-- Initial position -->
    <name>humanoid_robot</name>
  </include>
</world>
```

### Method 2: Spawn from ROS 2 Launch File

**Spawn robot dynamically** using ROS 2:

```python
from launch import LaunchDescription
from launch.actions import ExecuteProcess, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    # Path to robot description
    robot_desc_path = os.path.join(
        get_package_share_directory('my_robot_description'),
        'urdf',
        'humanoid.urdf'
    )

    # Read URDF file
    with open(robot_desc_path, 'r') as file:
        robot_desc = file.read()

    # Launch Gazebo
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(get_package_share_directory('ros_gz_sim'), 'launch'),
            '/gz_sim.launch.py'
        ]),
        launch_arguments={
            'gz_args': 'empty.sdf -r'  # Load empty world, start paused
        }.items()
    )

    # Spawn robot entity
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', 'humanoid',
            '-topic', 'robot_description',
            '-x', '0', '-y', '0', '-z', '1.0'
        ],
        output='screen'
    )

    # Robot state publisher (publishes TF from URDF)
    robot_state_pub = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_desc}],
        output='screen'
    )

    return LaunchDescription([
        gazebo,
        robot_state_pub,
        spawn_robot
    ])
```

**Usage**:
```bash
ros2 launch my_robot_gazebo spawn_robot.launch.py
```

## Sensor Simulation in Gazebo

### Camera Sensor

Add camera to robot URDF:

```xml
<gazebo reference="camera_link">
  <sensor name="camera" type="camera">
    <update_rate>30</update_rate>
    <camera>
      <horizontal_fov>1.047</horizontal_fov>  <!-- 60 degrees -->
      <image>
        <width>640</width>
        <height>480</height>
        <format>R8G8B8</format>
      </image>
      <clip>
        <near>0.1</near>
        <far>100</far>
      </clip>
      <noise>
        <type>gaussian</type>
        <mean>0.0</mean>
        <stddev>0.007</stddev>
      </noise>
    </camera>

    <!-- Bridge to ROS 2 -->
    <plugin name="camera_plugin" filename="libgazebo_ros_camera.so">
      <ros>
        <namespace>/camera</namespace>
        <argument>~/image_raw:=image_raw</argument>
        <argument>~/camera_info:=camera_info</argument>
      </ros>
      <camera_name>front_camera</camera_name>
      <frame_name>camera_link</frame_name>
    </plugin>
  </sensor>
</gazebo>
```

**ROS 2 topics published**:
- `/camera/image_raw` (sensor_msgs/Image)
- `/camera/camera_info` (sensor_msgs/CameraInfo)

### LiDAR Sensor

Add 2D/3D LiDAR (laser scanner):

```xml
<gazebo reference="lidar_link">
  <sensor name="lidar" type="gpu_ray">
    <update_rate>10</update_rate>
    <ray>
      <scan>
        <horizontal>
          <samples>360</samples>
          <resolution>1</resolution>
          <min_angle>-3.14159</min_angle>
          <max_angle>3.14159</max_angle>
        </horizontal>
      </scan>
      <range>
        <min>0.1</min>
        <max>30.0</max>
        <resolution>0.01</resolution>
      </range>
      <noise>
        <type>gaussian</type>
        <mean>0.0</mean>
        <stddev>0.01</stddev>
      </noise>
    </ray>

    <plugin name="lidar_plugin" filename="libgazebo_ros_ray_sensor.so">
      <ros>
        <namespace>/lidar</namespace>
        <argument>~/out:=scan</argument>
      </ros>
      <output_type>sensor_msgs/LaserScan</output_type>
      <frame_name>lidar_link</frame_name>
    </plugin>
  </sensor>
</gazebo>
```

**ROS 2 topic**: `/lidar/scan` (sensor_msgs/LaserScan)

### IMU Sensor

Inertial Measurement Unit for orientation and acceleration:

```xml
<gazebo reference="imu_link">
  <sensor name="imu_sensor" type="imu">
    <always_on>true</always_on>
    <update_rate>100</update_rate>
    <imu>
      <angular_velocity>
        <x>
          <noise type="gaussian">
            <mean>0.0</mean>
            <stddev>2e-4</stddev>
          </noise>
        </x>
        <!-- Repeat for y, z -->
      </angular_velocity>
      <linear_acceleration>
        <x>
          <noise type="gaussian">
            <mean>0.0</mean>
            <stddev>1.7e-2</stddev>
          </noise>
        </x>
        <!-- Repeat for y, z -->
      </linear_acceleration>
    </imu>

    <plugin name="imu_plugin" filename="libgazebo_ros_imu_sensor.so">
      <ros>
        <namespace>/imu</namespace>
        <argument>~/out:=data</argument>
      </ros>
      <frame_name>imu_link</frame_name>
    </plugin>
  </sensor>
</gazebo>
```

**ROS 2 topic**: `/imu/data` (sensor_msgs/Imu)

## ROS 2 - Gazebo Bridge

### Topic Bridging

Bridge Gazebo topics to ROS 2:

```python
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    # Bridge Gazebo clock to ROS 2
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            '/model/humanoid/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
            '/model/humanoid/odometry@nav_msgs/msg/Odometry@gz.msgs.Odometry',
            '/lidar/scan@sensor_msgs/msg/LaserScan@gz.msgs.LaserScan'
        ],
        output='screen'
    )

    return LaunchDescription([bridge])
```

**Bridge syntax**: `<topic>@<ros_type>[@<gz_type>]`

### Image Bridging

For camera images (requires `ros_gz_image`):

```python
image_bridge = Node(
    package='ros_gz_image',
    executable='image_bridge',
    arguments=['/camera/image_raw'],
    output='screen'
)
```

## Best Practices for Gazebo Simulation

### 1. Physics Timestep Tuning

**Stability vs Speed Trade-off**:
- **Smaller timestep** (0.001s = 1ms`): More stable, slower simulation
- **Larger timestep** (0.01s = 10ms`): Faster, less stable (may explode)

**Rule**: Timestep should be ≤ 1/(10 × fastest dynamics frequency)

For a 100 Hz control loop:
```xml
<max_step_size>0.001</max_step_size>  <!-- 1ms`, 10x faster than 100 Hz -->
```

### 2. Use Headless Mode for CI/CD

Run without GUI for automated testing:
```bash
gz sim -s world.sdf  # Server-only mode
```

### 3. Real-Time Factor Monitoring

Check if simulation keeps up with real time:
```bash
gz topic -e -t /stats
```

**Real-time factor = 1.0**: Simulation runs at real-time speed
**Real-time factor < 1.0**: Simulation is slower than real time (add GPU, reduce complexity)
**Real-time factor > 1.0**: Simulation faster than real time (for accelerated testing)

### 4. Collision Mesh Simplification

Use simplified collision geometries:
```xml
<collision name="collision">
  <geometry>
    <box>  <!-- Simple box collision -->
      <size>0.5 0.5 1.0</size>
    </box>
  </geometry>
</collision>

<visual name="visual">
  <geometry>
    <mesh>  <!-- Detailed visual mesh -->
      <uri>model://humanoid/meshes/torso.dae</uri>
    </mesh>
  </geometry>
</visual>
```

**Benefit**: 10-100× faster collision detection

### 5. Sensor Update Rate Matching

Match sensor rates to real hardware:
- Camera: 30 Hz (typical RGB camera)
- LiDAR: 10 Hz (Velodyne VLP-16)
- IMU: 100-1000 Hz (MPU-6050, Xsens)

**Avoid**: Setting all sensors to 1000 Hz (unnecessary computation)

## Summary

Gazebo provides a production-ready simulation environment for developing and validating humanoid robots before hardware deployment. Key takeaways:

- **Architecture**: Client-server model separates physics (server) from rendering (client)
- **Physics engines**: ODE (default), DART (humanoids), Bullet (speed)
- **ROS 2 integration**: Seamless via `ros_gz` packages for topic bridging
- **World creation**: SDF XML format for environments, models, and sensors
- **Sensor simulation**: Accurate models for cameras, LiDAR, IMU with realistic noise
- **Performance**: Tune timesteps, use headless mode, simplify collision meshes

In the next chapter, we'll explore **URDF to SDF conversion** and creating custom robot models for Gazebo simulation.

---

**Key Takeaways**:
- Gazebo enables safe, cost-effective testing before hardware deployment
- Multiple physics engines available (ODE, DART, Bullet) for different use cases
- ROS 2 integration via `ros_gz` packages bridges Gazebo ↔ ROS 2 topics
- SDF format describes worlds, models, sensors with XML syntax
- Sensor plugins generate realistic data (camera, LiDAR, IMU) with noise models
- Performance optimization: timestep tuning, headless mode, simplified collisions
