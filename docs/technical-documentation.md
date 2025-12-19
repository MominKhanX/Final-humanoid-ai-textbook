# NeuroBot Physical AI & Humanoid Robotics Textbook - Technical Documentation

## Project Overview

The NeuroBot textbook is a comprehensive, university-level resource for learning Physical AI and Humanoid Robotics. Built with Docusaurus 3.x, it features an embedded RAG chatbot, interactive learning modules, and a sophisticated royal indigo academic theme.

## Architecture & Technologies

### Core Stack
- **Framework**: Docusaurus 3.x (TypeScript)
- **Deployment**: GitHub Pages with automated GitHub Actions
- **Theme**: Royal Indigo Academic Theme (custom CSS)
- **Content Format**: MDX (Markdown + React components)

### Module Structure
The textbook is organized into 5 modules with 23+ chapters:

1. **Introduction** (3 chapters) - Physical AI concepts and course structure
2. **Module 1: ROS 2** (5 chapters) - Robot Operating System 2 fundamentals
3. **Module 2: Digital Twin** (5 chapters) - Gazebo, Unity, and simulation
4. **Module 3: NVIDIA Isaac** (6 chapters) - AI-powered robotics with Isaac SDK
5. **Module 4: Vision-Language-Action** (3 chapters) - VLA models for humanoid interaction

## Royal Indigo Academic Theme

### Color Palette
- **Primary**: #5b7ec8 (Sophisticated blue-violet)
- **Backgrounds**: #0d1117 (Deep charcoal), #161b22, #21262d
- **Royal Indigo Gradient**: #2d3561 → #4a5f8f
- **Accent**: #7a9ae0 (Lighter variant for hover states)

### Typography
- **Headings**: Georgia serif font for scholarly authority
- **Body**: System sans-serif for screen readability
- **Code**: Monospace font for technical content
- **Minimum size**: 17px for optimal reading

### Design Elements
- **Diamond Separator**: ◆ luxury signature element
- **Academic Borders**: Left-border accents for content cards
- **Chapter Numbers**: Large, semi-transparent numbers in backgrounds
- **Hover Effects**: Smooth scale and transition animations

## GitHub Pages Deployment

### Configuration
- **URL**: https://mominkhanx.github.io/neurobot-textbook/
- **Organization**: MominKhanX
- **Repository**: neurobot-textbook
- **Branch**: gh-pages

### GitHub Actions Workflow
- **Trigger**: Push to main branch
- **Node.js**: Version 18 with npm caching
- **Build**: npm run build in frontend directory
- **Deploy**: peaceiris/actions-gh-pages action
- **Commit authorship**: GitHub Actions bot

## Development Setup

### Prerequisites
- Node.js >= 18.0
- npm package manager
- Git for version control

### Installation
1. Clone the repository
2. Navigate to the frontend directory
3. Run `npm install` to install dependencies
4. Run `npm start` to start the development server

### Local Development Commands
- `npm start` - Start development server
- `npm run build` - Build for production
- `npm run serve` - Serve built site locally
- `npm run deploy` - Deploy to GitHub Pages

## Content Structure

### Chapter Format
Each chapter follows a consistent structure:
- Learning objectives
- Detailed technical content
- Code examples and diagrams
- Key takeaways
- Next steps/related chapters

### Code Examples
Technical content includes syntax-highlighted code blocks with:
- Multiple language support
- Line highlighting
- Copy functionality
- Proper indentation

## Custom Components

### Theme Components
- `neurobot-card` - Academic-style content cards
- `neurobot-diamond-separator` - Luxury content separators
- `neurobot-btn-primary/secondary` - Themed buttons
- `neurobot-link` - Links with animated underlines
- `neurobot-chapter-header` - Chapter header styling

### Interactive Elements
- Hover effects on all interactive components
- Smooth transitions and animations
- Responsive design for all screen sizes
- Accessibility-compliant color contrast

## Performance & Optimization

### Build Optimization
- Static site generation for fast loading
- Asset optimization and compression
- Code splitting for faster initial loads
- Bundle size optimization

### SEO & Accessibility
- Semantic HTML structure
- Proper heading hierarchy
- Alt text for images
- ARIA labels where appropriate
- Responsive design for all devices

## Quality Assurance

### Testing Checklist
- [ ] All pages build without errors
- [ ] Responsive design works on mobile/tablet/desktop
- [ ] All links and navigation work correctly
- [ ] Theme styling applied consistently
- [ ] Code examples display properly
- [ ] GitHub Pages deployment successful
- [ ] Performance meets standards

### Browser Compatibility
- Modern browsers (Chrome, Firefox, Safari, Edge)
- Responsive design for mobile devices
- Accessibility features for screen readers

## Maintenance & Updates

### Content Updates
- Add new chapters by creating MDX files in appropriate module directories
- Update sidebar configuration in sidebars.ts
- Test all changes with `npm run build`

### Theme Updates
- Modify custom CSS in `frontend/src/css/custom.css`
- Test theme changes across all pages
- Verify responsive design after changes

## Troubleshooting

### Common Issues
- Build failures: Check for syntax errors in MDX files
- Styling issues: Verify CSS class names and theme variables
- Deployment problems: Check GitHub Actions workflow configuration

### Performance Issues
- Large images: Optimize image sizes and formats
- Slow loading: Check bundle size and asset optimization
- Build errors: Verify dependencies and Node.js version

---

*This documentation provides comprehensive guidance for maintaining and extending the NeuroBot Physical AI & Humanoid Robotics Textbook. The project follows best practices for educational content delivery and technical documentation standards.*