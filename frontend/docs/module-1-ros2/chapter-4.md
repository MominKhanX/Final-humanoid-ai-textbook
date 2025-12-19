# Chapter 4: ROS 2 Launch Files and Package Management

## Introduction to ROS 2 Launches

As robotic systems grow in complexity, manually starting dozens of nodes with specific parameters becomes impractical and error-prone. **ROS 2 Launch** provides a powerful framework for orchestrating multi-node systems, configuring parameters, remapping topics, and managing node lifecycles—all from declarative configuration files.

Modern launch systems in ROS 2 offer significant improvements over ROS 1:
- **Python-based launch files**: Full programming capabilities for conditional logic
- **XML and YAML support**: Declarative syntax for simpler cases
- **Event-driven architecture**: React to node state changes dynamically
- **Composable nodes**: Launch multiple nodes in a single process for efficiency
- **Conditional execution**: Start nodes based on parameters or environment variables

This chapter explores ROS 2's launch system, package structure, and dependency management—the foundation for building maintainable, scalable robotic applications.

## The Need for Launch Files

### Manual Node Launching: The Problem

Consider launching a mobile robot system manually:

```bash
# Terminal 1: LIDAR driver
ros2 run lidar_driver lidar_node --ros-args -p port:=/dev/ttyUSB0

# Terminal 2: Camera driver
ros2 run camera_driver camera_node --ros-args -r /image:=/camera/image_raw

# Terminal 3: SLAM
ros2 run slam_toolbox async_slam_toolbox --ros-args -p use_sim_time:=false

# Terminal 4: Navigation
ros2 run nav2_bringup navigation_launch.py

# Terminal 5: Robot state publisher
ros2 run robot_state_publisher robot_state_publisher --ros-args -p robot_description:="$(cat robot.urdf)"
```

**Problems**:
- **Error-prone**: Easy to forget parameters or typos
- **Not reproducible**: Hard to replicate exact configuration
- **Debugging nightmare**: Which terminal had which node?
- **No coordination**: Nodes may start before dependencies are ready
- **Parameter management**: Hardcoded values, no central configuration

### Launch Files: The Solution

A single launch file replaces all manual commands:

```bash
ros2 launch my_robot robot.launch.py
```

**Benefits**:
- **Reproducibility**: Identical configuration every time
- **Version control**: Launch files in Git for team collaboration
- **Conditional logic**: Start nodes based on environment (sim vs real robot)
- **Parameter management**: Centralized YAML config files
- **Lifecycle coordination**: Ensure dependencies start in correct order

## ROS 2 Launch File Formats

ROS 2 supports three launch file formats, each with trade-offs:

### 1. Python Launch Files (Recommended)

**Advantages**:
- Full programming language capabilities (loops, conditionals, functions)
- Dynamic parameter computation
- Complex event handling
- Type checking and IDE support

**Use case**: Complex systems, conditional logic, multi-robot setups

**Example: Basic Python Launch File**

```python
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    """
    Launch LIDAR publisher and obstacle detector nodes
    """
    return LaunchDescription([
        # LIDAR publisher node
        Node(
            package='sensor_publishers',
            executable='lidar_publisher',
            name='lidar_node',
            parameters=[{
                'scan_rate': 10.0,
                'angle_range': 360.0,
                'min_range': 0.1,
                'max_range': 30.0
            }],
            remappings=[
                ('/scan', '/robot/scan')  # Remap topic
            ],
            output='screen'
        ),

        # Obstacle detector node
        Node(
            package='safety',
            executable='obstacle_detector',
            name='obstacle_detector',
            parameters=[{
                'warning_distance': 0.5,
                'emergency_stop_distance': 0.2
            }],
            output='screen'
        ),
    ])
```

**Launching**:
```bash
ros2 launch my_package basic.launch.py
```

### 2. XML Launch Files

**Advantages**:
- Declarative syntax (no programming required)
- Easy to read for simple cases
- Familiar to ROS 1 users

**Disadvantages**:
- Limited conditional logic
- Verbose for complex scenarios

