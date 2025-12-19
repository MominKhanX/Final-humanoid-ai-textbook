# Chapter 13: Perception with Isaac - Sensors, Segmentation, and Vision

## Introduction to Robot Perception

Perception is the bridge between raw sensor data and intelligent action. A humanoid robot must identify objects to grasp, detect obstacles to avoid, and estimate its pose to navigate—all from cameras, depth sensors, and LiDAR. **Isaac Sim** provides **RTX-accelerated sensor simulation** that generates photorealistic data for training perception models, while **Isaac ROS** offers **hardware-accelerated inference** for deploying those models on NVIDIA Jetson

.

This chapter explores Isaac's perception capabilities:
- **RTX Ray-Traced Sensors**: Physically-accurate camera, depth, and LiDAR simulation
- **Semantic/Instance Segmentation**: Pixel-perfect object labels for training
- **Depth Estimation**: Stereo and monocular depth prediction
- **Object Detection**: YOLO, DOPE (6D pose), and custom DNNs
- **Isaac ROS Perception**: Hardware-accelerated DNN inference on Jetson

## Sensor Simulation in Isaac Sim

### RGB Camera Sensor

**Create Camera** (Python API):

```python
from omni.isaac.core.utils.prims import create_prim
from pxr import UsdGeom

# Create camera prim
camera_path = "/World/Camera"
camera = create_prim(
    prim_path=camera_path,
    prim_type="Camera"
)

# Set camera properties
camera_prim = UsdGeom.Camera(stage.GetPrimAtPath(camera_path))
camera_prim.CreateFocalLengthAttr(24.0)  # 24mm lens
camera_prim.CreateHorizontalApertureAttr(20.955)  # Sensor width (mm)
camera_prim.CreateVerticalApertureAttr(15.2908)  # Sensor height
camera_prim.CreateClippingRangeAttr((0.1, 10000.0))  # Near/far planes

# Set resolution
from omni.isaac.core.utils.viewports import set_camera_view
set_camera_view(
    eye=np.array([3.0, 3.0, 2.0]),
    target=np.array([0.0, 0.0, 1.0]),
    camera_prim_path=camera_path
)
```

**Capture RGB Image**:

```python
import omni.replicator.core as rep

# Create render product (output)
render_product = rep.create.render_product(camera_path, (1280, 720))

# Attach RGB writer
rgb_writer = rep.WriterRegistry.get("BasicWriter")
rgb_writer.initialize(output_dir="./rgb_output", rgb=True)
rgb_writer.attach([render_product])

# Capture frame
rep.orchestrator.step()  # Run one frame

# Output: ./rgb_output/rgb_0000.png
```

### Depth Camera Sensor

**Enable Depth Rendering**:

```python
import omni.replicator.core as rep

# Create render product with depth
render_product = rep.create.render_product(camera_path, (1280, 720))

# Attach depth writer
depth_writer = rep.WriterRegistry.get("BasicWriter")
depth_writer.initialize(
    output_dir="./depth_output",
    distance_to_camera=True  # Depth map
)
depth_writer.attach([render_product])

rep.orchestrator.step()

# Output: ./depth_output/distance_to_camera_0000.npy (float32 depth in meters)
```

**Visualize Depth Map** (Python):

```python
import numpy as np
import matplotlib.pyplot as plt

# Load depth map
depth = np.load("./depth_output/distance_to_camera_0000.npy")

# Visualize
plt.imshow(depth, cmap='jet', vmin=0, vmax=10)  # 0-10 meter range
plt.colorbar(label='Depth (m)')
plt.show()
```

### Semantic Segmentation Sensor

**Assign Semantic Labels** to objects:

```python
from omni.isaac.core.utils.semantics import add_update_semantics

# Label ground plane
add_update_semantics(
    prim=stage.GetPrimAtPath("/World/GroundPlane"),
    semantic_label="ground",
    type_label="class"
)

# Label obstacles
add_update_semantics(
    prim=stage.GetPrimAtPath("/World/Obstacle1"),
    semantic_label="obstacle",
    type_label="class"
)

# Label target object
add_update_semantics(
    prim=stage.GetPrimAtPath("/World/TargetObject"),
    semantic_label="target",
    type_label="class"
)
```

