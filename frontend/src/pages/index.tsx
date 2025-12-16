import React from 'react';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';
import styles from './index.module.css';

export default function Home(): JSX.Element {
  return (
    <Layout
      title="NeuroBot Physical AI & Humanoid Robotics"
      description="A comprehensive, university-level guide to building intelligent humanoid robots with ROS 2, NVIDIA Isaac, and Vision-Language-Action models">

      {/* Hero Section */}
      <section className={styles.hero}>
        <div className={styles.heroBackground}>01</div>
        <div className={styles.heroContent}>
          <div className={styles.heroBadge}>Humanoid AI Textbook</div>
          <h1 className={styles.heroTitle}>
            Master <span className={styles.highlight}>NeuroBot</span> Architecture
          </h1>
          <p className={styles.heroSubtitle}>
            A comprehensive, university-level guide to Physical AI & Humanoid Robotics
          </p>
          <div className={styles.heroCTA}>
            <Link to="/docs/intro" className={styles.btnPrimary}>
              Start Learning
            </Link>
            <Link to="/docs/intro" className={styles.btnSecondary}>
              View Syllabus
            </Link>
          </div>
        </div>
      </section>

      {/* Diamond Separator */}
      <div className={styles.diamondSeparator}>◆</div>

      {/* Features Grid */}
      <section className={styles.featuresSection}>
        <div className={styles.container}>
          <h2 className={styles.sectionTitle}>Complete Curriculum for Physical AI</h2>
          <p className={styles.sectionSubtitle}>
            Master the essential technologies powering next-generation humanoid robots
          </p>

          <div className={styles.featuresGrid}>
            {/* Module 1: ROS 2 */}
            <Link to="/docs/module-1-ros2/chapter-1" className={styles.featureCard}>
              <div className={styles.featureIcon}>🤖</div>
              <h3 className={styles.featureTitle}>Module 1: ROS 2</h3>
              <p className={styles.featureSubtitle}>The Robotic Nervous System</p>
              <p className={styles.featureDescription}>
                Master Robot Operating System 2 architecture, nodes, topics, services, and actions.
                Learn to build distributed robotic systems with modern middleware.
              </p>
            </Link>

            {/* Module 2: Digital Twin */}
            <Link to="/docs/module-2-digital-twin/chapter-1" className={styles.featureCard}>
              <div className={styles.featureIcon}>🌐</div>
              <h3 className={styles.featureTitle}>Module 2: Gazebo & Unity</h3>
              <p className={styles.featureSubtitle}>Digital Twin Simulation</p>
              <p className={styles.featureDescription}>
                Create high-fidelity robot simulations with Gazebo and Unity. Master URDF modeling,
                physics engines, and photorealistic rendering for sim-to-real transfer.
              </p>
            </Link>

            {/* Module 3: NVIDIA Isaac */}
            <Link to="/docs/module-3-nvidia-isaac/chapter-1" className={styles.featureCard}>
              <div className={styles.featureIcon}>⚡</div>
              <h3 className={styles.featureTitle}>Module 3: NVIDIA Isaac</h3>
              <p className={styles.featureSubtitle}>AI-Powered Robotics</p>
              <p className={styles.featureDescription}>
                Leverage Isaac SDK for AI perception, reinforcement learning with Isaac Gym,
                and hardware-accelerated VSLAM for intelligent robot navigation.
              </p>
            </Link>

            {/* Module 4: VLA */}
            <Link to="/docs/module-4-vla/chapter-1" className={styles.featureCard}>
              <div className={styles.featureIcon}>💬</div>
              <h3 className={styles.featureTitle}>Module 4: VLA</h3>
              <p className={styles.featureSubtitle}>Vision-Language-Action Models</p>
              <p className={styles.featureDescription}>
                Train humanoid robots for natural social interaction using cutting-edge
                Vision-Language-Action models and cognitive architectures.
              </p>
            </Link>
          </div>
        </div>
      </section>

      {/* Diamond Separator */}
      <div className={styles.diamondSeparator}>◆</div>

      {/* Course Overview */}
      <section className={styles.overviewSection}>
        <div className={styles.container}>
          <div className={styles.overviewGrid}>
            <div className={styles.overviewContent}>
              <h2 className={styles.sectionTitle}>What You'll Learn</h2>
              <p className={styles.overviewText}>
                This comprehensive textbook guides you through building intelligent humanoid robots
                from the ground up. You'll master the complete technology stack—from low-level robot
                control with ROS 2, to high-fidelity simulation with Gazebo and Unity, to cutting-edge
                AI perception and decision-making with NVIDIA Isaac and Vision-Language-Action models.
              </p>
              <p className={styles.overviewText}>
                Each module combines rigorous technical content with hands-on examples, preparing you
                to design, build, and deploy production-ready humanoid robotic systems.
              </p>
            </div>

            <div className={styles.overviewSidebar}>
              <div className={styles.infoBox}>
                <h3 className={styles.infoBoxTitle}>Prerequisites</h3>
                <ul className={styles.infoBoxList}>
                  <li>Python programming fundamentals</li>
                  <li>Basic understanding of linear algebra</li>
                  <li>Familiarity with Linux/Ubuntu</li>
                  <li>Programming experience (any language)</li>
                </ul>
              </div>

              <div className={styles.infoBox}>
                <h3 className={styles.infoBoxTitle}>Expected Outcomes</h3>
                <ul className={styles.infoBoxList}>
                  <li>Build distributed robotic systems with ROS 2</li>
                  <li>Create high-fidelity robot simulations</li>
                  <li>Implement AI-powered perception and control</li>
                  <li>Deploy humanoid robots with social intelligence</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Diamond Separator */}
      <div className={styles.diamondSeparator}>◆</div>

      {/* CTA Section */}
      <section className={styles.ctaSection}>
        <div className={styles.container}>
          <h2 className={styles.ctaTitle}>Ready to Begin Your Journey?</h2>
          <p className={styles.ctaSubtitle}>
            Join thousands of engineers and researchers mastering Physical AI and Humanoid Robotics
          </p>
          <Link to="/docs/intro" className={styles.btnPrimary}>
            Start Learning Now
          </Link>
        </div>
      </section>
    </Layout>
  );
}
