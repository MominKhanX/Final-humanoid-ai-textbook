# Chapter 10: Unity Robotics Integration for Digital Twins

## Introduction to Unity for Robotics

While Gazebo excels at physics-accurate simulation, **Unity** offers complementary strengths: photorealistic rendering, VR/AR capabilities, and massive performance scaling for synthetic data generation. Unity's game engine heritage enables rendering 1000+ camera frames per second on GPUs—critical for training vision-based deep learning models.

**Unity Robotics Hub** bridges the gap between Unity's graphics prowess and ROS 2's robotics ecosystem, enabling:
- **Photorealistic sensor data** for computer vision (camera, depth, semantic segmentation)
- **Synthetic dataset generation** at scale (millions of annotated images for perception training)
- **VR/AR teleoperation** (control real robots with Oculus/HoloLens)
- **Reinforcement learning** (Unity ML-Agents + ROS 2 for sim-to-real transfer)
- **Digital twin visualization** (real-time 3D dashboards for robot fleets)

This chapter explores Unity's architecture for robotics, ROS 2 integration via TCP connectors, URDF import workflows, and practical examples of humanoid simulation with photorealistic sensors.

## Why Unity for Robotics?

### Unity vs Gazebo: Complementary Tools

| Feature | Gazebo (Ignition) | Unity |
|---------|-------------------|-------|
| **Physics Accuracy** | Excellent (ODE, DART) | Good (PhysX, ArticulationBody) |
| **Rendering Speed** | Moderate (60 FPS typical) | Excellent (1000+ FPS with GPU) |
| **Photorealism** | Basic (OGRE shaders) | Excellent (HDRP, ray tracing) |
| **Sensor Simulation** | Accurate (noise models) | Fast (GPU-accelerated) |
| **VR/AR Support** | None | Native (Oculus, HoloLens) |
| **Learning Curve** | Steep (robotics-focused) | Moderate (game dev background) |
| **License** | Open-source (Apache 2.0) | Free for revenue under $100k/year |

**Use Gazebo for**: Control algorithm validation, physics-critical tasks (contact dynamics, bipedal walking)
**Use Unity for**: Vision model training, synthetic data, VR/AR, digital twins, marketing demos

### Real-World Unity Robotics Applications

**1. Waymo (Autonomous Vehicles)**:
- Generate millions of synthetic driving scenarios (pedestrians, weather, traffic)
- Train perception models on edge cases impossible to capture in real data

**2. Boston Dynamics (Spot Manipulation)**:
- VR teleoperation for construction site inspection
- Photorealistic previsualization for customer demos

**3. Amazon Robotics (Warehouse Automation)**:
- Simulate 1000+ warehouse robots in parallel
- Test fleet coordination algorithms before deployment

## Unity Robotics Hub Architecture

### Core Components

