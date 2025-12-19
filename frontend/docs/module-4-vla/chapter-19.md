# Chapter 19: Training VLA Policies

## From Pre-Trained Models to Task-Specific Policies

Pre-trained VLA foundation models (OpenVLA, RT-2-X) provide strong visual and language understanding, but they need **task-specific adaptation** to excel at your robot's specific tasks. This chapter covers the complete training pipeline: data collection strategies, behavioral cloning,fine-tuning techniques, sim-to-real transfer, and deployment.

**Training Pipeline Overview**:
```
Data Collection → Preprocessing → Behavioral Cloning → Fine-Tuning → Sim-to-Real → Deployment
(100-10K demos)   (normalize)    (supervised learning)   (adapt)      (transfer)   (real robot)
```

**Key Challenges**:
1. **Data Efficiency**: Collecting robot demos is expensive ($50-100/demo)
2. **Distributional Shift**: Training data ≠ deployment conditions
3. **Compounding Errors**: Small prediction errors accumulate over time
4. **Safety**: Unsafe actions during exploration can damage robot or environment

This chapter provides practical solutions with hands-on code for training custom VLA policies from scratch or fine-tuning OpenVLA.

## Data Collection Strategies

### 1. Teleoperation (Human Demonstrations)

**Method**: Human operator controls robot remotely, system records (observation, action) pairs.

**Advantages**:
- High-quality demonstrations (human expertise)
- Works for complex tasks
- No need for analytical models

**Disadvantages**:
- Expensive ($50-100/demo including human labor)
- Slow (10-30 demos/hour depending on task complexity)
- Operator fatigue affects quality

**Hardware Setup**:
```
Operator Interface         Robot System
    │                          │
    ├─ VR Controller ──────────►├─ Joint Commands
    ├─ 3D Mouse                 ├─ Cameras (RGB-D)
    ├─ Haptic Device            ├─ Proprioception (joint angles)
    └─ Keyboard                 └─ Execution Feedback
```

**ROS 2 Teleoperation Node**:
```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState, Image
from geometry_msgs.msg import TwistStamped
import h5py
import numpy as np
from cv_bridge import CvBridge

class TeleoperationRecorder(Node):
    def __init__(self):
        super().__init__('teleoperation_recorder')

        # Subscribers
        self.joint_sub = self.create_subscription(
            JointState, '/joint_states', self.joint_callback, 10
        )
        self.camera_sub = self.create_subscription(
            Image, '/camera/rgb/image_raw', self.camera_callback, 10
        )
        self.cmd_sub = self.create_subscription(
            TwistStamped, '/teleoperation/cmd_vel', self.cmd_callback, 10
        )

        # Data storage
        self.trajectory = {
            'observations': [],  # (image, joint_state)
            'actions': [],  # joint velocities or end-effector commands
            'language_instruction': ""
        }

        self.bridge = CvBridge()
        self.recording = False

    def start_recording(self, instruction):
        """Start recording a new demonstration"""
        self.recording = True
        self.trajectory = {
            'observations': [],
            'actions': [],
            'language_instruction': instruction
        }
        self.get_logger().info(f'Recording started: {instruction}')

    def stop_recording(self, filename):
        """Stop recording and save to file"""
        self.recording = False

        # Save as HDF5
        with h5py.File(filename, 'w') as f:
            f.create_dataset('images', data=np.array(self.trajectory['observations']['images']))
            f.create_dataset('joint_states', data=np.array(self.trajectory['observations']['joint_states']))
            f.create_dataset('actions', data=np.array(self.trajectory['actions']))
            f.attrs['language_instruction'] = self.trajectory['language_instruction']

        self.get_logger().info(f'Saved {len(self.trajectory["actions"])} steps to {filename}')

    def camera_callback(self, msg):
        if not self.recording:
            return

        # Convert ROS Image to numpy
        image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='rgb8')

        if 'images' not in self.trajectory['observations']:
            self.trajectory['observations']['images'] = []
        self.trajectory['observations']['images'].append(image)

    def joint_callback(self, msg):
        if not self.recording:
            return

        joint_state = np.array(msg.position)

        if 'joint_states' not in self.trajectory['observations']:
            self.trajectory['observations']['joint_states'] = []
        self.trajectory['observations']['joint_states'].append(joint_state)

    def cmd_callback(self, msg):
        if not self.recording:
            return

        # Extract action (end-effector velocity)
        action = np.array([
            msg.twist.linear.x,
            msg.twist.linear.y,
            msg.twist.linear.z,
            msg.twist.angular.x,
            msg.twist.angular.y,
            msg.twist.angular.z,
            0.0  # Gripper (handle separately)
        ])

        self.trajectory['actions'].append(action)

def main():
    rclpy.init()
    recorder = TeleoperationRecorder()

    # Example: Record 10 demonstrations
    for i in range(10):
        input(f"Press Enter to start demo {i+1}...")
        recorder.start_recording(instruction="pick up the red block")

        # Human teleoperates robot for 10-30 seconds
        rclpy.spin_once(recorder, timeout_sec=30.0)

        input("Press Enter to stop recording...")
        recorder.stop_recording(f"demo_{i+1}.h5")

    recorder.destroy_node()
    rclpy.shutdown()
```

