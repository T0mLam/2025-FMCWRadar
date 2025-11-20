// @ts-check
// `@type` JSDoc annotations allow editor autocompletion and type checking
// (when paired with `@ts-check`).
// There are various equivalent ways to declare your Docusaurus config.
// See: https://docusaurus.io/docs/api/docusaurus-config

import {themes as prismThemes} from 'prism-react-renderer';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

/** @type {import('@docusaurus/types').Config} */
const config = {

  // Future flags, see https://docusaurus.io/docs/api/docusaurus-config#future
  future: {
    v4: true, // Improve compatibility with the upcoming Docusaurus v4
  },

  // Set the production url of your site here
  title: '2025-FMCWRadar Project',
  tagline: 'Identifying human subjects with FMCW Radar and Machine Learning',
  favicon: 'img/favicon.ico',
  url: 'https://spe-uob.github.io',
  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub pages deployment, it is often '/<projectName>/'
  baseUrl: '/2025-FMCWRadar/',

  // GitHub pages deployment config.
  // If you aren't using GitHub pages, you don't need these.
  organizationName: 'spe-uob', // Usually your GitHub org/user name.
  projectName: '2025-FMCWRadar', // Usually your repo name.
  deploymentBranch: 'gh-pages',

  onBrokenLinks: 'throw',

  // Even if you don't use internationalization, you can use this field to set
  // useful metadata like html lang. For example, if your site is Chinese, you
  // may want to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: './sidebars.js',
          // Please change this to your repo.
          // Remove this to remove the "edit this page" links.
          // editUrl:
          //   'https://github.com/spe-uob/2025-FMCWRadar/edit/main/docs',
        },
        blog: {
          showReadingTime: true,
          feedOptions: {
            type: ['rss', 'atom'],
            xslt: true,
          },
          // Please change this to your repo.
          // Remove this to remove the "edit this page" links.
          // editUrl:
          //   'https://github.com/spe-uob/2025-FMCWRadar/edit/main/docs',
          // Useful options to enforce blogging best practices
          onInlineTags: 'warn',
          onInlineAuthors: 'warn',
          onUntruncatedBlogPosts: 'warn',
        },
        theme: {
          customCss: './src/css/custom.css',
        },
      }),
    ],
  ],

  plugins: [
    [
      '@docusaurus/plugin-content-blog',
      {
        id: 'meetings',
        path: 'meetings',
        routeBasePath: 'meetings',
        blogTitle: 'Meetings',
        blogDescription: 'Meeting notes and updates',
        showReadingTime: true,
        feedOptions: { type: ['rss', 'atom'], xslt: true },
        // editUrl: 'https://github.com/spe-uob/2025-FMCWRadar/edit/main/docs',
        onInlineTags: 'warn',
        onInlineAuthors: 'warn',
        onUntruncatedBlogPosts: 'warn',
      },
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      // Replace with your project's social card
      docs: {
      sidebar: {
        hideable: true,
        },
      },
      image: 'img/docusaurus-social-card.jpg',
      colorMode: {
        respectPrefersColorScheme: true,
      },
      navbar: {
        title: '2025-FMCWRadar',
        logo: {
          alt: '2025-FMCWRadar Logo',
          src: 'img/logo.svg',
        },
        items: [
          {
            type: 'docSidebar',
            sidebarId: 'documentSidebar',
            position: 'left',
            label: 'Docs',
          },
          {to: '/meetings', label: 'Meetings', position: 'left'},
          {
            href: 'https://github.com/spe-uob/2025-FMCWRadar',
            label: 'GitHub',
            position: 'right',
          },
                    {
            href: 'https://uob-my.sharepoint.com/:f:/g/personal/ye24597_bristol_ac_uk/Ev_ahirvid1FjZCWQMA8qDoB7L83C-JUGdL5jHDYbqvm-A',
            label: 'OneDrive',
            position: 'right',
          },
          
        ],
      },
      footer: {
        style: 'dark',
        links: [
          {
            title: 'Docs',
            items: [
              {
                label: 'Tutorial',
                to: '/docs/tutorial/intro',
              },
            ],
          },
          {
            title: 'More',
            items: [
              {
                label: 'Meetings',
                to: '/meetings',
              },
              {
                label: 'GitHub',
                href: 'https://github.com/spe-uob/2025-FMCWRadar',
              },
            ],
          },
        ],
        copyright: `Copyright © ${new Date().getFullYear()} | 2025-FMCWRadar Project`,
      },
      prism: {
        theme: prismThemes.github,
        darkTheme: prismThemes.dracula,
      },
    }),
};

export default config;