```
┌─────────────────────────────────────────────────────┐
│                    Unity Editor                      │
│  ┌──────────────────────────────────────────────┐   │
│  │  Unity Scene (Simulation Environment)        │   │
│  │   ├─ Robot GameObjects (URDF imported)       │   │
│  │   ├─ Sensors (Camera, Depth, LiDAR)          │   │
│  │   ├─ ArticulationBody (Physics)              │   │
│  │   └─ ROS Communication Scripts               │   │
│  └──────────────────────────────────────────────┘   │
│                       ↓                              │
│  ┌──────────────────────────────────────────────┐   │
│  │  ROS-TCP-Connector (Unity Package)           │   │
│  │   - Serializes ROS messages to JSON          │   │
│  │   - Publishes/Subscribes to ROS topics       │   │
│  └──────────────────────────────────────────────┘   │
└───────────────────────┬─────────────────────────────┘
                        │ TCP Socket (Port 10000)
                        ↓
┌─────────────────────────────────────────────────────┐
│                  ROS 2 Workspace                     │
│  ┌──────────────────────────────────────────────┐   │
│  │  ROS-TCP-Endpoint (Python Node)              │   │
│  │   - Bridges Unity TCP ↔ ROS 2 DDS topics    │   │
│  │   - Handles message type conversion          │   │
│  └──────────────────────────────────────────────┘   │
│                       ↓                              │
│  ┌──────────────────────────────────────────────┐   │
│  │  ROS 2 Nodes (Planning, Control, Perception)│   │
│  └──────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

**ROS-TCP-Connector** (Unity side):
- Unity C# package for ROS message serialization
- Publishes Unity sensor data to ROS 2
- Subscribes to ROS 2 control commands

**ROS-TCP-Endpoint** (ROS 2 side):
- Python node that bridges TCP socket to DDS topics
- Converts JSON messages to ROS 2 message types

**URDF Importer**:
- Converts ROS URDF files to Unity GameObjects
- Maps joints to ArticulationBody components
- Imports meshes and materials

## Setting Up Unity for ROS 2

### Installation Steps

**1. Install Unity Hub and Unity Editor**:
```bash
# Download Unity Hub from https://unity.com/download
# Install Unity 2021.3 LTS (Long-Term Support recommended)
```

**2. Create New Unity Project**:
- Template: "3D Core" or "3D URP" (Universal Render Pipeline)
- Name: `HumanoidRoboticsSimulation`

**3. Install Unity Robotics Hub Packages**:

Open Unity Package Manager (Window → Package Manager):
- Click "+" → "Add package from git URL"
- Add these packages:
  ```
  https://github.com/Unity-Technologies/ROS-TCP-Connector.git?path=/com.unity.robotics.ros-tcp-connector
  https://github.com/Unity-Technologies/URDF-Importer.git?path=/com.unity.robotics.urdf-importer
  ```

**4. Install ROS 2 TCP Endpoint**:
```bash
cd ~/ros2_ws/src
git clone https://github.com/Unity-Technologies/ROS-TCP-Endpoint.git
cd ~/ros2_ws
colcon build --packages-select ros_tcp_endpoint
source install/setup.bash
```

### Configuring ROS Connection

**Unity side** (Robotics → ROS Settings):
- **ROS IP Address**: `127.0.0.1` (localhost, or remote machine IP)
- **ROS Port**: `10000`
- **Protocol**: ROS2

**ROS 2 side**:
```bash
ros2 run ros_tcp_endpoint default_server_endpoint --ros-args -p ROS_IP:=0.0.0.0
```

**Verify connection**:
- Unity Console should show: "Connected to ROS on 127.0.0.1:10000"

## Importing URDF into Unity

### Using URDF Importer

**1. Prepare URDF file**:
- Ensure all mesh file paths are correct (`.dae`, `.stl`, `.obj`)
- Unity prefers Collada (`.dae`) for materials

**2. Import URDF**:
- In Unity: Assets → Import Robot from URDF
- Select URDF file (e.g., `humanoid.urdf`)
- Choose import settings:
  - **Axis Type**: Y-Axis Up (Unity convention)
  - **Mesh Decomposer**: VHACD (for collision meshes)

**3. Result**:
- GameObject hierarchy created matching URDF links
- Each joint becomes an ArticulationBody component

**Example URDF import structure**:
```
humanoid (root)
├─ base_link (ArticulationBody: Fixed)
├─ torso_link (ArticulationBody: Fixed to base_link)
├─ left_hip_link (ArticulationBody: Revolute joint)
│  └─ left_thigh_link
│     └─ left_knee_link (Revolute)
│        └─ left_shin_link
│           └─ left_ankle_link (Revolute)
│              └─ left_foot_link
└─ ... (right leg, arms, head)
```

### ArticulationBody Physics

Unity's **ArticulationBody** is optimized for robotic chains (superior to Rigidbody for multi-joint robots):

**Key properties**:
- **Joint Type**: Revolute, Prismatic, Spherical, Fixed
- **Anchor**: Joint position relative to parent
- **Axis**: Joint rotation/translation axis
- **X/YZ Drive**: PD controller gains for position/velocity control

**Example ArticulationBody configuration** (knee joint):
```csharp
ArticulationBody knee = leftKnee.GetComponent<ArticulationBody>();

// Joint properties
knee.jointType = ArticulationJointType.RevoluteJoint;
knee.anchorPosition = new Vector3(0, -0.5f, 0);  // 0.5m below parent
knee.anchorRotation = Quaternion.Euler(0, 90, 0);  // Pitch axis

// Joint limits
knee.xDrive = new ArticulationDrive
{
    lowerLimit = 0,          // Minimum angle (degrees)
    upperLimit = 140,        // Maximum bend (degrees)
    stiffness = 10000,       // Position control gain
    damping = 100,           // Velocity control gain
    forceLimit = 150         // Max torque (N·m)
};
```

## Publishing and Subscribing with ROS 2

### Publishing Sensor Data from Unity

**Camera image publisher** (C# script):

```csharp
using UnityEngine;
using Unity.Robotics.ROSTCPConnector;
using RosMessageTypes.Sensor;

public class CameraPublisher : MonoBehaviour
{
    ROSConnection ros;
    public string topicName = "/camera/image_raw";
    public Camera sensorCamera;

    public float publishRate = 30f;  // Hz
    private float timeSinceLastPublish;

    void Start()
    {
        ros = ROSConnection.GetOrCreateInstance();
        ros.RegisterPublisher<ImageMsg>(topicName);
    }

