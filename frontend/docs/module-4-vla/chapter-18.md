# Chapter 18: Multimodal Foundation Models for Robotics

## From Task-Specific Models to Foundation Models

Traditional robotics models are **task-specific**: train a neural network to pick blocks, another to fold towels, another to open doors. Each requires thousands of demonstrations and fails catastrophically on variations. **Foundation models** take a radically different approach: train a single, massive model on diverse data (millions of demonstrations across hundreds of tasks and robot embodiments) to create a **general-purpose robot brain** that generalizes to new tasks, objects, and robots with minimal or zero additional training.

**Key Characteristics of Foundation Models**:
1. **Scale**: Billions of parameters (7B-55B+)
2. **Multi-Task**: Handle 100-1000+ distinct tasks
3. **Multi-Embodiment**: Control different robots (arms, mobile manipulators, humanoids)
4. **Pre-Trained**: Leverage internet-scale vision-language data
5. **Emergent Abilities**: Zero-shot generalization, reasoning, common-sense understanding

**Breakthrough Models**:
- **PaLM-E** (Google, 2023): 562B parameters, embodied reasoning
- **RT-X** (Open X-Embodiment, 2023): 500K+ demos, 22 robots
- **OpenVLA** (Stanford, 2024): 7B open-source, 970K demos
- **π0** (Physical Intelligence, 2024): Zero-shot internet→robot transfer

This chapter explores the architectures, training strategies, and deployment of these foundation models, with hands-on code for fine-tuning OpenVLA on custom tasks.

## PaLM-E: Embodied Multimodal Language Model

**Paper**: "PaLM-E: An Embodied Multimodal Language Model" (Google Research, 2023)

### Architecture Overview

**PaLM-E** combines a large language model (PaLM-540B) with visual encoders to create an **embodied reasoning system**: the robot understands not just language, but the physical world.

**Key Components**:
```
Vision Encoder (ViT-22B) → Continuous Object Representations
         ↓
Language Model (PaLM-540B) ← Interleaved Text + Vision Tokens
         ↓
Action Decoder → Robot Commands
```

**Innovations**:
1. **Multi-Image Input**: Process multiple camera views simultaneously
2. **State Injection**: Robot proprioception (joint angles) embedded as tokens
3. **Interleaved Modalities**: Text, images, and actions processed in same sequence
4. **Chain-of-Thought Reasoning**: Model explains its actions step-by-step

### Architecture Diagram

```
┌───────────────────────────────────────────────────────────┐
│                  PaLM-E Architecture                      │
└───────────────────────────────────────────────────────────┘

Multiple Camera Views              Language Instruction
    (224×224×3 each)                   "Pick apple"
         │                                    │
         ▼                                    ▼
   ┌──────────┐                        ┌──────────┐
   │   ViT    │                        │Tokenizer │
   │ (22B)    │                        └────┬─────┘
   └────┬─────┘                             │
        │                                   │
        │  Vision Tokens                    │  Text Tokens
        │  (256 per image)                  │  (variable)
        └───────────┬───────────────────────┘
                    ▼
         Interleaved Token Sequence
         [TEXT, IMG, IMG, TEXT, STATE, TEXT...]
                    │
                    ▼
         ┌────────────────────┐
         │      PaLM-540B     │
         │  (Language Model)  │
         └─────────┬──────────┘
                   │
        Contextualized Representations
                   │
                   ▼
         ┌────────────────────┐
         │   Action Decoder   │
         │   (Linear + MLP)   │
         └─────────┬──────────┘
                   │
                   ▼
         Robot Actions (7-dim)
         [x, y, z, roll, pitch, yaw, gripper]
```

### Example: Chain-of-Thought Reasoning

**Input**:
- Image: Kitchen counter with apple, banana, and bowl
- Instruction: "Put the fruit in the bowl"

**PaLM-E Output**:
```
Thought: I see an apple and a banana. Both are fruits. The bowl is empty.
         I should pick up each fruit and place it in the bowl.

Action 1: Pick up apple
  [predicted_action: x=0.15, y=-0.22, z=0.05, gripper=open→closed]

Thought: Apple picked. Now pick up the banana.

Action 2: Pick up banana
  [predicted_action: x=0.20, y=0.18, z=0.05, gripper=open→closed]

Thought: Both fruits collected. Place them in the bowl.

Action 3: Place in bowl
  [predicted_action: x=0.05, y=0.0, z=0.10, gripper=closed→open]
```

