# Chapter 3: ROS 2 Architecture and Communication

## Introduction to ROS 2

**ROS 2 (Robot Operating System 2)** represents a complete architectural redesign of the original ROS framework, addressing critical limitations discovered through a decade of real-world robotics deployments. While ROS 1 revolutionized academic and research robotics, its TCP-based communication, single-master architecture, and lack of real-time guarantees made it unsuitable for production environments, safety-critical systems, and commercial robots.

ROS 2 was built from the ground up to support:
- **Production-grade reliability** for commercial deployment
- **Real-time determinism** for control-critical applications
- **Multi-robot systems** without centralized coordinators
- **Security** through DDS encryption and authentication
- **Cross-platform support** (Linux, Windows, macOS, real-time OS)

This chapter explores the architectural foundations of ROS 2, focusing on its DDS middleware, communication patterns, and Quality of Service (QoS) system—the core concepts that enable building robust, distributed robotic systems.

## ROS 2 Design Philosophy

### Addressing ROS 1 Limitations

ROS 1's architecture had several fundamental constraints:

**Single Point of Failure (roscore)**:
- All nodes required connection to a centralized master (roscore)
- If roscore crashed, the entire system failed
- Multi-robot systems required complex networking workarounds

**No Real-Time Support**:
- TCP-based communication introduced unpredictable latency
- No priority-based message delivery
- Unsuitable for hard real-time control loops (e.g., motor PID at 1 kHz)

**Security Vulnerabilities**:
- No built-in authentication or encryption
- Any node could publish/subscribe to any topic
- Network traffic was unencrypted plain text

**Platform Limitations**:
- Linux-centric design
- Poor Windows and macOS support
- Incompatible with real-time operating systems (RTOS)

### ROS 2 Core Improvements

**1. Decentralized Discovery**:
ROS 2 eliminates the master node using DDS's peer-to-peer discovery protocol. Nodes automatically find each other through UDP multicast, enabling:
- Fault tolerance: No single point of failure
- Dynamic networks: Nodes can join/leave seamlessly
- Multi-robot coordination: Robots discover each other's topics automatically

**2. Real-Time Performance**:
Through DDS middleware, ROS 2 supports:
- **Deterministic communication**: Bounded latency with RELIABLE QoS
- **Priority queues**: High-priority messages preempt low-priority ones
- **RTOS compatibility**: Runs on VxWorks, QNX, Zephyr
- **Lockless data structures**: Minimize context-switching overhead

**3. Security (DDS Security)**:
Built-in security features include:
- **Authentication**: Nodes verify identity with certificates
- **Authorization**: Fine-grained topic access control
- **Encryption**: AES-256 for message payloads
- **Tamper detection**: HMAC integrity checks

**4. Multi-Platform Support**:
Native support for:
- **Linux** (Ubuntu, Debian, RHEL)
- **Windows 10/11**
- **macOS** (limited support)
- **Embedded RTOS** (FreeRTOS, Zephyr, VxWorks)

**5. Lifecycle Management**:
Managed nodes with state machines for graceful initialization and shutdown, critical for safety systems.

## DDS Middleware: The Foundation of ROS 2

### What is DDS?

**Data Distribution Service (DDS)** is an OMG (Object Management Group) standard for real-time, scalable, publish-subscribe communication. ROS 2 uses DDS as its middleware layer, abstracting away low-level networking while providing:
- **Automatic discovery**: No manual configuration required
- **Type safety**: Strongly-typed messages with IDL (Interface Definition Language)
- **QoS policies**: Fine-grained control over reliability, latency, and resource usage

### DDS Architecture

DDS operates on the concept of a **Global Data Space** shared by all participants:

```
┌─────────────────────────────────────────────────────────┐
│                  Global Data Space (DDS Domain)          │
│                                                          │
│  ┌──────────┐         ┌──────────┐         ┌──────────┐│
│  │Publisher │─topics─→│          │←─topics─│Subscriber││
│  │  Node A  │         │ DDS Cloud│         │  Node B  ││
│  └──────────┘         │ (Discovery)        └──────────┘│
│                       │                                 │
│  ┌──────────┐         │          │         ┌──────────┐│
│  │Publisher │─topics─→│          │←─topics─│Subscriber││
│  │  Node C  │         └──────────┘         │  Node D  ││
│  └──────────┘                               └──────────┘│
└─────────────────────────────────────────────────────────┘
```

**Key Components**:
- **Domain**: Isolated communication scope (like a virtual network)
- **Participant**: A node in the DDS network
- **Publisher/Subscriber**: Endpoints for sending/receiving data
- **Topic**: Named data stream with a specific type
- **DataWriter/DataReader**: Low-level DDS interfaces

