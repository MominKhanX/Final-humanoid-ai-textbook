# Data Model: NeuroBot Docusaurus Textbook

**Feature**: 001-docusaurus-init
**Date**: 2025-12-15
**Modeler**: Claude

## Entity: Module

**Description**: Represents a major section of the course curriculum (e.g., ROS 2, Digital Twin). Contains multiple chapters and has a position in the educational flow.

**Fields**:
- `id` (string): Unique identifier for the module (e.g., "introduction", "module-1-ros2")
- `title` (string): Display title of the module (e.g., "Introduction to Physical AI", "The Robotic Nervous System")
- `description` (string): Brief description of the module content
- `position` (integer): Order in the educational flow (1-5 for the 5 required modules)
- `chapterCount` (integer): Number of chapters in this module (2-3 for intro, 4-5 for main modules)
- `slug` (string): URL-friendly version of the title for routing

**Validation Rules**:
- `id` must be unique across all modules
- `position` must be unique and between 1-5
- `title` is required and must be 5-100 characters
- `chapterCount` must be between 2-5 (2-3 for introduction, 4-5 for main modules)
- `slug` must match pattern: ^[a-z0-9]+(?:-[a-z0-9]+)*$

**Relationships**:
- One-to-many with Chapter entity (one module contains many chapters)

## Entity: Chapter

**Description**: Represents a single learning unit within a module. Contains educational content in MDX format and has metadata for navigation and organization.

**Fields**:
- `id` (string): Unique identifier for the chapter (e.g., "intro-chapter-1", "ros2-chapter-2")
- `title` (string): Display title of the chapter
- `description` (string): Brief summary of chapter content
- `sidebar_position` (integer): Position within the parent module's sidebar (1-5)
- `module_id` (string): Reference to the parent module
- `content_path` (string): File path relative to docs directory
- `estimated_reading_time` (integer): Estimated time in minutes to read the chapter
- `learning_objectives` (array of strings): List of learning objectives for the chapter
- `prerequisites` (array of strings): List of prerequisite knowledge or chapters
- `slug` (string): URL-friendly version for routing

**Validation Rules**:
- `id` must be unique across all chapters
- `title` is required and must be 5-100 characters
- `sidebar_position` must be unique within the same `module_id` and between 1-5
- `module_id` must reference an existing Module entity
- `content_path` must exist in the file system and end with .md or .mdx
- `estimated_reading_time` must be between 5-45 minutes
- `slug` must match pattern: ^[a-z0-9]+(?:-[a-z0-9]+)*$

**Relationships**:
- Many-to-one with Module entity (many chapters belong to one module)

## Entity: Theme Configuration

**Description**: Represents the visual appearance settings for the textbook, including color scheme, typography, and responsive behavior.

**Fields**:
- `primary_color` (string): Main brand color in CSS format (hex, rgb, or named color)
- `secondary_color` (string): Secondary accent color
- `dark_mode_default` (boolean): Whether dark mode is enabled by default
- `font_family` (string): Primary font family for body text
- `heading_font_family` (string): Font family for headings
- `responsive_breakpoints` (object): Breakpoints for responsive design
  - `mobile` (string): Max width for mobile view (e.g., "768px")
  - `tablet` (string): Max width for tablet view (e.g., "996px")
  - `desktop` (string): Min width for desktop view (e.g., "997px")
- `academic_typography` (boolean): Whether to use academic-style typography (Georgia serif)

**Validation Rules**:
- `primary_color` must be a valid CSS color format
- `secondary_color` must be a valid CSS color format
- `font_family` and `heading_font_family` must be valid CSS font families
- `responsive_breakpoints` values must be valid CSS dimension strings
- `academic_typography` must be a boolean value

**Relationships**:
- Global configuration applied to all pages and components

## Entity: Deployment Configuration

**Description**: Represents GitHub Pages deployment settings including organization, project name, and base URL configuration.