**Capture Semantic Segmentation**:

```python
import omni.replicator.core as rep

render_product = rep.create.render_product(camera_path, (1280, 720))

# Attach semantic segmentation writer
seg_writer = rep.WriterRegistry.get("BasicWriter")
seg_writer.initialize(
    output_dir="./seg_output",
    semantic_segmentation=True,
    colorize_semantic_segmentation=True  # Color-coded output
)
seg_writer.attach([render_product])

rep.orchestrator.step()

# Output: ./seg_output/semantic_segmentation_0000.png (color-coded labels)
```

**Segmentation Output Format**:
- Each semantic class assigned unique color
- Example: ground=gray, obstacle=red, target=green
- Can be converted to class IDs for training

### Instance Segmentation

**Label instances** (distinguish multiple objects of same class):

```python
# Obstacle 1
add_update_semantics(
    prim=stage.GetPrimAtPath("/World/Obstacle1"),
    semantic_label="obstacle",
    type_label="class"
)
# Add instance ID
instance_mapping = {"instance_id": 1}
add_update_semantics(
    prim=stage.GetPrimAtPath("/World/Obstacle1"),
    semantic_label="obstacle_1",
    type_label="instance",
    attributes=instance_mapping
)

# Obstacle 2 (same class, different instance)
add_update_semantics(
    prim=stage.GetPrimAtPath("/World/Obstacle2"),
    semantic_label="obstacle",
    type_label="class"
)
instance_mapping = {"instance_id": 2}
add_update_semantics(
    prim=stage.GetPrimAtPath("/World/Obstacle2"),
    semantic_label="obstacle_2",
    type_label="instance",
    attributes=instance_mapping
)
```

**Capture Instance Segmentation**:

```python
seg_writer.initialize(
    output_dir="./instance_output",
    instance_segmentation=True
)
```

### LiDAR Sensor (Rotating)

**Create Rotating LiDAR** (Velodyne-style):

```python
from omni.isaac.range_sensor import _range_sensor

# Create LiDAR
lidar_path = "/World/Lidar"
result, lidar = omni.kit.commands.execute(
    "RangeSensorCreateLidar",
    path=lidar_path,
    parent=None,
    min_range=0.4,
    max_range=100.0,
    draw_points=True,
    draw_lines=False,
    horizontal_fov=360.0,
    vertical_fov=30.0,
    horizontal_resolution=0.4,  # 0.4° = 900 points/rotation
    vertical_resolution=2.0,  # 2° = 16 beams (like VLP-16)
    rotation_rate=10.0,  # 10 Hz rotation
    high_lod=True,  # High detail
    yaw_offset=0.0,
    enable_semantics=False
)
```

**Get LiDAR Point Cloud**:

```python
from omni.isaac.range_sensor import _range_sensor

# Get LiDAR interface
lidar_interface = _range_sensor.acquire_lidar_sensor_interface()

# Read point cloud
point_cloud = lidar_interface.get_point_cloud_data(lidar_path)

# point_cloud is numpy array (N, 3) with XYZ coordinates
print(f"LiDAR points: {len(point_cloud)}")

# Publish to ROS 2 (sensor_msgs/PointCloud2)
```

## Synthetic Data Generation for Perception Training

### Training Object Detection with Synthetic Data

**Goal**: Train YOLOv8 to detect "target" objects in cluttered scenes.

**1. Randomize Scene**:

```python
import omni.replicator.core as rep

with rep.new_layer():
    # Randomize camera viewpoint
    camera = rep.create.camera()
    with camera:
        rep.modify.pose(
            position=rep.distribution.uniform((-5, -5, 2), (5, 5, 5)),
            look_at=(0, 0, 1)
        )

    # Randomize target object pose
    target = rep.get.prim_at_path("/World/TargetObject")
    with target:
        rep.modify.pose(
            position=rep.distribution.uniform((-2, -2, 0.5), (2, 2, 2)),
            rotation=rep.distribution.uniform((0, 0, 0), (360, 360, 360))
        )

    # Randomize distractors (clutter)
    distractors = rep.get.prims(semantics=[("class", "distractor")])
    with distractors:
        rep.randomizer.scatter_2d(
            surface_prims=rep.get.prim_at_path("/World/GroundPlane"),
            count=rep.distribution.uniform(5, 20)  # 5-20 objects
        )

    # Randomize lighting
    light = rep.get.light()
    with light:
        rep.modify.attribute("intensity", rep.distribution.uniform(500, 2000))

# Generate 10,000 training images
rep.orchestrator.run(num_frames=10000)
```

**2. Export in COCO Format**:

```python
# Attach bounding box writer
bbox_writer = rep.WriterRegistry.get("BasicWriter")
bbox_writer.initialize(
    output_dir="./coco_dataset",
    bounding_box_2d_tight=True,  # Tight bounding boxes
    semantic_segmentation=False,
    rgb=True
)
bbox_writer.attach([render_product])
```

**Output**:
- `./coco_dataset/rgb_0000.png`, ..., `rgb_9999.png`
- `./coco_dataset/bounding_box_2d_tight_0000.json` (COCO format)

**3. Train YOLOv8**:

```bash
# Convert to YOLO format (use conversion script)
python coco_to_yolo.py --input ./coco_dataset --output ./yolo_dataset

# Train YOLOv8
yolo train data=yolo_dataset/data.yaml model=yolov8n.pt epochs=100 imgsz=640
```

**Result**: Object detector trained entirely on synthetic data, ready for sim-to-real transfer.

## Isaac ROS: Hardware-Accelerated Perception

### Isaac ROS DNN Inference

**Deploy trained model on NVIDIA Jetson** with hardware acceleration.

**Example: YOLOv8 Inference with Isaac ROS**:

**1. Install Isaac ROS DNN Inference**:

```bash
cd ~/isaac_ros_ws/src
git clone https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_dnn_inference.git
cd ~/isaac_ros_ws
colcon build --packages-select isaac_ros_dnn_inference
```

**2. Convert YOLOv8 to TensorRT** (for Jetson optimization):

```bash
# Export to ONNX
yolo export model=best.pt format=onnx

# Convert to TensorRT (on Jetson)
/usr/src/tensorrt/bin/trtexec \
  --onnx=best.onnx \
  --saveEngine=best.trt \
  --fp16  # Use FP16 precision for speed
```

**3. Run Isaac ROS Inference Node**:

```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from isaac_ros_tensor_list_interfaces.msg import TensorList

class YOLODetector(Node):
    def __init__(self):
        super().__init__('yolo_detector')

        # Subscribe to camera
        self.image_sub = self.create_subscription(
            Image, '/camera/image_raw', self.image_callback, 10
        )

        # Publish detections
        self.detection_pub = self.create_publisher(
            TensorList, '/detections', 10
        )

    def image_callback(self, msg):
        # Isaac ROS handles TensorRT inference automatically
        # Detections published to /detections topic
        pass
```

**Result**: Real-time object detection (30 FPS) on Jetson Orin with 15W power.

### Isaac ROS AprilTag Detection

**AprilTags** are fiducial markers for robot localization.

**Launch AprilTag Detector**:

```bash
ros2 launch isaac_ros_apriltag isaac_ros_apriltag.launch.py
```

**Publish camera images**, receive detected tags:

```bash
# Topic: /tag_detections (AprilTagDetectionArray)
# Contains: tag ID, pose (position + orientation)
```

**Use Case**: Humanoid localizes itself by detecting AprilTags on walls.

### Isaac ROS Visual SLAM

**Stereo Visual Odometry** for real-time SLAM:

```bash
# Install Isaac ROS Visual SLAM
cd ~/isaac_ros_ws/src
git clone https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_visual_slam.git
cd ~/isaac_ros_ws
colcon build --packages-select isaac_ros_visual_slam

# Launch Visual SLAM
ros2 launch isaac_ros_visual_slam isaac_ros_visual_slam.launch.py
```

