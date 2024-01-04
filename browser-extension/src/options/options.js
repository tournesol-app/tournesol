/**
 * This script manages the user's preferences.
 *
 * It sets up the UI, allowing the users to navigate between the local
 * preferences form and the online account preferences form.
 *
 * It also manage the loading and saving the local preferences.
 */

import { frontendUrl } from '../config.js';

const DEFAULT_RECO_LANG = ['en'];
// This delay is designed to be few miliseconds slower than our CSS fadeOut
// animation to let the success message disappear before re-enabling the
// submit button. Don't make it faster than the fadeOut animation.
const FEEDBACK_DELAY = 1804;

const removeAttribute = (element, attribute, delay) => {
  setTimeout(() => {
    element.removeAttribute(attribute);
  }, delay);
};

const _displayFeedbackElement = (selector) => {
  const element = document.querySelector(selector);
  element.classList.add('displayed');

  setTimeout(() => {
    element.classList.remove('displayed');
  }, FEEDBACK_DELAY);
};

const displayFeedback = (type) => {
  switch (type) {
    case 'error':
      _displayFeedbackElement('.feedback-error');
      break;
    case 'success':
      _displayFeedbackElement('.feedback-success');
      break;
  }
};

/**
 *
 * Loading and saving the user's local preferences.
 *
 */

const loadLegacyRecommendationsLanguages = () => {
  return new Promise((resolve) => {
    try {
      chrome.storage.local.get(
        'recommendationsLanguages',
        ({ recommendationsLanguages }) => resolve(recommendationsLanguages)
      );
    } catch (reason) {
      console.error(reason);
      resolve();
    }
  });
};

const loadLegacySearchState = () => {
  return new Promise((resolve) => {
    try {
      chrome.storage.local.get('searchEnabled', ({ searchEnabled }) =>
        resolve(searchEnabled)
      );
    } catch (reason) {
      console.error(reason);
      resolve();
    }
  });
};

/**
 * Load the user's local preferences from the extension storage.local area. In
 * case of error, display an alert in the UI.
 */
const loadLocalPreferences = async () => {
  let error = false;

  const legacyRecoLangs = await loadLegacyRecommendationsLanguages();
  const legacySearchReco = await loadLegacySearchState();

  try {
    chrome.storage.local.get('extension__search_reco', (settings) => {
      const searchState = settings?.extension__search_reco ?? legacySearchReco;

      if (searchState) {
        document.querySelector('input#extension__search_reco').checked = true;
      }
    });

    chrome.storage.local.get(
      'recommendations__default_languages',
      (settings) => {
        const languages =
          settings?.recommendations__default_languages ??
          legacyRecoLangs?.split(',') ??
          DEFAULT_RECO_LANG;

        document
          .querySelectorAll(
            'input[data-setting="recommendations__default_langagues"]'
          )
          .forEach((field) => {
            const name = field.getAttribute('name');

            if (languages.includes(name)) {
              field.checked = true;
            }
          });
      }
    );
  } catch (reason) {
    error = true;
    console.error(reason);
  }

  if (error) {
    document.getElementById('page-error').classList.remove('hidden');
  }
};

/**
 * Save the user's local preferences in the extension storage.local area. In
 * case of error, display an alert in the UI.
 */
const saveLocalPreferences = async () => {
  let error = false;

  const submit = document.getElementById('save-preferences');
  submit.setAttribute('disabled', '');

  const extSearchReco = document.querySelector('input#extension__search_reco');

  const recoDefaultLanguages = [];
  document
    .querySelectorAll(
      'input[data-setting="recommendations__default_langagues"]'
    )
    .forEach((field) => {
      if (field.checked) {
        recoDefaultLanguages.push(field.getAttribute('name'));
      }
    });

  try {
    await chrome.storage.local.set({
      extension__search_reco: extSearchReco.checked,
      recommendations__default_languages: recoDefaultLanguages,
    });
  } catch (reason) {
    error = true;
    console.log(error);
  }

  if (error) {
    displayFeedback('error');
  } else {
    displayFeedback('success');
  }

  removeAttribute(submit, 'disabled', FEEDBACK_DELAY);
};

/**
 *
 * Page navigation.
 *
 */

const hideAllTabs = () => {
  document.querySelectorAll('.page-tab').forEach((tab) => {
    tab.classList.remove('active');
  });

  document.querySelectorAll('.page-navigation button').forEach((btn) => {
    btn.classList.remove('active');
  });
};

const displaySingleTab = (tabId) => {
  document.querySelectorAll(`[data-tab=${tabId}]`).forEach((element) => {
    element.classList.add('active');
  });
};

const onpenTab = (event_) => {
  const tabId = event_.target.dataset.tab;

  hideAllTabs();
  displaySingleTab(tabId);
};

const initNavigation = () => {
  document.querySelectorAll('.page-navigation button').forEach((btn) => {
    btn.addEventListener('click', onpenTab);
  });

  // Make the tab Tournesol Account active by default for authenticated users.
  chrome.storage.local.get(['access_token'], (items) => {
    if (items.access_token) {
      hideAllTabs();
      displaySingleTab('tournesol-account');
    }
  });
};

/**
 *
 * Fields controls.
 *
 */

const _selectAll = (_event) => {
  const target = _event.target.dataset.actionTarget;

  document
    .querySelectorAll(`input[data-setting="${target}"]`)
    .forEach((field) => (field.checked = true));
};

const _deselectAll = (_event) => {
  const target = _event.target.dataset.actionTarget;

  document
    .querySelectorAll(`input[data-setting="${target}"]`)
    .forEach((field) => (field.checked = false));
};

const initControlSelectAll = () => {
  document
    .querySelectorAll('button[data-action-type="select-all"]')
    .forEach((field) => {
      field.addEventListener('click', _selectAll);
    });

  document
    .querySelectorAll('button[data-action-type="deselect-all"]')
    .forEach((field) => {
      field.addEventListener('click', _deselectAll);
    });
};

const initFieldsControls = () => {
  initControlSelectAll();
};

/**
 *
 * Initialization
 *
 */

document.addEventListener('DOMContentLoaded', initNavigation);
document.addEventListener('DOMContentLoaded', initFieldsControls);
document.addEventListener('DOMContentLoaded', loadLocalPreferences);

document
  .getElementById('save-preferences')
  .addEventListener('click', saveLocalPreferences);

document
  .getElementById('preferences-form')
  .addEventListener('submit', (event) => {
    event.preventDefault();
  });

document.getElementById('account-link').href = `${frontendUrl}/signup`;

document
  .getElementById('iframe-tournesol-preferences')
  .setAttribute('src', `${frontendUrl}/settings/preferences?embed=1`);
