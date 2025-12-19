# Chapter 20: Deployment on Humanoids

## From Research Prototypes to Production Systems

Training a high-performing VLA model is only half the battle—deploying it on real humanoid robots requires addressing **real-time constraints**, **hardware limitations**, **safety guarantees**, and **production reliability**. A 7B-parameter model that runs at 2 Hz on a desktop GPU is useless for a humanoid that needs 10-30 Hz control. This chapter covers the complete deployment pipeline: model optimization, hardware acceleration, real-time control architecture, safety systems, and production best practices.

**Deployment Challenges**:
1. **Latency**: 7B models take 50-100ms` per inference (too slow for 10 Hz control)
2. **Power**: Humanoid robots run on batteries (15-30W budget for AI compute)
3. **Safety**: Neural networks can predict unsafe actions (need safety shields)
4. **Reliability**: Must handle sensor failures, network dropouts, hardware faults

**Solution Stack**:
```
VLA Model → Quantization → TensorRT → Jetson Orin → Safety Monitor → Robot
(7B FP32)   (INT8, 4-bit)  (optimize)  (15W inference) (verify actions)  (execute)
```

This chapter provides production-ready code for deploying VLA models on NVIDIA Jetson-powered humanoids with real-time performance and safety guarantees.

## Model Optimization for Edge Deployment

### Quantization: Reducing Precision

**Problem**: FP32 models (32-bit floating point) are too large and slow for edge devices.

**Solution**: **Quantization**—reduce precision to INT8 (8-bit integers) or INT4 (4-bit), achieving:
- **4-8× faster inference**
- **4-8× smaller model size**
- **Minimal accuracy loss** (`<2%` for INT8, `<5%` for INT4)

**Quantization Types**:
1. **Post-Training Quantization (PTQ)**: Quantize trained model (no retraining)
2. **Quantization-Aware Training (QAT)**: Train with quantization (better accuracy)

**PTQ with PyTorch**:
```python
import torch
from transformers import AutoModel

# Load FP32 model
model_fp32 = AutoModel.from_pretrained("openvla/openvla-7b")

# Dynamic quantization (weights → INT8, activations → FP32 during inference)
model_int8 = torch.quantization.quantize_dynamic(
    model_fp32,
    {torch.nn.Linear},  # Quantize all Linear layers
    dtype=torch.qint8
)

# Save quantized model
torch.save(model_int8.state_dict(), "openvla_int8.pth")

# Inference speedup: 2-3× on Jetson Orin
# Model size: 14 GB → 3.5 GB
```

**Static Quantization** (weights + activations → INT8):
```python
import torch.quantization as quantization

# Prepare model for quantization
model.qconfig = quantization.get_default_qconfig('fbgemm')  # x86
# or 'qnnpack' for ARM (Jetson)

model_prepared = quantization.prepare(model, inplace=False)

# Calibrate with representative data (100-1000 samples)
with torch.no_grad():
    for images, instructions in calibration_loader:
        model_prepared(images, instructions)

# Convert to quantized model
model_quantized = quantization.convert(model_prepared, inplace=False)

# Inference speedup: 3-4× on Jetson Orin
# Accuracy drop: `<2%`
```

### TensorRT: NVIDIA's Inference Optimizer

**TensorRT** optimizes neural networks for NVIDIA GPUs:
- **Layer Fusion**: Merge multiple layers (Conv + BatchNorm + ReLU → single kernel)
- **Precision Calibration**: Mixed INT8/FP16 precision per layer
- **Kernel Auto-Tuning**: Select fastest CUDA kernels for target hardware

**Convert OpenVLA to TensorRT**:
```python
import torch
import tensorrt as trt
from torch2trt import torch2trt

# Load PyTorch model
model = OpenVLA.from_pretrained("openvla/openvla-7b").cuda().eval()

# Example inputs (for tracing)
dummy_image = torch.randn(1, 3, 224, 224).cuda()
dummy_instruction = torch.randint(0, 50000, (1, 20)).cuda()  # Tokenized instruction