**Inputs**:
- Stereo camera pair (left/right images)
- IMU (optional, for robustness)

**Outputs**:
- `/visual_slam/tracking/odometry` (nav_msgs/Odometry)
- `/visual_slam/tracking/vo_pose` (PoseStamped)
- `/visual_slam/tracking/slam_path` (Path)

**Performance**: 30 FPS SLAM on Jetson Orin NX.

## Real-World Perception Workflow

### 1. Train in Isaac Sim

**Generate 100,000 synthetic images** with domain randomization:
- Randomize lighting (day/night, indoor/outdoor)
- Randomize object poses, textures, backgrounds
- Perfect labels (bounding boxes, segmentation masks)

**Train perception model** (YOLOv8, SegFormer, DOPE):
```bash
# Train object detector
yolo train data=synthetic_data.yaml epochs=200

# Train 6D pose estimator (DOPE)
python train_dope.py --dataset synthetic_dope --epochs 100
```

### 2. Validate in Isaac Sim

**Test on held-out synthetic scenes**:
- Different lighting conditions not seen in training
- Novel object arrangements
- Measure precision/recall

**Iterate if needed**: Add more randomization, collect edge cases.

### 3. Deploy on Jetson with Isaac ROS

**Convert model to TensorRT**:
```bash
trtexec --onnx=model.onnx --saveEngine=model.trt --fp16
```

**Run inference node**:
```bash
ros2 run my_perception yolo_detector_node
```

**Subscribe to detections** in robot controller:
```python
def detection_callback(self, msg):
    # msg: detected bounding boxes, classes, scores
    # Plan grasp or navigation based on detections
    pass
```

### 4. Fine-Tune on Real Data (Optional)

**Collect 500-1000 real images**, fine-tune for sim-to-real:
```bash
yolo train data=real_finetuning.yaml model=best.pt epochs=20 lr=0.0001
```

**Result**: Perception model achieves 90%`+ accuracy on real robot.

## Case Study: Humanoid Object Grasping

**Task**: Detect objects on table, estimate 6D pose, plan grasp, execute.

**Perception Pipeline**:

1. **RGB-D Camera** captures table scene
2. **Isaac ROS DNN Inference** detects objects (YOLOv8)
3. **DOPE 6D Pose Estimation** computes object pose (position + orientation)
4. **Grasp Planner** selects grasp point based on pose
5. **MoveIt** plans arm trajectory to grasp
6. **Execute** grasp with gripper

**Training Data**: 50,000 synthetic images from Isaac Sim with randomized:
- Object poses (100+ orientations)
- Lighting (500-2000 lux)
- Backgrounds (kitchen, workshop, warehouse)
- Distractors (clutter objects)

**Real-World Performance**: 85%` grasp success on novel objects (zero-shot sim-to-real).

## Summary

Isaac provides end-to-end perception capabilities from sensor simulation to hardware deployment:

- **RTX-Accelerated Sensors**: Photorealistic RGB, depth, LiDAR, segmentation
- **Replicator**: Domain randomization for robust perception training
- **Synthetic Data**: Perfect labels (bounding boxes, masks, depth) at scale
- **Isaac ROS**: Hardware-accelerated DNN inference on Jetson
- **Workflow**: Train in Isaac Sim → Validate → Deploy on Jetson → Fine-tune

In the next chapter, we'll explore **Reinforcement Learning in Isaac Sim** for training control policies (walking, manipulation) directly in simulation.

---

**Key Takeaways**:
- Isaac Sim provides RTX-accelerated camera, depth, LiDAR, and segmentation sensors
- Replicator generates millions of labeled training samples with domain randomization
- Isaac ROS enables hardware-accelerated perception on NVIDIA Jetson (TensorRT)
- Synthetic data workflow: Train in sim → Validate → Deploy → Fine-tune on real data
- Real-world example: Humanoid grasping achieves 85%` success with synthetic training
- AprilTag detection and Visual SLAM available as Isaac ROS packages
