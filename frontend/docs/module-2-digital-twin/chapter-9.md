# Chapter 9: Physics Engines and Dynamics in Robot Simulation

## Introduction to Physics Simulation

The fidelity of robot simulation depends critically on how accurately the **physics engine** models real-world dynamics. A humanoid robot's ability to balance, walk, and manipulate objects in simulation directly translates to hardware performance—but only if the underlying physics accurately represent forces, torques, collisions, and constraints.

**Physics engines** are numerical solvers that compute the motion of rigid and soft bodies under forces, constraints, and collisions. They answer fundamental questions every simulation timestep:
- How does gravity affect each link of the robot?
- What happens when the foot contacts the ground?
- How do joint motors apply torque to achieve desired motion?
- What forces arise from collisions with obstacles?

This chapter explores the mathematical foundations of physics engines, compares engine architectures (ODE, DART, Bullet, Simbody), and provides practical guidance for configuring physics parameters to achieve stable, realistic humanoid simulations.

## Fundamentals of Rigid Body Dynamics

### Newton-Euler Equations of Motion

Every link in a robot is modeled as a **rigid body**—an object whose shape doesn't deform. Its motion is governed by Newton's second law:

**Translational motion**:
```
F = m * a
```
- **F**: Net force (N)
- **m**: Mass (kg)
- **a**: Linear acceleration (m/s²)

