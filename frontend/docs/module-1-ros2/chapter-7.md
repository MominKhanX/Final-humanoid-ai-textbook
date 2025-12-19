# Chapter 7: URDF and Robot Modeling

## Introduction to Robot Description Formats

Every robot in ROS 2—whether simulated or physical—requires a **machine-readable description** of its structure. This description defines:
- **Link**s (rigid bodies): Chassis, arms, wheels, sensors
- **Joint**s (connections): Revolute, prismatic, fixed, continuous
- **Visual geometry**: How the robot appears in visualization tools
- **Collision geometry**: Simplified shapes for collision detection
- **Inertial properties**: Mass, center of mass, inertia tensor
- **Sensors and actuators**: Cameras, LIDARs, motors

**URDF (Unified Robot Description Format)** is the standard XML-based format for describing robots in ROS. Combined with **Xacro** (XML Macros), it enables modular, maintainable robot models that scale from simple mobile robots to complex humanoid platforms.

This chapter covers URDF syntax, Xacro macros, robot_state_publisher, and best practices for modeling robots from scratch.

## Why Robot Descriptions Matter

### The Problem Without URDF

Imagine programming a robot arm controller without a formal model:

```python
# Hardcoded robot geometry (brittle, error-prone)
shoulder_to_elbow_length = 0.35  # meters
elbow_to_wrist_length = 0.25

# Manual forward kinematics (tedious, bug-prone)
end_effector_x = shoulder_to_elbow_length * cos(shoulder_angle) + \
                 elbow_to_wrist_length * cos(shoulder_angle + elbow_angle)
```

**Problems**:
- **No visualization**: Can't see robot in RViz
- **No collision checking**: Manual geometric calculations
- **No TF tree**: Must manually publish transforms
- **Not portable**: Code breaks if robot design changes
- **No simulation**: Can't test in Gazebo without separate model

### The Solution: URDF + robot_state_publisher

With URDF:
1. **Single source of truth**: One XML file defines all geometry
2. **Automatic TF tree**: robot_state_publisher broadcasts all transforms
3. **Visualization**: RViz displays robot automatically
4. **Simulation**: Gazebo loads URDF directly
5. **Kinematics libraries**: Use established IK/FK solvers

## URDF Syntax and Structure

### Basic URDF Components

A minimal URDF file contains:
- **`<robot>`**: Root element
- **`<link>`**: Rigid body definition
- **`<joint>`**: Connection between links

**Example: Simple 2-link arm**

```xml
<?xml version="1.0"?>
<robot name="simple_arm">

  <!-- Base link (fixed to world) -->
  <link name="base_link">
    <visual>
      <geometry>
        <cylinder length="0.1" radius="0.05"/>
      </geometry>
      <origin xyz="0 0 0.05" rpy="0 0 0"/>
      <material name="blue">
        <color rgba="0 0 1 1"/>
      </material>
    </visual>
  </link>

  <!-- Shoulder link -->
  <link name="shoulder_link">
    <visual>
      <geometry>
        <box size="0.05 0.05 0.3"/>
      </geometry>
      <origin xyz="0 0 0.15" rpy="0 0 0"/>
      <material name="red">
        <color rgba="1 0 0 1"/>
      </material>
    </visual>
  </link>

  <!-- Shoulder joint (revolute, rotates around Z-axis) -->
  <joint name="shoulder_joint" type="revolute">
    <parent link="base_link"/>
    <child link="shoulder_link"/>
    <origin xyz="0 0 0.1" rpy="0 0 0"/>
    <axis xyz="0 0 1"/>
    <limit lower="-1.57" upper="1.57" effort="10" velocity="1.0"/>
  </joint>

  <!-- Elbow link -->
  <link name="elbow_link">
    <visual>
      <geometry>
        <box size="0.05 0.05 0.25"/>
      </geometry>
      <origin xyz="0 0 0.125" rpy="0 0 0"/>
      <material name="green">
        <color rgba="0 1 0 1"/>
      </material>
    </visual>
  </link>

  <!-- Elbow joint (revolute, rotates around Y-axis) -->
  <joint name="elbow_joint" type="revolute">
    <parent link="shoulder_link"/>
    <child link="elbow_link"/>
    <origin xyz="0 0 0.3" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="-1.57" upper="1.57" effort="5" velocity="1.0"/>
  </joint>

</robot>
```