### DDS Implementations in ROS 2

ROS 2 supports multiple DDS vendors through the **RMW (ROS Middleware) abstraction layer**:

| DDS Implementation | Vendor | License | Characteristics |
|-------------------|--------|---------|----------------|
| **Fast DDS** | eProsima | Apache 2.0 | Default, high performance, open-source |
| **Cyclone DDS** | Eclipse | EPL 2.0 | Lightweight, low latency |
| **Connext DDS** | RTI | Commercial | Enterprise-grade, best tooling |
| **GurumDDS** | Gurum Networks | Commercial | Embedded systems focus |

**Switching DDS implementations**:
```bash
# Use Fast DDS (default)
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp

# Use Cyclone DDS
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
```

## Communication Patterns in ROS 2

ROS 2 provides three primary communication mechanisms, each suited for different use cases:

### 1. Topics: Asynchronous Publish-Subscribe

**Topics** enable many-to-many, asynchronous communication—ideal for streaming sensor data, telemetry, and continuous state updates.

**Characteristics**:
- **Decoupled**: Publishers and subscribers don't know about each other
- **Asynchronous**: Non-blocking, fire-and-forget
- **Many-to-many**: Multiple publishers and subscribers on one topic
- **Best-effort or reliable**: Configurable QoS

**Example: Publishing Sensor Data**

```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
import numpy as np

class LidarPublisher(Node):
    def __init__(self):
        super().__init__('lidar_publisher')

        # Create publisher on '/scan' topic
        self.publisher = self.create_publisher(
            LaserScan,
            '/scan',
            qos_profile=10  # Queue depth
        )

        # Publish at 10 Hz
        self.timer = self.create_timer(0.1, self.publish_scan)

        self.get_logger().info('LIDAR publisher started')

    def publish_scan(self):
        msg = LaserScan()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'laser_frame'

        # LIDAR parameters
        msg.angle_min = -np.pi
        msg.angle_max = np.pi
        msg.angle_increment = np.pi / 180  # 1 degree
        msg.time_increment = 0.0
        msg.scan_time = 0.1
        msg.range_min = 0.1
        msg.range_max = 30.0

        # Simulate 360 range measurements
        msg.ranges = [5.0 + np.random.normal(0, 0.1) for _ in range(360)]

        self.publisher.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = LidarPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
```

**Example: Subscribing to Sensor Data**

```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan

class ObstacleDetector(Node):
    def __init__(self):
        super().__init__('obstacle_detector')

        # Subscribe to '/scan' topic
        self.subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            qos_profile=10
        )

        self.get_logger().info('Obstacle detector started')

    def scan_callback(self, msg: LaserScan):
        # Find minimum range
        min_range = min(msg.ranges)

        if min_range < 0.5:  # Obstacle closer than 50 cm
            self.get_logger().warn(f'Obstacle detected at {min_range:.2f} m!')
        else:
            self.get_logger().info(f'Path clear. Min distance: {min_range:.2f} m')

def main(args=None):
    rclpy.init(args=args)
    node = ObstacleDetector()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
```

### 2. Services: Synchronous Request-Response

**Services** provide one-to-one, synchronous communication—ideal for configuration requests, state queries, and triggering actions that require confirmation.

**Characteristics**:
- **Blocking**: Client waits for response
- **One-to-one**: Single server, multiple clients
- **Reliable**: Uses RELIABLE QoS by default
- **Not for high-frequency**: Avoid in control loops

**Example: Service Server (Add Two Integers)**

```python
from rclpy.node import Node
from example_interfaces.srv import AddTwoInts

class AdditionServer(Node):
    def __init__(self):
        super().__init__('addition_server')

        self.srv = self.create_service(
            AddTwoInts,
            'add_two_ints',
            self.add_callback
        )

        self.get_logger().info('Addition service ready')

    def add_callback(self, request, response):
        response.sum = request.a + request.b
        self.get_logger().info(f'Request: {request.a} + {request.b} = {response.sum}')
        return response
```

**Example: Service Client**

```python
from rclpy.node import Node
from example_interfaces.srv import AddTwoInts

class AdditionClient(Node):
    def __init__(self):
        super().__init__('addition_client')

        self.client = self.create_client(AddTwoInts, 'add_two_ints')

        # Wait for service to become available
        while not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Service not available, waiting...')

    def send_request(self, a, b):
        request = AddTwoInts.Request()
        request.a = a
        request.b = b

        # Asynchronous call (non-blocking)
        future = self.client.call_async(request)
        return future

def main(args=None):
    rclpy.init(args=args)
    client = AdditionClient()

    # Send request
    future = client.send_request(5, 7)
    rclpy.spin_until_future_complete(client, future)

    if future.result() is not None:
        result = future.result()
        client.get_logger().info(f'Result: {result.sum}')
    else:
        client.get_logger().error('Service call failed')

    client.destroy_node()
    rclpy.shutdown()
```

