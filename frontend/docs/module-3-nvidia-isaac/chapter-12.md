# Chapter 12: Isaac SDK and Isaac Sim Overview

## Introduction to NVIDIA Isaac Platform

**NVIDIA Isaac** is the robotics platform powering the next generation of autonomous machines—from warehouse robots to humanoid assistants. Built on NVIDIA's GPU architecture, Isaac combines photorealistic simulation (**Isaac Sim**), perception/AI libraries (**Isaac SDK**), and edge deployment tools (**Isaac ROS**) into an end-to-end ecosystem for developing, testing, and deploying intelligent robots.

**Why Isaac for Humanoid Robotics?**
- **GPU-Accelerated Physics**: PhysX 5 runs on RTX GPUs (100× faster than CPU-based physics)
- **Photorealistic Rendering**: Real-time ray tracing generates synthetic data indistinguishable from reality
- **Scalable Sim**: Run 100+ robots in parallel for reinforcement learning
- **Domain Randomization**: Built-in tools for sim-to-real transfer
- **ROS 2 Native**: Seamless integration with robotics middleware
- **Omniverse Collaboration**: Multi-user, cloud-based 3D workflows

This chapter explores the Isaac platform architecture, Isaac Sim setup, URDF import, ROS 2 integration, and compares Isaac with Gazebo/Unity to understand when to use each tool.

## Isaac Platform Ecosystem

### Three Core Components

**1. Isaac Sim** (Simulation Environment):
- Built on **NVIDIA Omniverse** (USD-based 3D collaboration platform)
- **PhysX 5** physics engine (GPU-accelerated rigid body, articulations, soft bodies)
- **RTX Ray Tracing** for photorealistic sensors (cameras, LiDAR)
- **Synthetic Data Generation** (SDG) tools for training perception models

**2. Isaac SDK** (Perception & Navigation Libraries):
- **GEM (Graph Execution Manager)**: Modular robotics framework (deprecated in favor of Isaac ROS)
- **Navigation Stack**: Path planning, obstacle avoidance, localization
- **Perception Modules**: Object detection, depth estimation, semantic segmentation
- **Manipulation**: Grasp planning, trajectory optimization

**3. Isaac ROS** (Edge Deployment):
- **Hardware-accelerated ROS 2 packages** for NVIDIA Jetson/GPU
- **Perception**: NITROS-accelerated image processing, AprilTag detection, DNN inference
- **Vision**: Stereo depth, visual odometry, SLAM
- **Manipulation**: MoveIt integration, grasp synthesis

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                   NVIDIA Isaac Platform                      │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Isaac Sim (Omniverse-Based Simulation)                │ │
│  │   ├─ Omniverse Kit (USD rendering, UI)                 │ │
│  │   ├─ PhysX 5 (GPU physics: rigid, articulated, soft)   │ │
│  │   ├─ RTX Renderer (ray tracing, path tracing)          │ │
│  │   ├─ Replicator (synthetic data generation)            │ │
│  │   └─ ROS 2 Bridge (topic/service/action pub/sub)       │ │
│  └────────────────────────────────────────────────────────┘ │
│                          ↓                                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Isaac ROS (Hardware-Accelerated ROS 2 Packages)       │ │
│  │   ├─ NITROS (zero-copy message passing)                │ │
│  │   ├─ Perception (DNN inference, depth, segmentation)   │ │
│  │   ├─ Vision (SLAM, visual odometry, AprilTags)         │ │
│  │   └─ Manipulation (MoveIt, grasp planning)             │ │
│  └────────────────────────────────────────────────────────┘ │
│                          ↓                                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Deployment (NVIDIA Jetson / GPU Edge Devices)         │ │
│  │   - Jetson AGX Orin (275 TOPS AI)                      │ │
│  │   - Jetson Orin NX/Nano (100/40 TOPS)                  │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

**Workflow**:
1. **Develop in Isaac Sim**: Design robot, test algorithms, generate synthetic data
2. **Train with Isaac ROS GEMs**: Perception, navigation, manipulation
3. **Deploy on Jetson**: Hardware-accelerated inference on real robot

