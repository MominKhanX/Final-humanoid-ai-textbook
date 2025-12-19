import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

const config: Config = {
  title: 'NeuroBot Physical AI & Humanoid Robotics',
  tagline: 'Master Physical AI and Humanoid Robotics with ROS 2, Digital Twins, and Vision-Language-Action Models',
  favicon: 'img/blue-logo.png',

  // GitHub Pages deployment config
  url: 'https://mominkhanx.github.io',
  baseUrl: '/',
  organizationName: 'MominKhanX',
  projectName: 'neurobot-textbook',
  deploymentBranch: 'gh-pages',
  trailingSlash: false,

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          path: './docs',
          sidebarPath: './sidebars.ts',
          editUrl: 'https://github.com/MominKhanX/neurobot-textbook/tree/main/',
          routeBasePath: 'docs',
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    image: 'img/docusaurus-social-card.jpg',
    navbar: {
      title: 'NeuroBot Textbook',
      logo: {
        alt: 'NeuroBot Logo',
        src: 'img/blue-logo.png',
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'tutorialSidebar',
          position: 'left',
          label: 'Textbook',
        },
        {
          to: '/docs/chapter-1',
          label: 'Start Reading',
          position: 'left',
          className: 'neurobot-start-reading-button',
        },
        {
          href: 'https://github.com/MominKhanX/neurobot-textbook',
          label: 'GitHub',
          position: 'right',
        },
        {
          to: '/signup',
          label: 'Sign Up',
          position: 'right',
          className: 'neurobot-signup-button',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Learn',
          items: [
            {
              label: 'Textbook',
              to: '/docs/intro',
            },
          ],
        },
        {
          title: 'Community',
          items: [
            {
              label: 'GitHub',
              href: 'https://github.com/MominKhanX/neurobot-textbook',
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} NeuroBot Physical AI Textbook. Built with Docusaurus.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
      additionalLanguages: ['python', 'bash', 'yaml', 'json'],
    },
    colorMode: {
      defaultMode: 'dark',
      disableSwitch: false,
      respectPrefersColorScheme: false,
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
