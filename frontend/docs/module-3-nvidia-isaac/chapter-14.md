# Chapter 14: Reinforcement Learning in Isaac Sim

## Introduction to RL for Robotics

**Reinforcement Learning (RL)** enables robots to learn complex behaviors—bipedal walking, object manipulation, obstacle navigation—through trial and error in simulation. **Isaac Sim's** GPU-accelerated physics allows training 1000+ robots in parallel, achieving human-level performance in hours instead of weeks.

**Why Isaac Sim for RL?**
- **Parallel Simulation**: 100-1000 envs on single RTX GPU (vs 10-20 CPU envs)
- **Fast Physics**: PhysX 5 GPU solver (10-100× faster than ODE/DART)
- **Realistic Dynamics**: Accurate contact physics for walking/manipulation
- **Domain Randomization**: Built-in parameter variation for sim-to-real

This chapter covers RL fundamentals, Isaac Sim RL environment setup, training humanoid policies with PPO/SAC, and IsaacGymEnvs integration for massively parallel training.

## RL Fundamentals

**Agent-Environment Loop**:
1. **Agent** observes state s_t (joint positions, velocities, IMU)
2. **Agent** selects action a_t (joint torques/positions)
3. **Environment** transitions to s_\{t+1\}, returns reward r_t
4. **Goal**: Learn policy π(a|s) that maximizes cumulative reward

**Example: Humanoid Walking**:
- **State**: Joint angles (12), joint velocities (12), body orientation (4), target direction (2) → 30-dim vector
- **Action**: Joint torques (12 joints) → 12-dim continuous vector
- **Reward**: +0.01 per step alive, +velocity toward goal, -10 for falling

**Algorithms**:
- **PPO** (Proximal Policy Optimization): On-policy, stable, sample-efficient
- **SAC** (Soft Actor-Critic): Off-policy, max entropy, good for manipulation
- **TD3** (Twin Delayed DDPG): Off-policy, continuous control

## Isaac Sim RL Environment Setup

### Gym-Style Environment

**Create custom RL task** (Python):

```python
from omni.isaac.core import World
from omni.isaac.core.robots import Robot
from omni.isaac.core.utils.types import ArticulationAction
import numpy as np

class HumanoidWalkEnv:
    def __init__(self):
        # Initialize Isaac Sim world
        self.world = World(stage_units_in_meters=1.0)
        self.world.scene.add_default_ground_plane()

        # Add humanoid robot
        self.robot = self.world.scene.add(
            Robot(prim_path="/World/Humanoid", name="humanoid")
        )

        # Task parameters
        self.max_episode_steps = 1000
        self.step_count = 0
        self.target_velocity = 1.0  # m/s forward

    def reset(self):
        """Reset environment to initial state"""
        # Reset simulation
        self.world.reset()

        # Reset robot pose
        self.robot.set_world_pose(position=np.array([0, 0, 1.0]))
        self.robot.set_joint_positions(np.zeros(self.robot.num_dof))
        self.robot.set_joint_velocities(np.zeros(self.robot.num_dof))

        self.step_count = 0
        return self._get_observation()

    def step(self, action):
        """Execute action, return (obs, reward, done, info)"""
        # Apply joint torques
        self.robot.set_joint_efforts(action)

        # Step physics
        self.world.step(render=True)

        # Get new state
        obs = self._get_observation()
        reward = self._compute_reward()
        done = self._is_done()
        info = {}

        self.step_count += 1
        return obs, reward, done, info

    def _get_observation(self):
        """Get 30-dim state vector"""
        joint_pos = self.robot.get_joint_positions()  # 12
        joint_vel = self.robot.get_joint_velocities()  # 12
        orientation = self.robot.get_world_pose()[1]  # Quaternion (4)
        velocity = self.robot.get_linear_velocity()  # 3
        return np.concatenate([joint_pos, joint_vel, orientation, velocity[:2]])

    def _compute_reward(self):
        """Reward function for walking forward"""
        # Get forward velocity
        vel = self.robot.get_linear_velocity()
        forward_vel = vel[0]  # X-axis

        # Reward for moving toward target velocity
        vel_reward = -(forward_vel - self.target_velocity) ** 2

        # Penalty for falling
        height = self.robot.get_world_pose()[0][2]
        fall_penalty = -10.0 if height < 0.5 else 0.0

        # Penalty for excessive torques (energy efficiency)
        torques = self.robot.get_joint_efforts()
        torque_penalty = -0.0001 * np.sum(torques ** 2)

        # Alive bonus
        alive_bonus = 0.01

        return vel_reward + fall_penalty + torque_penalty + alive_bonus

    def _is_done(self):
        """Check termination conditions"""
        # Fall detection
        height = self.robot.get_world_pose()[0][2]
        if height < 0.5:
            return True

        # Max steps
        if self.step_count >= self.max_episode_steps:
            return True

        return False
```