**Data Augmentation**:
```python
def augment_demonstration(image, action):
    """Apply data augmentation to increase dataset diversity"""

    # Color jitter (randomize brightness, contrast, saturation)
    image = tf.image.random_brightness(image, max_delta=0.2)
    image = tf.image.random_contrast(image, lower=0.8, upper=1.2)
    image = tf.image.random_saturation(image, lower=0.8, upper=1.2)

    # Random crop (simulate camera position variation)
    image = tf.image.random_crop(image, size=[224, 224, 3])

    # Horizontal flip (50%` chance, if task is symmetric)
    if np.random.rand() < 0.5:
        image = tf.image.flip_left_right(image)
        action[1] = -action[1]  # Invert y-axis action

    # Gaussian noise
    image = image + tf.random.normal(shape=image.shape, mean=0, stddev=0.02)

    return image, action
```

### 2. Simulation Data Generation

**Advantages**:
- **Free**: No hardware wear, no human labor
- **Fast**: 1000× faster than real-time (parallel simulation)
- **Safe**: No risk to robot or environment
- **Scalable**: Generate millions of demos

**Disadvantages**:
- **Sim-to-Real Gap**: Physics/rendering differences
- **Limited Realism**: Hard to simulate deformable objects, fluids

**Isaac Sim Data Generation**:
```python
from omni.isaac.core import World
from omni.isaac.core.robots import Robot
import numpy as np

class SyntheticDataGenerator:
    def __init__(self, num_demos=10000):
        self.world = World(stage_units_in_meters=1.0)
        self.robot = self.world.scene.add(
            Robot(prim_path="/World/Franka", name="franka")
        )

        self.num_demos = num_demos
        self.dataset = []

    def generate_pick_and_place_dataset(self):
        """Generate synthetic pick-and-place demonstrations"""

        for i in range(self.num_demos):
            # Reset environment with domain randomization
            self.reset_scene_randomized()

            # Plan grasp
            object_pose = self.get_object_pose()
            grasp_pose = self.compute_grasp_pose(object_pose)

            # Execute and record
            trajectory = self.execute_pick_and_place(grasp_pose)

            # Store demo
            self.dataset.append({
                'observations': trajectory['observations'],
                'actions': trajectory['actions'],
                'language_instruction': np.random.choice([
                    "pick up the object",
                    "grasp the block",
                    "grab the item and place it"
                ])
            })

            if i % 100 == 0:
                print(f"Generated {i}/{self.num_demos} demos")

        # Save dataset
        self.save_dataset("synthetic_pick_place_10k.h5")

    def reset_scene_randomized(self):
        """Apply domain randomization"""
        # Randomize object position
        obj_x = np.random.uniform(-0.3, 0.3)
        obj_y = np.random.uniform(0.3, 0.7)
        self.set_object_pose([obj_x, obj_y, 0.05])

        # Randomize lighting
        light_intensity = np.random.uniform(500, 2000)
        self.set_light_intensity(light_intensity)

        # Randomize camera viewpoint (±10 degrees)
        camera_yaw = np.random.uniform(-10, 10)
        self.set_camera_yaw(camera_yaw)

        # Randomize object properties
        mass_scale = np.random.uniform(0.8, 1.2)
        self.set_object_mass_scale(mass_scale)
```

### 3. Intervention-Based Learning (DAgger)

**Problem**: Behavioral cloning suffers from **distributional shift**—robot encounters states not in training data, makes mistakes, enters new states, compounds errors.

**Solution**: **DAgger** (Dataset Aggregation)—iteratively collect data where the policy fails, add expert corrections, retrain.

**Algorithm**:
```
1. Train policy π on initial dataset D
2. Deploy policy π on robot
3. When robot deviates from expert behavior:
   a. Human intervenes with correct action
   b. Add (observation, expert_action) to dataset D
