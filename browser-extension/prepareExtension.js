import {
  selectValue,
  generateImportWrappers,
  writeManifest,
  writeConfig,
  readPackage,
} from './prepareTools.js';

const env = process.env.TOURNESOL_ENV || 'production';

const browser = process.env.EXTENSION_BROWSER || 'firefox';
if (process.env.EXTENSION_BROWSER && !process.env.MANIFEST_VERSION) {
  throw new Error(`MANIFEST_VERSION is required with EXTENSION_BROWSER`);
}

const manifestVersion = parseInt(process.env.MANIFEST_VERSION || 2);
if (manifestVersion != 2 && manifestVersion != 3)
  throw new Error(`Invalid manifest version: ${manifestVersion}`);
if (manifestVersion === 2) {
  console.info(
    `Extension will be configured with manifest version ${manifestVersion}.`
  );
} else {
  console.info(
    `Extension will be configured for ${browser} with manifest version ${manifestVersion}.`
  );
}

const { version } = await readPackage();
const hostPermissions = [
  ...selectValue(env, {
    production: ['https://tournesol.app/', 'https://api.tournesol.app/'],
    'dev-env': [
      'http://localhost/',
      'http://localhost:3000/',
      'http://localhost:8000/',
    ],
  }),
  'https://www.youtube.com/',
];

const permissions = [
  'activeTab',
  'contextMenus',
  'storage',
  'webNavigation',
  // webRequest and webReauestBlocking were used to overwrite
  // headers in the API response. This is no longer the case
  // with version > 3.5.2.
  // These permissions can be removed as soon as we are confident
  // the next release works as expected.
  ...selectValue(manifestVersion, {
    2: ['webRequest', 'webRequestBlocking'],
    3: ['scripting'],
  }),
];

const allPermissions = selectValue(manifestVersion, {
  2: { permissions: [...hostPermissions, ...permissions] },
  3: { permissions, host_permissions: hostPermissions },
});

const webAccessibleResourcesFromYouTube = [
  'Logo128.png',
  'html/*',
  'images/*',
  'utils.js',
  'models/*',
  'config.js',
];

const manifest = {
  name: 'Tournesol Extension',
  version,
  description: 'Open Tournesol directly from YouTube',
  ...allPermissions,
  manifest_version: manifestVersion,
  icons: {
    64: 'Logo64.png',
    128: 'Logo128.png',
    512: 'Logo512.png',
  },
  background: selectValue(manifestVersion, {
    2: { page: 'background.html', persistent: true },
    3: selectValue(browser, {
      // It's possible to make a browser-independent background value but
      // Chrome only supports that since version 121 released in January 2024.
      // See https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/manifest.json/background
      firefox: {
        scripts: ['background.js'],
        type: 'module',
      },
      chrome: {
        service_worker: 'background.js',
        type: 'module',
      },
    }),
  }),
  [selectValue(manifestVersion, { 2: 'browser_action', 3: 'action' })]: {
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
      js: ['addVideoStatistics.js', 'addModal.js', 'addVideoButtons.js'],
      css: ['addVideoStatistics.css', 'addModal.css', 'addVideoButtons.css'],
      run_at: 'document_end',
      all_frames: true,
    },
    {
      matches: selectValue(env, {
        production: ['https://tournesol.app/*'],
        'dev-env': ['http://localhost:3000/*'],
      }),
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
  web_accessible_resources: selectValue(manifestVersion, {
    2: webAccessibleResourcesFromYouTube,
    3: [
      {
        matches: [
          'https://*.youtube.com/*',
          selectValue(env, {
            production: 'https://tournesol.app/*',
            'dev-env': 'http://localhost:3000/*',
          }),
        ],
        resources: webAccessibleResourcesFromYouTube,
      },
    ],
  }),
};

// Please DO NOT add a trailing slash to front end URL, this prevents
// creating duplicates in our web analytics tool
const config = {
  manifestVersion,
  ...selectValue(env, {
    production: {
      frontendUrl: 'https://tournesol.app',
      frontendHost: 'tournesol.app',
      apiUrl: 'https://api.tournesol.app',
    },
    'dev-env': {
      frontendUrl: 'http://localhost:3000',
      frontendHost: 'localhost:3000',
      apiUrl: 'http://localhost:8000',
    },
  }),
};

(async () => {
  await generateImportWrappers(manifest, webAccessibleResourcesFromYouTube);
  await writeManifest(manifest, 'src/manifest.json');
  await writeConfig(config, 'src/config.js');
})();
