# Chapter 6: TF2 Coordinate Transforms

## Introduction to Coordinate Transforms in Robotics

Robots operate in three-dimensional space with multiple sensors, actuators, and coordinate frames. A humanoid robot might have coordinate frames for:
- **base_link** (robot torso)
- **left_foot, right_foot** (contact points with ground)
- **head, left_camera, right_camera** (visual sensors)
- **left_hand, right_hand** (end effectors)
- **map, odom** (world reference frames)

**TF2 (Transform Framework 2)** is ROS 2's library for managing coordinate frame relationships, enabling questions like:
- "Where is the coffee mug relative to the robot's hand?"
- "Transform this LIDAR point from the sensor frame to the world frame"
- "What is the pose of the left foot in the map frame?"

This chapter explores TF2's architecture, usage patterns, and best practices for building spatially-aware robotic systems.

## Why TF2 Matters

### The Coordinate Frame Problem

Consider a simple scenario: A robot arm with a camera mounted on the wrist must grasp an object.

**Challenge**: The camera sees the object in its local frame (`camera_frame`), but the arm controller needs the object position in the arm base frame (`arm_base_frame`).

**Without TF2**:
```python
# Manual transformation (error-prone, hardcoded)
object_in_camera = [0.3, 0.1, 0.5]  # x, y, z in camera frame

# Hardcoded transformation matrix (brittle, breaks if camera moves)
camera_to_arm = np.array([
    [1, 0, 0, 0.1],
    [0, 1, 0, 0.05],
    [0, 0, 1, 0.2],
    [0, 0, 0, 1]
])

object_in_arm = camera_to_arm @ [*object_in_camera, 1]
```

**Problems**:
- Hardcoded transformations become outdated (camera gets repositioned)
- No time synchronization (sensor data from different timestamps)
- No automatic frame tree management
- Manual matrix multiplications for chain transforms

**With TF2**:
```python
# Automatic, dynamic, time-synchronized transformation
object_in_arm = tf_buffer.transform(
    object_in_camera,
    target_frame='arm_base_frame',
    timeout=rospy.Duration(1.0)
)
```

TF2 automatically:
- Finds the transformation chain: `camera → wrist → elbow → shoulder → arm_base`
- Handles time synchronization
- Updates transformations dynamically as robot moves
- Provides error handling and diagnostics

## TF2 Core Concepts

### 1. Coordinate Frames

A **coordinate frame** (also called a TF frame) is a 3D Cartesian coordinate system with an origin and three axes (x, y, z).

**Common frame conventions**:
- **REP 103** (ROS Enhancement Proposal): x-forward, y-left, z-up
- **Right-hand rule**: Curling fingers from x to y, thumb points in z

**Frame naming**:
- Use lowercase with underscores: `base_link`, `left_camera`
- Avoid special characters
- Be descriptive: `base_link` not `frame1`

### 2. Transforms

A **transform** describes the relationship between two frames:
- **Translation**: (x, y, z) offset in meters
- **Rotation**: Quaternion (x, y, z, w) or Euler angles (roll, pitch, yaw)

**Representation**:
```python
from geometry_msgs.msg import TransformStamped

transform = TransformStamped()
transform.header.stamp = self.get_clock().now().to_msg()
transform.header.frame_id = 'base_link'  # Parent frame
transform.child_frame_id = 'camera_link'  # Child frame

# Translation
transform.transform.translation.x = 0.1
transform.transform.translation.y = 0.0
transform.transform.translation.z = 0.5

# Rotation (quaternion for 90° rotation around Z-axis)
transform.transform.rotation.x = 0.0
transform.transform.rotation.y = 0.0
transform.transform.rotation.z = 0.707
transform.transform.rotation.w = 0.707
```

### 3. Transform Tree

The **TF tree** is a directed acyclic graph (DAG) of frame relationships.

**Example humanoid robot tree**:
```
map
 └── odom
      └── base_link (robot torso)
           ├── left_hip
           │    └── left_knee
           │         └── left_ankle
           │              └── left_foot
           ├── right_hip
           │    └── right_knee
           │         └── right_ankle
           │              └── right_foot
           └── head
                ├── left_camera
                └── right_camera
```

**Key properties**:
- **Single parent**: Each frame has exactly one parent (except root)
- **Cycle-free**: No circular dependencies
- **Connected**: All frames reachable from root

### 4. Static vs Dynamic Transforms

**Static transforms**:
- Fixed relationships that never change
- Example: Camera mount offset from robot base
- Published once at startup
- Efficient (no repeated broadcasts)

