# Chapter 5: ROS 2 Services and Actions

## Introduction to Synchronous Communication

While topics excel at continuous data streaming (sensor feeds, state updates), many robotic tasks require **request-response patterns** where a client explicitly requests an operation and waits for confirmation. ROS 2 provides two mechanisms for this:

- **Services**: Synchronous, one-to-one request-response for quick operations (< 1 second)
- **Actions**: Asynchronous, goal-oriented tasks with feedback for long-running operations (seconds to minutes)

This chapter explores both patterns in depth, covering implementation, best practices, and real-world use cases. Understanding when to use services versus actions versus topics is critical for designing robust robotic architectures.

## Services: Request-Response Communication

### When to Use Services

Services are ideal for:
- **Configuration requests**: "Set motor speed to 50 RPM"
- **State queries**: "What is the current battery level?"
- **Triggering actions**: "Capture an image now"
- **Resource allocation**: "Reserve gripper for 10 seconds"
- **Coordinate transformations**: "Transform point from camera frame to base frame"

**Avoid services for**:
- High-frequency operations (> 10 Hz) – Use topics instead
- Long-running tasks – Use actions instead
- Fire-and-forget commands – Use topics instead

### Service Definition Format

Services use `.srv` files with request and response sections separated by `---`:

**example_interfaces/srv/AddTwoInts.srv**:
```
int64 a
int64 b
---
int64 sum
```

**geometry_msgs/srv/SetBool.srv**:
```
bool data
---
bool success
string message
```

**Custom service for robot control**:

**robot_interfaces/srv/SetMotorSpeed.srv**:
```
string motor_name
float64 speed_rpm
---
bool success
string error_message
float64 actual_speed
```

### Implementing a Service Server

A service server listens for requests and provides responses.

**Example: Motor control service server**

```python
import rclpy
from rclpy.node import Node
from robot_interfaces.srv import SetMotorSpeed
import time

class MotorControlServer(Node):
    def __init__(self):
        super().__init__('motor_control_server')

        # Create service
        self.srv = self.create_service(
            SetMotorSpeed,
            'set_motor_speed',
            self.set_speed_callback
        )

        # Simulated motor state
        self.motor_speeds = {
            'left_wheel': 0.0,
            'right_wheel': 0.0,
            'arm_joint_1': 0.0
        }

        self.get_logger().info('Motor control service ready')

    def set_speed_callback(self, request, response):
        """
        Handle motor speed requests
        """
        motor_name = request.motor_name
        requested_speed = request.speed_rpm

        self.get_logger().info(
            f'Request: Set {motor_name} to {requested_speed} RPM'
        )

        # Validate motor name
        if motor_name not in self.motor_speeds:
            response.success = False
            response.error_message = f'Unknown motor: {motor_name}'
            response.actual_speed = 0.0
            self.get_logger().error(response.error_message)
            return response

        # Validate speed range
        if abs(requested_speed) > 100.0:
            response.success = False
            response.error_message = 'Speed must be between -100 and 100 RPM'
            response.actual_speed = self.motor_speeds[motor_name]
            return response

        # Simulate motor actuation delay
        time.sleep(0.1)

        # Set motor speed
        self.motor_speeds[motor_name] = requested_speed

        response.success = True
        response.error_message = ''
        response.actual_speed = requested_speed

        self.get_logger().info(
            f'Success: {motor_name} set to {requested_speed} RPM'
        )

        return response

def main(args=None):
    rclpy.init(args=args)
    server = MotorControlServer()
    rclpy.spin(server)
    server.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### Implementing a Service Client

Service clients send requests and wait for responses.

**Example: Synchronous client (blocking)**

```python
import rclpy
from rclpy.node import Node
from robot_interfaces.srv import SetMotorSpeed
import sys

class MotorControlClient(Node):
    def __init__(self):
        super().__init__('motor_control_client')

        # Create client
        self.client = self.create_client(SetMotorSpeed, 'set_motor_speed')

        # Wait for service to be available
        while not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Service not available, waiting...')

        self.get_logger().info('Motor control client ready')

    def send_request_sync(self, motor_name, speed):
        """
        Send synchronous request (blocks until response)
        """
        request = SetMotorSpeed.Request()
        request.motor_name = motor_name
        request.speed_rpm = speed

        self.get_logger().info(f'Sending request: {motor_name} @ {speed} RPM')

        # Call service (blocks)
        future = self.client.call_async(request)
        rclpy.spin_until_future_complete(self, future)

        if future.result() is not None:
            response = future.result()
            if response.success:
                self.get_logger().info(
                    f'Success! Actual speed: {response.actual_speed} RPM'
                )
            else:
                self.get_logger().error(
                    f'Failed: {response.error_message}'
                )
            return response
        else:
            self.get_logger().error('Service call failed')
            return None

