---

description: "Task list for Docusaurus initialization feature"
---

# Tasks: NeuroBot Docusaurus Textbook Initialization

**Input**: Design documents from `/specs/001-docusaurus-init/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are NOT explicitly requested in the feature specification, so test tasks are not included.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: Root directory contains all Docusaurus files
- Paths shown below assume repository root

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Verify Node.js version 18.x or higher is installed
- [ ] T002 Verify npm package manager is available
- [ ] T003 Verify Git is configured and repository access is available

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T004 Initialize a Docusaurus project using npx create-docusaurus@latest with the classic template.
Create a frontend folder in the root directory, and initialize the Docusaurus project inside this folder
- [ ] T005 Configure package.json engines field to specify Node.js 18.x minimum version
- [ ] T006 [P] Install required dependencies (Docusaurus 3.x, React 18, TypeScript types)
- [ ] T007 [P] Create src/components/ directory for custom React components
- [ ] T008 [P] Create src/pages/ directory for custom pages
- [ ] T009 [P] Create src/css/ directory for custom styles
- [ ] T010 [P] Create src/theme/ directory for theme customizations
- [ ] T011 [P] Create static/img/ directory for static assets
- [ ] T012 Create basic docusaurus.config.js with site title "NeuroBot Physical AI & Humanoid Robotics Textbook"
- [ ] T013 Verify development server starts without errors using npm run start
- [ ] T014 Verify production build completes successfully using npm run build

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Project Foundation Setup (Priority: P1) 🎯 MVP

**Goal**: Initialize a Docusaurus project with correct configuration for solid foundation

**Independent Test**: Run `npm run build` successfully and verify generated static site contains correct module structure and default configuration

### Implementation for User Story 1

- [ ] T015 [US1] Update docusaurus.config.js with project metadata (title, tagline, favicon path)
- [ ] T016 [US1] Configure docusaurus.config.js with proper site metadata for SEO (description, keywords)
- [ ] T017 [US1] Add themeConfig section to docusaurus.config.js with navbar configuration
- [ ] T018 [US1] Add footer configuration to docusaurus.config.js with copyright and links
- [ ] T019 [US1] Create docs/ directory in repository root
- [ ] T020 [US1] Create docs/intro.mdx as main landing page with welcome message and course overview
- [ ] T021 [US1] Add frontmatter to docs/intro.mdx (title: "Welcome to NeuroBot Textbook", sidebar_position: 1)
- [ ] T022 [US1] Create basic sidebars.js configuration file with tutorial sidebar structure
- [ ] T023 [US1] Test development server startup time (should be under 10 seconds)
- [ ] T024 [US1] Test production build completion time (should be under 30 seconds)
- [ ] T025 [US1] Verify build output directory contains index.html and assets

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently - basic Docusaurus site runs and builds successfully

---

## Phase 4: User Story 2 - Module Structure Configuration (Priority: P2)

**Goal**: Create textbook module structure properly organized for educational content following 13-week curriculum

**Independent Test**: Verify all 5 module directories exist with proper naming, contain placeholder chapter files (2-3 for intro, 4-5 for each main module), and appear in sidebar navigation in correct educational flow order

### Implementation for User Story 2

- [ ] T026 [P] [US2] Create docs/introduction/ directory for introduction module
- [ ] T027 [P] [US2] Create docs/module-1-ros2/ directory for ROS 2 module
- [ ] T028 [P] [US2] Create docs/module-2-digital-twin/ directory for Digital Twin module
- [ ] T029 [P] [US2] Create docs/module-3-nvidia-isaac/ directory for NVIDIA Isaac module
- [ ] T030 [P] [US2] Create docs/module-4-vla/ directory for Vision-Language-Action module
- [ ] T031 [P] [US2] Create docs/introduction/chapter-1.mdx with frontmatter (title: "What is Physical AI?", description: "Introduction to Physical AI concepts", sidebar_position: 1)
- [ ] T032 [P] [US2] Create docs/introduction/chapter-2.mdx with frontmatter (title: "Humanoid Robotics Overview", description: "Overview of humanoid robotics field", sidebar_position: 2)
- [ ] T033 [P] [US2] Create docs/introduction/chapter-3.mdx with frontmatter (title: "Course Structure and Learning Path", description: "How this course is organized", sidebar_position: 3)
- [ ] T034 [P] [US2] Create docs/module-1-ros2/chapter-1.mdx with frontmatter (title: "Introduction to ROS 2 Architecture", sidebar_position: 1)
- [ ] T035 [P] [US2] Create docs/module-1-ros2/chapter-2.mdx with frontmatter (title: "Nodes, Topics, and Services", sidebar_position: 2)
- [ ] T036 [P] [US2] Create docs/module-1-ros2/chapter-3.mdx with frontmatter (title: "Building ROS 2 Packages with Python", sidebar_position: 3)
- [ ] T037 [P] [US2] Create docs/module-1-ros2/chapter-4.mdx with frontmatter (title: "Launch Files and Parameter Management", sidebar_position: 4)
- [ ] T038 [P] [US2] Create docs/module-1-ros2/chapter-5.mdx with frontmatter (title: "URDF for Humanoid Robots", sidebar_position: 5)
- [ ] T039 [P] [US2] Create docs/module-2-digital-twin/chapter-1.mdx with frontmatter (title: "Gazebo Simulation Environment Setup", sidebar_position: 1)
- [ ] T040 [P] [US2] Create docs/module-2-digital-twin/chapter-2.mdx with frontmatter (title: "Robot Description Formats (URDF/SDF)", sidebar_position: 2)
- [ ] T041 [P] [US2] Create docs/module-2-digital-twin/chapter-3.mdx with frontmatter (title: "Physics and Sensor Simulation", sidebar_position: 3)
- [ ] T042 [P] [US2] Create docs/module-2-digital-twin/chapter-4.mdx with frontmatter (title: "Unity for Robot Visualization", sidebar_position: 4)
- [ ] T043 [P] [US2] Create docs/module-2-digital-twin/chapter-5.mdx with frontmatter (title: "Integrating Gazebo with ROS 2", sidebar_position: 5)
- [ ] T044 [P] [US2] Create docs/module-3-nvidia-isaac/chapter-1.mdx with frontmatter (title: "NVIDIA Isaac SDK and Isaac Sim", sidebar_position: 1)
- [ ] T045 [P] [US2] Create docs/module-3-nvidia-isaac/chapter-2.mdx with frontmatter (title: "AI-Powered Perception", sidebar_position: 2)
- [ ] T046 [P] [US2] Create docs/module-3-nvidia-isaac/chapter-3.mdx with frontmatter (title: "Reinforcement Learning for Robot Control", sidebar_position: 3)
- [ ] T047 [P] [US2] Create docs/module-3-nvidia-isaac/chapter-4.mdx with frontmatter (title: "Sim-to-Real Transfer Techniques", sidebar_position: 4)
- [ ] T048 [P] [US2] Create docs/module-3-nvidia-isaac/chapter-5.mdx with frontmatter (title: "Hardware-Accelerated VSLAM", sidebar_position: 5)
- [ ] T049 [P] [US2] Create docs/module-4-vla/chapter-1.mdx with frontmatter (title: "Voice-to-Action with OpenAI Whisper", sidebar_position: 1)
- [ ] T050 [P] [US2] Create docs/module-4-vla/chapter-2.mdx with frontmatter (title: "LLMs for Cognitive Planning", sidebar_position: 2)
- [ ] T051 [P] [US2] Create docs/module-4-vla/chapter-3.mdx with frontmatter (title: "Multi-Modal Interaction Design", sidebar_position: 3)
- [ ] T052 [P] [US2] Create docs/module-4-vla/chapter-4.mdx with frontmatter (title: "Capstone Project: Autonomous Humanoid", sidebar_position: 4)
- [ ] T053 [P] [US2] Create docs/module-4-vla/chapter-5.mdx with frontmatter (title: "Debugging and Deployment", sidebar_position: 5)
- [ ] T054 [US2] Update sidebars.js to include introduction module as collapsible category
- [ ] T055 [US2] Update sidebars.js to include module-1-ros2 as collapsible category with label "Module 1: The Robotic Nervous System (ROS 2)"
- [ ] T056 [US2] Update sidebars.js to include module-2-digital-twin as collapsible category with label "Module 2: The Digital Twin (Gazebo & Unity)"
- [ ] T057 [US2] Update sidebars.js to include module-3-nvidia-isaac as collapsible category with label "Module 3: The AI-Robot Brain (NVIDIA Isaac™)"
- [ ] T058 [US2] Update sidebars.js to include module-4-vla as collapsible category with label "Module 4: Vision-Language-Action (VLA)"
- [ ] T059 [US2] Verify all 5 modules appear in sidebar navigation in correct educational flow order
- [ ] T060 [US2] Verify each module shows correct number of chapters (3 for intro, 5 for each main module = 23 total)
- [ ] T061 [US2] Test navigation between all generated pages works correctly
- [ ] T062 [US2] Verify build process generates static HTML for all 23 placeholder chapters

**Checkpoint**: At this point, User Story 2 should be fully functional and testable independently - all module directories exist with placeholder chapters and sidebar navigation works

---

## Phase 5: User Story 3 - GitHub Pages Deployment Configuration (Priority: P3)

**Goal**: Configure site for GitHub Pages deployment for public accessibility at correct URL

**Independent Test**: Run build command and verify generated files have correct base URL, or deploy to GitHub Pages and confirm site loads correctly at https://mominkhanx.github.io/neurobot-textbook/

### Implementation for User Story 3

- [ ] T063 [US3] Update docusaurus.config.js url field to "https://mominkhanx.github.io"
- [ ] T064 [US3] Update docusaurus.config.js baseUrl field to "/neurobot-textbook/"
- [ ] T065 [US3] Update docusaurus.config.js organizationName field to "MominKhanX"
- [ ] T066 [US3] Update docusaurus.config.js projectName field to "neurobot-textbook"
- [ ] T067 [US3] Update docusaurus.config.js deploymentBranch field to "gh-pages"
- [ ] T068 [US3] Add trailingSlash configuration to docusaurus.config.js (set to false for GitHub Pages compatibility)
- [ ] T069 [US3] Create .github/workflows/ directory for GitHub Actions
- [ ] T070 [US3] Create .github/workflows/deploy.yml with GitHub Pages deployment workflow
- [ ] T071 [US3] Configure deploy.yml to trigger on push to main branch
- [ ] T072 [US3] Configure deploy.yml to build Docusaurus site using npm run build
- [ ] T073 [US3] Configure deploy.yml to deploy to gh-pages branch using peaceiris/actions-gh-pages action
- [ ] T074 [US3] Test build output locally to verify baseUrl is applied to all asset paths
- [ ] T075 [US3] Verify all internal links use correct base URL prefix
- [ ] T076 [US3] Test built site locally using npx serve build to simulate GitHub Pages environment
- [ ] T077 [US3] Verify no 404 errors for CSS, JavaScript, or image assets in local test

**Checkpoint**: All user stories 1-3 should now work independently - site is ready for GitHub Pages deployment

---

## Phase 6: User Story 4 - Theme and UI Configuration (Priority: P4)

**Goal**: Apply professional academic appearance with dark mode as default for comfortable reading experience

**Independent Test**: Start development server and verify dark mode is active by default, color scheme uses royal indigo accents, and UI renders correctly on desktop and mobile viewports

### Implementation for User Story 4

- [ ] T078 [US4] Create src/css/custom.css file for theme customizations
- [ ] T079 [US4] Define CSS custom properties in custom.css for royal indigo primary color (#4338ca)
- [ ] T080 [US4] Define CSS custom properties for royal indigo variations (dark: #3730a3, light: #6366f1, lighter: #818cf8)
- [ ] T081 [US4] Define CSS custom property for dark background colors (#0d1117 for scholarly dark charcoal)
- [ ] T082 [US4] Define CSS custom property for academic typography (--ifm-font-family-base: Georgia, "Times New Roman", serif)
- [ ] T083 [US4] Update docusaurus.config.js themeConfig with colorMode configuration (defaultMode: "dark", disableSwitch: false, respectPrefersColorScheme: false)
- [ ] T084 [US4] Add navbar title and logo configuration to themeConfig in docusaurus.config.js
- [ ] T085 [US4] Add docs sidebar configuration to themeConfig (hideable: true for mobile)
- [ ] T086 [US4] Configure prism theme in themeConfig for code syntax highlighting (light: github, dark: dracula)
- [ ] T087 [US4] Add responsive breakpoints to custom.css for desktop (1920px), tablet (768px), mobile (375px)
- [ ] T088 [US4] Add CSS media queries to custom.css for tablet viewport adaptations
- [ ] T089 [US4] Add CSS media queries to custom.css for mobile viewport adaptations
- [ ] T090 [US4] Configure Algolia DocSearch in themeConfig (or use default Docusaurus search for MVP)
- [ ] T091 [US4] Add metadata configuration to docusaurus.config.js for SEO (description, og:image, twitter:card)
- [ ] T092 [US4] Test dark mode is active by default on first site visit
- [ ] T093 [US4] Test theme toggle switches between dark and light modes correctly
- [ ] T094 [US4] Test royal indigo colors appear in primary UI elements (links, buttons, active nav items)
- [ ] T095 [US4] Test responsive layout on desktop viewport (1920px width) - verify no layout breaking
- [ ] T096 [US4] Test responsive layout on tablet viewport (768px width) - verify sidebar becomes hideable
- [ ] T097 [US4] Test responsive layout on mobile viewport (375px width) - verify content is readable and navigation works
- [ ] T098 [US4] Verify academic typography (Georgia serif) appears in body text
- [ ] T099 [US4] Test navigation between pages preserves dark mode preference
- [ ] T100 [US4] Verify search functionality returns results for placeholder chapter content

**Checkpoint**: All user stories should now be independently functional - complete textbook site with proper theming ready for deployment

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements and validation that affect multiple user stories

- [ ] T101 [P] Add README.md in repository root with project overview, setup instructions, and deployment guide
- [ ] T102 [P] Add .gitignore file with Node.js, Docusaurus build artifacts, and IDE files
- [ ] T103 [P] Create LICENSE file (if required by project)
- [ ] T104 Verify all 23 placeholder chapters have proper frontmatter (title, description, sidebar_position)
- [ ] T105 Run final production build and measure build time (should be under 30 seconds)
- [ ] T106 Measure development server startup time (should be under 10 seconds)
- [ ] T107 Test page load time for any chapter (should be under 2 seconds on standard broadband)
- [ ] T108 Validate WCAG 2.1 AA color contrast compliance for dark mode theme
- [ ] T109 Test keyboard navigation works correctly throughout the site
- [ ] T110 Verify site works correctly on latest 2 versions of Chrome, Firefox, Safari, Edge
- [ ] T111 Run Lighthouse audit and verify scores (Performance, Accessibility, Best Practices, SEO)
- [ ] T112 Create deployment documentation in README.md with GitHub Pages deployment steps
- [ ] T113 Validate constitution compliance (5 modules, 23 chapters, dark mode default, responsive design, <5s load time)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User Story 1 (P1): Can start after Foundational - No dependencies on other stories
  - User Story 2 (P2): Can start after Foundational - No dependencies on other stories (but logically follows US1)
  - User Story 3 (P3): Can start after Foundational - No dependencies on other stories (but logically follows US1)
  - User Story 4 (P4): Can start after Foundational - No dependencies on other stories (but logically follows US1)
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Logically follows US1 but technically independent
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Requires US1 configuration to exist
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - Enhances US1 foundation

### Within Each User Story

- Tasks marked [P] can run in parallel (different files, no dependencies)
- Configuration tasks (docusaurus.config.js updates) should be done sequentially
- File creation tasks can mostly run in parallel
- Verification tasks should be done after implementation tasks complete

### Parallel Opportunities

- All Setup tasks (T001-T003) can run in parallel
- Foundational directory creation tasks (T007-T011) can run in parallel
- All User Story 2 chapter file creation tasks (T031-T053) can run in parallel - 23 files total
- User Story 3 workflow configuration tasks can be done in parallel with other user stories
- User Story 4 CSS and theme tasks can be developed in parallel with other user stories

---

## Parallel Example: User Story 2 (Module Structure)

```bash
# Launch all module directory creation together (T026-T030):
Task: "Create docs/introduction/ directory"
Task: "Create docs/module-1-ros2/ directory"
Task: "Create docs/module-2-digital-twin/ directory"
Task: "Create docs/module-3-nvidia-isaac/ directory"
Task: "Create docs/module-4-vla/ directory"