4. Retrain policy on augmented dataset D
5. Repeat steps 2-4 until performance converges
```

**Implementation**:
```python
def dagger_training(initial_dataset, num_iterations=10, robot, expert):
    """DAgger: Dataset Aggregation algorithm"""

    dataset = initial_dataset
    policy = train_policy(dataset)  # Initial policy

    for iteration in range(num_iterations):
        print(f"DAgger Iteration {iteration + 1}")

        # Deploy policy and collect corrections
        new_data = []

        for episode in range(50):  # 50 episodes per iteration
            obs = robot.reset()
            done = False

            while not done:
                # Policy prediction
                action_policy = policy.predict(obs)

                # Expert correction
                action_expert = expert.get_action(obs)

                # If policy action is unsafe or deviates significantly
                if not is_action_safe(action_policy) or np.linalg.norm(action_policy - action_expert) > 0.1:
                    # Execute expert action, record correction
                    robot.execute(action_expert)
                    new_data.append((obs, action_expert))
                else:
                    # Execute policy action
                    robot.execute(action_policy)

                obs, done = robot.step()

        # Augment dataset
        dataset = dataset + new_data

        # Retrain policy
        policy = train_policy(dataset)

        # Evaluate
        success_rate = evaluate_policy(policy, robot, num_eval=20)
        print(f"Iteration {iteration + 1}: Success Rate = {success_rate:.2f}")

    return policy
```

## Behavioral Cloning: Supervised Learning from Demonstrations

**Objective**: Learn policy π(a|o) that predicts expert actions from observations.

**Loss Function**:
```
L = E[(a_pred - a_expert)²]  # MSE for continuous actions
or
L = -E[log P(a_expert | o)]  # Cross-entropy for discrete actions
```

**PyTorch Training Loop**:
```python
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

class RobotDataset(Dataset):
    """Dataset of (observation, action) pairs"""
    def __init__(self, trajectories):
        self.observations = []
        self.actions = []

        for traj in trajectories:
            self.observations.extend(traj['observations'])
            self.actions.extend(traj['actions'])

        self.observations = torch.tensor(self.observations, dtype=torch.float32)
        self.actions = torch.tensor(self.actions, dtype=torch.float32)

    def __len__(self):
        return len(self.actions)

    def __getitem__(self, idx):
        return self.observations[idx], self.actions[idx]


def train_behavioral_cloning(model, train_loader, val_loader, epochs=100):
    """Train VLA model with behavioral cloning"""

    optimizer = torch.optim.Adam(model.parameters(), lr=1e-4)
    criterion = nn.MSELoss()

    for epoch in range(epochs):
        # Training
        model.train()
        train_loss = 0.0

        for batch_idx, (observations, actions) in enumerate(train_loader):
            # observations: (B, C, H, W) images + proprioception
            # actions: (B, action_dim)

            # Forward pass
            predicted_actions = model(observations)

            # Compute loss
            loss = criterion(predicted_actions, actions)

            # Backprop
            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()

            train_loss += loss.item()

        # Validation
        model.eval()
        val_loss = 0.0

        with torch.no_grad():
            for observations, actions in val_loader:
                predicted_actions = model(observations)
                loss = criterion(predicted_actions, actions)
                val_loss += loss.item()

        print(f"Epoch {epoch+1}: Train Loss = {train_loss/len(train_loader):.4f}, "
              f"Val Loss = {val_loss/len(val_loader):.4f}")

        # Save checkpoint
        if (epoch + 1) % 10 == 0:
            torch.save(model.state_dict(), f"checkpoint_epoch_{epoch+1}.pth")

    return model


# Example usage
trajectories = load_demonstrations("demo_dataset.h5")
dataset = RobotDataset(trajectories)
train_loader = DataLoader(dataset, batch_size=32, shuffle=True)

model = OpenVLA.from_pretrained("openvla/openvla-7b")
trained_model = train_behavioral_cloning(model, train_loader, val_loader, epochs=100)
```

## Fine-Tuning Pre-Trained VLA Models

### Full Fine-Tuning

**Approach**: Update all model parameters on task-specific data.

**Advantages**:
- Maximum adaptation to new task
- Best performance when sufficient data available (1000+ demos)

**Disadvantages**:
- Expensive (requires large GPU memory)
- Risk of catastrophic forgetting (lose pre-trained knowledge)
- Slow (hours to days on A100)

**Implementation**:
```python
from transformers import Trainer, TrainingArguments

# Load pre-trained OpenVLA
model = OpenVLA.from_pretrained("openvla/openvla-7b")

# Unfreeze all parameters
for param in model.parameters():
    param.requires_grad = True

