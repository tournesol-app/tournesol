/**
 * This script manages the user's preferences.
 *
 * It sets up the UI, allowing the users to navigate between the local
 * preferences form and the account preferences form.
 *
 * It also manage the loading and saving the local preferences.
 */

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

const loadLocalPreferences = async () => {
  let error = false;

  const legacy = await loadLegacyRecommendationsLanguages();

  try {
    chrome.storage.local.get(
      'recommendations__default_languages',
      (settings) => {
        const languages =
          settings?.recommendations__default_languages ??
          legacy?.split(',') ??
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

const saveLocalPreferences = async () => {
  let error = false;

  const submit = document.getElementById('save-preferences');
  submit.setAttribute('disabled', '');

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
    await browser.storage.local.set({
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

const onpenTab = (event_) => {
  const targetTab = event_.target.dataset.tab;
  document.querySelectorAll('.page-tab').forEach((tab) => {
    tab.classList.remove('active');
  });

  document.querySelectorAll('.page-navigation button').forEach((btn) => {
    btn.classList.remove('active');
  });

  document.querySelectorAll(`[data-tab=${targetTab}]`).forEach((element) => {
    element.classList.add('active');
  });
};

const initNavigation = () => {
  document.querySelectorAll('.page-navigation button').forEach((btn) => {
    btn.addEventListener('click', onpenTab);
  });
};

document.addEventListener('DOMContentLoaded', initNavigation);
document.addEventListener('DOMContentLoaded', loadLocalPreferences);

document
  .getElementById('save-preferences')
  .addEventListener('click', saveLocalPreferences);

document
  .getElementById('preferences-form')
  .addEventListener('submit', (event) => {
    event.preventDefault();
  });