**Key Insight**: Model generates intermediate reasoning steps, making actions interpretable and debuggable.

### Training Strategy

**Three-Stage Training**:

1. **Vision-Language Pre-Training** (10B image-text pairs)
   - Learn visual concepts from internet data
   - No robot data yet

2. **Multi-Task Robot Training** (300K robot demos)
   - 50+ tasks (pick, place, push, open, pour)
   - Supervised learning: predict actions from (image, language, state)

3. **Embodied Reasoning Fine-Tuning** (50K reasoning traces)
   - Train on (observation, thought, action) tuples
   - Learn to generate intermediate reasoning steps

**Loss Function**:
```python
# Simplified PaLM-E loss
def palm_e_loss(model, batch):
    images, text, states, actions = batch

    # Encode inputs
    vision_tokens = model.vision_encoder(images)  # (B, N_imgs, 256, D)
    text_tokens = model.tokenizer(text)  # (B, N_text, D)
    state_tokens = model.state_encoder(states)  # (B, D)

    # Interleave modalities
    input_tokens = interleave([text_tokens, vision_tokens, state_tokens])

    # Forward pass
    output_embeddings = model.language_model(input_tokens)

    # Predict actions
    predicted_actions = model.action_decoder(output_embeddings[:, -1])

    # Behavioral cloning loss
    action_loss = F.mse_loss(predicted_actions, actions)

    # Optional: reasoning loss (if chain-of-thought labels available)
    if batch.has_reasoning:
        reasoning_logits = model.language_model.lm_head(output_embeddings)
        reasoning_loss = F.cross_entropy(reasoning_logits, batch.reasoning_targets)
        return action_loss + 0.1 * reasoning_loss

    return action_loss
```

### Benchmarks

**Evaluation on 10 Unseen Tasks**:
- **PaLM-E-562B**: 78%` success rate
- **RT-2**: 62%` success rate
- **RT-1**: 45%` success rate

**Zero-Shot Generalization**:
- "Pick up the extinct animal" → correctly selects dinosaur toy
- "Place the edible item in the fridge" → identifies apple, opens fridge
- "Organize objects by color" → groups red, blue, green objects

**Limitation**: 562B parameters too large for real-time inference on edge devices (requires cloud deployment or TPU pods).

## RT-X: Open X-Embodiment Dataset and Models

**Paper**: "Open X-Embodiment: Robotic Learning Datasets and RT-X Models" (2023)

### The X-Embodiment Problem

**Challenge**: Every robot is different (kinematics, sensors, workspace). Training separate models for each is inefficient.

**Solution**: **Cross-embodiment learning**—train a single model on data from many robots, enabling:
- **Transfer Learning**: Skills from Robot A help Robot B
- **Data Efficiency**: Pool datasets across labs
- **Universal Policies**: Deploy same model on different robots

### RT-X Dataset Composition

**22 Robot Embodiments** from 34 institutions:

| Robot | DOF | Tasks | Demos |
|-------|-----|-------|-------|
| Franka Panda | 7 | Pick/place, open drawers | 150K |
| UR5 | 6 | Assembly, insertion | 80K |
| Google Robot | 7 | Office tasks (clean, fetch) | 120K |
| Mobile ALOHA | 14 (2 arms + mobile base) | Cooking, cleaning | 50K |
| KUKA iiwa | 7 | Industrial assembly | 40K |
| Sawyer | 7 | Tabletop manipulation | 30K |
| **Others** | Varied | Varied | 30K |

**Total**: 527,000 trajectories, 22 embodiments, 150+ tasks

**Task Categories**:
- **Manipulation**: Pick, place, push, slide, stack
- **Tool Use**: Pour, wipe, scoop, cut
- **Articulated Objects**: Open/close drawers, doors, containers
- **Mobile Manipulation**: Navigate + manipulate
- **Bimanual**: Two-arm coordination

### RT-1-X and RT-2-X Models

**RT-1-X**: RT-1 architecture trained on full RT-X dataset
**RT-2-X**: RT-2 architecture trained on full RT-X dataset

**Training Procedure**:
```python
# Simplified RT-X training loop
def train_rt_x(model, rt_x_dataset):
    optimizer = torch.optim.Adam(model.parameters(), lr=3e-4)

    for epoch in range(100):
        for batch in rt_x_dataset:
            # Batch contains mixed data from 22 robots
            images, instructions, states, actions, robot_id = batch

            # Normalize actions per robot embodiment
            actions_normalized = normalize_actions(actions, robot_id)

            # Forward pass
            predicted_actions = model(images, instructions, states)

            # Loss (MSE for continuous actions)
            loss = F.mse_loss(predicted_actions, actions_normalized)

            # Backprop
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        # Evaluate on held-out robots
        eval_success_rate = evaluate_on_unseen_robot(model, test_robot="Kinova Gen3")
        print(f"Epoch {epoch}: Eval Success Rate = {eval_success_rate:.2f}")