# Training arguments
training_args = TrainingArguments(
    output_dir="./openvla_full_finetuned",
    per_device_train_batch_size=8,
    gradient_accumulation_steps=8,  # Effective batch size = 64
    num_train_epochs=20,
    learning_rate=5e-6,  # Low LR to preserve pre-trained knowledge
    warmup_steps=500,
    weight_decay=0.01,
    logging_steps=50,
    save_steps=500,
    evaluation_strategy="steps",
    eval_steps=500,
    fp16=True,
    dataloader_num_workers=4
)

# Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset
)

# Train
trainer.train()
```

### Low-Rank Adaptation (LoRA)

**Key Idea**: Instead of updating all parameters W, add low-rank matrices ΔW:
```
W_finetuned = W_pretrained + B × A
where A ∈ R^(d × r), B ∈ R^(r × d), r << d
```

**Advantages**:
- **Parameter Efficient**: Only train 0.1-1%` of parameters (7B → 7M trainable)
- **Fast**: 10× faster training than full fine-tuning
- **Modular**: Can switch between tasks by swapping LoRA weights

**Implementation**:
```python
from peft import LoraConfig, get_peft_model

# Load pre-trained model
model = OpenVLA.from_pretrained("openvla/openvla-7b")

# LoRA configuration
lora_config = LoraConfig(
    r=8,  # Rank of decomposition
    lora_alpha=32,  # Scaling factor
    target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],  # Which layers to adapt
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)

# Apply LoRA
model = get_peft_model(model, lora_config)

# Print trainable parameters
model.print_trainable_parameters()
# Output: trainable params: 7,340,032 || all params: 7,016,677,376 || trainable%: 0.1046

# Train (same as full fine-tuning, but much faster)
trainer = Trainer(model=model, args=training_args, train_dataset=train_dataset)
trainer.train()

# Save LoRA weights (only ~30 MB instead of 14 GB for full model)
model.save_pretrained("./openvla_lora_pick_and_place")
```

**Loading LoRA Weights for Inference**:
```python
from peft import PeftModel

# Load base model
base_model = OpenVLA.from_pretrained("openvla/openvla-7b")

# Load LoRA weights
model = PeftModel.from_pretrained(base_model, "./openvla_lora_pick_and_place")

# Inference
action = model.predict_action(observation, instruction="pick up the red block")
```

### Prompt Tuning

**Key Idea**: Keep model frozen, only learn task-specific "soft prompts" (continuous vectors prepended to input).

**Advantages**:
- **Ultra-Efficient**: Only 100-1000 trainable parameters
- **Fast**: Train in minutes on single GPU
- **Multi-Task**: Store multiple prompt vectors, switch instantly

**Disadvantages**:
- Lower performance than LoRA/full fine-tuning
- Works best with very large models (>10B params)

**Implementation**:
```python
from peft import PromptTuningConfig, get_peft_model

# Prompt tuning configuration
prompt_config = PromptTuningConfig(
    task_type="CAUSAL_LM",
    num_virtual_tokens=20,  # Number of soft prompt tokens
    prompt_tuning_init="RANDOM"  # or "TEXT" to initialize from real text
)

model = get_peft_model(OpenVLA.from_pretrained("openvla/openvla-7b"), prompt_config)
model.print_trainable_parameters()
# Output: trainable params: 81,920 || all params: 7,016,759,296 || trainable%: 0.0012
```

## Sim-to-Real Transfer

**Challenge**: Models trained in simulation fail on real robots due to:
- **Visual Gap**: Rendering ≠ real camera (lighting, textures, noise)
- **Physics Gap**: Simulation ≠ real dynamics (friction, contact, delays)
- **Sensor Gap**: Perfect sim sensors ≠ noisy real sensors

### Domain Randomization

**Approach**: Randomize simulation parameters during training so model learns robust features.

**Randomize**:
- Lighting: intensity, color temperature, shadows
- Textures: object colors, patterns, materials
- Camera: position, orientation, focal length, noise
- Physics: mass, friction, damping, motor strength
- Backgrounds: random images, procedural generation

**Isaac Sim Domain Randomization**:
```python
import omni.replicator.core as rep

with rep.new_layer():
    # Randomize lighting
    light = rep.create.light(light_type="Sphere")
    with light:
        rep.modify.attribute("intensity", rep.distribution.uniform(500, 3000))
        rep.modify.attribute("color", rep.distribution.uniform((0.8, 0.8, 0.8), (1.0, 1.0, 1.0)))

    # Randomize object textures
    target_obj = rep.get.prim_at_path("/World/TargetObject")
    with target_obj:
        rep.randomizer.color(colors=rep.distribution.uniform((0, 0, 0), (1, 1, 1)))

    # Randomize camera parameters
    camera = rep.create.camera()
    with camera:
        rep.modify.pose(
            position=rep.distribution.uniform((-0.2, -0.2, 0.3), (0.2, 0.2, 0.5)),
            look_at=(0, 0, 0.1)
        )

    # Randomize physics
    rep.physics.rigid_body(
        mass=rep.distribution.uniform(0.05, 0.15),
        friction=rep.distribution.uniform(0.3, 1.0)
    )
```

