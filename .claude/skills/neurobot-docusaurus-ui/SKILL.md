---
name: "neurobot-docusaurus-ui"
description: "Design and build NeuroBot's royal indigo academic visual identity in Docusaurus: scholarly dark charcoal backgrounds (#0d1117), prestigious royal indigo gradients (#2d3561 → #4a5f8f), sophisticated blue-violet accents (#5b7ec8), luxury diamond separators (◆), academic journal-style borders, Georgia serif typography, and elegant hover effects with smooth scale and underline animations. Focuses on CSS styling, component appearance, and professional visual polish suitable for market-level AI textbooks. Use when user wants NeuroBot theme, scholarly/academic styling, or professional UI/UX improvements for educational content."
version: "1.0.0"
---

# NeuroBot Docusaurus UI Skill

## Core Design Philosophy

NeuroBot embodies **scholarly prestige** and **academic authority** - a visual language that commands respect while remaining approachable. Every design decision reflects the gravitas of university-level education combined with modern digital sophistication.

**Design Pillars:**
- **Authoritative**: Professional enough for publication
- **Timeless**: Classic design that won't feel dated
- **Accessible**: Clear hierarchy, readable typography
- **Refined**: Subtle luxury through details (diamond separators, serif typography, gradient accents)

---

## Color Palette (CRITICAL - Exact Values Required)

### Background Colors
```css
--neurobot-bg-primary: #0d1117;        /* Deep charcoal - main background */
--neurobot-bg-secondary: #161b22;      /* Elevated surfaces */
--neurobot-bg-tertiary: #21262d;       /* Cards and content areas */
```

### Royal Indigo Gradient (Signature Element)
```css
--neurobot-indigo-start: #2d3561;      /* Deep royal indigo */
--neurobot-indigo-mid: #3d4675;        /* Transition tone */
--neurobot-indigo-end: #4a5f8f;        /* Lighter indigo */

/* Primary gradient usage */
background: linear-gradient(135deg, #2d3561 0%, #4a5f8f 100%);
```

### Accent Colors
```css
--neurobot-accent-primary: #5b7ec8;    /* Sophisticated blue-violet - links, highlights */
--neurobot-accent-glow: #7a9ae0;       /* Lighter variant for hover states */
--neurobot-accent-muted: #4a6399;      /* Subdued version for borders */
```

### Text Colors
```css
--neurobot-text-primary: #ffffff;      /* Headings, emphasis */
--neurobot-text-secondary: #e6edf3;    /* Body text, standard content */
--neurobot-text-tertiary: #8b949e;     /* Captions, metadata, muted text */
--neurobot-text-quote: #a5b4c7;        /* Blockquotes, citations */
```

### Semantic Colors
```css
--neurobot-border-default: rgba(91, 126, 200, 0.15);  /* Subtle borders */
--neurobot-border-accent: rgba(91, 126, 200, 0.4);    /* Prominent borders */
--neurobot-shadow-sm: rgba(45, 53, 97, 0.3);          /* Subtle depth */
--neurobot-shadow-lg: rgba(45, 53, 97, 0.6);          /* Dramatic depth */
```

---

## Typography System

### Font Families
```css
/* Serif for headings - scholarly authority */
--neurobot-font-serif: 'Georgia', 'Times New Roman', serif;

/* Sans-serif for body - modern readability */
--neurobot-font-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica', sans-serif;

/* Monospace for code */
--neurobot-font-mono: 'SF Mono', 'Monaco', 'Cascadia Code', monospace;
```