### 3. Actions: Long-Running Tasks with Feedback

**Actions** provide asynchronous, goal-oriented communication with intermediate feedback—ideal for navigation, manipulation, and any task that takes significant time.

**Characteristics**:
- **Goal-feedback-result pattern**: Client sends goal, receives periodic feedback, gets final result
- **Cancelable**: Client can cancel goal mid-execution
- **Preemptable**: New goals can override current goal
- **Ideal for**: Navigation, trajectory execution, object search

**Architecture**:
```
Client                          Action Server
  │                                  │
  ├─────── Goal Request ────────────→│
  │←─────── Goal Accepted ───────────┤
  │                                  │
  │←─────── Feedback (periodic) ─────┤
  │←─────── Feedback ────────────────┤
  │                                  │
  │←─────── Result ──────────────────┤
  │        (Success/Aborted)          │
```

**Example action definition** (Fibonacci.action):
```
# Goal
int32 order
---
# Result
int32[] sequence
---
# Feedback
int32[] partial_sequence
```

## Quality of Service (QoS) Policies

QoS policies are ROS 2's most powerful feature, enabling fine-tuned control over communication trade-offs.

### Key QoS Parameters

**1. Reliability**:
- `RELIABLE`: Guarantees delivery (retransmits lost packets) – Use for commands, critical data
- `BEST_EFFORT`: No delivery guarantee (faster, lower overhead) – Use for sensor streams

**2. Durability**:
- `TRANSIENT_LOCAL`: New subscribers receive last N messages – Use for configuration, maps
- `VOLATILE`: No historical data – Use for real-time streams

**3. History**:
- `KEEP_LAST(N)`: Store last N messages in queue
- `KEEP_ALL`: Store all messages (risky for fast publishers)

**4. Deadline**:
- Maximum time between messages; triggers callback if violated

**5. Lifespan**:
- Message expiration time (stale data is discarded)

**QoS Example**:
```python
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy, HistoryPolicy

# Camera image stream: High-throughput, OK to drop frames
camera_qos = QoSProfile(
    reliability=ReliabilityPolicy.BEST_EFFORT,
    durability=DurabilityPolicy.VOLATILE,
    history=HistoryPolicy.KEEP_LAST,
    depth=1  # Only latest frame
)

# Robot commands: Critical, must not lose
command_qos = QoSProfile(
    reliability=ReliabilityPolicy.RELIABLE,
    durability=DurabilityPolicy.TRANSIENT_LOCAL,
    history=HistoryPolicy.KEEP_LAST,
    depth=10
)
```

## Node Lifecycle Management

ROS 2 **Managed Nodes** implement a state machine for graceful initialization and shutdown:

```
┌──────────────┐
│  Unconfigured │
└──────┬───────┘
       │ configure()
       ↓
┌──────────────┐
│   Inactive   │
└──────┬───────┘
       │ activate()
       ↓
┌──────────────┐
│    Active    │  ← Normal operation
└──────┬───────┘
       │ deactivate()
       ↓
┌──────────────┐
│   Inactive   │
└──────┬───────┘
       │ cleanup()
       ↓
┌──────────────┐
│  Unconfigured │
└──────────────┘
```

**Use cases**:
- Safe hardware initialization (configure sensors before use)
- Hot-swappable nodes (deactivate before parameter changes)
- Emergency stops (deactivate without full shutdown)

## Summary

ROS 2's architecture represents a paradigm shift from ROS 1, prioritizing production-grade reliability, real-time performance, and security. Key takeaways:

- **DDS middleware** provides decentralized discovery, QoS policies, and real-time guarantees
- **Topics** enable asynchronous pub-sub for sensor streams
- **Services** provide synchronous request-response for queries
- **Actions** support long-running, cancelable tasks with feedback
- **QoS policies** allow fine-tuning reliability, latency, and resource trade-offs
- **Lifecycle management** enables safe initialization and graceful degradation

In the next chapter, we'll explore ROS 2's computational graph, launch systems, and parameter management—the tools for orchestrating complex multi-node systems.

---

**Key Takeaways**:
- ROS 2 eliminates single points of failure through DDS peer-to-peer discovery
- Three communication patterns: Topics (async), Services (sync), Actions (goal-oriented)
- QoS policies enable trade-offs between reliability, latency, and resource usage
- Managed nodes support graceful state transitions for safety-critical systems
- DDS middleware layer is swappable (Fast DDS, Cyclone DDS, Connext)