# Convert to TensorRT
model_trt = torch2trt(
    model,
    [dummy_image, dummy_instruction],
    fp16_mode=True,  # Use FP16 precision
    max_batch_size=1,
    max_workspace_size=1 << 30  # 1 GB workspace
)

# Save TensorRT engine
torch.save(model_trt.state_dict(), "openvla_trt_fp16.pth")

# Inference speedup: 5-10× on Jetson Orin (vs PyTorch FP32)
# Latency: 100ms` → 10ms` (achieves 10 Hz control)
```

**Benchmarking**:
```python
import time

def benchmark_model(model, inputs, num_trials=100):
    """Measure inference latency"""

    # Warmup
    for _ in range(10):
        _ = model(*inputs)

    # Benchmark
    latencies = []
    for _ in range(num_trials):
        start = time.perf_counter()
        _ = model(*inputs)
        torch.cuda.synchronize()  # Wait for GPU
        latencies.append(time.perf_counter() - start)

    print(f"Mean latency: {np.mean(latencies)*1000:.2f} ms")
    print(f"P95 latency: {np.percentile(latencies, 95)*1000:.2f} ms")
    print(f"Throughput: {1.0 / np.mean(latencies):.2f} Hz")

# Results on Jetson Orin (15W mode):
# PyTorch FP32: 180 ms (5.5 Hz)
# PyTorch INT8: 60 ms (16 Hz)
# TensorRT FP16: 12 ms (83 Hz) ✅ Real-time capable
```

### Model Pruning and Distillation

**Pruning**: Remove unimportant weights (set to zero), achieve **50-70% sparsity** with &lt;3% accuracy drop.

```python
import torch.nn.utils.prune as prune

# Structured pruning: remove entire channels
for module in model.modules():
    if isinstance(module, torch.nn.Linear):
        prune.ln_structured(module, name="weight", amount=0.5, n=2, dim=0)

# Remove pruning reparameterization (make permanent)
for module in model.modules():
    if isinstance(module, torch.nn.Linear):
        prune.remove(module, 'weight')

# Result: 50%` fewer parameters, 1.5-2× speedup
```

**Knowledge Distillation**: Train small model (student) to mimic large model (teacher).

```python
def distillation_loss(student_logits, teacher_logits, temperature=2.0):
    """KL divergence between student and teacher predictions"""

    student_probs = F.softmax(student_logits / temperature, dim=-1)
    teacher_probs = F.softmax(teacher_logits / temperature, dim=-1)

    loss = F.kl_div(student_probs.log(), teacher_probs, reduction='batchmean')
    return loss * (temperature ** 2)

# Train 1B student to mimic 7B teacher
teacher = OpenVLA.from_pretrained("openvla/openvla-7b").eval()
student = OpenVLA_1B()  # Smaller architecture

for batch in train_loader:
    # Teacher predictions (frozen)
    with torch.no_grad():
        teacher_logits = teacher(batch['images'], batch['instructions'])

    # Student predictions
    student_logits = student(batch['images'], batch['instructions'])

    # Distillation loss
    loss = distillation_loss(student_logits, teacher_logits)

    # Backprop
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

# Result: 1B student achieves 90%` of 7B teacher's performance
# Inference: 5× faster, 7× less memory
```

## Real-Time Control Architecture

### Control Loop Design

**Humanoid Control Hierarchy**:
```
High-Level Controller (VLA Policy, 10 Hz)
         ↓
Mid-Level Controller (Whole-Body Control, 100 Hz)
         ↓
Low-Level Controller (Joint PID, 1000 Hz)
         ↓
Motor Drivers (Hardware)
```

**VLA Policy Node** (ROS 2):
```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, JointState
from geometry_msgs.msg import Twist
import torch
from openvla import OpenVLA
from cv_bridge import CvBridge

