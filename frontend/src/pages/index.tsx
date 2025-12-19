import React from 'react';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';

export default function Home(): JSX.Element {
  const {siteConfig} = useDocusaurusContext();

  return (
    <Layout
      title="NeuroBot Humanoid AI Textbook"
      description="Master Physical AI, ROS 2, Digital Twins, NVIDIA Isaac, and Vision-Language-Action Models">

      {/* Hero Section */}
      <div className="neurobot-hero">
        <div className="neurobot-hero-content">
          <div className="neurobot-hero-badge">University-Level Robotics Guide</div>
          <h1 className="neurobot-hero-title">
            Master <span className="highlight">NeuroBot</span> Physical AI
          </h1>
          <p className="neurobot-hero-subtitle">
            A comprehensive, market-ready textbook for building intelligent humanoid systems.
            Master ROS 2, Digital Twins, NVIDIA Isaac Platform, and Vision-Language-Action Models.
          </p>
          <div className="neurobot-hero-cta">
            <Link className="neurobot-btn-primary" to="/docs/chapter-1">
              Start Learning
            </Link>
            <Link className="neurobot-btn-secondary" to="#syllabus">
              View Syllabus
            </Link>
          </div>
        </div>
      </div>

      {/* Diamond Separator */}
      <div className="neurobot-diamond-separator">◆</div>

      {/* What You'll Master Section */}
      <section className="neurobot-features-section">
        <div className="neurobot-section-header">
          <h2 className="neurobot-section-title">What You'll Master</h2>
          <p className="neurobot-section-subtitle">
            Build production-ready humanoid AI systems with cutting-edge frameworks and methodologies
          </p>
        </div>

        <div className="neurobot-features-grid">
          {/* Feature Card 1: ROS 2 */}
          <div className="neurobot-feature-card">
            <div className="neurobot-feature-icon">🤖</div>
            <h3 className="neurobot-feature-title">ROS 2 Fundamentals</h3>
            <p className="neurobot-feature-description">
              Master the Robot Operating System 2 - the industry standard for robotics development.
              Learn DDS architecture, nodes, topics, services, and actions.
            </p>
            <div className="neurobot-feature-badges">
              <span className="neurobot-badge">5 Chapters</span>
              <span className="neurobot-badge">Module 1</span>
            </div>
          </div>

          {/* Feature Card 2: Digital Twin */}
          <div className="neurobot-feature-card">
            <div className="neurobot-feature-icon">🎮</div>
            <h3 className="neurobot-feature-title">Digital Twin & Simulation</h3>
            <p className="neurobot-feature-description">
              Build photo-realistic robot simulations with Gazebo and Unity. Master physics engines,
              sensor modeling, and sim-to-real transfer techniques.
            </p>
            <div className="neurobot-feature-badges">
              <span className="neurobot-badge">4 Chapters</span>
              <span className="neurobot-badge">Module 2</span>
            </div>
          </div>

          {/* Feature Card 3: NVIDIA Isaac */}
          <div className="neurobot-feature-card">
            <div className="neurobot-feature-icon">🧠</div>
            <h3 className="neurobot-feature-title">NVIDIA Isaac Platform</h3>
            <p className="neurobot-feature-description">
              Leverage GPU-accelerated robotics with Isaac SDK. Implement reinforcement learning,
              computer vision, and real-time perception pipelines.
            </p>
            <div className="neurobot-feature-badges">
              <span className="neurobot-badge">5 Chapters</span>
              <span className="neurobot-badge">Module 3</span>
            </div>
          </div>

          {/* Feature Card 4: VLA Models */}
          <div className="neurobot-feature-card">
            <div className="neurobot-feature-icon">👁️</div>
            <h3 className="neurobot-feature-title">Vision-Language-Action</h3>
            <p className="neurobot-feature-description">
              Implement cutting-edge VLA models for multimodal AI. Train embodied agents with
              natural language understanding and physical interaction.
            </p>
            <div className="neurobot-feature-badges">
              <span className="neurobot-badge">7 Chapters</span>
              <span className="neurobot-badge">Module 4</span>
            </div>
          </div>
        </div>
      </section>

      {/* Diamond Separator */}
      <div className="neurobot-diamond-separator">◆</div>

      {/* Complete Curriculum Section - Redesigned */}
      <section id="syllabus" className="neurobot-curriculum-redesign">
        <div className="neurobot-section-header">
          <h2 className="neurobot-section-title">Complete Curriculum</h2>
          <p className="neurobot-section-subtitle">
            23 comprehensive chapters covering the complete Physical AI development stack
          </p>
        </div>

        <div className="neurobot-curriculum-container">
          {/* Introduction Module */}
          <div className="neurobot-curriculum-module">
            <div className="neurobot-module-header">
              <div className="neurobot-module-icon">📚</div>
              <div className="neurobot-module-info">
                <h3 className="neurobot-module-name">Introduction</h3>
                <p className="neurobot-module-description">
                  Foundation concepts in Physical AI and humanoid robotics
                </p>
              </div>
            </div>
            <ul className="neurobot-module-chapters">
              <li>◆ Physical AI Fundamentals</li>
              <li>◆ Humanoid Robotics Overview</li>
            </ul>
            <Link to="/docs/chapter-1" className="neurobot-module-cta">
              Start Introduction →
            </Link>
          </div>

          <div className="neurobot-curriculum-divider">◆</div>

          {/* Module 1: ROS 2 */}
          <div className="neurobot-curriculum-module neurobot-module-alternate">
            <div className="neurobot-module-header">
              <div className="neurobot-module-icon">🤖</div>
              <div className="neurobot-module-info">
                <h3 className="neurobot-module-name">Module 1: ROS 2 Fundamentals</h3>
                <p className="neurobot-module-description">
                  Master the Robot Operating System 2 — the industry standard
                </p>
              </div>
            </div>
            <ul className="neurobot-module-chapters">
              <li>◆ ROS 2 Architecture & DDS</li>
              <li>◆ Topics & Publishers/Subscribers</li>
              <li>◆ Services & Actions</li>
              <li>◆ Packages & Workspaces</li>
              <li>◆ URDF & Robot Description</li>
            </ul>
            <Link to="/docs/module-1-ros2/chapter-3" className="neurobot-module-cta">
              Explore ROS 2 →
            </Link>
          </div>

          <div className="neurobot-curriculum-divider">◆</div>

          {/* Module 2: Digital Twin */}
          <div className="neurobot-curriculum-module">
            <div className="neurobot-module-header">
              <div className="neurobot-module-icon">🎮</div>
              <div className="neurobot-module-info">
                <h3 className="neurobot-module-name">Module 2: Digital Twin & Simulation</h3>
                <p className="neurobot-module-description">
                  Build photo-realistic robot simulations and virtual environments
                </p>
              </div>
            </div>
            <ul className="neurobot-module-chapters">
              <li>◆ Gazebo Simulation Setup</li>
              <li>◆ Physics Engines & Dynamics</li>
              <li>◆ Unity Integration & Rendering</li>
              <li>◆ Sim-to-Real Transfer</li>
            </ul>
            <Link to="/docs/module-2-digital-twin/chapter-8" className="neurobot-module-cta">
              Build Simulations →
            </Link>
          </div>

          <div className="neurobot-curriculum-divider">◆</div>

          {/* Module 3: NVIDIA Isaac */}
          <div className="neurobot-curriculum-module neurobot-module-alternate">
            <div className="neurobot-module-header">
              <div className="neurobot-module-icon">🧠</div>
              <div className="neurobot-module-info">
                <h3 className="neurobot-module-name">Module 3: NVIDIA Isaac Platform</h3>
                <p className="neurobot-module-description">
                  GPU-accelerated robotics with reinforcement learning and perception
                </p>
              </div>
            </div>
            <ul className="neurobot-module-chapters">
              <li>◆ Isaac SDK & Tools</li>
              <li>◆ Computer Vision & Perception</li>
              <li>◆ Reinforcement Learning Basics</li>
              <li>◆ Visual SLAM & Localization</li>
              <li>◆ AI Brain Integration</li>
            </ul>
            <Link to="/docs/module-3-nvidia-isaac/chapter-12" className="neurobot-module-cta">
              Master Isaac →
            </Link>
          </div>

          <div className="neurobot-curriculum-divider">◆</div>

          {/* Module 4: VLA Models */}
          <div className="neurobot-curriculum-module neurobot-module-large">
            <div className="neurobot-module-header">
              <div className="neurobot-module-icon">👁️</div>
              <div className="neurobot-module-info">
                <h3 className="neurobot-module-name">Module 4: Vision-Language-Action Models</h3>
                <p className="neurobot-module-description">
                  Cutting-edge multimodal AI for embodied intelligence and natural language control
                </p>
              </div>
            </div>
            <ul className="neurobot-module-chapters">
              <li>◆ VLA Model Introduction</li>
              <li>◆ Multimodal Learning Architectures</li>
              <li>◆ Natural Language Robot Control</li>
              <li>◆ Training Pipelines & Datasets</li>
              <li>◆ Deployment Strategies & Optimization</li>
              <li>◆ Ethics & Social Impact</li>
              <li>◆ Future of Embodied AI</li>
            </ul>
            <Link to="/docs/module-4-vla/chapter-17" className="neurobot-module-cta">
              Explore VLA Models →
            </Link>
          </div>
        </div>
      </section>

      {/* Diamond Separator */}
      <div className="neurobot-diamond-separator">◆</div>

      {/* Final CTA Section */}
      <section style={{
        padding: '5rem 2rem',
        textAlign: 'center',
        background: 'linear-gradient(180deg, var(--neurobot-bg-primary) 0%, var(--neurobot-bg-secondary) 100%)'
      }}>
        <h2 style={{
          fontFamily: 'var(--neurobot-font-serif)',
          fontSize: '2.5rem',
          color: 'var(--neurobot-text-primary)',
          marginBottom: '1.5rem'
        }}>
          Ready to Build the Future?
        </h2>
        <p style={{
          fontSize: '1.125rem',
          color: 'var(--neurobot-text-tertiary)',
          maxWidth: '700px',
          margin: '0 auto 2.5rem',
          lineHeight: '1.7'
        }}>
          Join thousands of students, researchers, and engineers mastering Physical AI and humanoid robotics.
          Start your journey today.
        </p>
        <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
          <Link className="neurobot-btn-primary" to="/docs/chapter-1">
            Begin Chapter 1
          </Link>
          <Link className="neurobot-btn-secondary" to="/docs/module-1-ros2/chapter-3">
            Explore ROS 2
          </Link>
        </div>
      </section>
    </Layout>
  );
}
