# Chapter 21: Evaluation Metrics and Benchmarks

## Introduction

Evaluating Vision-Language-Action (VLA) models presents unique challenges that differ fundamentally from traditional machine learning benchmarks. Unlike image classification (where accuracy is clear-cut) or language generation (where perplexity provides a consistent metric), robotic manipulation success depends on complex physical interactions with the real world.

**The Evaluation Challenge**: A VLA model might predict the "correct" action sequence according to a dataset, yet fail catastrophically when deployed on a real robot. Conversely, a model with lower accuracy on offline metrics might demonstrate superior real-world performance through robust error recovery and adaptability.

This chapter explores the comprehensive evaluation landscape for VLA models, covering:

- **Standardized Benchmarks**: RT-X, CALVIN, RLBench, MetaWorld, and Robomimic benchmark suites
- **Quantitative Metrics**: Success rate, generalization, robustness, sample efficiency, and latency
- **Leaderboard Comparisons**: How RT-1, RT-2, OpenVLA, and π0 stack up across different evaluation criteria
- **Benchmark Design**: Principles for creating reproducible, meaningful robotics benchmarks
- **Real-World Evaluation**: Moving beyond simulation to measure deployment-ready performance

By the end of this chapter, you'll understand how to rigorously evaluate VLA models, interpret benchmark results, design custom evaluation protocols, and assess whether a model is ready for real-world deployment.

---

## 21.1 Standardized Benchmarks

### 21.1.1 RT-X Benchmark Suite

The **RT-X (Robotics Transformer X-Embodiment)** benchmark is the gold standard for evaluating cross-embodiment generalization. Released alongside the Open X-Embodiment dataset, RT-X evaluates models on:

**Benchmark Statistics**:
- **22 Robot Embodiments**: Franka Panda, UR5, Fetch, Sawyer, ALOHA, etc.
- **527 Tasks**: Pick-and-place, drawer opening, wiping, assembly, pouring
- **150+ Objects**: Everyday items, tools, food, containers
- **9 Test Environments**: Office, kitchen, lab, warehouse

**Evaluation Protocol**:
1. **Training**: Model trained on 500K+ demonstrations from Open X-Embodiment dataset
2. **Seen Task Evaluation**: 100 episodes per task on objects/environments from training
3. **Unseen Task Evaluation**: 100 episodes on novel tasks with new objects
4. **Cross-Embodiment Transfer**: Evaluate on robot morphologies not seen during training

**Success Criteria**: Task completion within 30 seconds (varies by task complexity)

**RT-X Benchmark Code**:

```python
import numpy as np
from rtx_benchmark import RTXEvaluator, TaskSuite

class VLABenchmark:
    def __init__(self, model, robot_env):
        self.model = model
        self.env = robot_env
        self.evaluator = RTXEvaluator()

        # Load task suite
        self.task_suite = TaskSuite.from_config('rtx_benchmark_v1')

    def run_benchmark(self, num_episodes=100):
        """Run full RT-X benchmark evaluation"""
        results = {
            'seen_tasks': {},
            'unseen_tasks': {},
            'cross_embodiment': {}
        }

        # Evaluate seen tasks
        for task in self.task_suite.seen_tasks:
            success_rate = self.evaluate_task(task, num_episodes)
            results['seen_tasks'][task.name] = success_rate

        # Evaluate unseen tasks (generalization)
        for task in self.task_suite.unseen_tasks:
            success_rate = self.evaluate_task(task, num_episodes)
            results['unseen_tasks'][task.name] = success_rate

        # Cross-embodiment evaluation
        for embodiment in self.task_suite.test_embodiments:
            self.env.switch_robot(embodiment)
            success_rate = self.evaluate_task_suite(
                self.task_suite.transfer_tasks[embodiment],
                num_episodes
            )
            results['cross_embodiment'][embodiment] = success_rate

        # Compute aggregate metrics
        results['aggregate'] = {
            'seen_success_rate': np.mean(list(results['seen_tasks'].values())),
            'unseen_success_rate': np.mean(list(results['unseen_tasks'].values())),
            'cross_embodiment_success_rate': np.mean(list(results['cross_embodiment'].values())),
            'overall_success_rate': np.mean([
                results['aggregate']['seen_success_rate'],
                results['aggregate']['unseen_success_rate']
            ])
        }

        return results

    def evaluate_task(self, task, num_episodes):
        """Evaluate single task"""
        successes = 0

        for episode in range(num_episodes):
            obs = self.env.reset(task=task)
            done = False
            steps = 0
            max_steps = 300  # 30 seconds at 10 Hz

            while not done and steps < max_steps:
                # Get model action
                action = self.model.predict(
                    image=obs['image'],
                    instruction=task.instruction,
                    proprioception=obs['proprioception']
                )

                # Execute action
                obs, reward, done, info = self.env.step(action)
                steps += 1

            # Check success
            if info.get('success', False):
                successes += 1

        return successes / num_episodes

# Usage
from openvla import OpenVLA
from robot_env import RobotEnv

model = OpenVLA.from_pretrained('openvla/openvla-7b')
env = RobotEnv(robot_type='franka_panda')

benchmark = VLABenchmark(model, env)
results = benchmark.run_benchmark(num_episodes=100)

print(f"Seen Tasks Success Rate: {results['aggregate']['seen_success_rate']:.1%`}")
print(f"Unseen Tasks Success Rate: {results['aggregate']['unseen_success_rate']:.1%`}")
print(f"Cross-Embodiment Success Rate: {results['aggregate']['cross_embodiment_success_rate']:.1%`}")
```

**RT-X Leaderboard (as of 2025)**:

| Model | Seen Tasks | Unseen Tasks | Cross-Embodiment | Overall |
|-------|------------|--------------|------------------|---------|
| RT-2 (55B) | 89%` | 62%` | 51%` | 75.5%` |
| OpenVLA (7B) | 85%` | 68%` | 58%` | 76.5%` |
| π0 (3B) | 81%` | 71%` | 63%` | 76.0%` |
| RT-1 (35M) | 93%` | 17%` | 12%` | 55.0%` |

### 21.1.2 CALVIN Benchmark

**CALVIN (Composing Actions from Language and Vision)** evaluates long-horizon task composition and language grounding.

**Key Features**:
- **Multi-Task Chains**: Execute sequences of 5+ subtasks from single instruction
- **Language Variations**: 1,000+ natural language descriptions per task
- **Procedural Generation**: Randomized object arrangements and scene layouts
- **34 Manipulation Tasks**: Sliding, grasping, stacking, drawer opening/closing

**Benchmark Code**:

```python
from calvin_env import CALVINEnv
import torch

def evaluate_calvin(model, num_sequences=1000):
    """Evaluate on CALVIN long-horizon benchmark"""
    env = CALVINEnv(task_suite='ABC-D', split='validation')

    metrics = {
        'avg_sequence_length': [],  # How many consecutive tasks completed
        'success_rate_by_length': {i: [] for i in range(1, 6)},
        'language_grounding_accuracy': []
    }

    for seq_idx in range(num_sequences):
        # CALVIN provides chain of 5 tasks
        instruction_chain = env.reset()  # e.g., "open drawer, pick block, close drawer"

        completed_tasks = 0
        for task_idx, instruction in enumerate(instruction_chain):
            obs = env.get_observation()

            # Model predicts action from language + vision
            with torch.no_grad():
                action = model.predict(
                    image=obs['rgb_static'],
                    instruction=instruction,
                    proprioception=obs['robot_obs']
                )

            # Execute until subtask succeeds or 360 steps (1 minute)
            for step in range(360):
                obs, reward, done, info = env.step(action)

                if info['task_success']:
                    completed_tasks += 1
                    break

                # Recompute action
                action = model.predict(
                    image=obs['rgb_static'],
                    instruction=instruction,
                    proprioception=obs['robot_obs']
                )

            if not info['task_success']:
                break  # Chain broken

        metrics['avg_sequence_length'].append(completed_tasks)
        metrics['success_rate_by_length'][completed_tasks].append(1)

    # Compute aggregate metrics
    results = {
        'avg_sequence_length': np.mean(metrics['avg_sequence_length']),
        'success_rate_1_task': np.mean(metrics['success_rate_by_length'][1]) if metrics['success_rate_by_length'][1] else 0,
        'success_rate_2_tasks': np.mean(metrics['success_rate_by_length'][2]) if metrics['success_rate_by_length'][2] else 0,
        'success_rate_3_tasks': np.mean(metrics['success_rate_by_length'][3]) if metrics['success_rate_by_length'][3] else 0,
        'success_rate_4_tasks': np.mean(metrics['success_rate_by_length'][4]) if metrics['success_rate_by_length'][4] else 0,
        'success_rate_5_tasks': np.mean(metrics['success_rate_by_length'][5]) if metrics['success_rate_by_length'][5] else 0,
    }

    return results