# Launch all introduction chapter creation together (T031-T033):
Task: "Create docs/introduction/chapter-1.mdx with frontmatter"
Task: "Create docs/introduction/chapter-2.mdx with frontmatter"
Task: "Create docs/introduction/chapter-3.mdx with frontmatter"

# Launch all module-1-ros2 chapter creation together (T034-T038):
Task: "Create docs/module-1-ros2/chapter-1.mdx with frontmatter"
Task: "Create docs/module-1-ros2/chapter-2.mdx with frontmatter"
Task: "Create docs/module-1-ros2/chapter-3.mdx with frontmatter"
Task: "Create docs/module-1-ros2/chapter-4.mdx with frontmatter"
Task: "Create docs/module-1-ros2/chapter-5.mdx with frontmatter"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004-T014) - CRITICAL - blocks all stories
3. Complete Phase 3: User Story 1 (T015-T025)
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

This gives you a working Docusaurus site that builds successfully - minimal viable product.

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → MVP complete (basic working site)
3. Add User Story 2 → Test independently → Content structure ready (all modules and chapters)
4. Add User Story 3 → Test independently → Deployment ready (GitHub Pages configured)
5. Add User Story 4 → Test independently → Production ready (themed and polished)
6. Add Polish phase → Final validation → Release ready
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Foundation)
   - Developer B: User Story 2 (Module Structure) - can work in parallel with A after US1 basic config exists
   - Developer C: User Story 3 (Deployment) - can work in parallel
   - Developer D: User Story 4 (Theme) - can work in parallel
3. Stories complete and integrate independently

However, for single developer, recommended sequential order: US1 → US2 → US3 → US4

---

## Notes

- [P] tasks = different files, no dependencies (can execute in parallel)
- [Story] label maps task to specific user story for traceability (US1-US4)
- Each user story should be independently completable and testable
- Total chapters: 23 (3 intro + 5×4 main modules = 3+20 = 23) - exceeds minimum 18 requirement
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- All file paths are relative to repository root
- Tests are NOT included (not requested in specification)
- Verification tasks substitute for formal testing