**Dynamic transforms**:
- Time-varying relationships
- Example: Joint angles as robot moves
- Published continuously (10-100 Hz)
- Reflect real-time robot state

## Broadcasting Transforms

### Static Transform Publisher

For fixed frame relationships:

**Command-line**:
```bash
# Publish static transform: camera is 0.5m forward, 0.2m up from base
ros2 run tf2_ros static_transform_publisher \
  --x 0.5 --y 0.0 --z 0.2 \
  --roll 0.0 --pitch 0.0 --yaw 0.0 \
  --frame-id base_link --child-frame-id camera_link
```

**Python node**:
```python
import rclpy
from rclpy.node import Node
from tf2_ros import StaticTransformBroadcaster
from geometry_msgs.msg import TransformStamped
import math

class StaticFramePublisher(Node):
    def __init__(self):
        super().__init__('static_frame_publisher')

        self.tf_static_broadcaster = StaticTransformBroadcaster(self)

        # Publish static transforms
        self.publish_static_transforms()

    def publish_static_transforms(self):
        # Camera relative to base_link
        camera_transform = TransformStamped()
        camera_transform.header.stamp = self.get_clock().now().to_msg()
        camera_transform.header.frame_id = 'base_link'
        camera_transform.child_frame_id = 'camera_link'

        camera_transform.transform.translation.x = 0.5
        camera_transform.transform.translation.y = 0.0
        camera_transform.transform.translation.z = 0.2

        # No rotation (identity quaternion)
        camera_transform.transform.rotation.x = 0.0
        camera_transform.transform.rotation.y = 0.0
        camera_transform.transform.rotation.z = 0.0
        camera_transform.transform.rotation.w = 1.0

        # LIDAR relative to base_link
        lidar_transform = TransformStamped()
        lidar_transform.header.stamp = self.get_clock().now().to_msg()
        lidar_transform.header.frame_id = 'base_link'
        lidar_transform.child_frame_id = 'lidar_link'

        lidar_transform.transform.translation.x = 0.3
        lidar_transform.transform.translation.y = 0.0
        lidar_transform.transform.translation.z = 0.15

        lidar_transform.transform.rotation.w = 1.0

        # Broadcast static transforms
        self.tf_static_broadcaster.sendTransform([camera_transform, lidar_transform])

        self.get_logger().info('Static transforms published')

def main():
    rclpy.init()
    node = StaticFramePublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
```

### Dynamic Transform Broadcaster

For time-varying relationships (e.g., robot joints):

```python
import rclpy
from rclpy.node import Node
from tf2_ros import TransformBroadcaster
from geometry_msgs.msg import TransformStamped
from sensor_msgs.msg import JointState
import math

class DynamicFramePublisher(Node):
    def __init__(self):
        super().__init__('dynamic_frame_publisher')

        self.tf_broadcaster = TransformBroadcaster(self)

        # Subscribe to joint states
        self.subscription = self.create_subscription(
            JointState,
            'joint_states',
            self.joint_state_callback,
            10
        )

        # Timer for publishing odom -> base_link (from odometry)
        self.timer = self.create_timer(0.05, self.publish_odom_transform)  # 20 Hz

        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0

    def joint_state_callback(self, msg):
        """
        Publish transforms for each joint based on joint states
        """
        for i, joint_name in enumerate(msg.name):
            transform = TransformStamped()
            transform.header.stamp = self.get_clock().now().to_msg()

            # Map joint names to parent/child frames
            if joint_name == 'left_hip_joint':
                transform.header.frame_id = 'base_link'
                transform.child_frame_id = 'left_hip_link'

                # Joint rotation around Y-axis
                angle = msg.position[i]
                transform.transform.rotation.y = math.sin(angle / 2.0)
                transform.transform.rotation.w = math.cos(angle / 2.0)

                # Translation (fixed offset)
                transform.transform.translation.x = 0.0
                transform.transform.translation.y = 0.1
                transform.transform.translation.z = -0.05

                self.tf_broadcaster.sendTransform(transform)

    def publish_odom_transform(self):
        """
        Publish odom -> base_link transform (from wheel odometry/IMU)
        """
        # Simulate robot motion (in real system, get from odometry)
        self.x += 0.001
        self.theta += 0.01

        transform = TransformStamped()
        transform.header.stamp = self.get_clock().now().to_msg()
        transform.header.frame_id = 'odom'
        transform.child_frame_id = 'base_link'

        # Translation
        transform.transform.translation.x = self.x
        transform.transform.translation.y = self.y
        transform.transform.translation.z = 0.0

        # Rotation (quaternion from yaw angle)
        transform.transform.rotation.z = math.sin(self.theta / 2.0)
        transform.transform.rotation.w = math.cos(self.theta / 2.0)

        self.tf_broadcaster.sendTransform(transform)

def main():
    rclpy.init()
    node = DynamicFramePublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
```