```

**CALVIN Leaderboard**:

| Model | 1-Task | 2-Task | 3-Task | 4-Task | 5-Task | Avg Length |
|-------|--------|--------|--------|--------|--------|------------|
| RT-2-PaLI | 91%` | 73%` | 58%` | 42%` | 31%` | 2.95 |
| OpenVLA | 87%` | 69%` | 54%` | 38%` | 27%` | 2.75 |
| MCIL (SOTA) | 94%` | 81%` | 68%` | 54%` | 43%` | 3.40 |

### 21.1.3 RLBench

**RLBench** is a large-scale benchmark with 100 diverse manipulation tasks in PyBullet simulation.

**Tasks Include**:
- **Object Manipulation**: Pick, place, stack, insert, screw
- **Tool Use**: Hammer, screwdriver, knife, spatula
- **Articulated Objects**: Drawers, doors, windows, laptops
- **Deformable Objects**: Cloth folding, rope manipulation

**Evaluation Code**:

```python
from rlbench.environment import Environment
from rlbench.action_modes.action_mode import ArmActionMode, ActionMode
from rlbench.observation_config import ObservationConfig
from rlbench import tasks

def evaluate_rlbench(model, task_names, episodes_per_task=100):
    """Evaluate on RLBench simulation benchmark"""

    # Configure observations
    obs_config = ObservationConfig()
    obs_config.set_all(True)

    # Initialize environment
    action_mode = ActionMode(ArmActionMode.ABS_EE_POSE_PLAN_WORLD_FRAME)
    env = Environment(action_mode, obs_config=obs_config, headless=True)
    env.launch()

    results = {}

    for task_name in task_names:
        # Load task
        task_class = getattr(tasks, task_name)
        task = env.get_task(task_class)

        successes = 0
        for episode in range(episodes_per_task):
            descriptions, obs = task.reset()

            done = False
            steps = 0
            while not done and steps < 200:
                # Get action from VLA model
                action = model.predict(
                    image=obs.front_rgb,
                    instruction=descriptions[0],  # Natural language task description
                    proprioception=obs.joint_positions
                )

                try:
                    obs, reward, done = task.step(action)
                    steps += 1
                except Exception as e:
                    break

            if reward == 1.0:  # RLBench uses binary success
                successes += 1

        results[task_name] = successes / episodes_per_task

    env.shutdown()

    results['average_success_rate'] = np.mean(list(results.values()))
    return results

# Evaluate on subset of tasks
task_names = [
    'PickAndLift', 'ReachTarget', 'TakePlateOffColoredDishRack',
    'PutKnivesInKnifeBlock', 'StackBlocks', 'OpenDrawer'
]

results = evaluate_rlbench(model, task_names, episodes_per_task=100)
print(f"RLBench Average Success Rate: {results['average_success_rate']:.1%`}")
```

---

## 21.2 Evaluation Metrics

### 21.2.1 Success Rate (Primary Metric)

**Success rate** is the percentage of episodes where the robot completes the task within the allowed time/steps.

**Definition**:
```
Success Rate = (# Successful Episodes) / (# Total Episodes)
```

**Task-Specific Success Criteria**:

```python
class TaskSuccessChecker:
    """Define success criteria for different task types"""

    def check_pick_and_place(self, obs, goal_state):
        """Object within 2cm of goal position"""
        object_pos = obs['object_position']
        goal_pos = goal_state['target_position']
        distance = np.linalg.norm(object_pos - goal_pos)
        return distance < 0.02  # 2cm threshold

    def check_drawer_open(self, obs, goal_state):
        """Drawer opened > 80%` of maximum distance"""
        drawer_opening = obs['drawer_joint_position']
        max_opening = goal_state['drawer_max_opening']
        return drawer_opening > 0.8 * max_opening

    def check_button_press(self, obs, goal_state):
        """Button depression > 5mm"""
        button_depth = obs['button_position'][2]  # Z-axis
        return button_depth < -0.005  # 5mm pressed

    def check_stacking(self, obs, goal_state):
        """All blocks stacked within 1cm alignment"""
        block_positions = obs['block_positions']  # (N, 3)

        # Check vertical alignment
        for i in range(len(block_positions) - 1):
            xy_distance = np.linalg.norm(
                block_positions[i, :2] - block_positions[i+1, :2]
            )
            if xy_distance > 0.01:  # 1cm threshold
                return False

        # Check height ordering
        z_positions = block_positions[:, 2]
        if not np.all(z_positions[:-1] < z_positions[1:]):
            return False

        return True
```

### 21.2.2 Generalization Metrics

**Zero-Shot Generalization**: Performance on tasks never seen during training.

```python
def compute_generalization_metrics(model, seen_tasks, unseen_tasks, episodes=100):
    """Measure generalization gap"""

    # Evaluate on seen tasks
    seen_success = evaluate_tasks(model, seen_tasks, episodes)

    # Evaluate on unseen tasks
    unseen_success = evaluate_tasks(model, unseen_tasks, episodes)

    metrics = {
        'seen_success_rate': seen_success,
        'unseen_success_rate': unseen_success,
        'generalization_gap': seen_success - unseen_success,
        'generalization_ratio': unseen_success / seen_success if seen_success > 0 else 0
    }

    return metrics

# Object Generalization
def evaluate_object_generalization(model):
    """Test on novel object shapes, sizes, textures"""

    train_objects = ['red_cube', 'blue_cylinder', 'green_sphere']
    test_objects = ['yellow_pyramid', 'orange_torus', 'purple_cuboid']

    train_success = evaluate_with_objects(model, train_objects)
    test_success = evaluate_with_objects(model, test_objects)

    return {
        'train_object_success': train_success,
        'test_object_success': test_success,
        'object_generalization_gap': train_success - test_success
    }

# Environment Generalization
def evaluate_environment_generalization(model):
    """Test on novel backgrounds, lighting, distractors"""

    train_envs = ['office_bright', 'lab_neutral']
    test_envs = ['kitchen_dim', 'warehouse_cluttered']

    train_success = evaluate_in_environments(model, train_envs)
    test_success = evaluate_in_environments(model, test_envs)

    return {
        'train_env_success': train_success,
        'test_env_success': test_success,
        'env_generalization_gap': train_success - test_success
    }
```

### 21.2.3 Robustness Metrics

**Robustness** measures performance degradation under perturbations.

```python
class RobustnessEvaluator:
    def __init__(self, model, base_env):
        self.model = model
        self.env = base_env

    def evaluate_visual_perturbations(self):
        """Test robustness to camera noise, lighting changes, occlusions"""

        perturbations = {
            'gaussian_noise': [0.01, 0.05, 0.10],  # Noise std
            'brightness': [0.5, 0.7, 1.3, 1.5],     # Brightness multiplier
            'contrast': [0.5, 0.7, 1.3, 1.5],       # Contrast multiplier
            'occlusion': [0.1, 0.2, 0.3],           # % of image occluded
            'motion_blur': [3, 5, 7]                # Kernel size
        }

        results = {'baseline': self.evaluate_clean()}

        for perturb_type, levels in perturbations.items():
            results[perturb_type] = {}
            for level in levels:
                success_rate = self.evaluate_with_perturbation(perturb_type, level)
                results[perturb_type][level] = success_rate

        return results

    def evaluate_with_perturbation(self, perturb_type, level):
        """Run evaluation with specific perturbation"""
        self.env.set_visual_perturbation(perturb_type, level)

        successes = 0
        for episode in range(100):
            obs = self.env.reset()
            done = False
            steps = 0

            while not done and steps < 200:
                action = self.model.predict(
                    image=obs['image'],  # Perturbed image
                    instruction=obs['instruction'],
                    proprioception=obs['proprioception']
                )
                obs, reward, done, info = self.env.step(action)
                steps += 1

            if info['success']:
                successes += 1

        return successes / 100

    def evaluate_physical_perturbations(self):
        """Test robustness to object pose variations, mass changes"""

        results = {}

        # Object pose randomization
        for pose_noise in [0.01, 0.05, 0.10]:  # meters
            self.env.set_object_pose_noise(pose_noise)
            results[f'pose_noise_{pose_noise}m'] = self.evaluate_clean()

        # Object mass randomization
        for mass_factor in [0.5, 0.75, 1.25, 1.5]:
            self.env.set_object_mass_factor(mass_factor)
            results[f'mass_{mass_factor}x'] = self.evaluate_clean()

        # Object friction randomization
        for friction in [0.2, 0.5, 1.0, 2.0]:
            self.env.set_object_friction(friction)
            results[f'friction_{friction}'] = self.evaluate_clean()

        return results

# Usage
evaluator = RobustnessEvaluator(model, env)
visual_robustness = evaluator.evaluate_visual_perturbations()
physical_robustness = evaluator.evaluate_physical_perturbations()

print(f"Baseline Success: {visual_robustness['baseline']:.1%`}")
print(f"10%` Gaussian Noise: {visual_robustness['gaussian_noise'][0.10]:.1%`}")
print(f"30%` Occlusion: {visual_robustness['occlusion'][0.3]:.1%`}")
```

### 21.2.4 Sample Efficiency

**Sample efficiency** measures how many demonstrations the model needs to achieve target performance.

```python
def evaluate_sample_efficiency(model_class, dataset, target_success_rate=0.7):
    """Measure demonstrations needed to reach target performance"""

    demo_counts = [10, 50, 100, 500, 1000, 5000, 10000, 50000]
    results = []

    for num_demos in demo_counts:
        # Sample subset of dataset
        train_data = dataset.sample(num_demos)

        # Train model from scratch
        model = model_class()
        model.train(train_data, epochs=10)

        # Evaluate
        success_rate = evaluate_model(model, test_episodes=100)
        results.append({
            'num_demos': num_demos,
            'success_rate': success_rate,
            'reached_target': success_rate >= target_success_rate
        })

        print(f"{num_demos} demos: {success_rate:.1%`} success")

        if success_rate >= target_success_rate:
            print(f"Reached {target_success_rate:.0%`} with {num_demos} demonstrations")
            break

    return results

# Compare sample efficiency across models
models = {
    'RT-1': RT1Model,
    'RT-2': RT2Model,
    'OpenVLA': OpenVLAModel
}

for model_name, model_class in models.items():
    print(f"\n=== {model_name} Sample Efficiency ===")
    results = evaluate_sample_efficiency(model_class, dataset)
```

**Typical Sample Efficiency**:

| Model | 10 Demos | 100 Demos | 1K Demos | 10K Demos | 50K Demos |
|-------|----------|-----------|----------|-----------|-----------|
| RT-1 (from scratch) | 12%` | 28%` | 51%` | 73%` | 89%` |
| RT-2 (fine-tuned) | 31%` | 58%` | 79%` | 91%` | 94%` |
| OpenVLA (fine-tuned) | 38%` | 67%` | 84%` | 93%` | 96%` |

### 21.2.5 Latency and Throughput

**Inference latency** is critical for real-time control (target: `<100ms` for 10 Hz operation).

```python
import time
import torch

def benchmark_inference_latency(model, num_iterations=1000):
    """Measure end-to-end inference latency"""

    # Prepare dummy inputs
    image = torch.randn(1, 3, 224, 224).cuda()
    instruction = "pick up the red block"
    proprioception = torch.randn(1, 7).cuda()

    # Warmup
    for _ in range(10):
        _ = model.predict(image, instruction, proprioception)

    # Benchmark
    latencies = []
    torch.cuda.synchronize()

    for _ in range(num_iterations):
        start = time.perf_counter()

        with torch.no_grad():
            action = model.predict(image, instruction, proprioception)

        torch.cuda.synchronize()
        end = time.perf_counter()

        latencies.append((end - start) * 1000)  # Convert to ms

    # Compute statistics
    latencies = np.array(latencies)
    results = {
        'mean_latency_ms': np.mean(latencies),
        'std_latency_ms': np.std(latencies),
        'p50_latency_ms': np.percentile(latencies, 50),
        'p95_latency_ms': np.percentile(latencies, 95),
        'p99_latency_ms': np.percentile(latencies, 99),
        'max_latency_ms': np.max(latencies),
        'throughput_hz': 1000 / np.mean(latencies)
    }

    return results

# Benchmark on different hardware
for device in ['RTX_4090', 'Jetson_Orin', 'Jetson_Xavier']:
    print(f"\n=== {device} Benchmark ===")
    results = benchmark_inference_latency(model)
    print(f"Mean Latency: {results['mean_latency_ms']:.1f} ms")
    print(f"P95 Latency: {results['p95_latency_ms']:.1f} ms")
    print(f"Throughput: {results['throughput_hz']:.1f} Hz")
```

**Latency Benchmarks**:

| Model | RTX 4090 | Jetson Orin (15W) | Jetson Xavier |
|-------|----------|-------------------|---------------|
| RT-1 (35M params) | 8ms` | 45ms` | 120ms` |
| RT-2 (55B params) | 180ms` | N/A | N/A |
| OpenVLA-7B (FP16) | 42ms` | 110ms` | 350ms` |
| OpenVLA-7B (INT8) | 18ms` | 58ms` | 180ms` |
| OpenVLA-7B (TensorRT) | 12ms` | 35ms` | 95ms` |

---

## 21.3 Benchmark Design Principles

### 21.3.1 Reproducibility

```python
class ReproducibleBenchmark:
    """Ensure reproducible evaluation results"""

    def __init__(self, seed=42):
        # Set all random seeds
        np.random.seed(seed)
        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)

        # Deterministic operations (may reduce performance)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False

    def save_evaluation_config(self, filepath):
        """Save complete evaluation configuration"""
        config = {
            'model': {
                'name': self.model.__class__.__name__,
                'checkpoint': self.model.checkpoint_path,
                'parameters': self.model.num_parameters()
            },
            'environment': {
                'simulator': self.env.simulator_version,
                'physics_timestep': self.env.physics_dt,
                'control_frequency': self.env.control_freq
            },
            'tasks': [task.to_dict() for task in self.tasks],
            'hyperparameters': {
                'num_episodes': self.num_episodes,
                'max_steps_per_episode': self.max_steps,
                'success_threshold': self.success_threshold
            },
            'random_seed': self.seed,
            'timestamp': datetime.now().isoformat()
        }

        with open(filepath, 'w') as f:
            json.dump(config, f, indent=2)