### Training with Stable-Baselines3 PPO

**Install dependencies**:
```bash
pip install stable-baselines3 gym
```

**Wrap environment for Gym compatibility**:

```python
import gym
from gym import spaces

class HumanoidWalkGymEnv(gym.Env):
    def __init__(self):
        super().__init__()
        self.env = HumanoidWalkEnv()

        # Define observation/action spaces
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(30,), dtype=np.float32
        )
        self.action_space = spaces.Box(
            low=-150.0, high=150.0, shape=(12,), dtype=np.float32  # Joint torques
        )

    def reset(self):
        return self.env.reset()

    def step(self, action):
        return self.env.step(action)

    def render(self, mode='human'):
        pass  # Isaac Sim renders automatically
```

**Train with PPO**:

```python
from stable_baselines3 import PPO

# Create environment
env = HumanoidWalkGymEnv()

# Initialize PPO agent
model = PPO(
    "MlpPolicy",
    env,
    learning_rate=3e-4,
    n_steps=2048,
    batch_size=64,
    n_epochs=10,
    gamma=0.99,
    gae_lambda=0.95,
    clip_range=0.2,
    verbose=1,
    tensorboard_log="./tensorboard_logs/"
)

# Train for 1M timesteps (~10 hours on RTX 3090)
model.learn(total_timesteps=1_000_000)

# Save policy
model.save("humanoid_walk_ppo")
```

**Monitor training**:
```bash
tensorboard --logdir ./tensorboard_logs/
```

## IsaacGymEnvs: Massively Parallel RL

**IsaacGymEnvs** is NVIDIA's RL benchmark suite with 30+ tasks, supporting **1000+ parallel envs**.

### Installation

```bash
git clone https://github.com/NVIDIA-Omniverse/IsaacGymEnvs.git
cd IsaacGymEnvs
pip install -e .
```

### Training Ant Locomotion (Example)

**Run pre-built task**:
```bash
python train.py task=Ant headless=True num_envs=1024
```

**Parameters**:
- `task=Ant`: Quadruped walking task
- `headless=True`: No GUI (faster)
- `num_envs=1024`: 1024 parallel environments

**Training speed**: 100M steps in 2 hours (vs 20 hours with 10 CPU envs).

### Creating Custom IsaacGym Task

**Define task configuration** (`cfg/task/HumanoidWalk.yaml`):

```yaml
name: HumanoidWalk

physics_engine: ${..physics_engine}

env:
  numEnvs: ${resolve_default:2048,${...num_envs}}
  envSpacing: 5.0
  episodeLength: 1000
  enableDebugVis: False

  clipObservations: 5.0
  clipActions: 1.0

  controlFrequencyInv: 2  # Control every 2 physics steps

sim:
  dt: 0.0083  # 120 Hz
  substeps: 2
  physx:
    num_threads: ${...num_threads}
    solver_type: ${...solver_type}
    use_gpu: ${contains:"cuda",${....rl_device}}

task:
  randomize: True  # Domain randomization
```

**Implement task** (Python):

