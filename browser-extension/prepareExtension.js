/* eslint-env node */

import {
  getForEnv,
  generateImportWrappers,
  writeManifest,
  writeConfig,
} from './prepareTools.js';

const env = process.env.TOURNESOL_ENV || 'production';

const manifest = {
  name: 'Tournesol Extension',
  version: '3.4.0',
  description: 'Open Tournesol directly from YouTube',
  permissions: [
    ...getForEnv(
      {
        production: ['https://tournesol.app/', 'https://api.tournesol.app/'],
        'dev-env': [
          'http://localhost/',
          'http://localhost:3000/',
          'http://localhost:8000/',
        ],
      },
      env
    ),
    'https://www.youtube.com/',
    'activeTab',
    'contextMenus',
    'storage',
    'webNavigation',
    'webRequest',
    'webRequestBlocking',
  ],
  manifest_version: 2,
  icons: {
    64: 'Logo64.png',
    128: 'Logo128.png',
    512: 'Logo512.png',
  },
  background: {
    page: 'background.html',
    persistent: true,
  },
  browser_action: {
    default_icon: {
      16: 'Logo16.png',
      64: 'Logo64.png',
    },
    default_title: 'Tournesol actions',
    default_popup: 'browserAction/menu.html',
  },
  content_scripts: [
    {
      matches: ['https://*.youtube.com/*'],
      js: ['displayHomeRecommendations.js', 'displaySearchRecommendations.js'],
      css: ['addTournesolRecommendations.css'],
      run_at: 'document_start',
      all_frames: true,
    },
    {
      matches: ['https://*.youtube.com/*'],
      js: ['addVideoStatistics.js', 'addModal.js', 'addRateButtons.js'],
      css: ['addVideoStatistics.css', 'addModal.css', 'addRateButtons.css'],
      run_at: 'document_end',
      all_frames: true,
    },
    {
      matches: getForEnv(
        {
          production: ['https://tournesol.app/*'],
          'dev-env': ['http://localhost:3000/*'],
        },
        env
      ),
      js: [
        'fetchTournesolToken.js',
        'fetchTournesolRecommendationsLanguages.js',
      ],
      run_at: 'document_end',
      all_frames: true,
    },
  ],
  options_ui: {
    page: 'options/options.html',
    open_in_tab: true,
  },
  default_locale: 'en',
  web_accessible_resources: [
    'Logo128.png',
    'html/*',
    'images/*',
    'utils.js',
    'models/*',
  ],
};

const config = getForEnv(
  {
    production: {
      frontendUrl: 'https://tournesol.app/',
      frontendHostEquals: 'tournesol.app',
      apiUrl: 'https://api.tournesol.app/',
    },
    'dev-env': {
      frontendUrl: 'http://localhost:3000/',
      frontendHostEquals: 'localhost:3000',
      apiUrl: 'http://localhost:8000/',
    },
  },
  env
);

(async () => {
  await generateImportWrappers(manifest);
  await writeManifest(manifest, 'src/manifest.json');
  await writeConfig(config, 'src/config.js');
})();