### Type Scale
```css
/* Headings - Georgia serif, generous spacing */
.neurobot-h1 {
  font-family: var(--neurobot-font-serif);
  font-size: 2.5rem;
  font-weight: 700;
  line-height: 1.2;
  letter-spacing: -0.02em;
  color: var(--neurobot-text-primary);
}

.neurobot-h2 {
  font-family: var(--neurobot-font-serif);
  font-size: 2rem;
  font-weight: 600;
  line-height: 1.3;
  letter-spacing: -0.01em;
  color: var(--neurobot-text-primary);
}

.neurobot-h3 {
  font-family: var(--neurobot-font-serif);
  font-size: 1.5rem;
  font-weight: 600;
  line-height: 1.4;
  color: var(--neurobot-text-primary);
}

/* Body text - sans-serif for screen readability */
.neurobot-body {
  font-family: var(--neurobot-font-sans);
  font-size: 1.0625rem;  /* 17px - optimal reading size */
  line-height: 1.7;
  color: var(--neurobot-text-secondary);
}

/* Chapter/Section numbers - Large, semi-transparent */
.neurobot-chapter-number {
  font-family: var(--neurobot-font-serif);
  font-size: 6rem;
  font-weight: 700;
  color: rgba(91, 126, 200, 0.08);
  line-height: 1;
  position: absolute;
  z-index: 0;
}
```

---

## Signature Design Elements

### Diamond Separator (◆)
The diamond is NeuroBot's luxury signature - use it to separate sections with elegance.

```css
.neurobot-diamond-separator {
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 3rem 0;
  color: var(--neurobot-accent-primary);
  font-size: 1.25rem;
  opacity: 0.6;
}

.neurobot-diamond-separator::before,
.neurobot-diamond-separator::after {
  content: '';
  flex: 1;
  height: 1px;
  background: linear-gradient(
    to right,
    transparent,
    var(--neurobot-border-accent),
    transparent
  );
  margin: 0 1.5rem;
}
```

**HTML Usage:**
```html
<div class="neurobot-diamond-separator">◆</div>
```

### Academic Left-Border Accent
Journal-style left border for content cards and important sections.

```css
.neurobot-academic-border {
  border-left: 4px solid var(--neurobot-accent-primary);
  padding-left: 1.5rem;
  margin-left: 0;
}

/* Gradient variant for extra polish */
.neurobot-academic-border-gradient {
  border-left: 4px solid transparent;
  border-image: linear-gradient(to bottom, #2d3561, #5b7ec8, #4a5f8f) 1;
  padding-left: 1.5rem;
  margin-left: 0;
}
```

---

## Interactive Elements & Hover Effects

### Universal Hover Principles
- **Scale**: 1.02-1.05x enlargement for subtle elegance
- **Transition**: 0.3s ease for smoothness
- **Cursor**: Always `pointer` for interactivity
- **Underline**: Animated from left to right for links

### Navigation Links
```css
.neurobot-nav-link {
  position: relative;
  color: var(--neurobot-text-secondary);
  font-family: var(--neurobot-font-sans);
  font-size: 0.9375rem;
  font-weight: 500;
  text-decoration: none;
  padding: 0.5rem 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.neurobot-nav-link:hover {
  color: var(--neurobot-accent-primary);
  transform: translateY(-1px);
}

/* Animated underline */
.neurobot-nav-link::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 0%;
  height: 2px;
  background: var(--neurobot-accent-primary);
  transition: width 0.3s ease;
}

.neurobot-nav-link:hover::after {
  width: 100%;
}

.neurobot-nav-link.active {
  color: var(--neurobot-accent-primary);
  font-weight: 600;
}

.neurobot-nav-link.active::after {
  width: 100%;
}
```

### Content Cards
Academic-style cards with left border accent and subtle scale hover.

```css
.neurobot-card {
  background: var(--neurobot-bg-tertiary);
  border: 1px solid var(--neurobot-border-default);
  border-left: 4px solid var(--neurobot-accent-primary);
  border-radius: 8px;
  padding: 1.75rem;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.neurobot-card:hover {
  transform: scale(1.02) translateY(-4px);
  border-color: var(--neurobot-border-accent);
  box-shadow: 
    0 8px 24px var(--neurobot-shadow-sm),
    0 0 0 1px var(--neurobot-border-accent);
}

/* Optional: Gradient background on hover */
.neurobot-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(45, 53, 97, 0.1) 0%, rgba(74, 95, 143, 0.1) 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
  z-index: 0;
  pointer-events: none;
}

.neurobot-card:hover::before {
  opacity: 1;
}

/* Ensure content stays above gradient */
.neurobot-card > * {
  position: relative;
  z-index: 1;
}
```

### Buttons
Professional button system with gradient backgrounds.