class VLAPolicyNode(Node):
    def __init__(self):
        super().__init__('vla_policy_node')

        # Load optimized model
        self.model = torch.jit.load("openvla_trt_fp16.pth").cuda().eval()

        # ROS subscriptions
        self.image_sub = self.create_subscription(
            Image, '/camera/rgb/image_raw', self.image_callback, 1
        )
        self.joint_sub = self.create_subscription(
            JointState, '/joint_states', self.joint_callback, 1
        )

        # ROS publisher
        self.action_pub = self.create_publisher(Twist, '/vla/action', 1)

        # State
        self.latest_image = None
        self.latest_joint_state = None
        self.instruction = "pick up the red block"  # Task instruction

        # Control loop timer (10 Hz)
        self.timer = self.create_timer(0.1, self.control_loop)

        self.bridge = CvBridge()
        self.get_logger().info('VLA Policy Node initialized (10 Hz control)')

    def image_callback(self, msg):
        self.latest_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='rgb8')

    def joint_callback(self, msg):
        self.latest_joint_state = torch.tensor(msg.position, dtype=torch.float32)

    def control_loop(self):
        """10 Hz control loop"""
        if self.latest_image is None or self.latest_joint_state is None:
            return

        # Prepare inputs
        image_tensor = torch.from_numpy(self.latest_image).permute(2, 0, 1).unsqueeze(0).cuda()
        image_tensor = image_tensor / 255.0  # Normalize

        # VLA inference
        with torch.no_grad():
            start = time.perf_counter()
            action = self.model.predict_action(
                observation={"image": image_tensor, "proprio": self.latest_joint_state.cuda()},
                instruction=self.instruction
            )
            latency = time.perf_counter() - start

        # Publish action
        action_msg = Twist()
        action_msg.linear.x = float(action[0])
        action_msg.linear.y = float(action[1])
        action_msg.linear.z = float(action[2])
        action_msg.angular.x = float(action[3])
        action_msg.angular.y = float(action[4])
        action_msg.angular.z = float(action[5])

        self.action_pub.publish(action_msg)

        # Log performance
        if latency > 0.08:  # Warn if >80ms` (unsafe for 10 Hz control)
            self.get_logger().warn(f'High latency: {latency*1000:.1f} ms')
        else:
            self.get_logger().debug(f'Latency: {latency*1000:.1f} ms')

def main():
    rclpy.init()
    node = VLAPolicyNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
```

### Asynchronous Perception and Action

**Problem**: VLA inference (10ms`) + camera capture (33ms`) + preprocessing (5ms`) = 48ms` total latency.

**Solution**: **Parallel processing**—capture next image while processing current image.

```python
from threading import Thread, Lock
from queue import Queue

class AsyncVLAController:
    def __init__(self):
        self.model = load_optimized_vla()

        # Queues for async processing
        self.image_queue = Queue(maxsize=2)
        self.action_queue = Queue(maxsize=2)

        # Threads
        self.perception_thread = Thread(target=self.perception_loop, daemon=True)
        self.inference_thread = Thread(target=self.inference_loop, daemon=True)
        self.control_thread = Thread(target=self.control_loop, daemon=True)

        # Start threads
        self.perception_thread.start()
        self.inference_thread.start()
        self.control_thread.start()

    def perception_loop(self):
        """Capture images at 30 Hz"""
        camera = connect_camera()

        while True:
            image = camera.capture()
            if not self.image_queue.full():
                self.image_queue.put(image)
            time.sleep(1/30)  # 30 FPS

    def inference_loop(self):
        """VLA inference loop"""
        while True:
            if self.image_queue.empty():
                continue

            image = self.image_queue.get()
            action = self.model.predict_action(image, self.instruction)

            if not self.action_queue.full():
                self.action_queue.put(action)

    def control_loop(self):
        """Execute actions at 10 Hz"""
        robot = connect_robot()

        while True:
            if not self.action_queue.empty():
                action = self.action_queue.get()
                robot.execute(action)
            time.sleep(0.1)  # 10 Hz