**Fields**:
- `organization_name` (string): GitHub organization/user name (e.g., "MominKhanX")
- `project_name` (string): GitHub repository name (e.g., "neurobot-textbook")
- `base_url` (string): Base URL path for the site (e.g., "/neurobot-textbook/")
- `deployment_branch` (string): Branch to deploy from (typically "main" or "gh-pages")
- `url` (string): Base URL for the deployed site (e.g., "https://mominkhanx.github.io")
- `favicon` (string): Path to favicon file
- `trailing_slash` (string): Whether to add trailing slashes to URLs ("always", "never", or "auto")

**Validation Rules**:
- `organization_name` must follow GitHub naming conventions (1-39 characters, alphanumeric and hyphens only)
- `project_name` must follow GitHub repository naming conventions
- `base_url` must start with "/" and end with "/" (e.g., "/project-name/")
- `url` must be a valid URL without trailing slash
- `trailing_slash` must be one of "always", "never", or "auto"

**Relationships**:
- Used by build process to generate correct asset paths and links

## Entity: Sidebar Configuration

**Description**: Represents the navigation structure that organizes modules and chapters in the sidebar.

**Fields**:
- `type` (string): Always "category" for module-level items
- `label` (string): Display name for the sidebar item
- `items` (array): Array of child items (subcategories or doc links)
- `collapsed` (boolean): Whether the category is collapsed by default
- `collapsible` (boolean): Whether the category can be expanded/collapsed
- `link` (object, optional): Link to a specific document or page
  - `type` (string): "doc" for internal documentation links
  - `id` (string): ID of the linked document

**Validation Rules**:
- `type` must be "category" for modules or "doc" for individual chapters
- `label` is required and must be 1-50 characters
- `items` array must contain valid sidebar item objects
- If `link` is provided, `type` must be "doc" and `id` must reference an existing document

**Relationships**:
- References Module and Chapter entities to build navigation hierarchy
- Used by Docusaurus to generate sidebar navigation

## Entity: Metadata Configuration

**Description**: Represents SEO and social sharing metadata for pages and the site as a whole.

**Fields**:
- `title` (string): Page title (overrides document title if provided)
- `description` (string): Page description for search engines and social sharing
- `image` (string): Path to social sharing image (recommended 1200x630px)
- `keywords` (array of strings): SEO keywords for the page
- `author` (string): Author of the content
- `tags` (array of strings): Content tags for organization and search
- `og:type` (string): Open Graph type (e.g., "article", "website")
- `twitter:card` (string): Twitter card type (e.g., "summary", "summary_large_image")

**Validation Rules**:
- `title` should be 10-60 characters for optimal SEO
- `description` should be 50-160 characters
- `image` path must exist in static directory
- `keywords` array should have 3-10 items
- `og:type` must be a valid Open Graph type
- `twitter:card` must be a valid Twitter card type

**Relationships**:
- Applied to individual Chapter entities through frontmatter
- Global defaults defined in docusaurus.config.js

## Entity: Search Configuration

**Description**: Represents search functionality settings for the site.

**Fields**:
- `enabled` (boolean): Whether search is enabled
- `type` (string): Search implementation type ("algolia", "local")
- `algolia` (object, optional): Algolia-specific configuration
  - `appId` (string): Algolia application ID
  - `apiKey` (string): Algolia search-only API key
  - `indexName` (string): Name of the Algolia index
  - `contextualSearch` (boolean): Whether to enable contextual search
  - `searchParameters` (object): Additional search parameters
- `local` (object, optional): Local search configuration
  - `highlightSearchTermsOnTargetPage` (boolean): Highlight search terms
  - `indexDocs` (boolean): Whether to index documentation pages
  - `indexBlog` (boolean): Whether to index blog pages
  - `indexPages` (boolean): Whether to index custom pages

**Validation Rules**:
- If `type` is "algolia", all required algolia fields must be provided
- If `type` is "local", local search configuration must be provided
- `appId`, `apiKey`, and `indexName` must be non-empty strings for Algolia
- Only one search type can be active at a time

**Relationships**:
- Applied globally to the entire site through docusaurus.config.js
- Affects searchability of all Chapter entities