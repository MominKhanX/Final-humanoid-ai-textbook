<!--
  SYNC IMPACT REPORT
  ==================
  Version Change: INITIAL → 1.0.0
  Type: MINOR (initial constitution creation)
  Date: 2025-12-15

  Modified Principles:
  - NEW: I. Educational Excellence
  - NEW: II. AI-Native Architecture
  - NEW: III. Technical Rigor
  - NEW: IV. Accessibility & Inclusivity
  - NEW: V. Content Completeness
  - NEW: VI. Code Quality & Reproducibility

  Added Sections:
  - Content Structure Standards
  - Technical Implementation Standards
  - Constraints & Requirements
  - Success Criteria & Evaluation

  Templates Status:
  ✅ plan-template.md - Reviewed, compatible with constitution checks
  ✅ spec-template.md - Reviewed, aligns with user story requirements
  ✅ tasks-template.md - Reviewed, supports user story-based organization

  Follow-up TODOs:
  - None (all placeholders filled)
-->

# AI-Native Textbook for Physical AI & Humanoid Robotics Course Constitution

## Core Principles

### I. Educational Excellence

Every piece of content MUST be technically accurate and pedagogically sound. This principle is NON-NEGOTIABLE and enforced through:

- **Theory-Practice Bridge**: All theoretical concepts MUST be accompanied by practical implementation examples
- **Progressive Learning Curve**: Content difficulty MUST progress from fundamentals to advanced concepts within each module
- **Real-World Applicability**: All examples and projects MUST be relevant to humanoid robotics and embodied AI applications
- **Clear Learning Objectives**: Every chapter MUST state explicit learning objectives at the start
- **Assessment Integration**: Every chapter MUST end with assessment questions or hands-on exercises
- **Estimated Reading Time**: Each chapter MUST provide estimated reading time (15-25 minutes per chapter)

**Rationale**: This is an educational product. Technical accuracy and pedagogical soundness are the foundation of student trust and learning outcomes.

### II. AI-Native Architecture

The textbook MUST integrate conversational AI seamlessly as a core learning companion, not an afterthought. Requirements:

- **RAG Chatbot Integration**: OpenAI Agents/ChatKit SDK implementation with Qdrant vector store
- **Context-Aware Responses**: Chatbot MUST use book content as knowledge base for accurate responses
- **Selected Text Queries**: Users MUST be able to highlight text and ask questions about it
- **Intelligent Personalization**: Content adaptation based on user background (software/hardware experience, ROS 2 knowledge, programming proficiency)
- **Source Citations**: Chatbot responses MUST cite specific chapters/sections
- **Response Performance**: <3 seconds for typical queries (NON-NEGOTIABLE)

**Rationale**: This is not just a book—it's an intelligent learning companion. The AI integration defines the product's competitive advantage.

### III. Technical Rigor

All technical content, code examples, and hardware specifications MUST be accurate, tested, and reproducible. Mandatory requirements:

- **Code Verification**: All code examples MUST be tested on Ubuntu 22.04 LTS
- **Version Specifications**: Software versions MUST be explicitly specified (ROS 2 Humble/Iron, NVIDIA Isaac versions)
- **Hardware Accuracy**: Hardware specifications MUST match current market availability (as of Nov 2025)
- **Working Examples**: Minimum 20 working code examples across all modules
- **Dependencies Documented**: Include requirements.txt, package.xml, or equivalent for all examples
- **Setup Instructions**: Provide complete setup instructions for each major example
- **Troubleshooting Sections**: Include troubleshooting guidance for common issues
- **External Links Verified**: All external links MUST be functional before deployment

**Rationale**: Broken code examples destroy student trust and learning momentum. Reproducibility is fundamental to technical education.

### IV. Accessibility & Inclusivity

Content MUST be accessible to learners with varying backgrounds and across multiple languages and devices. Requirements:

- **Clear Explanations**: Technical concepts explained for learners with varying backgrounds
- **Bilingual Support**: English/Urdu translation capability (BONUS feature, but if implemented, MUST be high-quality)
- **Responsive Design**: Book MUST work on desktop, tablet, and mobile devices
- **Progressive Disclosure**: Complex topics introduced gradually, avoiding information overload
- **Browser Compatibility**: Support Chrome, Firefox, Safari (latest 2 versions)
- **Loading Performance**: <5 seconds on standard broadband (NON-NEGOTIABLE)
- **Dark/Light Mode**: Both themes MUST be supported

**Rationale**: Inclusivity expands the potential student base and aligns with Panaversity's mission of accessible education.

### V. Content Completeness

Module structure MUST follow the 4-module, 18-22 chapter framework. This is NON-NEGOTIABLE:

- **Module 1: The Robotic Nervous System (ROS 2)** - Weeks 3-5 - 4-5 chapters
  - Topics: ROS 2 architecture, nodes/topics/services, Python packages, launch files, URDF
- **Module 2: The Digital Twin (Gazebo & Unity)** - Weeks 6-7 - 4-5 chapters
  - Topics: Simulation setup, URDF/SDF, physics/sensors, Unity visualization, Gazebo-ROS 2 integration