```css
/* Primary Button - Royal Indigo Gradient */
.neurobot-btn-primary {
  background: linear-gradient(135deg, #2d3561 0%, #4a5f8f 100%);
  color: white;
  font-family: var(--neurobot-font-sans);
  font-size: 1rem;
  font-weight: 600;
  padding: 0.875rem 2rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px var(--neurobot-shadow-sm);
}

.neurobot-btn-primary:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 16px var(--neurobot-shadow-lg);
}

/* Secondary Button - Outline Style */
.neurobot-btn-secondary {
  background: transparent;
  color: var(--neurobot-accent-primary);
  font-family: var(--neurobot-font-sans);
  font-size: 1rem;
  font-weight: 600;
  padding: 0.875rem 2rem;
  border: 2px solid var(--neurobot-accent-primary);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.neurobot-btn-secondary:hover {
  background: rgba(91, 126, 200, 0.1);
  transform: scale(1.03);
  box-shadow: 0 0 20px rgba(91, 126, 200, 0.2);
}
```

### Inline Links
```css
.neurobot-link {
  position: relative;
  color: var(--neurobot-accent-primary);
  text-decoration: none;
  cursor: pointer;
  transition: color 0.2s ease;
}

.neurobot-link:hover {
  color: var(--neurobot-accent-glow);
}

/* Animated underline */
.neurobot-link::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 0%;
  height: 2px;
  background: var(--neurobot-accent-primary);
  transition: width 0.3s ease;
}

.neurobot-link:hover::after {
  width: 100%;
}
```

---

## Component Styling Guide

### Hero Section
```css
.neurobot-hero {
  background: linear-gradient(180deg, #0d1117 0%, #161b22 50%, #21262d 100%);
  padding: 5rem 2rem;
  text-align: center;
  position: relative;
  overflow: hidden;
}

/* Large decorative chapter number */
.neurobot-hero::before {
  content: '01';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-family: var(--neurobot-font-serif);
  font-size: 20rem;
  font-weight: 700;
  color: rgba(91, 126, 200, 0.03);
  z-index: 0;
  line-height: 1;
}

.neurobot-hero-content {
  position: relative;
  z-index: 1;
}

.neurobot-hero-badge {
  display: inline-block;
  background: rgba(45, 53, 97, 0.3);
  border: 1px solid var(--neurobot-accent-primary);
  color: var(--neurobot-accent-primary);
  font-family: var(--neurobot-font-sans);
  font-size: 0.875rem;
  font-weight: 600;
  padding: 0.5rem 1.25rem;
  border-radius: 20px;
  margin-bottom: 1.5rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.neurobot-hero-title {
  font-family: var(--neurobot-font-serif);
  font-size: 3.5rem;
  font-weight: 700;
  color: white;
  margin-bottom: 1rem;
  line-height: 1.2;
}

.neurobot-hero-title .highlight {
  background: linear-gradient(135deg, #2d3561 0%, #5b7ec8 50%, #4a5f8f 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.neurobot-hero-subtitle {
  font-family: var(--neurobot-font-sans);
  font-size: 1.25rem;
  color: var(--neurobot-text-tertiary);
  max-width: 700px;
  margin: 0 auto 2.5rem;
  line-height: 1.6;
}

.neurobot-hero-cta {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}
```

**HTML Example:**
```html
<div class="neurobot-hero">
  <div class="neurobot-hero-content">
    <div class="neurobot-hero-badge">Humanoid AI Textbook</div>
    <h1 class="neurobot-hero-title">
      Master <span class="highlight">NeuroBot</span> Architecture
    </h1>
    <p class="neurobot-hero-subtitle">
      A comprehensive, university-level guide to building intelligent humanoid systems
    </p>
    <div class="neurobot-hero-cta">
      <button class="neurobot-btn-primary">Start Learning</button>
      <button class="neurobot-btn-secondary">View Syllabus</button>
    </div>
  </div>
</div>
```