## Isaac Sim: GPU-Accelerated Robotics Simulator

### What is Isaac Sim?

**Isaac Sim** is a robotics simulator built on **NVIDIA Omniverse**, leveraging:
- **Universal Scene Description (USD)**: Pixar's 3D file format for collaborative workflows
- **PhysX 5**: Massively parallel physics (10,000+ rigid bodies on single GPU)
- **RTX Real-Time Ray Tracing**: Film-quality rendering for sensor simulation
- **Replicator**: Domain randomization and synthetic data generation at scale

**Use Cases**:
- Train perception models with photorealistic synthetic data (no manual labeling)
- Validate navigation algorithms in digital twin warehouses
- Test humanoid balance controllers with accurate contact physics
- Generate millions of training samples (pose estimation, object detection)

### Isaac Sim vs Gazebo vs Unity

| Feature | Isaac Sim | Gazebo (Ignition) | Unity Robotics |
|---------|-----------|-------------------|----------------|
| **Physics Engine** | PhysX 5 (GPU) | ODE/DART (CPU) | PhysX (GPU) |
| **Physics Accuracy** | Excellent (articulations) | Excellent (DART) | Good |
| **Physics Speed** | 100× faster (GPU) | Baseline | 10× faster (GPU) |
| **Rendering** | RTX ray tracing | OGRE (basic) | HDRP (excellent) |
| **Sensor Realism** | Excellent (RTX) | Good | Excellent |
| **ROS 2 Integration** | Native | Native | TCP bridge |
| **Synthetic Data** | Replicator (built-in) | Manual scripting | Manual scripting |
| **License** | Free (some enterprise features paid) | Open-source | Free (&lt;$100k revenue) |
| **GPU Requirement** | RTX GPU (CUDA) | Optional | Optional |

**When to Use Isaac Sim**:
- Photorealistic sensor data generation (vision-based learning)
- Large-scale parallel simulation (100+ robots for RL)
- Warehouse/logistics digital twins
- GPU-accelerated physics (articulated humanoids, soft bodies)

**When to Use Gazebo**:
- Physics-accurate control validation (DART engine)
- Open-source requirement
- CPU-only environments

**When to Use Unity**:
- Game-quality graphics for demos/marketing
- VR/AR teleoperation
- ML-Agents reinforcement learning

## Installing Isaac Sim

### System Requirements

**Minimum**:
- **GPU**: NVIDIA RTX 2060 (6 GB VRAM)
- **CPU**: Intel i7 / AMD Ryzen 7
- **RAM**: 32 GB
- **OS**: Ubuntu 20.04/22.04, Windows 10/11

**Recommended**:
- **GPU**: RTX 3090 / RTX 4090 (24 GB VRAM)
- **CPU**: Intel i9 / AMD Ryzen 9
- **RAM**: 64 GB

### Installation Steps (Ubuntu)

**1. Install Omniverse Launcher**:
```bash
# Download from https://www.nvidia.com/en-us/omniverse/download/
wget https://install.launcher.omniverse.nvidia.com/installers/omniverse-launcher-linux.AppImage
chmod +x omniverse-launcher-linux.AppImage
./omniverse-launcher-linux.AppImage
```

**2. Install Isaac Sim from Launcher**:
- Open Omniverse Launcher
- Go to "Exchange" tab
- Search "Isaac Sim"
- Click "Install" (version 2023.1.1 or later recommended)

**3. Verify Installation**:
```bash
# Isaac Sim installs to ~/.local/share/ov/pkg/isaac_sim-*
cd ~/.local/share/ov/pkg/isaac_sim-2023.1.1
./isaac-sim.sh
```

**4. Install Isaac ROS (Optional, for ROS 2 integration)**:
```bash
# Install Isaac ROS prerequisites
sudo apt-get install python3-rosdep python3-rosinstall-generator

# Create Isaac ROS workspace
mkdir -p ~/isaac_ros_ws/src
cd ~/isaac_ros_ws/src

# Clone Isaac ROS common
git clone https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_common.git

# Build with Docker (recommended for dependencies)
cd ~/isaac_ros_ws
colcon build --symlink-install
```