```

### 21.3.2 Statistical Significance

```python
from scipy import stats

def compare_models_with_significance(model_a_results, model_b_results, alpha=0.05):
    """Statistical comparison of two models"""

    # model_a_results and model_b_results are lists of success rates (0 or 1) per episode

    # Compute means
    mean_a = np.mean(model_a_results)
    mean_b = np.mean(model_b_results)

    # Two-sample t-test
    t_statistic, p_value = stats.ttest_ind(model_a_results, model_b_results)

    # Bootstrap confidence intervals
    def bootstrap_mean(data, num_bootstrap=10000):
        means = []
        for _ in range(num_bootstrap):
            sample = np.random.choice(data, size=len(data), replace=True)
            means.append(np.mean(sample))
        return np.percentile(means, [2.5, 97.5])  # 95%` CI

    ci_a = bootstrap_mean(model_a_results)
    ci_b = bootstrap_mean(model_b_results)

    results = {
        'model_a_mean': mean_a,
        'model_b_mean': mean_b,
        'difference': mean_a - mean_b,
        'model_a_ci_95': ci_a,
        'model_b_ci_95': ci_b,
        't_statistic': t_statistic,
        'p_value': p_value,
        'significant': p_value < alpha,
        'winner': 'Model A' if mean_a > mean_b and p_value < alpha else
                  'Model B' if mean_b > mean_a and p_value < alpha else
                  'No significant difference'
    }

    return results