### Chapter Headers
```css
.neurobot-chapter-header {
  position: relative;
  padding: 3rem 0 2rem;
  margin-bottom: 2rem;
  border-bottom: 2px solid var(--neurobot-border-default);
}

.neurobot-chapter-number-display {
  font-family: var(--neurobot-font-serif);
  font-size: 6rem;
  font-weight: 700;
  color: rgba(91, 126, 200, 0.08);
  line-height: 1;
  margin: 0;
  position: absolute;
  top: 0;
  left: -1rem;
  z-index: 0;
}

.neurobot-chapter-title {
  font-family: var(--neurobot-font-serif);
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--neurobot-text-primary);
  margin: 0 0 0.5rem 0;
  position: relative;
  z-index: 1;
}

.neurobot-chapter-description {
  font-family: var(--neurobot-font-sans);
  font-size: 1.125rem;
  color: var(--neurobot-text-tertiary);
  max-width: 600px;
  position: relative;
  z-index: 1;
}
```

### Feature Grid
```css
.neurobot-features-section {
  padding: 4rem 2rem;
}

.neurobot-features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin-top: 3rem;
}

.neurobot-feature-card {
  background: var(--neurobot-bg-tertiary);
  border: 1px solid var(--neurobot-border-default);
  border-left: 4px solid var(--neurobot-accent-primary);
  border-radius: 8px;
  padding: 2rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.neurobot-feature-card:hover {
  transform: scale(1.03) translateY(-6px);
  border-color: var(--neurobot-border-accent);
  box-shadow: 0 12px 32px var(--neurobot-shadow-sm);
}

.neurobot-feature-icon {
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, #2d3561 0%, #4a5f8f 100%);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.75rem;
  margin-bottom: 1.5rem;
  transition: transform 0.3s ease;
}

.neurobot-feature-card:hover .neurobot-feature-icon {
  transform: scale(1.1) rotate(5deg);
}

.neurobot-feature-title {
  font-family: var(--neurobot-font-serif);
  font-size: 1.375rem;
  font-weight: 600;
  color: var(--neurobot-text-primary);
  margin-bottom: 0.75rem;
}

.neurobot-feature-description {
  font-family: var(--neurobot-font-sans);
  font-size: 1rem;
  color: var(--neurobot-text-tertiary);
  line-height: 1.6;
}
```