```

**Key Technique: Action Normalization**:
```python
def normalize_actions(actions, robot_id):
    """Normalize actions to [-1, 1] per robot embodiment"""
    # Each robot has different action ranges
    action_ranges = {
        "franka": {"x": [-0.5, 0.5], "y": [-0.5, 0.5], "z": [0.0, 0.8]},
        "ur5": {"x": [-0.6, 0.6], "y": [-0.6, 0.6], "z": [0.0, 1.0]},
        # ... for all 22 robots
    }

    ranges = action_ranges[robot_id]
    normalized = (actions - ranges["min"]) / (ranges["max"] - ranges["min"])
    normalized = normalized * 2.0 - 1.0  # Map to [-1, 1]
    return normalized
```

### Cross-Embodiment Results

**Evaluation**: Train on 21 robots, test on held-out 22nd robot (zero-shot).

| Model | Same-Robot Success | Cross-Embodiment Success |
|-------|-------------------|-------------------------|
| RT-1 (single robot) | 76%` | 0%` (fails completely) |
| RT-1-X | 82%` | 50%` |
| RT-2-X | 88%` | 67%` |

**Key Insight**: Training on diverse robots improves generalization, even to robots never seen during training.

## OpenVLA: Open-Source 7B Foundation Model

**Paper**: "OpenVLA: An Open-Source Vision-Language-Action Model" (Stanford, 2024)

### Why OpenVLA Matters

**Before OpenVLA**:
- RT-1, RT-2, PaLM-E: proprietary (no weights, no code)
- Academic research blocked (can't reproduce, can't extend)
- Commercial use restricted

**After OpenVLA**:
- **Fully open-source**: model weights, training code, datasets
- **Permissive license**: Apache 2.0 (commercial use allowed)
- **Performance**: 68%` success rate (competitive with proprietary models)

### Architecture Deep Dive

**OpenVLA = SigLIP (vision) + LLaMA-2-7B (language) + Diffusion Policy (actions)**

**1. Vision Encoder: SigLIP**
- **SigLIP**: Sigmoid Loss for Language-Image Pre-training
- **Pre-training**: 2 billion image-text pairs (WebLI dataset)
- **Architecture**: Vision Transformer (ViT-L/14)
- **Output**: 256 visual tokens per image (1024-dim each)

**2. Language Encoder: LLaMA-2-7B**
- **Pre-training**: 2 trillion text tokens (books, web, code)
- **Fine-Tuning**: Add action vocabulary tokens
- **Parameters**: 7 billion (vs 540B for PaLM-E)

**3. Action Decoder: Diffusion Policy**
- **Why Diffusion?** Continuous actions have multimodal distributions (multiple valid grasps)
- **Process**: Iteratively denoise random noise → action sequence
- **Output**: 10-step action sequence (not single action)