# Example usage
model_a_success = [1, 1, 0, 1, 1, 1, 0, 1, 1, 1]  # 80%` success
model_b_success = [1, 0, 0, 1, 1, 0, 0, 1, 1, 0]  # 50%` success

comparison = compare_models_with_significance(model_a_success, model_b_success)
print(f"Model A: {comparison['model_a_mean']:.1%`} (95%` CI: {comparison['model_a_ci_95']})")
print(f"Model B: {comparison['model_b_mean']:.1%`} (95%` CI: {comparison['model_b_ci_95']})")
print(f"P-value: {comparison['p_value']:.4f}")
print(f"Winner: {comparison['winner']}")
```

---

## 21.4 Real-World vs. Simulation Evaluation

### 21.4.1 Sim-to-Real Gap Analysis

```python
class SimToRealGapAnalyzer:
    def __init__(self, model):
        self.model = model

    def measure_sim_real_gap(self, tasks, sim_env, real_env):
        """Quantify performance difference between simulation and reality"""

        results = {}

        for task in tasks:
            # Evaluate in simulation
            sim_success = self.evaluate_in_env(task, sim_env, episodes=100)

            # Evaluate on real robot (expensive!)
            real_success = self.evaluate_in_env(task, real_env, episodes=20)

            results[task.name] = {
                'sim_success_rate': sim_success,
                'real_success_rate': real_success,
                'sim2real_gap': sim_success - real_success,
                'sim2real_transfer_ratio': real_success / sim_success if sim_success > 0 else 0
            }

        return results

    def identify_failure_modes(self, task, real_env, num_episodes=50):
        """Analyze why real-world failures occur"""

        failure_categories = {
            'perception_error': 0,      # Wrong object detection/localization
            'grasping_failure': 0,      # Failed to grasp object
            'collision': 0,             # Collision with environment
            'control_instability': 0,   # Oscillations, jitter
            'task_misunderstanding': 0, # Executed wrong task
            'hardware_fault': 0         # Sensor/actuator failure
        }

        for episode in range(num_episodes):
            obs = real_env.reset(task=task)
            success, failure_mode = self.run_episode(obs, real_env)

            if not success:
                failure_categories[failure_mode] += 1

        # Compute percentages
        total_failures = num_episodes - sum(1 for _ in range(num_episodes) if success)
        failure_distribution = {
            mode: count / total_failures if total_failures > 0 else 0
            for mode, count in failure_categories.items()
        }

        return failure_distribution

