# Chapter 3: ROS 2 Architecture and Communication

## ROS 2 Design Philosophy

ROS 2 addresses limitations of ROS 1:

### Key Improvements
1. **Real-Time Performance**: Deterministic execution
2. **Security**: DDS Security plugins
3. **Multi-Platform**: Linux, Windows, macOS, RTOS

## DDS Middleware

```python
from rclpy.qos import QoSProfile, ReliabilityPolicy

qos = QoSProfile(
    reliability=ReliabilityPolicy.RELIABLE,
    depth=10
)
```

## Communication Patterns

- **Topics**: Asynchronous, many-to-many
- **Services**: Synchronous, one-to-one
- **Actions**: Long-running tasks with feedback