**Architecture Code**:
```python
import torch
import torch.nn as nn
from transformers import LlamaModel, AutoModel

class OpenVLA(nn.Module):
    def __init__(self):
        super().__init__()

        # Vision encoder: SigLIP (400M params)
        self.vision_encoder = AutoModel.from_pretrained("google/siglip-so400m-patch14-384")

        # Language encoder: LLaMA-2-7B
        self.language_encoder = LlamaModel.from_pretrained("meta-llama/Llama-2-7b-hf")

        # Projection layers
        self.vision_projection = nn.Linear(1024, 4096)  # SigLIP dim → LLaMA dim
        self.action_projection = nn.Linear(4096, 256)  # LLaMA dim → Diffusion dim

        # Diffusion policy for action prediction
        self.diffusion_policy = DiffusionPolicy(
            action_dim=7,  # (x, y, z, roll, pitch, yaw, gripper)
            horizon=10,  # Predict 10-step action sequence
            n_diffusion_steps=100
        )

    def forward(self, images, instructions, proprioceptive_state):
        # Encode vision
        vision_features = self.vision_encoder(images).last_hidden_state  # (B, 256, 1024)
        vision_tokens = self.vision_projection(vision_features)  # (B, 256, 4096)

        # Encode language
        instruction_tokens = self.language_encoder.embeddings(instructions)  # (B, L, 4096)

        # Concatenate modalities
        combined_tokens = torch.cat([instruction_tokens, vision_tokens], dim=1)

        # Process through language model
        outputs = self.language_encoder(inputs_embeds=combined_tokens)

        # Pool for action prediction (take last token)
        pooled = outputs.last_hidden_state[:, -1]  # (B, 4096)

        # Project to diffusion space
        action_embedding = self.action_projection(pooled)  # (B, 256)

        # Diffusion policy: predict action sequence
        action_sequence = self.diffusion_policy.sample(
            condition=action_embedding,
            proprioceptive=proprioceptive_state
        )  # (B, 10, 7)

        return action_sequence[:, 0]  # Return first action


class DiffusionPolicy(nn.Module):
    """Simplified diffusion policy for action prediction"""
    def __init__(self, action_dim, horizon, n_diffusion_steps):
        super().__init__()
        self.action_dim = action_dim
        self.horizon = horizon
        self.n_diffusion_steps = n_diffusion_steps

        # Noise prediction network
        self.noise_pred_net = nn.Sequential(
            nn.Linear(action_dim * horizon + 256, 512),
            nn.ReLU(),
            nn.Linear(512, 512),
            nn.ReLU(),
            nn.Linear(512, action_dim * horizon)
        )

    def sample(self, condition, proprioceptive, num_samples=1):
        """Sample action sequence via denoising diffusion"""
        # Start from random noise
        x_t = torch.randn(num_samples, self.horizon, self.action_dim, device=condition.device)

        # Iterative denoising
        for t in reversed(range(self.n_diffusion_steps)):
            # Flatten action sequence
            x_flat = x_t.reshape(num_samples, -1)

            # Concatenate with conditioning
            input_vec = torch.cat([x_flat, condition], dim=-1)

            # Predict noise
            predicted_noise = self.noise_pred_net(input_vec)
            predicted_noise = predicted_noise.reshape(num_samples, self.horizon, self.action_dim)

            # Denoise (simplified DDPM update)
            alpha_t = 1 - (t / self.n_diffusion_steps)
            x_t = (x_t - (1 - alpha_t) * predicted_noise) / torch.sqrt(torch.tensor(alpha_t))

        return x_t  # Denoised action sequence
```

### Training Recipe

**Phase 1: Pre-Training (Vision + Language)**
- **Data**: 2B image-text pairs (LAION-2B, WebLI)
- **Objective**: Contrastive learning (align image and text embeddings)
- **Duration**: 50,000 GPU-hours (A100)
- **Frozen**: Keep these weights frozen for robot training

**Phase 2: Robot Fine-Tuning**
- **Data**: 970K robot trajectories (RT-X dataset)
- **Objective**: Behavioral cloning (predict actions from observations)
- **Duration**: 500 GPU-hours (A100)
- **Learning Rate**: 1e-5 (low to preserve pre-trained knowledge)

**Phase 3: Task-Specific Adaptation** (optional)
- **Data**: 50-500 demos for specific task
- **Objective**: Low-rank adaptation (LoRA) or full fine-tuning
- **Duration**: 10 GPU-hours (A100)

**Complete Training Script**:
```python
from transformers import Trainer, TrainingArguments
from openvla import OpenVLA, RTXDataset

# Load pre-trained OpenVLA
model = OpenVLA.from_pretrained("openvla/openvla-7b")

# Load RT-X dataset
train_dataset = RTXDataset(
    data_path="gs://rt-x-dataset/train",
    embodiments=["franka", "ur5", "google_robot", "aloha"]
)

# Training arguments
training_args = TrainingArguments(
    output_dir="./openvla_finetuned",
    per_device_train_batch_size=16,
    gradient_accumulation_steps=4,  # Effective batch size = 64
    num_train_epochs=10,
    learning_rate=1e-5,
    warmup_steps=1000,
    logging_steps=100,
    save_steps=1000,
    fp16=True,  # Mixed precision training
    dataloader_num_workers=8
)

# Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    data_collator=lambda batch: collate_robot_batch(batch)
)

# Train
trainer.train()

# Save fine-tuned model
model.save_pretrained("./openvla_rtx_finetuned")
```

