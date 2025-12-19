import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

const sidebars: SidebarsConfig = {
  tutorialSidebar: [
    {
      type: 'category',
      label: 'Introduction',
      collapsed: false,
      items: [
        'chapter-1',
        'chapter-2',
        'intro-course-structure',
      ],
    },
    {
      type: 'category',
      label: 'Module 1: ROS 2 Fundamentals',
      collapsed: false,
      items: [
        'module-1-ros2/chapter-3',
        'module-1-ros2/chapter-4',
        'module-1-ros2/chapter-5',
        'module-1-ros2/chapter-6',
        'module-1-ros2/chapter-7',
      ],
    },
    {
      type: 'category',
      label: 'Module 2: Digital Twin & Simulation',
      collapsed: true,
      items: [
        'module-2-digital-twin/chapter-8',
        'module-2-digital-twin/chapter-9',
        'module-2-digital-twin/chapter-10',
        'module-2-digital-twin/chapter-11',
      ],
    },
    {
      type: 'category',
      label: 'Module 3: NVIDIA Isaac Platform',
      collapsed: true,
      items: [
        'module-3-nvidia-isaac/chapter-12',
        'module-3-nvidia-isaac/chapter-13',
        'module-3-nvidia-isaac/chapter-14',
        'module-3-nvidia-isaac/chapter-15',
        'module-3-nvidia-isaac/chapter-16',
      ],
    },
    {
      type: 'category',
      label: 'Module 4: Vision-Language-Action',
      collapsed: true,
      items: [
        'module-4-vla/chapter-17',
        'module-4-vla/chapter-18',
        'module-4-vla/chapter-19',
        'module-4-vla/chapter-20',
        'module-4-vla/chapter-21',
        'module-4-vla/chapter-22',
        'module-4-vla/chapter-23',
      ],
    },
  ],
};

export default sidebars;