## Creating Your First Isaac Sim Scene

### 1. Launch Isaac Sim and Create Scene

**Open Isaac Sim**:
```bash
~/.local/share/ov/pkg/isaac_sim-2023.1.1/isaac-sim.sh
```

**Create New Stage**:
- File → New (or Ctrl+N)
- This creates a new USD stage (scene)

### 2. Add Ground Plane

**Using GUI**:
- Create → Physics → Ground Plane
- Properties: 100m × 100m, friction = 0.8

**Using Python API** (preferred for automation):
```python
from omni.isaac.core.utils.stage import add_reference_to_stage
from omni.isaac.core.utils.prims import create_prim

# Create ground plane
create_prim(
    prim_path="/World/GroundPlane",
    prim_type="Plane",
    attributes={
        "size": 100.0,  # 100m × 100m
        "axis": "Z"
    }
)

# Add physics material (friction)
from pxr import UsdPhysics, PhysxSchema

ground = stage.GetPrimAtPath("/World/GroundPlane")
material = UsdPhysics.MaterialAPI.Apply(ground)
material.CreateStaticFrictionAttr(0.8)
material.CreateDynamicFrictionAttr(0.7)
```

### 3. Add Lighting

**Environment Light** (HDRI sky):
```python
from omni.isaac.core.utils.stage import add_reference_to_stage

# Add HDRI environment
add_reference_to_stage(
    usd_path="/Isaac/Environments/Simple_Warehouse/warehouse.usd",
    prim_path="/World/Warehouse"
)
```

**Distant Light** (sun):
```python
from pxr import UsdLux

light = UsdLux.DistantLight.Define(stage, "/World/Sun")
light.CreateIntensityAttr(1000.0)
light.CreateAngleAttr(0.5)  # Degrees (sun angular diameter)
light.CreateColorAttr((1.0, 0.95, 0.9))  # Slightly warm white
```

### 4. Spawn a Robot

**Import URDF as USD**:

Isaac Sim includes a URDF importer that converts ROS robot descriptions to USD format.

**GUI Method**:
- Isaac Utils → Import Robot → URDF Importer
- Select URDF file (e.g., `humanoid.urdf`)
- Import Settings:
  - **Merge Fixed Joints**: Yes (simplifies physics)
  - **Fix Base**: No (for mobile robots), Yes (for manipulators)
  - **Self-Collision**: Yes
- Click "Import"

**Python API Method**:
```python
from omni.isaac.core.utils.extensions import enable_extension
enable_extension("omni.isaac.urdf")

from omni.isaac.urdf import _urdf

# Import URDF
urdf_path = "/path/to/humanoid.urdf"
imported_robot = _urdf.acquire_urdf_interface()

# Convert URDF to USD
robot_prim_path = "/World/Humanoid"
imported_robot.parse_urdf(
    urdf_path=urdf_path,
    prim_path=robot_prim_path,
    merge_fixed_joints=True,
    import_inertia_tensor=True,
    default_drive_strength=1000.0,
    default_drive_damping=100.0
)
```

**Result**: Robot appears in scene with:
- **ArticulationRoot**: Base link with physics
- **Joints**: Revolute/prismatic/fixed joints
- **Visual meshes**: Rendered geometry
- **Collision meshes**: Physics proxies

## ROS 2 Integration with Isaac Sim

### Enabling ROS 2 Bridge

Isaac Sim includes a native ROS 2 bridge (no TCP required, unlike Unity).

**Activate ROS 2 Extension**:
```python
# In Isaac Sim Python script
from omni.isaac.core.utils.extensions import enable_extension

enable_extension("omni.isaac.ros2_bridge")
```

**Or via GUI**:
- Window → Extensions
- Search "ROS2 Bridge"
- Enable extension

### Publishing Joint States

**Create ROS 2 Joint State Publisher**:

```python
import rclpy
from omni.isaac.core import World
from omni.isaac.core.robots import Robot

# Initialize Isaac Sim world
world = World(stage_units_in_meters=1.0)

# Add robot
robot = world.scene.add(
    Robot(
        prim_path="/World/Humanoid",
        name="humanoid_robot"
    )
)

# Reset world (initialize physics)
world.reset()

# Get ROS2 context
from omni.isaac.ros2_bridge import OmniverseROS2

ros_context = OmniverseROS2.OmniverseROS2Context()

# Create joint state publisher
joint_state_pub = ros_context.create_publisher(
    msg_type="sensor_msgs/JointState",
    topic_name="/joint_states",
    queue_size=10
)

# Publish loop
for i in range(1000):
    # Step simulation
    world.step(render=True)

    # Get joint positions/velocities
    joint_positions = robot.get_joint_positions()
    joint_velocities = robot.get_joint_velocities()

    # Publish to ROS 2
    msg = {
        "header": {
            "stamp": {"sec": i // 60, "nanosec": (i % 60) * 16666667},
            "frame_id": "base_link"
        },
        "name": robot.dof_names,  # Joint names
        "position": joint_positions.tolist(),
        "velocity": joint_velocities.tolist(),
        "effort": [0.0] * len(joint_positions)  # Not measured in sim
    }

    joint_state_pub.publish(msg)
```

**ROS 2 Side** (verify):
```bash
source /opt/ros/humble/setup.bash
ros2 topic echo /joint_states
```

### Subscribing to Joint Commands

**Control joints from ROS 2**:

```python
from omni.isaac.ros2_bridge import OmniverseROS2

ros_context = OmniverseROS2.OmniverseROS2Context()

# Callback for joint commands
def joint_command_callback(msg):
    # msg is a ROS 2 JointState message
    target_positions = msg["position"]

    # Apply to robot in Isaac Sim
    robot.set_joint_position_targets(target_positions)

# Subscribe to /joint_commands
joint_cmd_sub = ros_context.create_subscription(
    msg_type="sensor_msgs/JointState",
    topic_name="/joint_commands",
    callback=joint_command_callback,
    queue_size=10
)
```

**ROS 2 Side** (send commands):
```bash
ros2 topic pub /joint_commands sensor_msgs/msg/JointState \
  "{name: ['left_hip', 'left_knee'], position: [0.1, -0.5]}" --once
```

## Isaac Sim Python API Basics

### Standalone vs Extension Mode

**Standalone Scripts** (headless, for batch processing):
```python
#!/usr/bin/env python3
from omni.isaac.kit import SimulationApp

# Launch Isaac Sim in headless mode
simulation_app = SimulationApp({"headless": True})

# Import Isaac modules AFTER SimulationApp
from omni.isaac.core import World
from omni.isaac.core.robots import Robot

# Create world
world = World(stage_units_in_meters=1.0)
world.scene.add_default_ground_plane()

# Add robot
robot = Robot(prim_path="/World/Robot", name="my_robot")
world.scene.add(robot)

# Reset and run
world.reset()

for i in range(1000):
    world.step(render=False)  # No GUI rendering
    if i % 100 == 0:
        print(f"Step {i}: Joint pos = {robot.get_joint_positions()}")

simulation_app.close()
```

**Extension Mode** (interactive, GUI available):
- Write extensions in `~/.local/share/ov/pkg/isaac_sim-*/exts/`
- Extensions appear in Isaac Sim UI as menu items

### Common API Patterns

**Get/Set Joint Positions**:
```python
# Get current positions (read-only)
positions = robot.get_joint_positions()  # numpy array

# Set target positions (PD control)
robot.set_joint_position_targets([0.1, -0.5, 0.2, ...])
```

**Apply Forces/Torques**:
```python
# Apply torque to joint
robot.set_joint_efforts([100.0, -50.0, ...])  # N·m

# Apply external force to link
from omni.isaac.core.utils.prims import get_prim_at_path
link_prim = get_prim_at_path("/World/Robot/left_foot")
# Use PhysX API to apply force (advanced)
```