def main(args=None):
    rclpy.init(args=args)
    client = MotorControlClient()

    # Send request
    if len(sys.argv) >= 3:
        motor = sys.argv[1]
        speed = float(sys.argv[2])
        client.send_request_sync(motor, speed)
    else:
        print('Usage: ros2 run pkg motor_client <motor_name> <speed_rpm>')

    client.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

**Running the service**:
```bash
# Terminal 1: Start server
ros2 run robot_control motor_server

# Terminal 2: Call service
ros2 run robot_control motor_client left_wheel 50.0

# Or use command line
ros2 service call /set_motor_speed robot_interfaces/srv/SetMotorSpeed \
  "{motor_name: 'left_wheel', speed_rpm: 50.0}"
```

### Asynchronous Service Clients

For non-blocking service calls in event-driven systems:

```python
class AsyncMotorClient(Node):
    def __init__(self):
        super().__init__('async_motor_client')
        self.client = self.create_client(SetMotorSpeed, 'set_motor_speed')

    def send_request_async(self, motor_name, speed):
        """
        Send asynchronous request (non-blocking)
        """
        request = SetMotorSpeed.Request()
        request.motor_name = motor_name
        request.speed_rpm = speed

        # Async call
        future = self.client.call_async(request)
        future.add_done_callback(self.response_callback)

    def response_callback(self, future):
        """
        Called when response arrives
        """
        try:
            response = future.result()
            if response.success:
                self.get_logger().info(f'Motor set successfully')
            else:
                self.get_logger().error(f'Failed: {response.error_message}')
        except Exception as e:
            self.get_logger().error(f'Service call failed: {e}')
```

## Actions: Long-Running Goal-Oriented Tasks

### When to Use Actions

Actions are designed for:
- **Navigation**: "Drive to waypoint (x, y, theta)" – Takes seconds, provides progress updates
- **Manipulation**: "Pick up object at pose P" – Multi-step operation with feedback
- **Trajectory execution**: "Follow this joint trajectory" – Reports completion percentage
- **Scanning**: "Scan room and build map" – Long operation with periodic status

**Action advantages over services**:
- **Feedback**: Periodic progress updates during execution
- **Cancellation**: Client can cancel goal mid-execution
- **Result**: Final outcome with detailed status
- **Preemption**: New goals can override current goal

### Action Definition Format

Actions use `.action` files with goal, result, and feedback sections:

**example_interfaces/action/Fibonacci.action**:
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

**Custom action for navigation**:

**robot_interfaces/action/NavigateToPosition.action**:
```
# Goal
geometry_msgs/PoseStamped target_pose
float64 speed_limit
---
# Result
bool success
string message
float64 final_distance_error
float64 elapsed_time
---
# Feedback
geometry_msgs/PoseStamped current_pose
float64 distance_remaining
float64 estimated_time_remaining
int32 progress_percentage
```

### Implementing an Action Server

Action servers manage goal execution with feedback.

**Example: Fibonacci action server with cancellation**