**Example: XML Launch File**

```xml
<launch>
    <!-- LIDAR publisher -->
    <node pkg="sensor_publishers" exec="lidar_publisher" name="lidar_node" output="screen">
        <param name="scan_rate" value="10.0"/>
        <param name="angle_range" value="360.0"/>
        <remap from="/scan" to="/robot/scan"/>
    </node>

    <!-- Obstacle detector -->
    <node pkg="safety" exec="obstacle_detector" name="obstacle_detector" output="screen">
        <param name="warning_distance" value="0.5"/>
        <param name="emergency_stop_distance" value="0.2"/>
    </node>
</launch>
```

### 3. YAML Launch Files

**Advantages**:
- Most concise for parameter-heavy systems
- Human-readable
- Easy parameter inheritance

**Example: YAML Launch File**

```yaml
launch:
  - node:
      pkg: sensor_publishers
      exec: lidar_publisher
      name: lidar_node
      param:
        - name: scan_rate
          value: 10.0
        - name: angle_range
          value: 360.0
      remap:
        - from: /scan
          to: /robot/scan

  - node:
      pkg: safety
      exec: obstacle_detector
      name: obstacle_detector
      param:
        - name: warning_distance
          value: 0.5
```

## Advanced Launch Features

### 1. Including Other Launch Files

Modularize complex systems by composing launch files:

```python
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    # Get paths to other launch files
    sensors_launch = os.path.join(
        get_package_share_directory('robot_sensors'),
        'launch',
        'sensors.launch.py'
    )

    navigation_launch = os.path.join(
        get_package_share_directory('robot_navigation'),
        'launch',
        'navigation.launch.py'
    )

    return LaunchDescription([
        # Include sensor launch file
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(sensors_launch),
            launch_arguments={
                'use_sim_time': 'false',
                'lidar_enabled': 'true'
            }.items()
        ),

        # Include navigation launch file
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(navigation_launch)
        ),
    ])
```

### 2. Conditional Node Launching

Start nodes based on parameters or environment:

```python
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch.conditions import IfCondition, UnlessCondition

def generate_launch_description():
    # Declare launch arguments
    use_sim_arg = DeclareLaunchArgument(
        'use_sim',
        default_value='false',
        description='Use simulation time'
    )

    use_rviz_arg = DeclareLaunchArgument(
        'rviz',
        default_value='true',
        description='Launch RViz visualization'
    )

    # Get launch configuration
    use_sim = LaunchConfiguration('use_sim')
    use_rviz = LaunchConfiguration('rviz')

    return LaunchDescription([
        use_sim_arg,
        use_rviz_arg,

        # Launch real robot driver (only if NOT using sim)
        Node(
            package='robot_driver',
            executable='hardware_interface',
            name='robot_hw',
            condition=UnlessCondition(use_sim),
            parameters=[{'use_sim_time': False}],
            output='screen'
        ),

        # Launch simulator (only if using sim)
        Node(
            package='gazebo_ros',
            executable='spawn_entity.py',
            name='spawn_robot',
            condition=IfCondition(use_sim),
            arguments=['-entity', 'my_robot', '-topic', 'robot_description'],
            output='screen'
        ),

        # Launch RViz (if enabled)
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            condition=IfCondition(use_rviz),
            arguments=['-d', '/path/to/config.rviz'],
            output='screen'
        ),
    ])
```

**Usage**:
```bash
# Launch with simulation
ros2 launch my_robot robot.launch.py use_sim:=true

# Launch without RViz
ros2 launch my_robot robot.launch.py rviz:=false
```

### 3. Loading Parameters from YAML Files

Separate configuration from logic:

**params/robot_params.yaml**:
```yaml
lidar_node:
  ros__parameters:
    scan_rate: 10.0
    angle_range: 360.0
    min_range: 0.1
    max_range: 30.0
    frame_id: "laser_frame"

obstacle_detector:
  ros__parameters:
    warning_distance: 0.5
    emergency_stop_distance: 0.2
    alert_topic: "/safety/alerts"
```