## Listening to Transforms

### Transform Lookup

Query transforms between any two frames:

```python
import rclpy
from rclpy.node import Node
from tf2_ros import TransformListener, Buffer
from geometry_msgs.msg import PointStamped
import math

class TransformListenerNode(Node):
    def __init__(self):
        super().__init__('transform_listener')

        # TF2 buffer and listener
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        # Timer to periodically lookup transforms
        self.timer = self.create_timer(1.0, self.lookup_transform)

    def lookup_transform(self):
        """
        Lookup transform from camera to base_link
        """
        try:
            # Lookup latest available transform
            transform = self.tf_buffer.lookup_transform(
                'base_link',  # Target frame
                'camera_link',  # Source frame
                rclpy.time.Time()  # Latest available
            )

            self.get_logger().info(
                f'Transform camera → base: '
                f'x={transform.transform.translation.x:.3f}, '
                f'y={transform.transform.translation.y:.3f}, '
                f'z={transform.transform.translation.z:.3f}'
            )

        except Exception as e:
            self.get_logger().warn(f'Could not transform: {e}')

    def lookup_transform_at_time(self, target_frame, source_frame, timestamp):
        """
        Lookup transform at specific time (for sensor data synchronization)
        """
        try:
            transform = self.tf_buffer.lookup_transform(
                target_frame,
                source_frame,
                timestamp,
                timeout=rclpy.duration.Duration(seconds=1.0)
            )
            return transform

        except Exception as e:
            self.get_logger().error(f'Transform lookup failed: {e}')
            return None

def main():
    rclpy.init()
    node = TransformListenerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
```

### Transforming Points and Poses

Transform geometric data between frames:

```python
from tf2_ros import TransformException
from geometry_msgs.msg import PointStamped, PoseStamped
import rclpy
from rclpy.node import Node
from tf2_ros import Buffer, TransformListener
from tf2_geometry_msgs import do_transform_point, do_transform_pose

class TransformGeometryNode(Node):
    def __init__(self):
        super().__init__('transform_geometry')

        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

    def transform_point(self, point_in_camera):
        """
        Transform point from camera frame to base frame
        """
        point_stamped = PointStamped()
        point_stamped.header.frame_id = 'camera_link'
        point_stamped.header.stamp = self.get_clock().now().to_msg()
        point_stamped.point.x = point_in_camera[0]
        point_stamped.point.y = point_in_camera[1]
        point_stamped.point.z = point_in_camera[2]

        try:
            # Transform to base_link frame
            point_in_base = self.tf_buffer.transform(
                point_stamped,
                'base_link',
                timeout=rclpy.duration.Duration(seconds=1.0)
            )

            self.get_logger().info(
                f'Point in base frame: '
                f'[{point_in_base.point.x:.3f}, '
                f'{point_in_base.point.y:.3f}, '
                f'{point_in_base.point.z:.3f}]'
            )

            return point_in_base

        except TransformException as e:
            self.get_logger().error(f'Transform failed: {e}')
            return None

    def transform_pose(self, pose_in_map):
        """
        Transform full pose (position + orientation) between frames
        """
        pose_stamped = PoseStamped()
        pose_stamped.header.frame_id = 'map'
        pose_stamped.header.stamp = self.get_clock().now().to_msg()

        # Set position
        pose_stamped.pose.position.x = pose_in_map['x']
        pose_stamped.pose.position.y = pose_in_map['y']
        pose_stamped.pose.position.z = 0.0

        # Set orientation (quaternion)
        pose_stamped.pose.orientation.w = 1.0

        try:
            pose_in_odom = self.tf_buffer.transform(
                pose_stamped,
                'odom',
                timeout=rclpy.duration.Duration(seconds=1.0)
            )

            return pose_in_odom

        except TransformException as e:
            self.get_logger().error(f'Pose transform failed: {e}')
            return None
```

## Debugging and Visualization

### Command-Line Tools

**View TF tree**:
```bash
# Generate PDF visualization of frame tree
ros2 run tf2_tools view_frames

# Output: frames.pdf (open with PDF viewer)
evince frames.pdf
```

**Echo transform**:
```bash
# Print transform from base_link to camera_link
ros2 run tf2_ros tf2_echo base_link camera_link
```