    void Update()
    {
        timeSinceLastPublish += Time.deltaTime;

        if (timeSinceLastPublish < 1f / publishRate)
            return;

        timeSinceLastPublish = 0;

        // Capture camera frame
        RenderTexture rt = new RenderTexture(640, 480, 24);
        sensorCamera.targetTexture = rt;
        sensorCamera.Render();

        Texture2D image = new Texture2D(640, 480, TextureFormat.RGB24, false);
        RenderTexture.active = rt;
        image.ReadPixels(new Rect(0, 0, 640, 480), 0, 0);
        image.Apply();

        // Convert to ROS message
        ImageMsg msg = new ImageMsg
        {
            header = new RosMessageTypes.Std.HeaderMsg
            {
                stamp = new RosMessageTypes.BuiltinInterfaces.TimeMsg
                {
                    sec = (int)Time.time,
                    nanosec = (uint)((Time.time % 1) * 1e9)
                },
                frame_id = "camera_frame"
            },
            height = 480,
            width = 640,
            encoding = "rgb8",
            is_bigendian = 0,
            step = 640 * 3,
            data = image.GetRawTextureData()
        };

        ros.Publish(topicName, msg);

        // Cleanup
        sensorCamera.targetTexture = null;
        RenderTexture.active = null;
        Destroy(rt);
    }
}
```

**Attach to camera GameObject** in Unity Inspector.

### Subscribing to Joint Commands

**Joint controller subscriber** (C# script):

```csharp
using UnityEngine;
using Unity.Robotics.ROSTCPConnector;
using RosMessageTypes.Sensor;

public class JointController : MonoBehaviour
{
    ROSConnection ros;
    public string topicName = "/joint_commands";
    public ArticulationBody[] joints;  // Assign in Inspector

    void Start()
    {
        ros = ROSConnection.GetOrCreateInstance();
        ros.Subscribe<JointStateMsg>(topicName, ApplyJointCommands);
    }

    void ApplyJointCommands(JointStateMsg msg)
    {
        for (int i = 0; i < msg.position.Length && i < joints.Length; i++)
        {
            // Set target position (radians to degrees)
            var drive = joints[i].xDrive;
            drive.target = (float)msg.position[i] * Mathf.Rad2Deg;
            joints[i].xDrive = drive;
        }
    }
}
```

**ROS 2 side** (publish commands):
```python
from sensor_msgs.msg import JointState

joint_pub = node.create_publisher(JointState, '/joint_commands', 10)

msg = JointState()
msg.name = ['left_hip', 'left_knee', 'left_ankle']
msg.position = [0.1, -0.5, 0.2]  # Radians

joint_pub.publish(msg)
```

## Unity ML-Agents for Reinforcement Learning

### Training Humanoid Walking with PPO

**Unity ML-Agents** enables training RL policies directly in Unity:

**1. Install ML-Agents Package**:
```bash
pip install mlagents
# In Unity Package Manager: com.unity.ml-agents
```

**2. Create Agent Script** (Humanoid walker):

```csharp
using UnityEngine;
using Unity.MLAgents;
using Unity.MLAgents.Actuators;
using Unity.MLAgents.Sensors;

public class HumanoidWalker : Agent
{
    public ArticulationBody[] joints;  // Hip, knee, ankle joints
    public Transform target;  // Goal position

    public override void OnEpisodeBegin()
    {
        // Reset robot to standing position
        transform.position = new Vector3(0, 1, 0);
        transform.rotation = Quaternion.identity;

        // Randomize target location
        target.position = new Vector3(Random.Range(-5f, 5f), 0, Random.Range(-5f, 5f));
    }

    public override void CollectObservations(VectorSensor sensor)
    {
        // Observe: target direction, joint angles, joint velocities, orientation
        sensor.AddObservation(target.position - transform.position);  // 3 values

        foreach (var joint in joints)
        {
            sensor.AddObservation(joint.jointPosition[0]);  // Current angle
            sensor.AddObservation(joint.jointVelocity[0]);  // Angular velocity
        }

        sensor.AddObservation(transform.up);  // Body orientation (upright?)
    }

    public override void OnActionReceived(ActionBuffers actions)
    {
        // Apply joint torques (continuous actions)
        for (int i = 0; i < joints.Length; i++)
        {
            float torque = actions.ContinuousActions[i] * 150f;  // Scale to N·m
            joints[i].AddRelativeTorque(new Vector3(torque, 0, 0));
        }

        // Rewards
        float distanceToTarget = Vector3.Distance(transform.position, target.position);
        float velocityTowardTarget = Vector3.Dot(
            transform.forward,
            (target.position - transform.position).normalized
        );

        AddReward(-0.001f * distanceToTarget);  // Closer to target = better
        AddReward(0.01f * velocityTowardTarget);  // Moving toward target = better

        // Penalties
        if (transform.position.y < 0.5f)  // Fell down
        {
            AddReward(-10f);
            EndEpisode();
        }

        if (distanceToTarget < 1.0f)  // Reached target
        {
            AddReward(10f);
            EndEpisode();
        }
    }