### Joint Types

ROS 2 supports six joint types:

**1. Fixed**:
- No movement
- Example: Camera mounted rigidly to robot base

```xml
<joint name="camera_mount" type="fixed">
  <parent link="base_link"/>
  <child link="camera_link"/>
  <origin xyz="0.5 0 0.2" rpy="0 0 0"/>
</joint>
```

**2. Revolute**:
- Rotation around axis with limits
- Example: Robot arm joint

```xml
<joint name="elbow" type="revolute">
  <parent link="upper_arm"/>
  <child link="forearm"/>
  <origin xyz="0 0 0.3" rpy="0 0 0"/>
  <axis xyz="0 1 0"/>  <!-- Rotate around Y -->
  <limit lower="-2.0" upper="2.0" effort="10" velocity="2.0"/>
</joint>
```

**3. Continuous**:
- Unlimited rotation (no limits)
- Example: Wheel

```xml
<joint name="wheel" type="continuous">
  <parent link="chassis"/>
  <child link="wheel_link"/>
  <origin xyz="0.2 0.15 0" rpy="0 0 0"/>
  <axis xyz="0 1 0"/>
</joint>
```

**4. Prismatic**:
- Linear sliding motion
- Example: Elevator platform

```xml
<joint name="lift" type="prismatic">
  <parent link="base"/>
  <child link="platform"/>
  <origin xyz="0 0 0" rpy="0 0 0"/>
  <axis xyz="0 0 1"/>  <!-- Slide along Z -->
  <limit lower="0" upper="1.0" effort="100" velocity="0.5"/>
</joint>
```

**5. Floating**:
- Unconstrained 6-DOF motion
- Example: Drone in simulation

**6. Planar**:
- Motion in 2D plane
- Example: Mobile robot on flat ground

### Link Geometry

Links have three geometric representations:

**Visual**: How the robot appears in RViz
```xml
<visual>
  <geometry>
    <mesh filename="package://my_robot/meshes/arm.dae" scale="1 1 1"/>
  </geometry>
  <origin xyz="0 0 0" rpy="0 0 0"/>
  <material name="aluminum">
    <color rgba="0.8 0.8 0.8 1"/>
  </material>
</visual>
```

**Collision**: Simplified geometry for collision checking
```xml
<collision>
  <geometry>
    <cylinder length="0.3" radius="0.05"/>  <!-- Simpler than mesh -->
  </geometry>
  <origin xyz="0 0 0.15" rpy="0 0 0"/>
</collision>
```

**Inertial**: Mass and inertia matrix for physics simulation
```xml
<inertial>
  <mass value="2.5"/>
  <origin xyz="0 0 0.15" rpy="0 0 0"/>
  <inertia ixx="0.01" ixy="0" ixz="0"
           iyy="0.01" iyz="0"
           izz="0.005"/>
</inertial>
```

## Xacro: XML Macros for Maintainable URDFs

Raw URDF becomes unwieldy for complex robots. **Xacro** adds:
- **Constants and properties**: Define once, use everywhere
- **Math operations**: Compute derived values
- **Macros**: Reusable components (e.g., wheel, leg)
- **Conditional inclusion**: Different configs for sim vs real

### Xacro Constants and Properties

```xml
<?xml version="1.0"?>
<robot name="mobile_robot" xmlns:xacro="http://www.ros.org/wiki/xacro">

  <!-- Properties (constants) -->
  <xacro:property name="wheel_radius" value="0.05"/>
  <xacro:property name="wheel_width" value="0.03"/>
  <xacro:property name="wheel_separation" value="0.3"/>
  <xacro:property name="chassis_length" value="0.4"/>
  <xacro:property name="chassis_width" value="0.25"/>
  <xacro:property name="chassis_height" value="0.1"/>

  <!-- Math operations -->
  <xacro:property name="chassis_mass" value="${chassis_length * chassis_width * chassis_height * 1000}"/>

  <!-- Base link -->
  <link name="base_link">
    <visual>
      <geometry>
        <box size="${chassis_length} ${chassis_width} ${chassis_height}"/>
      </geometry>
    </visual>
    <inertial>
      <mass value="${chassis_mass}"/>
      <inertia ixx="${(chassis_mass/12) * (chassis_width*chassis_width + chassis_height*chassis_height)}"
               iyy="${(chassis_mass/12) * (chassis_length*chassis_length + chassis_height*chassis_height)}"
               izz="${(chassis_mass/12) * (chassis_length*chassis_length + chassis_width*chassis_width)}"
               ixy="0" ixz="0" iyz="0"/>
    </inertial>
  </link>

</robot>
```