---
### RAG Chatbot Widget
Royal indigo academic theme for the AI assistant.
```css
/* Chatbot Container - Floating widget */
.neurobot-chatbot {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  width: 400px;
  max-height: 600px;
  background: var(--neurobot-bg-secondary);
  border: 1px solid var(--neurobot-border-accent);
  border-left: 4px solid var(--neurobot-accent-primary);
  border-radius: 12px;
  box-shadow: 0 8px 32px var(--neurobot-shadow-lg);
  z-index: 1000;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* Chatbot Header */
.neurobot-chatbot-header {
  background: linear-gradient(135deg, #2d3561 0%, #4a5f8f 100%);
  padding: 1rem 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--neurobot-border-accent);
}

.neurobot-chatbot-title {
  font-family: var(--neurobot-font-serif);
  font-size: 1.125rem;
  font-weight: 600;
  color: white;
  margin: 0;
}

.neurobot-chatbot-subtitle {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.7);
  margin-top: 0.25rem;
}

.neurobot-chatbot-close {
  background: transparent;
  border: none;
  color: white;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0.25rem;
  transition: all 0.2s ease;
}

.neurobot-chatbot-close:hover {
  transform: scale(1.1);
  color: var(--neurobot-accent-glow);
}

/* Chatbot Messages Area */
.neurobot-chatbot-messages {
  flex: 1;
  padding: 1.5rem;
  overflow-y: auto;
  background: var(--neurobot-bg-primary);
}

/* Message Bubbles */
.neurobot-message {
  margin-bottom: 1rem;
  display: flex;
  flex-direction: column;
}

.neurobot-message-user {
  align-items: flex-end;
}

.neurobot-message-assistant {
  align-items: flex-start;
}

.neurobot-message-bubble {
  max-width: 80%;
  padding: 0.875rem 1.25rem;
  border-radius: 12px;
  font-size: 0.9375rem;
  line-height: 1.5;
}

.neurobot-message-user .neurobot-message-bubble {
  background: linear-gradient(135deg, #2d3561 0%, #4a5f8f 100%);
  color: white;
  border-bottom-right-radius: 4px;
}

.neurobot-message-assistant .neurobot-message-bubble {
  background: var(--neurobot-bg-tertiary);
  color: var(--neurobot-text-secondary);
  border: 1px solid var(--neurobot-border-default);
  border-left: 3px solid var(--neurobot-accent-primary);
  border-bottom-left-radius: 4px;
}

/* Citations in assistant messages */
.neurobot-citation {
  display: inline-block;
  margin-left: 0.25rem;
  padding: 0.125rem 0.5rem;
  background: rgba(91, 126, 200, 0.15);
  border: 1px solid var(--neurobot-accent-primary);
  border-radius: 4px;
  font-size: 0.75rem;
  color: var(--neurobot-accent-primary);
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.neurobot-citation:hover {
  background: rgba(91, 126, 200, 0.25);
  transform: scale(1.05);
}

/* Timestamp */
.neurobot-message-time {
  font-size: 0.6875rem;
  color: var(--neurobot-text-tertiary);
  margin-top: 0.25rem;
}

/* Chatbot Input Area */
.neurobot-chatbot-input {
  padding: 1rem 1.5rem;
  background: var(--neurobot-bg-secondary);
  border-top: 1px solid var(--neurobot-border-default);
}

.neurobot-input-wrapper {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.neurobot-input-field {
  flex: 1;
  background: var(--neurobot-bg-primary);
  border: 1px solid var(--neurobot-border-default);
  border-radius: 8px;
  padding: 0.75rem 1rem;
  color: var(--neurobot-text-secondary);
  font-size: 0.9375rem;
  transition: all 0.2s ease;
}

.neurobot-input-field:focus {
  outline: none;
  border-color: var(--neurobot-accent-primary);
  box-shadow: 0 0 0 3px rgba(91, 126, 200, 0.1);
}

.neurobot-input-field::placeholder {
  color: var(--neurobot-text-tertiary);
}

.neurobot-send-button {
  background: linear-gradient(135deg, #2d3561 0%, #4a5f8f 100%);
  border: none;
  border-radius: 8px;
  padding: 0.75rem 1.25rem;
  color: white;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.neurobot-send-button:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 12px var(--neurobot-shadow-sm);
}

.neurobot-send-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

/* Chatbot Toggle Button (when minimized) */
.neurobot-chatbot-toggle {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #2d3561 0%, #4a5f8f 100%);
  border: 2px solid var(--neurobot-accent-primary);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 4px 16px var(--neurobot-shadow-lg);
  transition: all 0.3s ease;
  z-index: 999;
}

.neurobot-chatbot-toggle:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 24px var(--neurobot-shadow-lg);
}

.neurobot-chatbot-toggle-icon {
  font-size: 1.75rem;
  color: white;
}

/* Loading indicator */
.neurobot-typing-indicator {
  display: flex;
  gap: 0.375rem;
  padding: 0.875rem 1.25rem;
  background: var(--neurobot-bg-tertiary);
  border: 1px solid var(--neurobot-border-default);
  border-left: 3px solid var(--neurobot-accent-primary);
  border-radius: 12px;
  border-bottom-left-radius: 4px;
  max-width: fit-content;
}

.neurobot-typing-dot {
  width: 8px;
  height: 8px;
  background: var(--neurobot-accent-primary);
  border-radius: 50%;
  animation: typing 1.4s infinite;
}

.neurobot-typing-dot:nth-child(2) {
  animation-delay: 0.2s;
}

.neurobot-typing-dot:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
    opacity: 0.7;
  }
  30% {
    transform: translateY(-10px);
    opacity: 1;
  }
}

/* Mobile responsive */
@media (max-width: 768px) {
  .neurobot-chatbot {
    width: calc(100vw - 2rem);
    max-height: calc(100vh - 4rem);
    right: 1rem;
    bottom: 1rem;
  }
  
  .neurobot-chatbot-toggle {
    right: 1rem;
    bottom: 1rem;
  }
}
```

---

## Docusaurus-Specific CSS Overrides