**Camera Rendering**:
```python
from omni.isaac.core.utils.viewports import set_camera_view

# Set camera pose
set_camera_view(
    eye=np.array([3.0, 3.0, 2.0]),  # Camera position
    target=np.array([0.0, 0.0, 1.0]),  # Look-at target
    camera_prim_path="/OmniverseKit_Persp"
)

# Capture RGB image
from omni.isaac.core.utils.render import get_rgb_image
rgb_image = get_rgb_image()  # (H, W, 3) numpy array
```

## Synthetic Data Generation with Replicator

### Why Synthetic Data?

Training perception models (object detection, pose estimation, segmentation) requires:
- Millions of labeled images
- Diverse scenarios (lighting, occlusion, backgrounds)
- Perfect ground-truth labels (bounding boxes, masks, depth)

**Manual labeling**: 1000 images takes 10+ hours
**Isaac Sim Replicator**: 1 million images in 10 hours (100,000× faster)

### Domain Randomization with Replicator

**Example: Randomize object poses and lighting**:

```python
import omni.replicator.core as rep

# Define randomization function
with rep.new_layer():
    # Randomize camera pose
    camera = rep.create.camera(position=(3, 3, 2))
    with camera:
        rep.modify.pose(
            position=rep.distribution.uniform((-5, -5, 1), (5, 5, 3)),
            look_at=(0, 0, 1)
        )

    # Randomize object (target to detect)
    target_obj = rep.get.prim_at_path("/World/TargetObject")
    with target_obj:
        rep.modify.pose(
            position=rep.distribution.uniform((-2, -2, 0.5), (2, 2, 2)),
            rotation=rep.distribution.uniform((0, 0, 0), (360, 360, 360))
        )

    # Randomize lighting
    light = rep.get.light()
    with light:
        rep.modify.attribute("intensity", rep.distribution.uniform(500, 2000))
        rep.modify.attribute("color", rep.distribution.uniform((0.8, 0.8, 0.8), (1, 1, 1)))

    # Randomize textures
    materials = rep.get.material()
    with materials:
        rep.randomizer.materials(
            textures_dir="/Isaac/Materials/Textures"
        )

# Run randomization for 10,000 frames
rep.orchestrator.run(num_frames=10000)

# Output: 10,000 RGB images + depth + segmentation masks + bounding boxes
```

**Outputs**:
- RGB images: `rgb_0000.png`, `rgb_0001.png`, ...
- Depth maps: `depth_0000.npy`
- Semantic segmentation: `semantic_0000.png` (color-coded labels)
- Bounding boxes: `bboxes_0000.json` (COCO format)

## Summary

NVIDIA Isaac is the GPU-accelerated robotics platform combining simulation (Isaac Sim), perception libraries (Isaac SDK/ROS), and edge deployment (Jetson). Key takeaways:

- **Isaac Sim**: Omniverse-based simulator with PhysX 5 (GPU physics) and RTX ray tracing
- **100× Faster Physics**: GPU acceleration enables large-scale parallel simulation
- **Photorealistic Sensors**: Real-time ray tracing for camera, LiDAR, depth
- **ROS 2 Native**: Built-in bridge (no TCP required)
- **Replicator**: Domain randomization and synthetic data generation at scale
- **Comparison**: Isaac Sim (GPU speed + realism), Gazebo (physics accuracy), Unity (graphics quality)

In the next chapter, we'll explore **Perception with Isaac**, including sensor simulation, semantic segmentation, and depth estimation for vision-based autonomy.

---

**Key Takeaways**:
- Isaac Sim combines Omniverse USD, PhysX 5 GPU physics, and RTX ray tracing
- GPU acceleration enables 100× faster physics simulation than CPU-based engines
- Native ROS 2 bridge allows seamless topic/service/action communication
- Replicator generates millions of labeled training samples with domain randomization
- Use Isaac Sim for photorealistic sensor data, Gazebo for control validation, Unity for VR/AR
- Isaac ROS provides hardware-accelerated perception/navigation on NVIDIA Jetson