### Inference and Deployment

**Real-Time Control Loop**:
```python
from openvla import OpenVLA
import numpy as np

# Load model
model = OpenVLA.from_pretrained("openvla/openvla-7b", device="cuda")
model.eval()

# Control loop (10 Hz)
while True:
    # Get observation
    image = robot.get_camera_image()  # (224, 224, 3)
    proprio = robot.get_joint_state()  # (7,)

    # Predict action
    with torch.no_grad():
        action = model.predict_action(
            observation={"image": image, "proprio": proprio},
            instruction="pick up the red block"
        )

    # Execute action (with safety checks)
    if is_action_safe(action):
        robot.execute_action(action, duration=0.1)
    else:
        robot.emergency_stop()

    time.sleep(0.1)  # 10 Hz control
```

**Optimization for Jetson**:
```python
# Quantize model to INT8 for Jetson Orin
import torch.quantization as quantization

model_fp32 = OpenVLA.from_pretrained("openvla/openvla-7b")
model_int8 = quantization.quantize_dynamic(
    model_fp32,
    {nn.Linear},
    dtype=torch.qint8
)

# Save quantized model
torch.save(model_int8.state_dict(), "openvla_int8.pth")

# Inference: 10 Hz on Jetson Orin (vs 2 Hz for FP32)
```

## π0: Internet-to-Robot Foundation Model

**Paper**: "π0: A Vision-Language-Action Flow Model for General Robot Control" (Physical Intelligence, 2024)

### Key Innovation: Pre-Training on Human Videos

**Problem**: Robot demonstrations are expensive ($50-100 per demo).

**Solution**: Pre-train on **10 million human videos** from internet (free data):
- YouTube: cooking, cleaning, assembly
- EpicKitchens: first-person manipulation
- Ego4D: egocentric daily activities

**Transfer Learning**: Human videos → humanoid robots (embodiment similar enough).

### Architecture

**Flow Matching** instead of diffusion:
- Faster inference (10 steps vs 100 steps)
- Better action smoothness
- Deterministic sampling

**Training**:
1. **Human Video Pre-Training**: Learn visual representations from 10M videos
2. **Robot Fine-Tuning**: Adapt to 100K robot demos

**Result**: 50%` success rate on tasks with **zero** robot training data (pure transfer from human videos).

## Comparison of Foundation Models

| Model | Parameters | Training Data | Success Rate | Open Source | Inference Speed |
|-------|-----------|---------------|--------------|-------------|----------------|
| **PaLM-E** | 562B | 10B images + 300K demos | 78%` | ❌ No | 1 Hz (cloud) |
| **RT-2-X** | 55B | 10B images + 500K demos | 71%` | ❌ No | 5 Hz (TPU) |
| **OpenVLA** | 7B | 2B images + 970K demos | 68%` | ✅ Yes | 10 Hz (Jetson) |
| **π0** | 3B | 10M videos + 100K demos | 62%` | ❌ No | 20 Hz (GPU) |

**Key Takeaway**: Larger models achieve higher success rates but require more compute. OpenVLA offers the best **performance/accessibility tradeoff** for research and commercial use.

## Summary

Multimodal foundation models represent the cutting edge of robotic learning:

- **PaLM-E**: 562B-parameter embodied reasoning (chain-of-thought)
- **RT-X**: Cross-embodiment learning (22 robots, 500K+ demos)
- **OpenVLA**: First high-performance open-source VLA (7B params, 68%` success)
- **π0**: Internet-to-robot transfer (10M human videos)

In the next chapter, we'll explore **Training VLA Policies**: data collection strategies, behavioral cloning, fine-tuning techniques, and sim-to-real transfer.

---

**Key Takeaways**:
- Foundation models achieve generalization by training on diverse, large-scale datasets
- PaLM-E demonstrates embodied reasoning with 562B parameters (78%` success on unseen tasks)
- RT-X enables cross-embodiment learning: train on 21 robots, deploy on 22nd (67%` success)
- OpenVLA is the first open-source 7B-parameter VLA model (Apache 2.0, 68%` success)
- Diffusion policies model multimodal action distributions (multiple valid solutions)
- π0 achieves 50%` zero-shot success by pre-training on 10M human videos
- Scaling laws: larger models → better generalization, but diminishing returns after 7-55B params
- Real-time inference requires optimization: quantization, model compression, hardware acceleration