# Example results
sim_real_gap = analyzer.measure_sim_real_gap(tasks, sim_env, real_env)
print(f"Average Sim Success: {np.mean([r['sim_success_rate'] for r in sim_real_gap.values()]):.1%`}")
print(f"Average Real Success: {np.mean([r['real_success_rate'] for r in sim_real_gap.values()]):.1%`}")
print(f"Average Sim2Real Gap: {np.mean([r['sim2real_gap'] for r in sim_real_gap.values()]):.1%`}")
```

### 21.4.2 Human Evaluation Protocols

```python
class HumanEvaluationProtocol:
    """Collect human ratings for VLA performance"""

    def __init__(self, tasks, models):
        self.tasks = tasks
        self.models = models

    def collect_human_ratings(self, num_raters=5, episodes_per_task=10):
        """Have human evaluators rate robot performance"""

        ratings = []

        for task in self.tasks:
            for model in self.models:
                for episode in range(episodes_per_task):
                    # Record video of robot performing task
                    video_path = self.record_episode(model, task, episode)

                    # Collect ratings from multiple human raters
                    episode_ratings = []
                    for rater_id in range(num_raters):
                        rating = self.show_video_and_collect_rating(
                            video_path,
                            rater_id,
                            rating_criteria=[
                                'task_completion',      # 1-5: Did robot complete task?
                                'motion_quality',       # 1-5: Smooth, efficient motion?
                                'safety',               # 1-5: Safe behavior?
                                'robustness',           # 1-5: Recovered from errors?
                                'human_like_behavior'   # 1-5: Natural, human-like?
                            ]
                        )
                        episode_ratings.append(rating)

                    # Aggregate ratings
                    ratings.append({
                        'task': task.name,
                        'model': model.name,
                        'episode': episode,
                        'ratings': episode_ratings,
                        'avg_task_completion': np.mean([r['task_completion'] for r in episode_ratings]),
                        'avg_motion_quality': np.mean([r['motion_quality'] for r in episode_ratings]),
                        'avg_safety': np.mean([r['safety'] for r in episode_ratings]),
                        'inter_rater_agreement': self.compute_inter_rater_agreement(episode_ratings)
                    })

        return ratings

    def compute_inter_rater_agreement(self, ratings):
        """Measure consistency across human raters using Krippendorff's alpha"""
        from krippendorff import alpha

        # Convert ratings to matrix (raters x criteria)
        rating_matrix = np.array([
            [r['task_completion'], r['motion_quality'], r['safety']]
            for r in ratings
        ])

        return alpha(rating_matrix.T)