```python
from isaacgymenvs.tasks.base.vec_task import VecTask
import torch

class HumanoidWalkTask(VecTask):
    def __init__(self, cfg, sim_params, physics_engine, device):
        self.cfg = cfg
        self.max_episode_length = 1000

        super().__init__(
            config=self.cfg,
            sim_params=sim_params,
            physics_engine=physics_engine,
            device=device
        )

        # Define obs/action dims
        self.num_obs = 30
        self.num_actions = 12

    def create_sim(self):
        # Load humanoid URDF
        self.gym.load_asset(self.sim, asset_root, "humanoid.urdf")

    def reset_idx(self, env_ids):
        # Reset specified environments
        self.robot_pos[env_ids] = torch.tensor([0, 0, 1], device=self.device)
        self.dof_pos[env_ids] = 0
        self.dof_vel[env_ids] = 0

    def pre_physics_step(self, actions):
        # Apply actions (joint torques)
        self.gym.set_dof_actuation_force_tensor(
            self.sim, gymtorch.unwrap_tensor(actions)
        )

    def post_physics_step(self):
        # Compute observations and rewards
        self.obs_buf[:] = self.compute_observations()
        self.rew_buf[:] = self.compute_rewards()
        self.reset_buf[:] = self.check_termination()

    def compute_observations(self):
        # Stack: joint pos (12) + joint vel (12) + orientation (4) + velocity (2)
        return torch.cat([
            self.dof_pos, self.dof_vel, self.root_quats, self.root_linvels[:, :2]
        ], dim=-1)

    def compute_rewards(self):
        # Vectorized reward computation (2048 envs simultaneously)
        forward_vel = self.root_linvels[:, 0]
        height = self.root_states[:, 2]

        # Reward shaping
        vel_reward = -(forward_vel - 1.0) ** 2
        fall_penalty = torch.where(height < 0.5, -10.0, 0.0)
        alive_bonus = 0.01

        return vel_reward + fall_penalty + alive_bonus
```

**Train**:
```bash
python train.py task=HumanoidWalk num_envs=2048
```

**Result**: Learns stable bipedal walking in 5M steps (~30 minutes on RTX 4090).

## Domain Randomization for Sim-to-Real

**Randomize physics parameters** during training:

```python
class HumanoidWalkTask(VecTask):
    def reset_idx(self, env_ids):
        # Randomize mass (±20%)
        self.robot_mass[env_ids] = self.nominal_mass * torch.rand(
            len(env_ids), device=self.device
        ) * 0.4 + 0.8  # [0.8, 1.2]

        # Randomize friction (0.5-1.5)
        self.ground_friction[env_ids] = torch.rand(
            len(env_ids), device=self.device
        ) * 1.0 + 0.5

        # Randomize motor strength (±30%)
        self.motor_strength[env_ids] = torch.rand(
            len(env_ids), device=self.device
        ) * 0.6 + 0.7  # [0.7, 1.3]

        # Apply randomized properties
        self.gym.set_actor_rigid_body_properties(...)
```

**Benefit**: Policy robust to parameter uncertainty → better real-world transfer.

## Deploying RL Policy to Real Robot

**1. Export trained policy**:
```python
# Save as ONNX for TensorRT conversion
policy = model.policy
dummy_input = torch.randn(1, 30)
torch.onnx.export(policy, dummy_input, "policy.onnx")
```

**2. Convert to TensorRT** (on Jetson):
```bash
trtexec --onnx=policy.onnx --saveEngine=policy.trt --fp16
```

**3. Deploy on robot**:
```python
import tensorrt as trt
import pycuda.autoinit

# Load TensorRT engine
with open("policy.trt", "rb") as f:
    engine = trt.Runtime(trt.Logger()).deserialize_cuda_engine(f.read())

# Run inference
def get_action(observation):
    # observation: (30,) numpy array
    # Returns: (12,) joint torques
    inputs = observation.astype(np.float32)
    outputs = np.empty(12, dtype=np.float32)

    # TensorRT inference (10 ms on Jetson Orin)
    # ... (TensorRT execution code)

    return outputs
```

**Result**: Real-time policy execution (100 Hz control loop) on Jetson.

## Summary

Isaac Sim enables efficient RL training through GPU-accelerated parallel simulation:

- **Parallel Simulation**: 1000+ envs on single GPU (100× speedup)
- **IsaacGymEnvs**: Pre-built tasks and massively parallel training framework
- **Domain Randomization**: Robust policies for sim-to-real transfer
- **Deployment**: Export to TensorRT for real-time inference on Jetson

In the next chapter, we'll explore **Visual SLAM and Navigation** in Isaac for autonomous robot localization and path planning.

---

**Key Takeaways**:
- Isaac Sim's PhysX 5 GPU physics enables 100-1000 parallel RL environments
- RL workflow: Define environment → Train with PPO/SAC → Deploy to Jetson
- IsaacGymEnvs provides massively parallel training (5M steps in 30 min)
- Domain randomization during training improves sim-to-real transfer
- Trained policies exported as TensorRT for 100 Hz real-time control on Jetson
- Example: Humanoid walking learned in 5M steps (~30 minutes on RTX 4090)