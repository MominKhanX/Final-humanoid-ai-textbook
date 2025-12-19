# Chapter 11: Sim-to-Real Transfer for Humanoid Robotics

## Introduction to the Reality Gap

The ultimate test of any simulation is whether algorithms trained virtually work on real hardware. **Sim-to-real transfer** is the process of deploying policies, controllers, and perception models learned in simulation to physical robots—a challenge plagued by the **reality gap**: the inevitable mismatch between simulated and real-world dynamics, sensors, and environments.

**The Reality Gap** arises from:
- **Unmodeled physics**: Friction varies with temperature, motors have backlash, cables create drag
- **Sensor imperfections**: Real cameras have motion blur, IMUs drift, LiDAR has multi-path reflections
- **Timing differences**: Simulation runs in discrete timesteps; reality is continuous
- **Environmental variations**: Lighting changes, floor texture varies, wind affects balance

This chapter explores strategies to bridge the reality gap: **domain randomization**, **system identification**, **residual learning**, and **progressive transfer**—techniques proven by Boston Dynamics, OpenAI, and DeepMind to enable zero-shot or few-shot deployment from simulation to real robots.

## Understanding the Reality Gap

### Sources of Simulation Inaccuracy

**1. Physics Approximations**:
- **Rigid body assumption**: Real links flex under load (carbon fiber arms, plastic joints)
- **Contact models**: Gazebo uses simplified Coulomb friction; reality has stick-slip, material deformation
- **Numerical errors**: ODE timestep = 1ms`; reality evolves continuously

**Example**: A simulated humanoid's foot doesn't slip on a polished floor (μ = 0.1), but the real robot's rubber sole grips (μ = 0.8).

**2. Actuator Dynamics**:
- **Simulation**: Instant torque application (ideal PID controller)
- **Reality**: Motors have current limits, back-EMF, thermal shutoff, gear backlash

**Example**: Commanding 150 N·m knee torque works in Gazebo but saturates the real motor at 100 N·m, causing falls.

**3. Sensor Noise and Delays**:
- **Simulation**: Perfect state observation unless manually added noise
- **Reality**: IMU drift (0.1°/s), camera motion blur (fast movements), LiDAR multipath errors (glass, mirrors)

**Example**: Simulated balance controller uses perfect IMU orientation; real IMU drifts 5° in 30 seconds, destabilizing the robot.

**4. Environmental Variability**:
- **Simulation**: Uniform lighting, flat ground, static obstacles
- **Reality**: Shadows confuse vision, uneven terrain, dynamic pedestrians

### Quantifying the Reality Gap

**Success Rate Degradation**:
- Algorithm achieves 95%` task success in simulation
- Deploys to hardware: drops to 40%` success (55%` reality gap)
- Goal: Reduce gap to under 10%`

**Example metrics**:
- **Navigation**: Path completion rate (simulation 98%` → real 60%`)
- **Grasping**: Pick success rate (simulation 90%` → real 50%`)
- **Walking**: Steps before fall (simulation 1000 → real 20)

## Strategy 1: Domain Randomization

### Core Idea

Train policies on a **distribution of simulated environments** so wide that reality is just another sample. By randomizing physics parameters, sensor noise, and visual properties, the policy learns robust strategies that generalize to the real world.

**OpenAI's Dactyl (2018)**: Trained a humanoid hand to solve a Rubik's Cube using domain randomization—achieving zero-shot transfer to hardware despite training entirely in simulation.

### What to Randomize

**Physics Parameters**:
- **Masses**: ±20%` around nominal (10 kg torso → 8-12 kg)
- **Friction coefficients**: μ ∈ [0.5, 1.2] (rubber sole on various surfaces)
- **Joint damping**: ±50%` (model motor wear)
- **Timestep**: Vary simulation dt ∈ [0.0005s, 0.002s] (numerical uncertainty)

**Sensor Noise**:
- **IMU**: Add Gaussian noise σ_gyro ∈ [0.001, 0.01] rad/s, σ_accel ∈ [0.01, 0.1] m/s²
- **Camera**: Brightness ±30%`, motion blur radius ∈ [0, 5 pixels], lens distortion
- **LiDAR**: Range noise σ_range ∈ [0.01, 0.05] m, random dropouts (1-5%`)

**Visual Appearance**:
- **Lighting**: Directional light intensity ∈ [0.5, 1.5], HDRI sky rotation
- **Textures**: Randomize floor/wall materials (wood, tile, carpet)
- **Object colors**: Hue shift ±30°, saturation ×[0.5, 1.5]

**Actuation Delays**:
- **Motor lag**: Add 5-20ms` delay between command and torque application
- **Communication latency**: 10-50ms` network delay for remote control

### Implementation in Gazebo/Unity

**Gazebo SDF with randomized friction** (Python launch file):

```python
import random
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_randomized_world():
    friction_mu = random.uniform(0.5, 1.2)  # Random friction

    sdf_content = f"""
    <sdf version="1.8">
      <world name="random_world">
        <physics name="ode_physics" type="ode">
          <max_step_size>0.001</max_step_size>
        </physics>

        <model name="ground_plane">
          <static>true</static>
          <link name="link">
            <collision name="collision">
              <surface>
                <friction>
                  <ode>
                    <mu>{friction_mu}</mu>  <!-- Randomized! -->
                    <mu2>{friction_mu}</mu2>
                  </ode>
                </friction>
              </surface>
            </collision>
          </link>
        </model>
      </world>
    </sdf>
    """

    # Save and launch
    with open('/tmp/random_world.sdf', 'w') as f:
        f.write(sdf_content)

def generate_launch_description():
    generate_randomized_world()

    return LaunchDescription([
        Node(
            package='gazebo_ros',
            executable='gazebo',
            arguments=['/tmp/random_world.sdf']
        )
    ])
```

**Unity domain randomization** (C# script):

```csharp
using UnityEngine;

public class DomainRandomizer : MonoBehaviour
{
    public Rigidbody[] robotLinks;
    public PhysicMaterial groundMaterial;
    public Light sunLight;

    void OnEpisodeBegin()  // Reset environment for each training episode
    {
        // Randomize link masses (±20%`)
        foreach (var link in robotLinks)
        {
            float nominalMass = link.mass;
            link.mass = nominalMass * Random.Range(0.8f, 1.2f);
        }

        // Randomize ground friction
        groundMaterial.staticFriction = Random.Range(0.5f, 1.2f);
        groundMaterial.dynamicFriction = Random.Range(0.4f, 1.0f);

        // Randomize lighting (brightness and direction)
        sunLight.intensity = Random.Range(0.5f, 1.5f);
        sunLight.transform.rotation = Quaternion.Euler(
            Random.Range(30f, 70f),  // Elevation
            Random.Range(0f, 360f),  // Azimuth
            0f
        );

        // Randomize floor texture
        Renderer floorRenderer = GameObject.Find("Floor").GetComponent<Renderer>();
        floorRenderer.material.color = new Color(
            Random.Range(0.7f, 1.0f),  // Grayscale variation
            Random.Range(0.7f, 1.0f),
            Random.Range(0.7f, 1.0f)
        );
    }
}
```

### Limitations of Domain Randomization

**Overly conservative**: To cover reality, randomization ranges must be wide → policies may be suboptimal
**Compute-intensive**: Requires millions of simulation samples across diverse environments
**Hard to debug**: When transfer fails, unclear which parameter distribution was wrong

## Strategy 2: System Identification

### Core Idea

**Measure** real robot parameters precisely, then update the simulation to match hardware exactly. This "calibrated simulation" minimizes the reality gap for that specific robot.

**Approach**:
1. Run controlled experiments on real hardware
2. Record sensor data (joint positions, velocities, torques)
3. Estimate unknown parameters (friction, inertia, motor constants) via optimization
4. Update URDF/SDF with measured values

### Parameter Estimation Workflow

**Example: Estimate joint friction**

**1. Real Robot Experiment**:
```python
import rclpy
from sensor_msgs.msg import JointState

class FrictionEstimator(Node):
    def __init__(self):
        super().__init__('friction_estimator')
        self.joint_sub = self.create_subscription(
            JointState, '/joint_states', self.record_data, 10
        )
        self.data = []

    def record_data(self, msg):
        # Record: commanded torque, actual velocity
        self.data.append({
            'torque': msg.effort,  # From motor controller
            'velocity': msg.velocity  # From encoder
        })

# Run on real robot: apply constant torques, measure resulting velocities
# τ = b * ω + c (friction model: viscous damping + Coulomb friction)
```

**2. Parameter Fitting** (offline, Python):
```python
import numpy as np
from scipy.optimize import curve_fit

# Load recorded data
torques = np.array([d['torque'][0] for d in data])
velocities = np.array([d['velocity'][0] for d in data])

# Fit friction model: τ = b * ω + c
def friction_model(omega, b, c):
    return b * omega + c * np.sign(omega)

params, _ = curve_fit(friction_model, velocities, torques)
damping_b, friction_c = params

print(f"Estimated damping: {damping_b:.4f} N·m·s/rad")
print(f"Estimated Coulomb friction: {friction_c:.4f} N·m")
```

**3. Update URDF**:
```xml
<joint name="knee_joint" type="revolute">
  <axis xyz="0 1 0"/>
  <dynamics damping="0.0523" friction="0.0189"/>  <!-- Measured values! -->
</joint>
```

### System ID for Inertia Tensors

**Swing test**:
1. Suspend link from pivot, let it swing freely
2. Measure oscillation period T
3. Compute inertia: I = (m * g * L * T²) / (4π²)
   - m: mass, g: gravity, L: center of mass distance from pivot

**Result**: Replace URDF `<inertia>` with measured tensor.

### Limitations

**Robot-specific**: Parameters valid only for that hardware unit (not fleet)
**Wear over time**: Friction increases with motor wear (re-calibrate periodically)
**Laborious**: Requires careful experiments, can't measure all parameters

## Strategy 3: Residual Learning

### Core Idea

Train a base policy in simulation, then fine-tune a **residual correction policy** on real hardware to compensate for unmodeled dynamics.

**Policy decomposition**:
```
Action_real = Policy_sim(state) + Policy_residual(state)
```

- **Policy_sim**: Trained offline in simulation (millions of samples)
- **Policy_residual**: Trained online on hardware (few hundred samples) to fix errors

**Advantage**: Requires minimal real-world data (safe, fast convergence).

### Implementation with RL Fine-Tuning

**1. Train base policy in simulation** (e.g., PPO for bipedal walking):
```python
# Train in Gazebo/Unity (10M steps, 10 hours GPU)
policy_sim = PPO.load("humanoid_walk_sim.pth")
```

**2. Initialize residual policy** (small network):
```python
import torch
import torch.nn as nn

class ResidualPolicy(nn.Module):
    def __init__(self, state_dim, action_dim):
        super().__init__()
        self.fc = nn.Sequential(
            nn.Linear(state_dim, 64),
            nn.ReLU(),
            nn.Linear(64, action_dim),
            nn.Tanh()  # Residual bounded to [-1, 1]
        )

    def forward(self, state):
        return 0.1 * self.fc(state)  # Small corrections (±10%` of base action)

policy_residual = ResidualPolicy(state_dim=30, action_dim=10)
```

**3. Deploy to real robot**:
```python
def get_action(state):
    base_action = policy_sim(state)  # From simulation training
    residual_action = policy_residual(state)  # Learned on hardware
    return base_action + residual_action

# Fine-tune policy_residual with real-world rollouts (100-500 episodes)
```

**Real-World Example**: Google's robotic grasping (2018)
- Pretrained grasping policy in simulation
- Fine-tuned on 7 real robots (14,000 grasps over 4 months)
- Achieved 96%` success on novel objects

### Limitations

**Requires real robot access**: Can't be fully sim-only
**Safety critical**: Initial sim policy must be safe enough not to damage hardware during fine-tuning

## Strategy 4: Progressive Transfer

### Core Idea

Gradually increase fidelity: simple simulation → detailed simulation → reality.

**Stages**:
1. **Toy simulation** (fast, low fidelity): Prove concept (simple physics, no noise)
2. **High-fidelity simulation** (slow, realistic): Validate with randomization (DART, photorealistic sensors)
3. **Hardware-in-the-loop**: Simulate most components, use real sensors/actuators
4. **Full deployment**: Run on real robot

**Boston Dynamics Spot** development:
- Stage 1: Kinematic model (no physics) validates gait patterns
- Stage 2: Gazebo with DART, domain randomization for rough terrain
- Stage 3: Tethered robot (safety harness) tests balance recovery
- Stage 4: Untethered field tests (quarries, construction sites)

### Hardware-in-the-Loop (HIL) Testing

**Concept**: Mix simulated and real components to bridge the gap incrementally.

**Example setup**:
- **Real**: IMU sensor, motor controllers
- **Simulated**: Environment, gravity, ground contact forces

**Code**:
```python
class HIL_Simulator(Node):
    def __init__(self):
        super().__init__('hil_sim')

        # Subscribe to REAL IMU
        self.imu_sub = self.create_subscription(
            Imu, '/real_imu/data', self.imu_callback, 10
        )

        # Publish to REAL motor controllers
        self.cmd_pub = self.create_publisher(
            Float64MultiArray, '/real_motors/command', 10
        )

        # Simulate physics in Gazebo (virtual ground, gravity)
        self.gz_client = GazeboClient()

    def imu_callback(self, real_imu_msg):
        # Feed real sensor data into simulated controller
        orientation = real_imu_msg.orientation
        controller_output = self.balance_controller(orientation)

        # Send commands to real motors
        self.cmd_pub.publish(controller_output)
```

**Benefit**: Tests sensor integration and actuation without full physics risk.

## Evaluation Metrics for Sim-to-Real

**Success Rate**:
```
Success Rate = (Successful trials on real robot) / (Total trials)
```

**Goal**: Sim success - Real success < 10%`

**Zero-Shot Transfer**:
- Deploy trained policy without any real-world fine-tuning
- **Metric**: Real-world success rate on first try

**Few-Shot Transfer**:
- Fine-tune policy with K real-world episodes (K = 10-100)
- **Metric**: Success rate after K episodes

**Performance Degradation**:
```
Degradation = 1 - (Real Performance / Sim Performance)
```

**Example**: Navigation path length increases 20%` in reality → 20%` degradation

## Case Studies

### 1. OpenAI Dactyl (Rubik's Cube Solving Hand)

**Problem**: Manipulate Rubik's Cube with humanoid hand (24 DOF)

**Approach**:
- Domain randomization: 1000+ physics/visual variations
- Trained in simulation: 100 years of robot experience (parallelized)
- Zero-shot transfer to real hardware

**Result**: Solved Rubik's Cube on first real-world deployment (2019)

### 2. Boston Dynamics Atlas Backflip

**Problem**: Perform gymnastic backflip (requires precise timing, high torques)

**Approach**:
- Stage 1: Offline trajectory optimization (simulate 1000 variations)
- Stage 2: Model-predictive control in high-fidelity Gazebo
- Stage 3: Tethered tests with safety harness
- Stage 4: Untethered attempt

**Result**: Successful backflip after 6 months development, 100+ sim iterations, 20 real attempts

### 3. ANYmal Quadruped (Autonomous Hiking)

**Problem**: Navigate rocky alpine terrain (uneven ground, slippery rocks)

**Approach**:
- System identification: Measured leg inertias, joint friction on hardware
- Domain randomization: Ground height map noise, friction variations
- Progressive deployment: Flat ground → gravel → rocky trails

**Result**: 1-hour autonomous hikes, 95%` uptime (ETH Zurich, 2020)

## Practical Sim-to-Real Workflow

**Step 1: Rapid Prototyping in Sim**
- Use simple physics (ODE), test basic feasibility
- Iterate on controller design quickly (hours, not days)

**Step 2: High-Fidelity Validation**
- Switch to DART or Bullet, add domain randomization
- Train for robustness (100k-1M simulation episodes)

**Step 3: System Identification**
- Build hardware prototype, measure key parameters
- Update URDF/SDF with real values

**Step 4: Hardware-in-the-Loop Testing**
- Integrate real sensors into simulation loop
- Validate sensor fusion, actuation pipelines

**Step 5: Staged Deployment**
- Constrained environment (tether, soft floor mats)
- Gradual increase in difficulty (flat → slopes → obstacles)

**Step 6: Field Testing**
- Deploy in target environment
- Collect failure data, retrain, repeat

## Summary

Sim-to-real transfer is the bridge between algorithmic development and real-world robotics impact. Key takeaways:

- **Reality gap**: Inevitable mismatch between simulation and hardware (physics, sensors, environment)
- **Domain randomization**: Train on diverse simulated worlds → robust policies
- **System identification**: Measure real parameters → calibrated simulation
- **Residual learning**: Base policy (sim) + correction policy (real) → data-efficient transfer
- **Progressive transfer**: Incremental fidelity increases → safe deployment
- **Metrics**: Success rate, zero-shot vs few-shot, performance degradation

With these strategies, developers can leverage simulation's speed and safety while achieving reliable real-world performance—the foundation of production humanoid robotics.

---

**Key Takeaways**:
- Reality gap arises from unmodeled physics, sensor noise, and environmental variations
- Domain randomization enables zero-shot transfer by training on parameter distributions
- System identification calibrates simulation to match specific hardware
- Residual learning combines sim-trained base policy with real-world fine-tuning
- Progressive transfer (toy sim → detailed sim → HIL → hardware) minimizes deployment risk
- Successful examples: OpenAI Dactyl (Rubik's Cube), Boston Dynamics Atlas (backflip), ANYmal (hiking)