### Xacro Macros for Reusable Components

**Define a wheel macro**:
```xml
<xacro:macro name="wheel" params="prefix reflect">
  <link name="${prefix}_wheel">
    <visual>
      <geometry>
        <cylinder length="${wheel_width}" radius="${wheel_radius}"/>
      </geometry>
      <material name="black">
        <color rgba="0.1 0.1 0.1 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <cylinder length="${wheel_width}" radius="${wheel_radius}"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="0.5"/>
      <inertia ixx="0.001" iyy="0.001" izz="0.001" ixy="0" ixz="0" iyz="0"/>
    </inertial>
  </link>

  <joint name="${prefix}_wheel_joint" type="continuous">
    <parent link="base_link"/>
    <child link="${prefix}_wheel"/>
    <origin xyz="0 ${reflect * wheel_separation/2} 0" rpy="-1.57 0 0"/>
    <axis xyz="0 0 1"/>
  </joint>
</xacro:macro>

<!-- Instantiate wheels -->
<xacro:wheel prefix="left" reflect="1"/>
<xacro:wheel prefix="right" reflect="-1"/>
```

### Conditional Xacro

```xml
<!-- Simulation vs real robot -->
<xacro:arg name="use_sim" default="false"/>
<xacro:property name="use_sim" value="$(arg use_sim)"/>

<xacro:if value="${use_sim}">
  <!-- Add Gazebo plugins -->
  <gazebo>
    <plugin name="differential_drive" filename="libgazebo_ros_diff_drive.so"/>
  </gazebo>
</xacro:if>

<xacro:unless value="${use_sim}">
  <!-- Real hardware interface -->
  <ros2_control name="real_hardware" type="system">
    <hardware>
      <plugin>my_robot/RealHardwareInterface</plugin>
    </hardware>
  </ros2_control>
</xacro:unless>
```

## robot_state_publisher

**robot_state_publisher** is a ROS 2 node that:
1. Reads URDF from parameter `/robot_description`
2. Subscribes to `/joint_states` (joint angles from sensors/controllers)
3. Computes forward kinematics
4. Publishes TF transforms for all links

**Launch file example**:
```python
from launch import LaunchDescription
from launch_ros.actions import Node
import os
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    # Path to URDF file
    urdf_file = os.path.join(
        get_package_share_directory('my_robot_description'),
        'urdf',
        'robot.urdf.xacro'
    )

    # Process Xacro to URDF
    from xacro import process_file
    robot_description = process_file(urdf_file).toxml()

    return LaunchDescription([
        # robot_state_publisher
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            output='screen',
            parameters=[{
                'robot_description': robot_description,
                'use_sim_time': False
            }]
        ),

        # joint_state_publisher_gui (for manual joint control)
        Node(
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui',
            output='screen'
        ),

        # RViz
        Node(
            package='rviz2',
            executable='rviz2',
            output='screen',
            arguments=['-d', os.path.join(
                get_package_share_directory('my_robot_description'),
                'rviz',
                'robot.rviz'
            )]
        )
    ])
```

**Running**:
```bash
ros2 launch my_robot_description display.launch.py
```

This launches:
- **robot_state_publisher**: Publishes TF tree
- **joint_state_publisher_gui**: GUI sliders to move joints
- **RViz**: 3D visualization

## Example: Humanoid Robot Leg

**Simplified humanoid leg with hip, knee, ankle**:

```xml
<?xml version="1.0"?>
<robot name="humanoid_leg" xmlns:xacro="http://www.ros.org/wiki/xacro">

  <!-- Properties -->
  <xacro:property name="hip_length" value="0.1"/>
  <xacro:property name="thigh_length" value="0.4"/>
  <xacro:property name="shin_length" value="0.4"/>
  <xacro:property name="foot_length" value="0.2"/>
  <xacro:property name="foot_width" value="0.1"/>

  <!-- Base (pelvis) -->
  <link name="pelvis">
    <visual>
      <geometry>
        <box size="0.2 0.3 0.1"/>
      </geometry>
      <material name="gray">
        <color rgba="0.5 0.5 0.5 1"/>
      </material>
    </visual>
  </link>

  <!-- Hip link -->
  <link name="left_hip">
    <visual>
      <geometry>
        <cylinder length="${hip_length}" radius="0.05"/>
      </geometry>
      <origin xyz="0 0 ${-hip_length/2}" rpy="0 0 0"/>
      <material name="blue"><color rgba="0 0 1 1"/></material>
    </visual>
    <inertial>
      <mass value="1.0"/>
      <inertia ixx="0.01" iyy="0.01" izz="0.01" ixy="0" ixz="0" iyz="0"/>
    </inertial>
  </link>

  <joint name="left_hip_joint" type="revolute">
    <parent link="pelvis"/>
    <child link="left_hip"/>
    <origin xyz="0 0.1 0" rpy="0 0 0"/>
    <axis xyz="1 0 0"/>  <!-- Pitch axis -->
    <limit lower="-0.5" upper="1.5" effort="100" velocity="5.0"/>
  </joint>

  <!-- Thigh -->
  <link name="left_thigh">
    <visual>
      <geometry>
        <box size="0.08 0.08 ${thigh_length}"/>
      </geometry>
      <origin xyz="0 0 ${-thigh_length/2}" rpy="0 0 0"/>
      <material name="red"><color rgba="1 0 0 1"/></material>
    </visual>
    <inertial>
      <mass value="3.0"/>
      <origin xyz="0 0 ${-thigh_length/2}" rpy="0 0 0"/>
      <inertia ixx="0.05" iyy="0.05" izz="0.01" ixy="0" ixz="0" iyz="0"/>
    </inertial>
  </link>

  <joint name="left_knee_joint" type="revolute">
    <parent link="left_hip"/>
    <child link="left_thigh"/>
    <origin xyz="0 0 ${-hip_length}" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>  <!-- Pitch axis -->
    <limit lower="0" upper="2.5" effort="150" velocity="5.0"/>
  </joint>

  <!-- Shin -->
  <link name="left_shin">
    <visual>
      <geometry>
        <box size="0.06 0.06 ${shin_length}"/>
      </geometry>
      <origin xyz="0 0 ${-shin_length/2}" rpy="0 0 0"/>
      <material name="green"><color rgba="0 1 0 1"/></material>
    </visual>
    <inertial>
      <mass value="2.0"/>
      <origin xyz="0 0 ${-shin_length/2}" rpy="0 0 0"/>
      <inertia ixx="0.03" iyy="0.03" izz="0.005" ixy="0" ixz="0" iyz="0"/>
    </inertial>
  </link>

  <joint name="left_ankle_joint" type="revolute">
    <parent link="left_thigh"/>
    <child link="left_shin"/>
    <origin xyz="0 0 ${-thigh_length}" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="-0.5" upper="0.5" effort="50" velocity="3.0"/>
  </joint>

  <!-- Foot -->
  <link name="left_foot">
    <visual>
      <geometry>
        <box size="${foot_length} ${foot_width} 0.05"/>
      </geometry>
      <origin xyz="${foot_length/2 - 0.05} 0 -0.025" rpy="0 0 0"/>
      <material name="black"><color rgba="0.1 0.1 0.1 1"/></material>
    </visual>
    <collision>
      <geometry>
        <box size="${foot_length} ${foot_width} 0.05"/>
      </geometry>
      <origin xyz="${foot_length/2 - 0.05} 0 -0.025" rpy="0 0 0"/>
    </collision>
    <inertial>
      <mass value="0.5"/>
      <inertia ixx="0.001" iyy="0.002" izz="0.002" ixy="0" ixz="0" iyz="0"/>
    </inertial>
  </link>

  <joint name="left_foot_joint" type="fixed">
    <parent link="left_shin"/>
    <child link="left_foot"/>
    <origin xyz="0 0 ${-shin_length}" rpy="0 0 0"/>
  </joint>

</robot>
```