### Sim-to-Real Fine-Tuning

**Approach**: Pre-train on 100K sim demos, fine-tune on 50-500 real demos.

**Training Schedule**:
```
1. Pre-train on simulation (100K demos, 500 GPU-hours)
2. Collect real-world demos (50-500 demos, 10-50 human-hours)
3. Fine-tune on real demos (10 GPU-hours)
```

**Implementation**:
```python
# Load sim-trained model
model = OpenVLA.from_pretrained("./openvla_sim_trained")

# Collect real-world demonstrations
real_demos = collect_real_world_demos(num_demos=200)

# Fine-tune with low learning rate
training_args = TrainingArguments(
    per_device_train_batch_size=16,
    num_train_epochs=10,
    learning_rate=1e-6,  # Very low LR to avoid forgetting sim knowledge
    warmup_ratio=0.1
)

trainer = Trainer(model=model, args=training_args, train_dataset=real_demos)
trainer.train()

# Result: 70-80%` success rate on real robot
```

## Evaluation Metrics

**Success Rate**:
- Primary metric: % of successful task completions
- Evaluate on 50-100 held-out test episodes

**Action Error**:
- `L2_error = ||a_predicted - a_expert||²`
- Useful for debugging, but doesn't correlate perfectly with success

**Robustness**:
- Test with perturbations: occlusions, lighting changes, novel objects
- Measure generalization gap

**Safety**:
- Track unsafe actions (collisions, joint limits, singularities)
- Constraint violation rate

**Evaluation Script**:
```python
def evaluate_policy(model, robot, test_tasks, num_trials=50):
    """Evaluate policy on real robot"""

    results = {
        'success_rate': 0.0,
        'avg_action_error': 0.0,
        'unsafe_actions': 0,
        'task_completion_time': []
    }

    for task in test_tasks:
        for trial in range(num_trials):
            robot.reset()
            obs = robot.get_observation()

            success = False
            trajectory_length = 0
            action_errors = []

            while trajectory_length < 100:  # Max 100 steps per episode
                # Predict action
                action = model.predict_action(obs, task['instruction'])

                # Safety check
                if not is_action_safe(action):
                    results['unsafe_actions'] += 1
                    break

                # Execute
                obs_next, reward, done = robot.step(action)

                # Track metrics
                if 'expert_action' in obs:
                    action_errors.append(np.linalg.norm(action - obs['expert_action']))

                trajectory_length += 1

                if done:
                    success = True
                    results['task_completion_time'].append(trajectory_length * 0.1)  # 10 Hz control
                    break

                obs = obs_next

            results['success_rate'] += success / num_trials
            if action_errors:
                results['avg_action_error'] += np.mean(action_errors) / num_trials

    return results
```

## Summary

Training VLA policies requires careful consideration of data collection, training algorithms, and sim-to-real transfer:

- **Data Collection**: Teleoperation (high-quality, expensive), Simulation (free, scalable), DAgger (iterative improvement)
- **Behavioral Cloning**: Supervised learning from expert demonstrations
- **Fine-Tuning**: Full fine-tuning (best performance), LoRA (parameter-efficient), Prompt tuning (ultra-efficient)
- **Sim-to-Real**: Domain randomization + real-world fine-tuning (50-500 demos)
- **Evaluation**: Success rate, action error, robustness, safety metrics

In the next chapter, we'll explore **Deployment on Humanoids**: optimizing VLA models for real-time control, hardware acceleration, safety constraints, and production-ready systems.

---

**Key Takeaways**:
- Behavioral cloning learns policies from expert demonstrations via supervised learning
- DAgger addresses distributional shift by iteratively collecting corrections where policy fails
- LoRA fine-tuning trains only 0.1%` of parameters (7M vs 7B) with 10× speedup
- Domain randomization makes sim-trained policies robust to real-world variations
- Sim-to-real transfer: 100K sim demos + 50-500 real demos achieves 70-80%` success
- Data augmentation (color jitter, random crop, noise) increases dataset diversity
- Evaluation metrics: success rate (primary), action error, robustness, safety
- Best practice: Pre-train on large sim dataset, fine-tune on small real dataset