- **Module 3: The AI-Robot Brain (NVIDIA Isaac™)** - Weeks 8-10 - 4-5 chapters
  - Topics: Isaac SDK/Sim, AI perception, RL for control, sim-to-real transfer, hardware-accelerated VSLAM
- **Module 4: Vision-Language-Action (VLA)** - Weeks 11-13 - 4-5 chapters
  - Topics: Whisper voice-to-action, LLMs for planning, multi-modal interaction, capstone project, debugging/deployment
- **Additional: Introduction to Physical AI** - Weeks 1-2 - 2-3 chapters (recommended but not mandatory)

**Chapter Quality Requirements**:
- Minimum 18 chapters total (4 modules × 4 chapters + intro)
- Recommended 20-22 chapters for comprehensive coverage
- Each chapter: learning objectives + practical examples + exercises + assessments
- Minimum 30 technical diagrams/illustrations across all modules

**Rationale**: Content completeness is a base requirement (100 points). Incomplete coverage fails to deliver on the hackathon promise.

### VI. Code Quality & Reproducibility

All code MUST be production-ready and follow established conventions. Mandatory standards:

- **Python Style**: All Python code follows PEP 8 style guide
- **ROS 2 Conventions**: ROS 2 code follows official ROS conventions
- **Inline Comments**: Complex logic MUST include inline comments
- **README Files**: Each major example MUST have a README
- **Hardware Setup Guides**: Provide hardware setup documentation where needed
- **Claude Code Usage**: All content generation/management via Claude Code
- **Spec-Kit Plus**: Use Spec-Kit Plus for project structure and specifications
- **Reusable Subagents**: Create reusable Subagents for repetitive tasks (BONUS - 50 points)
- **Agent Skills**: Implement Agent Skills for domain-specific operations (BONUS - 50 points)

**Rationale**: Code quality directly impacts student learning experience. Poor code creates frustration; clean code builds confidence.

## Content Structure Standards

### Module Organization (MANDATORY)

- **4 Core Modules**: Each covering 3-4 weeks of coursework
- **4-5 Chapters Per Module**: Depth and comprehensive coverage required
- **Total Chapter Count**: Minimum 18, recommended 20-22 chapters
- **Chapter Length**: 15-25 minutes estimated reading time per chapter
- **Navigation**: Sidebar + breadcrumbs for easy traversal
- **Search Functionality**: Full-text search across all content

### Hardware Coverage (MANDATORY)

All four hardware categories MUST be documented:

1. **Workstation Requirements**
   - GPU: NVIDIA RTX 4070 Ti minimum (12GB VRAM), RTX 4090 recommended (24GB)
   - CPU: Intel i7 13th Gen+ or AMD Ryzen 9
   - RAM: 64GB DDR5 (32GB minimum)
   - OS: Ubuntu 22.04 LTS

2. **Edge Computing Kit**
   - NVIDIA Jetson Orin Nano (8GB) or Orin NX (16GB)
   - Intel RealSense D435i or D455
   - USB IMU (BNO055) if needed
   - ReSpeaker USB Mic Array

3. **Robot Hardware Options**
   - Budget: Unitree Go2 Edu ($1,800-$3,000)
   - Mid-range: Unitree G1 ($16,000)
   - Premium: Full humanoid platforms
   - Alternative: Hiwonder TonyPi Pro ($600)

4. **Cloud Alternative**
   - AWS g5.2xlarge or g6e.xlarge instances
   - Cost breakdown per quarter
   - Sim-to-real transfer workflow

### Software Stack Coverage (MANDATORY)

All listed topics MUST be covered across the 4 modules:

- ROS 2 (Humble/Iron) architecture
- URDF/SDF robot description
- Gazebo physics simulation
- Unity for visualization
- NVIDIA Isaac Sim workflow
- Isaac ROS perception
- Nav2 path planning
- OpenAI Whisper integration
- LLM-to-action pipelines

## Technical Implementation Standards

### Book Platform (Docusaurus)

- **Platform**: Docusaurus (latest stable version)
- **Deployment**: GitHub Pages or Vercel (public deployment required)
- **Design**: Responsive (desktop/tablet/mobile)
- **Themes**: Dark/light mode support
- **Search**: Integrated search functionality
- **Performance**: <5 seconds loading time on standard broadband

### RAG Chatbot (MANDATORY)

- **SDK**: OpenAI Agents/ChatKit SDKs
- **Backend**: FastAPI
- **Database**: Neon Serverless Postgres
- **Vector Store**: Qdrant Cloud (Free Tier)
- **Features**:
  - General Q&A about book content
  - Selected text queries (highlight → ask)
  - Context-aware follow-up questions
  - Source citation (chapter/section references)
  - <3 seconds response time

### Authentication System (BONUS - 50 points)