## Best Practices for URDF Modeling

### 1. Use Xacro for Modularity

```xml
<!-- robot.urdf.xacro -->
<robot name="my_humanoid" xmlns:xacro="http://www.ros.org/wiki/xacro">
  <xacro:include filename="$(find my_robot)/urdf/leg.xacro"/>
  <xacro:include filename="$(find my_robot)/urdf/arm.xacro"/>
  <xacro:include filename="$(find my_robot)/urdf/head.xacro"/>

  <link name="torso">
    <!-- ... -->
  </link>

  <!-- Instantiate legs -->
  <xacro:leg prefix="left" reflect="1"/>
  <xacro:leg prefix="right" reflect="-1"/>

  <!-- Instantiate arms -->
  <xacro:arm prefix="left" reflect="1"/>
  <xacro:arm prefix="right" reflect="-1"/>
</robot>
```

### 2. Accurate Inertial Properties

Use CAD software (SolidWorks, Fusion 360) to compute:
- Mass
- Center of mass
- Inertia tensor

**Export from CAD**:
```xml
<inertial>
  <mass value="2.345"/>
  <origin xyz="0.012 -0.003 0.145" rpy="0 0 0"/>
  <inertia ixx="0.0123" ixy="-0.0001" ixz="0.0002"
           iyy="0.0145" iyz="0.0003"
           izz="0.0098"/>
</inertial>
```

### 3. Collision Geometry Simpler Than Visual

```xml
<!-- Visual: High-poly mesh for aesthetics -->
<visual>
  <geometry>
    <mesh filename="package://my_robot/meshes/arm_hires.stl"/>
  </geometry>
</visual>

<!-- Collision: Low-poly or primitives for speed -->
<collision>
  <geometry>
    <cylinder length="0.3" radius="0.05"/>
  </geometry>
</collision>
```

### 4. Consistent Coordinate Frames

Follow REP 103 conventions:
- **base_link**: Robot origin (usually center of chassis/torso)
- **X-forward, Y-left, Z-up**
- Joint axes aligned with coordinate axes when possible

### 5. Validate URDF

```bash
# Check for errors
check_urdf robot.urdf

# Visualize kinematic tree
urdf_to_graphviz robot.urdf
```

## Integration with Gazebo

Add Gazebo-specific tags for simulation:

```xml
<gazebo reference="left_wheel">
  <material>Gazebo/Black</material>
  <mu1>1.0</mu1>  <!-- Friction coefficient -->
  <mu2>1.0</mu2>
</gazebo>

<gazebo>
  <plugin name="diff_drive" filename="libgazebo_ros_diff_drive.so">
    <left_joint>left_wheel_joint</left_joint>
    <right_joint>right_wheel_joint</right_joint>
    <wheel_separation>0.3</wheel_separation>
    <wheel_diameter>0.1</wheel_diameter>
    <command_topic>cmd_vel</command_topic>
    <odometry_topic>odom</odometry_topic>
  </plugin>
</gazebo>
```

## Summary

URDF and Xacro provide the declarative foundation for robot modeling in ROS 2. Key takeaways:

- **URDF** defines links, joints, geometry, and properties in XML
- **Xacro** adds macros, constants, and math for maintainable models
- **robot_state_publisher** converts joint states to TF transforms
- **Joint types**: Fixed, revolute, continuous, prismatic for different motions
- **Three geometries**: Visual (appearance), collision (physics), inertial (dynamics)
- **Best practices**: Modularity, accurate inertia, simple collisions, validation

With a well-crafted URDF, your robot model seamlessly integrates with visualization (RViz), simulation (Gazebo), and motion planning libraries—forming the foundation for all higher-level behaviors.

---

**Key Takeaways**:
- URDF is the standard XML format for robot descriptions in ROS 2
- Links represent rigid bodies, joints connect links with motion constraints
- Visual, collision, and inertial geometries serve different purposes
- Xacro extends URDF with macros, properties, and conditional logic
- robot_state_publisher publishes TF tree from URDF + joint states
- Validation tools (check_urdf, urdf_to_graphviz) ensure correctness
- Accurate inertial properties critical for realistic simulation
- Modular Xacro files enable reusable components (wheels, legs, sensors)