```

---

## 21.5 Comprehensive Evaluation Framework

Here's a complete evaluation framework combining all metrics:

```python
class ComprehensiveVLAEvaluator:
    def __init__(self, model, config):
        self.model = model
        self.config = config

    def run_full_evaluation(self):
        """Execute complete evaluation protocol"""

        results = {}

        print("=== 1. RT-X Benchmark ===")
        results['rtx_benchmark'] = self.evaluate_rtx()

        print("\n=== 2. CALVIN Long-Horizon ===")
        results['calvin_benchmark'] = self.evaluate_calvin()

        print("\n=== 3. Generalization Analysis ===")
        results['generalization'] = self.evaluate_generalization()

        print("\n=== 4. Robustness Testing ===")
        results['robustness'] = self.evaluate_robustness()

        print("\n=== 5. Sample Efficiency ===")
        results['sample_efficiency'] = self.evaluate_sample_efficiency()

        print("\n=== 6. Latency Benchmarks ===")
        results['latency'] = self.benchmark_latency()

        print("\n=== 7. Sim-to-Real Transfer ===")
        results['sim2real'] = self.evaluate_sim2real()

        print("\n=== 8. Human Evaluation ===")
        results['human_eval'] = self.collect_human_ratings()

        # Generate comprehensive report
        self.generate_report(results)

        return results

    def generate_report(self, results):
        """Generate markdown report with all metrics"""

        report = f"""
# VLA Model Evaluation Report

**Model**: {self.model.name}
**Date**: {datetime.now().strftime('%Y-%m-%d')}
**Evaluator**: {self.config.evaluator}

---

## Summary

| Metric Category | Score | Benchmark |
|----------------|-------|-----------|
| RT-X Overall Success | {results['rtx_benchmark']['aggregate']['overall_success_rate']:.1%`} | 75%`+ (SOTA) |
| CALVIN Avg Sequence Length | {results['calvin_benchmark']['avg_sequence_length']:.2f} | 3.0+ (SOTA) |
| Generalization Gap | {results['generalization']['generalization_gap']:.1%`} | `<15%` (Good) |
| Robustness (30%` Occlusion) | {results['robustness']['occlusion'][0.3]:.1%`} | >60%` (Good) |
| Sample Efficiency (1K demos) | {results['sample_efficiency']['1000_demos']['success_rate']:.1%`} | >70%` (Good) |
| Inference Latency (P95) | {results['latency']['p95_latency_ms']:.1f} ms | `<100ms` (Real-time) |
| Sim2Real Transfer Ratio | {results['sim2real']['avg_transfer_ratio']:.1%`} | >80%` (Excellent) |
| Human Rating (Task Completion) | {results['human_eval']['avg_task_completion']:.1f}/5.0 | >4.0 (Good) |

---

## Detailed Results

[Full metrics and analysis]

---

## Recommendations

Based on evaluation results:
1. **Strengths**: {self.identify_strengths(results)}
2. **Weaknesses**: {self.identify_weaknesses(results)}
3. **Next Steps**: {self.recommend_improvements(results)}
"""

        with open(f'evaluation_report_{self.model.name}.md', 'w') as f:
            f.write(report)