If implemented, MUST use Better-Auth (https://www.better-auth.com/) and collect:

- Software background (AI/ML experience level)
- Hardware background (robotics/electronics experience)
- Prior ROS 2 knowledge
- Programming proficiency (Python, C++)
- User profiles stored securely with session management

### Personalization (BONUS - 50 points)

If implemented:

- Button at chapter start for personalization toggle
- Content adapts to beginner/intermediate/advanced levels
- Uses stored user background effectively
- Smooth UX for enabling/disabling personalization

### Translation (BONUS - 50 points)

If implemented:

- Translation button at chapter start
- High-quality Urdu technical translation (not machine-generated gibberish)
- Maintains formatting and code blocks
- Bidirectional text rendering correct

## Constraints & Requirements

### Technical Constraints (NON-NEGOTIABLE)

- **Deployment**: GitHub Pages or Vercel (public URL required)
- **Repository**: Public GitHub repo with meaningful commits (not one giant commit)
- **Demo Video**: Maximum 90 seconds showcasing key features
- **Chatbot Response**: <3 seconds for typical queries
- **Book Loading**: <5 seconds on standard broadband
- **Browser Support**: Chrome, Firefox, Safari (latest 2 versions)
- **Security**: NO API keys exposed in public repo (use environment variables)

### Content Constraints (NON-NEGOTIABLE)

- **Minimum Chapters**: 18 chapters (4-5 per module across 4 modules)
- **Recommended Chapters**: 20-22 chapters for comprehensive coverage
- **Code Examples**: Minimum 20 working examples across all modules
- **Visuals**: Minimum 30 technical diagrams/illustrations
- **Assessment Items**: Minimum 4 assessment/project descriptions
- **External Resources**: Properly cited and hyperlinked

### Timeline Constraints (CRITICAL)

- **Submission Deadline**: Sunday, November 30, 2025 at 6:00 PM PKT (HARD DEADLINE)
- **Form Closes**: Exactly at 6:00 PM (late submissions NOT accepted)
- **Live Presentations**: Sunday, November 30, 2025 starting at 6:00 PM on Zoom

## Success Criteria & Evaluation

### Base Requirements (100 points - MUST COMPLETE)

- [ ] Docusaurus book deployed successfully with public URL
- [ ] RAG chatbot functional and embedded in book
- [ ] All 4 modules covered comprehensively
- [ ] ChatKit integration working properly
- [ ] Selected text query feature operational
- [ ] Neon Postgres + Qdrant properly configured
- [ ] Public GitHub repo with clear README
- [ ] 90-second demo video submitted
- [ ] Minimum 18 chapters with proper structure
- [ ] Minimum 20 working code examples
- [ ] Minimum 30 technical diagrams

### Bonus Achievements (Up to 200 additional points)

- **Subagents & Agent Skills** (50 points): Reusable components demonstrating efficiency gains
- **Authentication & User Profiling** (50 points): Better-Auth with secure profile storage
- **Content Personalization** (50 points): Background-based content adaptation with smooth UX
- **Urdu Translation** (50 points): High-quality technical translation with proper rendering

### Quality Indicators (Evaluated During Presentation)

- **User Experience**: Intuitive navigation, fast load times, professional design
- **Content Depth**: Comprehensive coverage without overwhelming students
- **Code Quality**: Clean, commented, reproducible examples
- **Chatbot Intelligence**: Accurate, contextual responses with proper citations
- **Visual Design**: Professional, consistent, accessible styling
- **Documentation**: Clear setup and usage instructions in README

## Governance

This constitution supersedes all other practices and documents in this project. All development work, content creation, and feature implementation MUST verify compliance with these principles.

### Amendment Process

- **Version Numbering**: MAJOR.MINOR.PATCH semantic versioning
  - MAJOR: Backward-incompatible governance/principle removals or redefinitions
  - MINOR: New principle/section added or materially expanded guidance
  - PATCH: Clarifications, wording, typo fixes, non-semantic refinements
- **Documentation**: All amendments MUST include rationale and migration plan
- **Propagation**: Template updates MUST be synchronized with constitution changes
- **Approval**: Constitution changes require explicit user consent and documentation

### Compliance Review

- All PRs/reviews MUST verify compliance with Core Principles I-VI
- Content Structure Standards MUST be validated before deployment
- Technical Implementation Standards MUST be tested end-to-end
- Complexity or deviations MUST be justified in plan.md Complexity Tracking section
- Use CLAUDE.md for runtime development guidance and PHR creation requirements

### Success Measurement

This project's success is measured by:

1. **Functional Completeness**: All base requirements (100 points) delivered and working
2. **Technical Excellence**: Code quality, performance, and reproducibility standards met
3. **Educational Impact**: Content clarity, accuracy, and pedagogical effectiveness
4. **Innovation**: Bonus features implemented with high quality (up to 200 additional points)
5. **Presentation Quality**: Ability to demonstrate value and impact in 90-second demo

### Risk Mitigation

Common pitfalls to avoid:

- **Over-ambitious scope**: Focus on base requirements first, add bonuses incrementally
- **API rate limits**: Implement proper error handling for OpenAI calls
- **Large file sizes**: Optimize images and videos for web delivery
- **Security**: Never commit API keys or credentials to public repo
- **Browser compatibility**: Test on multiple browsers throughout development
- **Last-minute deployment issues**: Deploy early, iterate often

**Version**: 1.0.0 | **Ratified**: 2025-12-15 | **Last Amended**: 2025-12-15