### Custom CSS File (src/css/custom.css)
```css
/**
 * NeuroBot Royal Indigo Academic Theme
 * Professional styling for market-level AI textbook
 */

:root {
  /* Color System */
  --ifm-color-primary: #5b7ec8;
  --ifm-color-primary-dark: #4a6bb5;
  --ifm-color-primary-darker: #4263a8;
  --ifm-color-primary-darkest: #354f8a;
  --ifm-color-primary-light: #7091d4;
  --ifm-color-primary-lighter: #7f9cd9;
  --ifm-color-primary-lightest: #a4b8e6;
  
  /* Backgrounds */
  --ifm-background-color: #0d1117;
  --ifm-background-surface-color: #161b22;
  --ifm-navbar-background-color: rgba(13, 17, 23, 0.95);
  --ifm-footer-background-color: #161b22;
  --ifm-card-background-color: #21262d;
  
  /* Typography */
  --ifm-font-family-base: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica', sans-serif;
  --ifm-heading-font-family: 'Georgia', 'Times New Roman', serif;
  --ifm-font-color-base: #e6edf3;
  --ifm-heading-color: #ffffff;
  --ifm-font-size-base: 17px;
  --ifm-line-height-base: 1.7;
  
  /* Links */
  --ifm-link-color: #5b7ec8;
  --ifm-link-hover-color: #7a9ae0;
  --ifm-link-decoration: none;
  
  /* Code */
  --ifm-code-font-size: 0.9375rem;
  --ifm-code-background: #161b22;
  --ifm-code-border-radius: 4px;
  --ifm-pre-background: #161b22;
  
  /* Borders */
  --ifm-color-emphasis-300: rgba(91, 126, 200, 0.15);
  --ifm-hr-background-color: rgba(91, 126, 200, 0.2);
  
  /* Spacing */
  --ifm-spacing-horizontal: 1.5rem;
  --ifm-spacing-vertical: 1.5rem;
}

/* Dark mode consistency */
[data-theme='dark'] {
  --ifm-background-color: #0d1117;
  --ifm-background-surface-color: #161b22;
}

/* Navigation Bar - Sticky with backdrop blur */
.navbar {
  background: rgba(13, 17, 23, 0.95);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(91, 126, 200, 0.1);
  padding: 0.75rem 1.5rem;
}

.navbar__brand {
  cursor: pointer;
  transition: transform 0.3s ease;
}

.navbar__brand:hover {
  transform: scale(1.05);
}

.navbar__title {
  font-family: var(--ifm-heading-font-family);
  font-size: 1.375rem;
  font-weight: 700;
  color: white;
}

.navbar__link {
  position: relative;
  color: var(--ifm-font-color-base);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  padding-bottom: 0.25rem;
}

.navbar__link:hover {
  color: var(--ifm-color-primary);
}

.navbar__link::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 0%;
  height: 2px;
  background: var(--ifm-color-primary);
  transition: width 0.3s ease;
}

.navbar__link:hover::after,
.navbar__link--active::after {
  width: 100%;
}

/* Sidebar - Academic journal style */
.menu {
  padding: 1rem;
}

.menu__link {
  color: var(--ifm-font-color-base);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
  padding: 0.5rem 0.75rem;
}

.menu__link:hover {
  background: rgba(91, 126, 200, 0.1);
  color: var(--ifm-color-primary);
}

.menu__link--active {
  background: rgba(91, 126, 200, 0.15);
  color: var(--ifm-color-primary);
  font-weight: 600;
  border-left: 3px solid var(--ifm-color-primary);
  padding-left: calc(0.75rem - 3px);
}

.menu__list-item-collapsible:hover {
  background: rgba(91, 126, 200, 0.05);
}

/* Table of Contents */
.table-of-contents {
  border-left: 2px solid rgba(91, 126, 200, 0.2);
  padding-left: 0;
}

.table-of-contents__link {
  color: var(--ifm-color-emphasis-700);
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s ease;
  display: block;
  padding: 0.25rem 0 0.25rem 1rem;
  border-left: 2px solid transparent;
  margin-left: -2px;
}

.table-of-contents__link:hover {
  color: var(--ifm-color-primary);
  border-left-color: var(--ifm-color-primary);
  background: rgba(91, 126, 200, 0.05);
}

.table-of-contents__link--active {
  color: var(--ifm-color-primary);
  font-weight: 600;
  border-left-color: var(--ifm-color-primary);
}

/* Documentation Content */
.markdown {
  color: var(--ifm-font-color-base);
  font-size: var(--ifm-font-size-base);
  line-height: var(--ifm-line-height-base);
}

.markdown > h1,
.markdown > h2,
.markdown > h3,
.markdown > h4 {
  font-family: var(--ifm-heading-font-family);
  color: var(--ifm-heading-color);
  margin-top: 2rem;
  margin-bottom: 1rem;
}

.markdown > h1 {
  font-size: 2.5rem;
  border-bottom: 2px solid rgba(91, 126, 200, 0.2);
  padding-bottom: 0.75rem;
  margin-bottom: 1.5rem;
}

.markdown > h2 {
  font-size: 2rem;
  border-bottom: 1px solid rgba(91, 126, 200, 0.15);
  padding-bottom: 0.5rem;
}

.markdown > h3 {
  font-size: 1.5rem;
}

/* Inline code */
.markdown code {
  background: var(--ifm-code-background);
  color: var(--ifm-color-primary);
  border: 1px solid rgba(91, 126, 200, 0.2);
  border-radius: var(--ifm-code-border-radius);
  padding: 0.2rem 0.4rem;
  font-size: 0.9em;
}

/* Code blocks */
.prism-code,
.codeBlockContainer {
  background: var(--ifm-pre-background) !important;
  border: 1px solid rgba(91, 126, 200, 0.15);
  border-radius: 8px;
  border-left: 4px solid var(--ifm-color-primary);
}

.codeBlockTitle {
  background: rgba(45, 53, 97, 0.3);
  color: var(--ifm-color-primary);
  border-bottom: 1px solid rgba(91, 126, 200, 0.2);
  font-family: var(--ifm-font-family-monospace);
}

/* Blockquotes - Academic citation style */
.markdown blockquote {
  border-left: 4px solid var(--ifm-color-primary);
  background: rgba(45, 53, 97, 0.1);
  color: var(--ifm-color-emphasis-800);
  padding: 1rem 1.5rem;
  margin: 1.5rem 0;
  border-radius: 0 4px 4px 0;
}

/* Admonitions */
.admonition {
  border-left: 4px solid var(--ifm-color-primary);
  border-radius: 0 6px 6px 0;
  background: rgba(45, 53, 97, 0.1);
}

.admonition-heading {
  font-family: var(--ifm-heading-font-family);
}

/* Tables */
.markdown table {
  border-collapse: collapse;
  margin: 1.5rem 0;
}

.markdown th {
  background: linear-gradient(135deg, #2d3561 0%, #4a5f8f 100%);
  color: white;
  font-family: var(--ifm-heading-font-family);
  font-weight: 600;
  padding: 0.75rem 1rem;
  border: 1px solid rgba(91, 126, 200, 0.3);
}

.markdown td {
  background: var(--ifm-card-background-color);
  padding: 0.75rem 1rem;
  border: 1px solid rgba(91, 126, 200, 0.15);
}

.markdown tr:hover td {
  background: rgba(91, 126, 200, 0.05);
}

/* Pagination */
.pagination-nav__link {
  border: 1px solid rgba(91, 126, 200, 0.2);
  border-left: 4px solid var(--ifm-color-primary);
  cursor: pointer;
  transition: all 0.3s ease;
}

.pagination-nav__link:hover {
  background: rgba(91, 126, 200, 0.1);
  border-color: var(--ifm-color-primary);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(45, 53, 97, 0.3);
}

.pagination-nav__label {
  font-family: var(--ifm-heading-font-family);
  color: var(--ifm-color-primary);
}

/* Footer */
.footer {
  background: var(--ifm-footer-background-color);
  border-top: 1px solid rgba(91, 126, 200, 0.2);
  padding: 2rem 0;
}

.footer__title {
  font-family: var(--ifm-heading-font-family);
  color: white;
  font-size: 1.125rem;
}

.footer__link-item {
  color: var(--ifm-color-emphasis-700);
  cursor: pointer;
  transition: all 0.2s ease;
}

.footer__link-item:hover {
  color: var(--ifm-color-primary);
  text-decoration: underline;
}

/* Search bar integration */
.navbar__search-input {
  background: rgba(22, 27, 34, 0.8);
  border: 1px solid rgba(91, 126, 200, 0.2);
  color: var(--ifm-font-color-base);
  border-radius: 6px;
  transition: all 0.3s ease;
}

.navbar__search-input:focus {
  border-color: var(--ifm-color-primary);
  box-shadow: 0 0 0 3px rgba(91, 126, 200, 0.1);
}
```