    public override void Heuristic(in ActionBuffers actionsOut)
    {
        // Manual control for testing (keyboard input)
        var continuousActions = actionsOut.ContinuousActions;
        continuousActions[0] = Input.GetAxis("Horizontal");  // Hip left/right
        continuousActions[1] = Input.GetKey(KeyCode.Space) ? 1f : 0f;  // Knee bend
    }
}
```

**3. Train with PPO** (Proximal Policy Optimization):
```bash
mlagents-learn config/humanoid_walker.yaml --run-id=humanoid_v1
# Press Play in Unity Editor to start training
```

**Training config** (`humanoid_walker.yaml`):
```yaml
behaviors:
  HumanoidWalker:
    trainer_type: ppo
    hyperparameters:
      batch_size: 2048
      buffer_size: 20480
      learning_rate: 0.0003
      beta: 0.005
      epsilon: 0.2
      lambd: 0.95
      num_epoch: 3
    network_settings:
      normalize: true
      hidden_units: 512
      num_layers: 3
    reward_signals:
      extrinsic:
        gamma: 0.99
        strength: 1.0
    max_steps: 10000000
```

**Result**: After ~5M steps (2-3 hours on GPU), humanoid learns stable bipedal walking.

## Photorealistic Sensor Simulation

### High-Definition Render Pipeline (HDRP)

Enable photorealistic rendering:

**1. Convert project to HDRP**:
- Window → Rendering → Render Pipeline Converter
- Select "Built-in to URP/HDRP" → Convert

**2. Add Post-Processing**:
- Create Volume GameObject
- Add "Exposure", "Bloom", "Motion Blur" overrides
- Realistic lens effects (depth of field, chromatic aberration)

**3. Realistic Lighting**:
- Use HDRI sky (Assets → Import → HDRI)
- Add Directional Light (sun), Area Lights (indoor)
- Enable real-time ray tracing (requires RTX GPU)

### Semantic Segmentation Camera

For vision training, generate pixel-perfect object labels:

```csharp
using UnityEngine;
using UnityEngine.Rendering;

public class SemanticSegmentation : MonoBehaviour
{
    public Camera mainCamera;
    public Shader replacementShader;  // Flat color shader

    void Start()
    {
        // Assign unique colors to each object category
        GameObject[] obstacles = GameObject.FindGameObjectsWithTag("Obstacle");
        foreach (var obj in obstacles)
        {
            obj.GetComponent<Renderer>().material.SetColor("_Color", Color.red);
        }

        GameObject[] goals = GameObject.FindGameObjectsWithTag("Goal");
        foreach (var obj in goals)
        {
            obj.GetComponent<Renderer>().material.SetColor("_Color", Color.green);
        }
    }

    void Update()
    {
        mainCamera.RenderWithShader(replacementShader, "RenderType");

        // Capture and publish segmentation mask to ROS 2
        // (Similar to CameraPublisher above)
    }
}
```

**Use case**: Train perception networks (YOLO, Mask R-CNN) with perfect ground-truth labels.

## Summary

Unity extends the digital twin beyond physics simulation into photorealistic rendering, VR/AR, and large-scale synthetic data generation. Key takeaways:

- **Unity complements Gazebo**: Use Unity for vision tasks, Gazebo for control validation
- **ROS-TCP-Connector**: Bridges Unity ↔ ROS 2 via TCP socket
- **URDF Importer**: Converts ROS robots to Unity GameObjects with ArticulationBody
- **ArticulationBody**: Superior physics for multi-joint robots (vs Rigidbody)
- **ML-Agents**: Train RL policies in Unity, deploy to real robots
- **HDRP**: Photorealistic rendering for synthetic datasets

In the next chapter, we'll explore **NVIDIA Isaac Sim**, combining Unity's graphics with Gazebo's physics via Omniverse.

---

**Key Takeaways**:
- Unity excels at photorealistic rendering (1000+ FPS) for vision model training
- ROS-TCP-Connector enables seamless Unity ↔ ROS 2 communication
- URDF Importer converts ROS robot descriptions to Unity GameObjects
- ArticulationBody provides optimized physics for robotic chains
- Unity ML-Agents trains RL policies directly in simulation
- Semantic segmentation cameras generate perfect training labels for perception
