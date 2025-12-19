# Quickstart Guide: NeuroBot Docusaurus Textbook

**Feature**: 001-docusaurus-init
**Date**: 2025-12-15
**Guide**: Claude

## Overview

This quickstart guide provides the essential steps to set up, develop, and deploy the NeuroBot Docusaurus textbook project. The project follows the constitution requirements for an AI-native textbook with 4 main modules and 18-22 chapters.

## Prerequisites

Before starting, ensure you have:

- **Node.js**: Version 18.x or higher
- **npm**: Package manager (comes with Node.js)
- **Git**: Version control system
- **GitHub Account**: With write access to the `MominKhanX/neurobot-textbook` repository

Verify your setup:
```bash
node --version    # Should show v18.x or higher
npm --version     # Should show version number
git --version     # Should show version number
```

## Installation

1. **Clone the repository** (if not already done):
```bash
git clone https://github.com/MominKhanX/neurobot-textbook.git
cd neurobot-textbook
```

2. **Install dependencies**:
```bash
npm install
```

3. **Verify installation** by starting the development server:
```bash
npm run start
```

The site should be accessible at `http://localhost:3000` within 10 seconds.

## Project Structure

The project follows this structure:

```
neurobot-textbook/
├── docs/                    # Educational content
│   ├── introduction/        # Introduction module (2-3 chapters)
│   ├── module-1-ros2/       # ROS 2 module (4-5 chapters)
│   ├── module-2-digital-twin/ # Digital Twin module (4-5 chapters)
│   ├── module-3-nvidia-isaac/ # NVIDIA Isaac module (4-5 chapters)
│   └── module-4-vla/        # Vision-Language-Action module (4-5 chapters)
├── src/                     # Custom components and theme
│   ├── components/          # Reusable React components
│   ├── pages/               # Custom pages
│   ├── css/custom.css       # Custom styling
│   └── theme/               # Custom theme components
├── static/                  # Static assets
├── docusaurus.config.js     # Main configuration
├── sidebars.js              # Navigation structure
└── package.json             # Project metadata and scripts
```

## Creating New Content

### Adding a New Chapter

1. **Create a new MDX file** in the appropriate module directory:
```bash
# Example: Adding a chapter to the ROS 2 module
touch docs/module-1-ros2/my-new-chapter.mdx
```

2. **Add frontmatter** to your new chapter file:
```md
---
title: "My New Chapter Title"
description: "Brief description of the chapter content"
sidebar_position: 3  # Position within the module (1-5)
tags: [tag1, tag2]
keywords: [keyword1, keyword2]
---

# My New Chapter Title

Your chapter content goes here...
```

3. **The new chapter** will automatically appear in the sidebar based on its `sidebar_position`.

### Adding a New Module

1. **Create a new directory** in the `docs/` folder:
```bash
mkdir docs/module-5-new-module
```

2. **Add chapter files** to the new module directory with appropriate frontmatter.

3. **Update `sidebars.js`** to include the new module in the navigation:
```javascript
// In sidebars.js
module.exports = {
  tutorial: [
    'intro',
    {
      type: 'category',
      label: 'New Module',
      items: ['module-5-new-module/chapter-1', 'module-5-new-module/chapter-2'],
      collapsed: false,
    },
  ],
};
```

## Development Workflow

### 1. Start Development Server
```bash
npm run start
```
- Watches for file changes
- Hot reloads changes automatically
- Runs on http://localhost:3000

### 2. Build for Production
```bash
npm run build
```
- Creates optimized static files in `build/` directory
- Should complete in under 30 seconds for initial structure
- Tests SSR/SSG compatibility

### 3. Serve Production Build Locally
```bash
npm run serve
```
- Serves the built site locally for testing
- Simulates production environment
- Useful for verifying GitHub Pages deployment

### 4. Check Build Performance
```bash
npm run build -- --stats
```
- Analyzes bundle sizes and build performance
- Helps identify optimization opportunities

## Configuration

### Main Configuration (`docusaurus.config.js`)

Key settings for the textbook:

```javascript
module.exports = {
  // Deployment settings
  url: 'https://mominkhanx.github.io',
  baseUrl: '/neurobot-textbook/',
  organizationName: 'MominKhanX',
  projectName: 'neurobot-textbook',

  // Theme settings
  themeConfig: {
    colorMode: {
      defaultMode: 'dark',        // Dark mode as default
      disableSwitch: false,       // Allow user to switch modes
      respectPrefersColorScheme: false, // Don't override default
    },
    // Academic theme colors
    prism: {
      theme: require('prism-react-renderer/themes/github'),
      darkTheme: require('prism-react-renderer/themes/dracula'),
    },
  },
};
```

### Styling (`src/css/custom.css`)

Custom royal indigo academic theme:

```css
:root {
  /* Royal indigo color scheme */
  --ifm-color-primary: #4338ca;
  --ifm-color-primary-dark: #3730a3;
  --ifm-color-primary-darker: #312e81;
  --ifm-color-primary-darkest: #1e1b4b;
  --ifm-color-primary-light: #6366f1;
  --ifm-color-primary-lighter: #818cf8;
  --ifm-color-primary-lightest: #c7d2fe;

  /* Academic typography */
  --ifm-font-family-base: 'Georgia', 'Times New Roman', serif;
}
```

## Deployment

### GitHub Pages Deployment

The site is configured for GitHub Pages deployment to `https://mominkhanx.github.io/neurobot-textbook/`.

1. **Ensure configuration** in `docusaurus.config.js`:
```javascript
module.exports = {
  url: 'https://mominkhanx.github.io',
  baseUrl: '/neurobot-textbook/',
  // ... other settings
};
```

2. **Deploy manually** (if needed):
```bash
npm run deploy
```
This command builds the site and pushes the `build/` directory to the `gh-pages` branch.

3. **Automatic deployment** is handled by GitHub Actions workflow (configured in `.github/workflows/deploy.yml`).

### Verification Steps

After deployment, verify:

1. Site loads at https://mominkhanx.github.io/neurobot-textbook/
2. All navigation works correctly
3. Dark mode is active by default
4. All internal links resolve properly
5. Assets (CSS, JS, images) load without 404 errors
6. Responsive design works on different screen sizes

## Troubleshooting

### Common Issues

**Issue**: Site doesn't load after deployment (404 errors)
- **Solution**: Verify `baseUrl` in `docusaurus.config.js` matches the repository name

**Issue**: Dark mode not default
- **Solution**: Check `defaultMode: 'dark'` in theme configuration

**Issue**: Build takes longer than 30 seconds
- **Solution**: Check for large assets or complex components, optimize as needed

**Issue**: Sidebar navigation not showing new content
- **Solution**: Verify frontmatter has correct `sidebar_position`, check `sidebars.js` configuration

### Performance Tips

1. **Optimize images**: Use WebP format where possible, compress to <100KB
2. **Split large MDX files**: Break down chapters that exceed 50KB
3. **Minimize custom components**: Use Docusaurus built-in components when possible
4. **Monitor bundle size**: Use `npm run build -- --stats` to analyze

## Next Steps

After completing the initial setup:

1. **Add educational content** to the placeholder chapters
2. **Configure search** (Algolia DocSearch recommended for large documentation)
3. **Add custom components** for interactive learning elements
4. **Set up CI/CD** with GitHub Actions for automated deployment
5. **Plan RAG chatbot integration** for AI-native textbook features

## Support

For additional help:
- Check the [Docusaurus documentation](https://docusaurus.io/docs)
- Review the project constitution for requirements
- Consult the feature specification and implementation plan
- Reach out to the development team for complex issues