**Monitor TF tree**:
```bash
# Check for missing/broken transforms
ros2 run tf2_ros tf2_monitor
```

### RViz Visualization

RViz can display TF frames in 3D:

1. Add **TF** display
2. Enable **Show Names** to label frames
3. Enable **Show Axes** to visualize frame orientations
4. Adjust **Marker Scale** for visibility

## Best Practices

### 1. Consistent Frame Naming

```python
# Good: Descriptive, lowercase, underscores
'base_link', 'left_camera', 'right_foot'

# Bad: Ambiguous or inconsistent
'frame1', 'Camera', 'RIGHT-FOOT'
```

### 2. Publish Transforms at Appropriate Rates

```python
# Static transforms: Once at startup
static_broadcaster.sendTransform(transform)

# Slow-moving joints: 10-30 Hz
self.create_timer(0.05, self.publish_joint_transforms)  # 20 Hz

# Fast odometry: 50-100 Hz
self.create_timer(0.01, self.publish_odom)  # 100 Hz
```

### 3. Handle Transform Exceptions

```python
try:
    transform = self.tf_buffer.lookup_transform(
        target_frame,
        source_frame,
        timestamp,
        timeout=rclpy.duration.Duration(seconds=1.0)
    )
except TransformException as e:
    # Log error and handle gracefully
    self.get_logger().error(f'TF lookup failed: {e}')
    return None
```

### 4. Use Time Synchronization for Sensor Fusion

```python
# Transform LIDAR point using timestamp from LIDAR message
lidar_point_stamped.header.stamp = lidar_msg.header.stamp

# TF2 will interpolate transforms at exact timestamp
point_in_base = self.tf_buffer.transform(
    lidar_point_stamped,
    'base_link',
    timeout=rclpy.duration.Duration(seconds=0.1)
)
```

### 5. Avoid Transform Loops

```python
# Good: Tree structure
map → odom → base_link → camera

# Bad: Creates a loop (TF will fail)
map → odom → base_link → camera → map  # Circular!
```

## Real-World Application: Humanoid Grasping

**Scenario**: A humanoid robot uses a wrist-mounted camera to detect an object and grasp it.

**Frame chain**: `map → odom → base_link → shoulder → elbow → wrist → camera`

```python
class HumanoidGraspingNode(Node):
    def __init__(self):
        super().__init__('humanoid_grasping')

        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        # Subscribe to object detections from camera
        self.create_subscription(
            DetectedObject,
            '/camera/detections',
            self.object_detected_callback,
            10
        )

    def object_detected_callback(self, msg):
        """
        Transform object position from camera frame to hand frame for grasping
        """
        # Object position in camera frame
        object_point = PointStamped()
        object_point.header = msg.header  # Timestamp from camera
        object_point.point = msg.position

        try:
            # Transform to hand frame
            object_in_hand = self.tf_buffer.transform(
                object_point,
                'right_hand',
                timeout=rclpy.duration.Duration(seconds=0.5)
            )

            # Send grasp command
            self.grasp_object(object_in_hand.point)

        except TransformException as e:
            self.get_logger().error(f'Cannot transform object: {e}')

    def grasp_object(self, position_in_hand_frame):
        """
        Execute grasp using object position relative to hand
        """
        self.get_logger().info(
            f'Grasping object at hand-relative position: '
            f'[{position_in_hand_frame.x:.3f}, '
            f'{position_in_hand_frame.y:.3f}, '
            f'{position_in_hand_frame.z:.3f}]'
        )
        # ... send joint commands to close gripper
```

## Summary

TF2 is the backbone of spatial reasoning in ROS 2, enabling seamless coordinate transformations across complex robotic systems. Key takeaways:

- **Frames** represent coordinate systems; **transforms** describe relationships between frames
- **Static transforms** for fixed relationships; **dynamic transforms** for time-varying joints/odometry
- **TransformBroadcaster** publishes transforms; **TransformListener** queries transforms
- **tf_buffer.transform()** converts points/poses between frames with time synchronization
- **Best practices**: Consistent naming, appropriate rates, exception handling, avoid loops

In the next chapter, we'll explore URDF robot descriptions—the declarative format for defining robot geometry, kinematics, and sensors.

---

**Key Takeaways**:
- TF2 manages coordinate frame relationships in a tree structure
- Static transforms for fixed mounts, dynamic transforms for moving joints
- TransformBroadcaster publishes, TransformListener queries transforms
- Transform geometric data (points, poses) between any frames
- Use timestamps for sensor synchronization
- Visualize TF tree with RViz and view_frames tool
- Exception handling critical for robust transform lookups