**Launch file loading parameters**:
```python
from launch import LaunchDescription
from launch_ros.actions import Node
import os
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    # Path to parameter file
    params_file = os.path.join(
        get_package_share_directory('my_robot'),
        'config',
        'robot_params.yaml'
    )

    return LaunchDescription([
        Node(
            package='sensor_publishers',
            executable='lidar_publisher',
            name='lidar_node',
            parameters=[params_file],  # Load from YAML
            output='screen'
        ),

        Node(
            package='safety',
            executable='obstacle_detector',
            name='obstacle_detector',
            parameters=[params_file],
            output='screen'
        ),
    ])
```

### 4. Event Handlers and Lifecycle Management

React to node state changes:

```python
from launch import LaunchDescription
from launch_ros.actions import Node, LifecycleNode
from launch.actions import RegisterEventHandler, EmitEvent
from launch.event_handlers import OnProcessStart, OnProcessExit
from launch_ros.events.lifecycle import ChangeState
from lifecycle_msgs.msg import Transition

def generate_launch_description():
    # Managed (lifecycle) node
    camera_node = LifecycleNode(
        package='camera_driver',
        executable='camera_node',
        name='camera',
        namespace='',
        output='screen'
    )

    # Auto-configure camera when it starts
    configure_camera = RegisterEventHandler(
        OnProcessStart(
            target_action=camera_node,
            on_start=[
                EmitEvent(
                    event=ChangeState(
                        lifecycle_node_matcher=lambda node: node == camera_node,
                        transition_id=Transition.TRANSITION_CONFIGURE
                    )
                )
            ]
        )
    )

    # Auto-activate camera after configuration
    activate_camera = RegisterEventHandler(
        OnProcessStart(
            target_action=camera_node,
            on_start=[
                EmitEvent(
                    event=ChangeState(
                        lifecycle_node_matcher=lambda node: node == camera_node,
                        transition_id=Transition.TRANSITION_ACTIVATE
                    )
                )
            ]
        )
    )

    return LaunchDescription([
        camera_node,
        configure_camera,
        activate_camera
    ])
```

## ROS 2 Package Structure

### Anatomy of a ROS 2 Package

A well-structured ROS 2 package follows conventions for maintainability:

```
my_robot_package/
├── package.xml           # Package metadata and dependencies
├── setup.py              # Python package setup (for Python packages)
├── CMakeLists.txt        # Build configuration (for C++ packages)
├── resource/             # Package marker file
├── my_robot_package/     # Python source code
│   ├── __init__.py
│   ├── lidar_publisher.py
│   └── obstacle_detector.py
├── launch/               # Launch files
│   ├── robot.launch.py
│   └── sensors.launch.py
├── config/               # Parameter files
│   └── robot_params.yaml
├── urdf/                 # Robot descriptions
│   └── robot.urdf.xacro
├── rviz/                 # RViz configurations
│   └── default.rviz
└── test/                 # Unit tests
    └── test_lidar.py
```

### package.xml: Dependency Declaration

**package.xml**:
```xml
<?xml version="1.0"?>
<?xml-model href="http://download.ros.org/schema/package_format3.xsd" schematypens="http://www.w3.org/2001/XMLSchema"?>
<package format="3">
  <name>my_robot_package</name>
  <version>1.0.0</version>
  <description>Mobile robot sensor processing</description>
  <maintainer email="you@example.com">Your Name</maintainer>
  <license>Apache-2.0</license>

  <!-- Build dependencies -->
  <build_depend>rclpy</build_depend>
  <build_depend>sensor_msgs</build_depend>
  <build_depend>geometry_msgs</build_depend>

  <!-- Execution dependencies -->
  <exec_depend>rclpy</exec_depend>
  <exec_depend>sensor_msgs</exec_depend>
  <exec_depend>geometry_msgs</exec_depend>

  <!-- Test dependencies -->
  <test_depend>pytest</test_depend>

  <export>
    <build_type>ament_python</build_type>
  </export>
</package>
```