# Result: Effective latency reduced by 30-40%`
```

## Safety Systems for VLA Deployment

### Action Space Constraints

**Problem**: VLA can predict actions outside safe bounds (joint limits, workspace boundaries, collision zones).

**Solution**: **Safety shield**—verify and clamp actions before execution.

```python
class SafetyShield:
    def __init__(self, robot_config):
        # Joint limits
        self.joint_min = robot_config['joint_limits']['min']  # (7,)
        self.joint_max = robot_config['joint_limits']['max']  # (7,)

        # Workspace boundaries
        self.workspace_min = np.array([-0.5, -0.5, 0.0])  # (x, y, z)
        self.workspace_max = np.array([0.5, 0.5, 1.0])

        # Maximum velocity/acceleration
        self.max_velocity = 0.5  # m/s
        self.max_acceleration = 2.0  # m/s²

        # Collision zones (forbidden regions)
        self.collision_zones = [
            {'center': [0.0, 0.0, 0.5], 'radius': 0.15}  # Protect robot base
        ]

    def verify_action(self, action, current_state):
        """Verify action safety before execution"""

        # Predict next state
        next_state = self.forward_kinematics(action, current_state)

        # Check 1: Joint limits
        if not self.check_joint_limits(next_state):
            self.get_logger().warn('Action violates joint limits')
            return False, None

        # Check 2: Workspace boundaries
        if not self.check_workspace(next_state):
            self.get_logger().warn('Action exits workspace')
            return False, None

        # Check 3: Velocity limits
        if not self.check_velocity(action, current_state):
            self.get_logger().warn('Action exceeds velocity limit')
            # Clamp velocity
            action = self.clamp_velocity(action, current_state)

        # Check 4: Collision zones
        if not self.check_collisions(next_state):
            self.get_logger().warn('Action enters collision zone')
            return False, None

        return True, action

    def check_joint_limits(self, state):
        """Verify joint angles within limits"""
        return np.all(state['joint_positions'] >= self.joint_min) and \
               np.all(state['joint_positions'] <= self.joint_max)

    def check_workspace(self, state):
        """Verify end-effector in workspace"""
        ee_pos = state['end_effector_position']
        return np.all(ee_pos >= self.workspace_min) and \
               np.all(ee_pos <= self.workspace_max)

    def check_velocity(self, action, current_state):
        """Verify velocity within limits"""
        velocity = np.linalg.norm(action[:3])  # Linear velocity
        return velocity <= self.max_velocity

    def clamp_velocity(self, action, current_state):
        """Clamp velocity to safe limits"""
        velocity = np.linalg.norm(action[:3])
        if velocity > self.max_velocity:
            action[:3] = action[:3] / velocity * self.max_velocity
        return action

    def check_collisions(self, state):
        """Verify no collisions with forbidden zones"""
        ee_pos = state['end_effector_position']

        for zone in self.collision_zones:
            distance = np.linalg.norm(ee_pos - zone['center'])
            if distance < zone['radius']:
                return False

        return True

# Usage in control loop
safety_shield = SafetyShield(robot_config)

for step in control_loop:
    action = vla_model.predict(observation)

    # Verify safety
    is_safe, safe_action = safety_shield.verify_action(action, robot.get_state())

    if is_safe:
        robot.execute(safe_action)
    else:
        robot.emergency_stop()
        log_unsafe_action(action)
```

### Fault Detection and Recovery

**Monitoring**:
```python
class FaultDetector:
    def __init__(self):
        # Thresholds
        self.max_joint_torque = 50.0  # Nm
        self.max_temperature = 70.0  # °C
        self.min_battery_voltage = 20.0  # V

        # Fault counters
        self.fault_counts = {
            'high_torque': 0,
            'high_temperature': 0,
            'low_battery': 0,
            'sensor_timeout': 0
        }

    def check_faults(self, robot_state):
        """Detect hardware/software faults"""

        faults = []

        # Check joint torques
        if np.any(np.abs(robot_state['joint_torques']) > self.max_joint_torque):
            faults.append('high_torque')

        # Check temperatures
        if np.any(robot_state['joint_temperatures'] > self.max_temperature):
            faults.append('high_temperature')

        # Check battery
        if robot_state['battery_voltage'] < self.min_battery_voltage:
            faults.append('low_battery')

        # Check sensor staleness
        if time.time() - robot_state['last_camera_update'] > 0.5:
            faults.append('sensor_timeout')

        # Update fault counts
        for fault in faults:
            self.fault_counts[fault] += 1

        # Trigger recovery if persistent faults
        if any(count > 5 for count in self.fault_counts.values()):
            return True, faults

        return False, faults

    def recover_from_fault(self, faults):
        """Execute recovery procedure"""

        if 'high_torque' in faults:
            # Reduce control gains
            robot.set_control_gains(kp=0.5, kd=0.1)

        if 'high_temperature' in faults:
            # Reduce motor usage (enter low-power mode)
            robot.set_torque_limit(0.3)
            time.sleep(60)  # Cool down

        if 'low_battery' in faults:
            # Return to charging station
            robot.navigate_to_charger()

        if 'sensor_timeout' in faults:
            # Reset camera
            robot.reset_camera()