```

---

## Summary

This chapter covered comprehensive evaluation methodologies for Vision-Language-Action models:

**Key Takeaways**:

1. **Standardized Benchmarks**: RT-X, CALVIN, and RLBench provide reproducible baselines for comparing models across seen/unseen tasks, long-horizon composition, and cross-embodiment transfer.

2. **Core Metrics**:
   - **Success Rate**: Primary metric (target: >80%` on seen tasks, >60%` on unseen)
   - **Generalization**: Measured via seen vs. unseen task performance gap
   - **Robustness**: Resilience to visual/physical perturbations
   - **Sample Efficiency**: Demonstrations needed to reach target performance
   - **Latency**: Inference speed (target: `<100ms` for real-time control)

3. **Evaluation Best Practices**:
   - Use statistical significance testing (t-tests, bootstrap confidence intervals)
   - Ensure reproducibility with fixed random seeds and saved configurations
   - Combine simulation and real-world evaluation to quantify sim-to-real gap
   - Incorporate human evaluation for subjective quality metrics

4. **Real-World Deployment**: Simulation benchmarks alone are insufficient. Always measure performance on physical robots to identify perception errors, grasping failures, and control instability that don't manifest in simulation.

The next chapter explores **Ethical Considerations in Embodied AI**, addressing bias, safety, transparency, and societal impact of deploying VLA-powered humanoid robots in real-world settings.

---

## Exercises

1. **Implement RT-X Evaluation**: Write code to evaluate a VLA model on the RT-X benchmark suite and generate a leaderboard comparison.

2. **Robustness Analysis**: Test your model's robustness to visual perturbations (blur, occlusion, lighting) and plot performance degradation curves.

3. **Sample Efficiency Study**: Measure how many demonstrations your model needs to achieve 70%` success rate on a pick-and-place task.

4. **Sim-to-Real Gap**: If you have access to a real robot, quantify the sim-to-real performance gap and identify primary failure modes.

5. **Statistical Comparison**: Compare two VLA models using t-tests and bootstrap confidence intervals to determine if performance differences are statistically significant.