### setup.py: Entry Points and Data Files

**setup.py** (for Python packages):
```python
from setuptools import setup
import os
from glob import glob

package_name = 'my_robot_package'

setup(
    name=package_name,
    version='1.0.0',
    packages=[package_name],
    data_files=[
        # Package marker
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),

        # Package.xml
        ('share/' + package_name, ['package.xml']),

        # Launch files
        (os.path.join('share', package_name, 'launch'),
            glob('launch/*.launch.py')),

        # Config files
        (os.path.join('share', package_name, 'config'),
            glob('config/*.yaml')),

        # URDF files
        (os.path.join('share', package_name, 'urdf'),
            glob('urdf/*.urdf*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Your Name',
    maintainer_email='you@example.com',
    description='Mobile robot sensor processing',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'lidar_publisher = my_robot_package.lidar_publisher:main',
            'obstacle_detector = my_robot_package.obstacle_detector:main',
        ],
    },
)
```

## Building and Running Packages

### Workspace Setup with colcon

**Create a workspace**:
```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src

# Clone or create packages
git clone https://github.com/example/my_robot_package.git

cd ~/ros2_ws

# Install dependencies
rosdep install --from-paths src --ignore-src -r -y

# Build all packages
colcon build

# Source the workspace
source install/setup.bash
```

### Building Specific Packages

```bash
# Build single package
colcon build --packages-select my_robot_package

# Build with symbolic links (for Python, avoid rebuild on code changes)
colcon build --symlink-install

# Build with compile commands (for IDE integration)
colcon build --cmake-args -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
```

### Running Nodes

```bash
# Run executable
ros2 run my_robot_package lidar_publisher

# Run with parameters
ros2 run my_robot_package lidar_publisher --ros-args -p scan_rate:=20.0

# Run launch file
ros2 launch my_robot_package robot.launch.py
```

## Best Practices for Launch Files and Packages

### 1. Modular Launch Files

Break complex systems into reusable components:
- `sensors.launch.py`: All sensor drivers
- `perception.launch.py`: SLAM, localization, object detection
- `navigation.launch.py`: Path planning, obstacle avoidance
- `robot.launch.py`: Top-level file including all above

### 2. Use Namespaces for Multi-Robot Systems

```python
Node(
    package='robot_driver',
    executable='driver_node',
    namespace='robot1',  # All topics prefixed with /robot1/
    name='driver',
    output='screen'
)
```

### 3. Parameterize Everything

Avoid hardcoded values:
```python
# Bad
parameters=[{'port': '/dev/ttyUSB0'}]

# Good
parameters=[{
    'port': LaunchConfiguration('lidar_port'),
    'baud_rate': LaunchConfiguration('lidar_baud')
}]
```

### 4. Document Launch Arguments

```python
DeclareLaunchArgument(
    'use_sim',
    default_value='false',
    description='Use Gazebo simulation instead of real robot',
    choices=['true', 'false']
)
```

## Summary

ROS 2's launch system and package management provide the scaffolding for building complex, maintainable robotic systems. Key takeaways:

- **Launch files** orchestrate multi-node systems with parameters, remappings, and lifecycle management
- **Python launch files** offer full programming capabilities for complex logic
- **Parameter files** (YAML) separate configuration from code
- **Conditional launching** enables environment-specific behavior (sim vs real)
- **Package structure** conventions ensure consistency and ease collaboration
- **colcon** build tool handles dependencies and workspace management

In the next chapter, we'll explore TF2 coordinate transforms—the system that enables robots to reason about spatial relationships between sensors, actuators, and the world.

---

**Key Takeaways**:
- Launch files replace manual node starting with declarative orchestration
- Python, XML, and YAML formats available (Python recommended for complexity)
- Conditional execution, parameter files, and event handlers enable advanced workflows
- ROS 2 packages follow standard structure: package.xml, setup.py, launch/, config/
- colcon build system manages workspace compilation and dependencies
- Modular, parameterized launch files are essential for maintainability