```

## Production Deployment on Jetson Orin

### Docker Container for Reproducible Deployment

**Dockerfile**:
```dockerfile
FROM nvcr.io/nvidia/l4t-pytorch:r35.2.1-pth2.0-py3

# Install dependencies
RUN apt-get update && apt-get install -y \
    ros-humble-ros-base \
    python3-colcon-common-extensions \
    tensorrt \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
COPY requirements.txt /app/
RUN pip3 install -r /app/requirements.txt

# Copy VLA model
COPY openvla_trt_fp16.pth /app/models/

# Copy ROS workspace
COPY ros2_ws /app/ros2_ws

# Build ROS workspace
WORKDIR /app/ros2_ws
RUN . /opt/ros/humble/setup.sh && colcon build --symlink-install

# Entry point
CMD ["bash", "-c", "source /app/ros2_ws/install/setup.bash && ros2 launch vla_control vla_humanoid.launch.py"]
```

**Build and Deploy**:
```bash
# Build Docker image
docker build -t humanoid-vla:v1.0 .

# Run on Jetson Orin
docker run --runtime nvidia --network host \
  -v /dev:/dev --privileged \
  -e ROS_DOMAIN_ID=42 \
  humanoid-vla:v1.0
```

### Monitoring and Logging

**Prometheus Metrics**:
```python
from prometheus_client import start_http_server, Gauge, Counter

# Metrics
vla_latency = Gauge('vla_inference_latency_ms', 'VLA inference latency in milliseconds')
vla_throughput = Gauge('vla_inference_hz', 'VLA inference frequency')
unsafe_actions = Counter('vla_unsafe_actions', 'Number of unsafe actions blocked')
fault_count = Counter('robot_faults', 'Number of fault detections', ['fault_type'])

# Update metrics in control loop
vla_latency.set(latency * 1000)
vla_throughput.set(1.0 / latency)

if not is_safe:
    unsafe_actions.inc()

# Start Prometheus server (port 8000)
start_http_server(8000)
```

**Grafana Dashboard** (query Prometheus metrics):
- VLA inference latency (P50, P95, P99)
- Control loop frequency
- Unsafe action rate
- Fault detection rate
- Battery voltage, joint temperatures

## Summary

Deploying VLA models on humanoid robots requires optimization, real-time architecture, and safety systems:

- **Model Optimization**: Quantization (INT8/INT4), TensorRT (5-10× speedup), pruning, distillation
- **Real-Time Control**: 10 Hz VLA policy, async perception/action, parallel processing
- **Safety**: Action space constraints, collision avoidance, fault detection/recovery
- **Production**: Docker deployment, monitoring (Prometheus/Grafana), logging

In the next chapter, we'll explore **Evaluation Metrics and Benchmarks**: how to measure VLA performance, standardized benchmarks, and leaderboard comparisons.

---

**Key Takeaways**:
- TensorRT achieves 5-10× speedup on Jetson Orin (100ms` → 10ms` latency for 7B model)
- INT8 quantization reduces model size 4× with `<2%` accuracy loss
- Asynchronous perception/action reduces effective latency by 30-40%`
- Safety shields verify actions before execution (joint limits, workspace, collisions)
- Fault detection monitors joint torques, temperatures, battery, sensor timeouts
- Docker containers enable reproducible deployment across Jetson devices
- Prometheus + Grafana provide real-time monitoring of VLA performance
- Best practice: TensorRT FP16 + safety shield achieves 10 Hz real-time control