```python
import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from example_interfaces.action import Fibonacci
import time

class FibonacciActionServer(Node):
    def __init__(self):
        super().__init__('fibonacci_action_server')

        self._action_server = ActionServer(
            self,
            Fibonacci,
            'fibonacci',
            execute_callback=self.execute_callback,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback
        )

        self.get_logger().info('Fibonacci action server started')

    def goal_callback(self, goal_request):
        """
        Accept or reject incoming goals
        """
        if goal_request.order < 0:
            self.get_logger().warn('Rejecting negative Fibonacci order')
            return GoalResponse.REJECT

        self.get_logger().info(f'Accepting goal: Fibonacci({goal_request.order})')
        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle):
        """
        Handle cancellation requests
        """
        self.get_logger().info('Received cancel request')
        return CancelResponse.ACCEPT

    async def execute_callback(self, goal_handle):
        """
        Execute the Fibonacci sequence
        """
        self.get_logger().info('Executing goal...')

        # Get goal parameters
        order = goal_handle.request.order

        # Initialize feedback
        feedback_msg = Fibonacci.Feedback()
        feedback_msg.partial_sequence = [0, 1]

        # Compute Fibonacci sequence
        for i in range(1, order):
            # Check if goal was cancelled
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                self.get_logger().info('Goal canceled')
                return Fibonacci.Result()

            # Compute next Fibonacci number
            next_num = feedback_msg.partial_sequence[i] + \
                       feedback_msg.partial_sequence[i - 1]
            feedback_msg.partial_sequence.append(next_num)

            # Publish feedback
            self.get_logger().info(f'Feedback: {feedback_msg.partial_sequence}')
            goal_handle.publish_feedback(feedback_msg)

            # Simulate computation time
            time.sleep(0.5)

        # Mark goal as succeeded
        goal_handle.succeed()

        # Prepare result
        result = Fibonacci.Result()
        result.sequence = feedback_msg.partial_sequence

        self.get_logger().info(f'Goal succeeded! Result: {result.sequence}')
        return result

def main(args=None):
    rclpy.init(args=args)
    server = FibonacciActionServer()
    rclpy.spin(server)
    server.destroy_node()
    rclpy.shutdown()
```

### Implementing an Action Client

Action clients send goals, monitor feedback, and retrieve results.

**Example: Full-featured action client**

```python
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from example_interfaces.action import Fibonacci

class FibonacciActionClient(Node):
    def __init__(self):
        super().__init__('fibonacci_action_client')

        self._action_client = ActionClient(
            self,
            Fibonacci,
            'fibonacci'
        )

        self.get_logger().info('Fibonacci action client started')

    def send_goal(self, order):
        """
        Send goal to action server
        """
        goal_msg = Fibonacci.Goal()
        goal_msg.order = order

        self.get_logger().info(f'Sending goal: Fibonacci({order})')

        # Wait for server
        self._action_client.wait_for_server()

        # Send goal with callbacks
        self._send_goal_future = self._action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback
        )

        self._send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        """
        Called when server accepts/rejects goal
        """
        goal_handle = future.result()

        if not goal_handle.accepted:
            self.get_logger().error('Goal rejected by server')
            return

        self.get_logger().info('Goal accepted by server')

        # Get result
        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)

    def feedback_callback(self, feedback_msg):
        """
        Called periodically with feedback
        """
        feedback = feedback_msg.feedback
        self.get_logger().info(f'Feedback: {feedback.partial_sequence}')

    def get_result_callback(self, future):
        """
        Called when action completes
        """
        result = future.result().result
        status = future.result().status

        if status == 4:  # SUCCEEDED
            self.get_logger().info(f'Goal succeeded! Result: {result.sequence}')
        elif status == 5:  # CANCELED
            self.get_logger().warn('Goal was canceled')
        else:
            self.get_logger().error(f'Goal failed with status: {status}')

def main(args=None):
    rclpy.init(args=args)
    client = FibonacciActionClient()

    # Send goal
    client.send_goal(10)

    # Spin to process callbacks
    rclpy.spin(client)

    client.destroy_node()
    rclpy.shutdown()
```

**Canceling a goal**:
```python
# In action client
def cancel_goal(self):
    self.get_logger().info('Canceling goal...')
    cancel_future = self._goal_handle.cancel_goal_async()
    cancel_future.add_done_callback(self.cancel_done_callback)

def cancel_done_callback(self, future):
    cancel_response = future.result()
    if cancel_response.goals_canceling:
        self.get_logger().info('Goal successfully canceled')
```

## Real-World Use Cases

### Use Case 1: Autonomous Navigation

**Action**: NavigateToGoal
```python
# Goal
target_x: 5.0
target_y: 3.0
target_theta: 1.57

# Feedback (every 0.5s)
current_x: 2.3
current_y: 1.5
distance_remaining: 3.1
progress: 35%`

# Result
success: true
final_error: 0.02 meters
time_elapsed: 12.3 seconds
```

### Use Case 2: Object Grasping

**Action**: PickAndPlace
```python
# Goal
object_id: "red_cube"
place_position: [0.5, 0.3, 0.1]