---

## Responsive Design

```css
/* Mobile (< 768px) */
@media (max-width: 768px) {
  .neurobot-hero-title {
    font-size: 2.25rem;
  }
  
  .neurobot-chapter-number-display {
    font-size: 4rem;
  }
  
  .neurobot-features-grid {
    grid-template-columns: 1fr;
  }
  
  .neurobot-hero {
    padding: 3rem 1.5rem;
  }
  
  .neurobot-card {
    padding: 1.25rem;
  }
}

/* Tablet (768px - 1024px) */
@media (min-width: 768px) and (max-width: 1024px) {
  .neurobot-features-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .neurobot-hero-title {
    font-size: 3rem;
  }
}

/* Large screens (> 1400px) */
@media (min-width: 1400px) {
  .neurobot-hero-title {
    font-size: 4rem;
  }
  
  .markdown {
    max-width: 900px;
  }
}
```

---

## Quality Assurance Checklist

Before delivering, verify:

**Colors & Branding**
- [ ] All backgrounds use #0d1117, #161b22, or #21262d
- [ ] Royal indigo gradient (#2d3561 → #4a5f8f) used for accents
- [ ] Accent color #5b7ec8 used for links and highlights
- [ ] No colors outside the defined palette

**Typography**
- [ ] Georgia serif for all headings (h1-h4)
- [ ] Sans-serif for body text and navigation
- [ ] Font size minimum 17px for body text
- [ ] Line height 1.7 for optimal readability

**Interactive Elements**
- [ ] All cards have hover effects (scale 1.02-1.03 + lift)
- [ ] All buttons have hover effects (scale 1.03-1.05)
- [ ] All links have underline animation on hover
- [ ] cursor: pointer on all clickable elements
- [ ] Smooth transitions (0.3s ease) everywhere

**Academic Design Elements**
- [ ] Diamond separators (◆) used between major sections
- [ ] Left border accent (4px) on content cards
- [ ] Large semi-transparent chapter numbers in backgrounds
- [ ] Academic journal-style borders and layouts

**Polish & Professionalism**
- [ ] Generous spacing and padding throughout
- [ ] Consistent border radius (6-8px for cards, 4px for small elements)
- [ ] Box shadows for depth and elevation
- [ ] Responsive design tested on mobile, tablet, desktop
- [ ] No jarring animations or abrupt transitions

---

## Usage Notes

**This skill is focused EXCLUSIVELY on:**
- Visual design and CSS styling
- Component appearance and polish
- Color schemes and typography
- Hover effects and animations
- Professional UI/UX for educational content

**This skill does NOT handle:**
- Docusaurus configuration (docusaurus.config.js)
- Plugin installation or setup
- File structure and architecture
- Build processes or deployment
- Content writing or markdown generation

For architectural setup, use a separate Docusaurus architecture skill.

---

## Professional Design Tips

1. **Consistency is Authority**: Use the exact same spacing, colors, and effects throughout
2. **Subtlety is Sophistication**: Hover effects should be smooth and refined, not dramatic
3. **Hierarchy Matters**: Use font sizes and weights to create clear visual hierarchy
4. **White Space is Content**: Generous padding and margins convey professionalism
5. **Details are Everything**: Diamond separators, left borders, and chapter numbers add prestige

---

**NeuroBot UI Skill v1.0.0**
*Royal Indigo Academic Theme for Market-Level AI Textbooks*
