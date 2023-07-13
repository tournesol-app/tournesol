const DEFAULT_RECO_LANG = 'en';

// This delay is designed to be few miliseconds slower than our CSS fadeOut
// animation to let the success message disappear before re-enabling the
// submit button. Don't make it faster than the fadeOut animation.
const FEEDBACK_DELAY = 1804;

const removeAttribute = (element, attribute, delay) => {
  setTimeout(() => {
    element.removeAttribute(attribute);
  }, delay);
};

const displayFeedback = (type) => {
  if (type === 'success') {
    const success = document.querySelector('.feedback-success');
    success.classList.add('displayed');

    setTimeout(() => {
      success.classList.remove('displayed');
    }, FEEDBACK_DELAY);

    return;
  }
};

const loadLocalPreferences = () => {
  chrome.storage.local.get(
    { recommendations__default_languages: DEFAULT_RECO_LANG },
    (settings) => {
      document.getElementById('recommendations__default_languages').value =
        settings.recommendations__default_languages;
    }
  );
};

const saveLocalPreferences = () => {
  const submit = document.getElementById('save-preferences');
  submit.setAttribute('disabled', '');

  const recoDefaultLanguages = document.getElementById(
    'recommendations__default_languages'
  ).value;

  browser.storage.local
    .set({ recommendations__default_languages: recoDefaultLanguages })
    .then(() => {
      displayFeedback('success');
      removeAttribute(submit, 'disabled', FEEDBACK_DELAY);
    })
    .catch(() => {
      removeAttribute(submit, 'disabled', FEEDBACK_DELAY);
    });
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