# Feedback
current_phase: "approaching"  # approaching → grasping → lifting → moving → placing
progress: 60%`

# Result
success: true
grasp_force: 15.2 N
execution_time: 8.5 s
```

### Use Case 3: Battery Management (Service)

**Service**: GetBatteryStatus
```python
# Request
include_cell_voltages: true

# Response
battery_percentage: 67.5
voltage: 24.3 V
current: -2.1 A (discharging)
estimated_runtime: 3600 seconds
cell_voltages: [4.05, 4.06, 4.04, 4.07, 4.05, 4.06] V
status: "healthy"
```

## Comparison: Topics vs Services vs Actions

| Feature | Topics | Services | Actions |
|---------|--------|----------|---------|
| **Pattern** | Pub-Sub | Request-Response | Goal-Feedback-Result |
| **Communication** | Asynchronous | Synchronous | Asynchronous |
| **Blocking** | No | Yes (client) | No |
| **Feedback** | N/A | N/A | Yes (periodic) |
| **Cancellation** | N/A | N/A | Yes |
| **Use Case** | Sensor streams | Quick queries | Long tasks |
| **Frequency** | High (> 10 Hz) | Low (< 10 Hz) | One-shot |
| **Many-to-many** | Yes | No (1-to-1) | No (1-to-1) |

## Best Practices

### Service Design

**1. Keep services fast (< 1 second)**
```python
# Good: Quick computation
def get_current_position(self, request, response):
    response.x = self.current_x
    response.y = self.current_y
    return response

# Bad: Blocking I/O in service
def capture_image(self, request, response):
    image = self.camera.read()  # Could take 0.5s
    response.image = image
    return response  # Use action instead
```

**2. Return detailed error messages**
```python
if not self.is_motor_calibrated(motor_name):
    response.success = False
    response.error_message = \
        f"Motor '{motor_name}' not calibrated. Run calibration service first."
    response.error_code = ErrorCodes.NOT_CALIBRATED
    return response
```

**3. Validate inputs**
```python
# Check ranges
if speed < MIN_SPEED or speed > MAX_SPEED:
    response.success = False
    response.error_message = f"Speed {speed} out of range [{MIN_SPEED}, {MAX_SPEED}]"
    return response
```

### Action Design

**1. Provide meaningful feedback**
```python
# Good: Detailed progress
feedback.current_phase = "lifting_object"
feedback.distance_to_target = 0.15
feedback.estimated_time = 3.2
feedback.progress_percentage = 75

# Bad: Minimal feedback
feedback.progress = 75
```

**2. Handle cancellation gracefully**
```python
async def execute_callback(self, goal_handle):
    for i in range(100):
        if goal_handle.is_cancel_requested:
            # Stop motors safely
            self.stop_all_motors()

            # Return to safe position
            self.return_to_home()

            goal_handle.canceled()
            return Result()
```

**3. Set appropriate timeouts**
```python
# In action client
self._action_client.wait_for_server(timeout_sec=5.0)

# In action server
goal_handle.set_executing()
start_time = time.time()
timeout = 60.0  # 1 minute max

while not done:
    if time.time() - start_time > timeout:
        goal_handle.abort()
        return Result(success=False, message="Timeout exceeded")
```

## Summary

Services and actions are essential for structured communication in ROS 2 robotic systems. Key takeaways:

- **Services** provide synchronous request-response for quick operations (configuration, queries)
- **Actions** enable long-running, cancelable tasks with feedback (navigation, manipulation)
- **Service servers** validate inputs, return detailed errors, and execute quickly
- **Action servers** provide feedback, handle cancellation, and support preemption
- **Choose wisely**: Topics for streams, Services for queries, Actions for goals

In the next chapter, we'll explore TF2 coordinate transforms—the mathematical foundation for spatial reasoning in robotics.

---

**Key Takeaways**:
- Services are blocking, one-to-one request-response for fast operations
- Actions are non-blocking, goal-oriented with feedback for long tasks
- Service definitions use `.srv` files (request --- response)
- Action definitions use `.action` files (goal --- result --- feedback)
- Always validate inputs and provide detailed error messages
- Handle cancellation gracefully in action servers
- Use appropriate timeouts to prevent indefinite blocking
