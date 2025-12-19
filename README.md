# NeuroBot Physical AI & Humanoid Robotics Textbook

A comprehensive, university-level AI-native textbook for Physical AI & Humanoid Robotics, built with Docusaurus and featuring embedded RAG chatbot capabilities.

## 🎯 Project Overview

The NeuroBot textbook is an interactive, comprehensive resource for learning Physical AI and Humanoid Robotics. It combines cutting-edge educational content with sophisticated visual design to create a market-level learning experience.

### 📚 Content Structure
- **Introduction Module** (3 chapters) - Physical AI concepts and course structure
- **Module 1: ROS 2** (5 chapters) - Robot Operating System 2 fundamentals
- **Module 2: Digital Twin** (5 chapters) - Gazebo, Unity, and simulation environments
- **Module 3: NVIDIA Isaac** (6 chapters) - AI-powered robotics with Isaac SDK
- **Module 4: Vision-Language-Action** (3 chapters) - VLA models for humanoid interaction

**Total**: 23+ chapters covering the complete Physical AI & Humanoid Robotics curriculum

## 🎨 Royal Indigo Academic Theme

The textbook features a sophisticated **Royal Indigo Academic Theme** with:
- **Color Palette**: Deep charcoal backgrounds (#0d1117), royal indigo gradients (#2d3561 → #4a5f8f), blue-violet accents (#5b7ec8)
- **Typography**: Georgia serif for headings, sans-serif for body text (minimum 17px)
- **Design Elements**: Diamond separators (◆), academic journal-style borders, luxury hover effects
- **Interactive Features**: Smooth transitions, scale animations, animated underlines

## 🚀 Quick Start

### Prerequisites
- Node.js >= 18.0
- npm package manager

### Installation
```bash
# Clone the repository
git clone <repository-url>

# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

### Build & Deployment
```bash
# Build for production
npm run build

# Serve built site locally
npm run serve

# Deploy to GitHub Pages (if configured)
npm run deploy
```

## 🏗️ Project Architecture

### Core Technologies
- **Framework**: Docusaurus 3.x (TypeScript)
- **Content**: MDX (Markdown + React components)
- **Deployment**: GitHub Pages with automated GitHub Actions
- **Theme**: Custom Royal Indigo Academic CSS

### Directory Structure
```
frontend/
├── docs/                 # Educational content (23+ chapters)
├── src/
│   ├── css/
│   │   └── custom.css    # Royal Indigo Academic Theme
│   └── pages/            # Additional pages
├── static/               # Static assets
├── docusaurus.config.ts  # Site configuration
└── sidebars.ts           # Navigation structure
```

## 🌐 GitHub Pages Deployment

The site is configured for GitHub Pages deployment with:
- **URL**: https://mominkhanx.github.io/Final-humanoid-ai-textbook/
- **Organization**: MominKhanX
- **Repository**: Final-humanoid-ai-textbook
- **Workflow**: Automated GitHub Actions on push to main branch

### Local Development
For local development with the correct base URL:
```bash
# Build the site first (required for proper base URL handling)
npm run build

# Then serve the built site locally (this handles the base URL correctly)
npm run serve
```

For faster development iterations without GitHub Pages base URL:
- Temporarily change `baseUrl` in `docusaurus.config.ts` to `'/'`
- Use `npm start` for development
- Remember to revert the change before committing

## 📖 Content Features

### Educational Excellence
- University-level technical accuracy
- Pedagogically sound content structure
- Interactive learning elements
- Real-world applications and examples

### Technical Rigor
- ROS 2 architecture and communication patterns
- Digital twin simulation with Gazebo and Unity
- NVIDIA Isaac SDK for AI-powered robotics
- Vision-Language-Action models for social interaction

### Accessibility & Inclusivity
- Responsive design for all devices
- Proper semantic HTML structure
- High contrast color schemes
- Clear navigation and content hierarchy

## 🛠️ Development Workflow

### Adding New Content
1. Create new MDX files in the appropriate module directory
2. Update `sidebars.ts` to include the new content in navigation
3. Test with `npm start` to ensure proper rendering
4. Build with `npm run build` to verify production compatibility

### Theme Customization
- Modify `frontend/src/css/custom.css` for styling changes
- Use provided CSS classes for consistent theming
- Test responsive design across all screen sizes

## 🧪 Quality Assurance

### Testing Checklist
- [x] All pages build successfully
- [x] Responsive design works on mobile/tablet/desktop
- [x] All navigation and links function correctly
- [x] Royal Indigo theme applied consistently
- [x] Code examples display properly with syntax highlighting
- [x] GitHub Pages deployment configured and tested

### Performance Standards
- Fast loading times through static site generation
- Optimized bundle sizes
- Proper SEO and accessibility features
- Cross-browser compatibility

## 🤝 Contributing

We welcome contributions to enhance the NeuroBot textbook:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test thoroughly (`npm run build`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support, please open an issue in the GitHub repository or contact the development team.

---

*Built with ❤️ for the future of Physical AI & Humanoid Robotics education*

**🤖 Generated with [Claude Code](https://claude.com/claude-code)**

**Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>**