**Rotational motion** (Euler's equation):
```
τ = I * α + ω × (I * ω)
```
- **τ**: Net torque (N·m)
- **I**: Inertia tensor (kg·m²) - 3×3 matrix describing rotational resistance
- **α**: Angular acceleration (rad/s²)
- **ω**: Angular velocity (rad/s)
- **ω × (I * ω)**: Gyroscopic effect (important for spinning wheels, drone propellers)

### State Representation

Each rigid body has a 13-dimensional state:

**Position and Orientation (7 DOF)**:
- **Position**: (x, y, z) in world frame
- **Orientation**: Quaternion (w, x, y, z) or Euler angles (roll, pitch, yaw)

**Velocity (6 DOF)**:
- **Linear velocity**: (vx, vy, vz)
- **Angular velocity**: (ωx, ωy, ωz)

**Example**: A humanoid torso state:
```python
state = {
    'position': [0.0, 0.0, 1.0],  # 1m above ground
    'orientation_quat': [1.0, 0.0, 0.0, 0.0],  # No rotation
    'linear_velocity': [0.5, 0.0, 0.0],  # Moving forward at 0.5 m/s
    'angular_velocity': [0.0, 0.0, 0.1]  # Slowly yawing (turning)
}
```

### Numerical Integration

Physics engines simulate motion by discretizing time into small steps (e.g., 1ms`). At each step, they integrate accelerations to update velocities and positions.

**Explicit Euler Integration** (simplest, but unstable for stiff systems):
```python
def euler_step(state, dt):
    # Compute forces and torques
    F = compute_forces(state)  # Gravity, motors, collisions
    τ = compute_torques(state)

    # Compute accelerations
    a = F / mass
    α = inverse(I) @ (τ - cross(ω, I @ ω))

    # Update velocities
    state.v += a * dt
    state.ω += α * dt

    # Update positions
    state.position += state.v * dt
    state.orientation += quaternion_derivative(state.orientation, state.ω) * dt

    return state
```

**Problem**: Explicit Euler is unstable for stiff springs, high friction. Errors accumulate exponentially.

**Runge-Kutta 4th Order (RK4)** (more accurate, 4× slower):
- Evaluates dynamics at 4 intermediate points per timestep
- 4th-order accuracy (error ∝ dt⁴ instead of dt)
- Used in DART for precise manipulation tasks

**Semi-Implicit Euler** (good trade-off):
```python
def semi_implicit_euler(state, dt):
    a = F / mass
    state.v += a * dt  # Update velocity first
    state.position += state.v * dt  # Then position (using new velocity)
    return state
```

**Benefit**: Energy-preserving (doesn't artificially gain/lose energy like explicit Euler).

## Contact Dynamics and Collision Detection

### The Contact Problem

When a humanoid foot touches the ground, the physics engine must:
1. **Detect collision**: Determine if geometries overlap
2. **Compute contact points**: Find exact collision location and normal direction
3. **Resolve penetration**: Separate overlapping bodies
4. **Apply contact forces**: Calculate friction, normal force, restitution (bounce)

### Collision Detection Pipeline

**Broad Phase** (fast, approximate):
- Use **Axis-Aligned Bounding Boxes (AABBs)** or spatial hashing
- Quickly eliminate pairs of objects that can't be colliding
- Example: "Robot arm bounding box doesn't overlap table bounding box → skip"

**Narrow Phase** (slow, exact):
- **GJK algorithm** (Gilbert-Johnson-Keerthi): Distance between convex shapes
- **SAT** (Separating Axis Theorem): Fast for polyhedra
- **Mesh collision**: Check triangle-triangle intersections (expensive)

**Contact Point Generation**:
- Find **penetration depth** (how much objects overlap)
- Compute **contact normal** (direction to separate bodies)
- Identify **contact patch** (single point or polygon)

### Contact Force Models

**Penalty Method** (ODE, Bullet default):
- Model contact as a **stiff spring-damper**:
  ```
  F_normal = -k * penetration_depth - b * penetration_velocity
  ```
  - **k**: Contact stiffness (N/m) - higher = less sinking into ground
  - **b**: Contact damping (N·s/m) - prevents bouncing
- **Problem**: Requires very small timesteps for stiff contacts (or objects sink into each other)

**Constraint-Based Method** (DART, advanced ODE):
- Formulate contact as a **non-penetration constraint**:
  ```
  distance(bodyA, bodyB) ≥ 0
  ```
- Solve as **Linear Complementarity Problem (LCP)** or **Quadratic Program (QP)**
- **Benefit**: Handles stacking, grasping, precise contact (but slower)

### Friction Models

**Coulomb Friction**:
```
|F_tangent| ≤ μ * F_normal
```
- **μ**: Friction coefficient (0.0 = ice, 1.0 = rubber)
- **F_normal**: Normal force (pushing bodies together)
- **F_tangent**: Friction force (opposes sliding)

**Friction Cone Approximation**:
- True friction cone (infinite directions) approximated by 4-sided pyramid
- Faster to solve than full nonlinear cone

**URDF friction parameters**:
```xml
<collision>
  <surface>
    <friction>
      <ode>
        <mu>0.8</mu>   <!-- Primary friction (tangent 1) -->
        <mu2>0.8</mu2> <!-- Secondary friction (tangent 2) -->
      </ode>
    </friction>
  </surface>
</collision>
```

**Typical values**:
- Wood on wood: μ = 0.3-0.5
- Rubber on concrete: μ = 0.7-0.9
- Metal on metal: μ = 0.15-0.25

## Physics Engine Comparison

### ODE (Open Dynamics Engine)

**Architecture**:
- Constraint-based solver with **iterative LCP solver**
- **Dantzig algorithm** or **Projected Gauss-Seidel (PGS)** for constraints
- Fast, stable for wheeled robots and manipulators

**Strengths**:
- Default in Gazebo (well-tested)
- Good performance for simple robots (< 20 joints)
- Handles stacking, grasping reasonably well

**Weaknesses**:
- **Drift**: Constraints not perfectly enforced (robots slowly sink into ground)
- **Instability at high joint counts**: Humanoids with 30+ joints may jitter
- No direct support for soft bodies

**Configuration in SDF**:
```xml
<physics name="ode_physics" type="ode">
  <max_step_size>0.001</max_step_size>
  <real_time_factor>1.0</real_time_factor>
  <ode>
    <solver>
      <type>quick</type>  <!-- or 'world' for Dantzig -->
      <iters>50</iters>  <!-- More iters = more accurate, slower -->
      <sor>1.3</sor>  <!-- Successive Over-Relaxation parameter -->
    </solver>
    <constraints>
      <cfm>0.0</cfm>  <!-- Constraint Force Mixing (softness) -->
      <erp>0.2</erp>  <!-- Error Reduction Parameter (stiffness) -->
    </constraints>
  </ode>
</physics>
```

**Tuning**:
- Increase `iters` (50 → 100) for more accurate contact forces
- Lower `cfm` (0.0 = rigid, 0.01 = soft) to reduce joint drift
- Higher `erp` (0.2 → 0.8) reduces penetration but may cause jitter

### DART (Dynamic Animation and Robotics Toolkit)

**Architecture**:
- **Featherstone's Articulated Body Algorithm** for joint kinematics
- **Constraint solver**: LCP with Lemke's algorithm or interior-point methods
- **Continuous collision detection** (prevents tunneling at high speeds)

**Strengths**:
- **Best for humanoids**: Precise constraint satisfaction (no drift)
- **Stable for bipedal walking**: Handles complex contact sequences
- **Differentiable physics**: Gradient-based optimization for motion planning

**Weaknesses**:
- Slower than ODE/Bullet (3-5× for equivalent accuracy)
- Smaller community, less tooling support

**Configuration**:
```xml
<physics name="dart_physics" type="dart">
  <max_step_size>0.001</max_step_size>
  <dart>
    <solver>
      <type>pgs</type>  <!-- Projected Gauss-Seidel -->
    </solver>
    <collision_detector>bullet</collision_detector>  <!-- Use Bullet for collision detection -->
  </dart>
</physics>
```

**Use case**: Research on bipedal locomotion, contact-rich manipulation (grasping, assembly).

### Bullet Physics

**Architecture**:
- **Discrete and continuous collision detection**
- **Sequential Impulse Solver** (SI) for constraints
- **GPU acceleration** for massive parallelism (1000+ objects)

**Strengths**:
- **Fastest** for multi-robot simulations (10+ robots)
- Soft body dynamics (cloth, deformable objects)
- Real-time performance (used in video games)

**Weaknesses**:
- Less accurate than DART for precise tasks
- Constraint drift (similar to ODE but better tuned)

**Configuration**:
```xml
<physics name="bullet_physics" type="bullet">
  <max_step_size>0.001</max_step_size>
  <bullet>
    <solver>
      <type>sequential_impulse</type>
      <iters>50</iters>
    </solver>
  </bullet>
</physics>
```

**Use case**: Swarm robotics, games, cloth simulation.

### Simbody

**Architecture**:
- **Biomechanically accurate**: Models muscles, tendons, ligaments
- **Implicit integrator**: Handles stiff systems (muscle forces)

**Strengths**:
- Human motion simulation (medical, sports science)
- Stable for extremely stiff constraints

**Weaknesses**:
- Not designed for general robotics
- Slow for complex robots

## Configuring Physics Parameters in URDF

### Inertial Properties

Every link needs correct **mass** and **inertia tensor**:

```xml
<link name="torso">
  <inertial>
    <origin xyz="0 0 0.1" rpy="0 0 0"/>  <!-- Center of mass offset -->
    <mass value="10.0"/>  <!-- kg -->
    <inertia
      ixx="0.1" ixy="0.0" ixz="0.0"
      iyy="0.1" iyz="0.0"
      izz="0.05"/>  <!-- kg·m² -->
  </inertial>
</link>
```

**Computing inertia for basic shapes**:

**Solid box** (mass m, dimensions a×b×c):
```
Ixx = (1/12) * m * (b² + c²)
Iyy = (1/12) * m * (a² + c²)
Izz = (1/12) * m * (a² + b²)
```

**Solid cylinder** (mass m, radius r, height h, axis along z):
```
Ixx = Iyy = (1/12) * m * (3r² + h²)
Izz = (1/2) * m * r²
```

**Solid sphere** (mass m, radius r):
```
Ixx = Iyy = Izz = (2/5) * m * r²
```

**Meshlab tool** for complex meshes:
```bash
meshlab torso_mesh.stl
# Filters → Quality Measure → Compute Geometric Measures
# Copy inertia tensor values
```

### Joint Dynamics

**Damping**: Resists motion (like air resistance):
```xml
<joint name="knee_joint" type="revolute">
  <axis xyz="0 1 0"/>
  <dynamics damping="0.1" friction="0.01"/>
</joint>
```
- **damping**: Velocity-dependent torque (N·m·s/rad)
- **friction**: Constant opposing torque (N·m)

**Too little damping**: Joints oscillate wildly
**Too much damping**: Motion looks slow, underwater-like

### Contact Properties

```xml
<gazebo reference="foot_link">
  <collision>
    <surface>
      <contact>
        <ode>
          <kp>1000000.0</kp>  <!-- Contact stiffness (N/m) -->
          <kd>1.0</kd>        <!-- Contact damping (N·s/m) -->
        </ode>
      </contact>
      <friction>
        <ode>
          <mu>0.8</mu>
          <mu2>0.8</mu2>
        </ode>
      </friction>
    </surface>
  </collision>
</gazebo>
```

**Tuning for stable walking**:
1. **High friction** (μ = 0.8-1.0) prevents foot slipping
2. **Moderate stiffness** (kp = 10⁵ - 10⁶) prevents sinking but allows compliance
3. **Low damping** (kd = 1-10) avoids sticky contacts

## Debugging Physics Issues

### Common Problems

**1. Robot explodes on spawn**:
- **Cause**: Joint limits violated, overlapping collision meshes
- **Fix**: Check URDF joint limits, use `<collision>` with simplified geometries

**2. Robot sinks into ground**:
- **Cause**: Contact stiffness too low, mass too high
- **Fix**: Increase `kp` (contact stiffness), verify mass units (kg not g)

**3. Joints jitter/vibrate**:
- **Cause**: Timestep too large, constraint solver iterations too low
- **Fix**: Reduce `max_step_size` (0.001 → 0.0005), increase `iters` (50 → 100)

**4. Simulation slower than real-time**:
- **Cause**: Too many collision checks, complex meshes
- **Fix**: Use simplified collision boxes, reduce sensor update rates

### Validation Tools

**Check inertia tensors**:
```bash
gz sdf -p robot.urdf | grep inertia
```

**Visualize collision meshes** (RViz):
```bash
ros2 launch robot_description view_robot.launch.py
# Enable "Collision Enabled" in robot_model display
```

**Monitor physics performance**:
```python
# In Gazebo plugin
auto stats = world->SimTime();
auto real_time_factor = world->RealTimeFactor();
std::cout << "RTF: " << real_time_factor << std::endl;  # Should be ~1.0
```

## Real-World vs Simulated Physics Gaps

### Unmodeled Phenomena

**1. Motor dynamics**:
- **Reality**: Motors have current limits, thermal losses, back-EMF
- **Simulation**: Instant torque (unless using motor plugins)

**2. Sensor noise**:
- **Reality**: IMU drift, camera motion blur, LiDAR multi-path errors
- **Simulation**: Perfect measurements (unless noise is added manually)

**3. Flexible links**:
- **Reality**: Links bend under load (aluminum beams, carbon fiber)
- **Simulation**: Rigid bodies (no flexion)

**4. Cable dynamics**:
- **Reality**: Power cables pull on robot, create drag
- **Simulation**: No cables modeled

### Sim-to-Real Transfer Strategies

**1. Domain Randomization**:
- Vary friction μ ∈ [0.5, 1.0], mass ±20%`, sensor noise σ ∈ [0.01, 0.1]
- Train control policies robust to parameter uncertainty

**2. System Identification**:
- Measure real robot parameters (friction, inertia, motor constants)
- Update URDF to match hardware precisely

**3. Residual Learning**:
- Train policy in simulation, fine-tune on real robot with delta corrections

## Summary

Physics engines are the backbone of robot simulation, translating URDF descriptions into dynamic motion. Key takeaways:

- **Rigid body dynamics**: Newton-Euler equations govern translational and rotational motion
- **Numerical integration**: Trade-offs between speed (Euler) and accuracy (RK4)
- **Contact dynamics**: Penalty methods (fast) vs constraint solvers (accurate)
- **Engine choice**: ODE (default), DART (humanoids), Bullet (speed), Simbody (biomechanics)
- **URDF parameters**: Accurate mass, inertia, friction, damping critical for stability
- **Debugging**: Common issues are joint limits, collision overlaps, insufficient solver iterations

In the next chapter, we'll explore **Sensor Simulation and Perception**, bridging the gap between raw physics and high-level robot intelligence.

---

**Key Takeaways**:
- Physics engines solve Newton-Euler equations numerically at each timestep
- Contact forces arise from collision detection + constraint/penalty solvers
- ODE: fast and stable for wheeled robots; DART: precise for humanoids; Bullet: fastest for swarms
- Correct inertia tensors and friction coefficients are essential for realistic simulation
- Sim-to-real gap requires domain randomization or system identification
- Debugging tools: inertia validation, collision visualization, real-time factor monitoring
