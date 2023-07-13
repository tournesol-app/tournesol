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

const loadLegacyRecommendationsLanguages = () => {
  return new Promise((resolve) =>
    chrome.storage.local.get(
      'recommendationsLanguages',
      ({ recommendationsLanguages }) => resolve(recommendationsLanguages)
    )
  );
};

const loadLocalPreferences = async () => {
  // todo: handle promise rejection?
  const legacy = await loadLegacyRecommendationsLanguages();

  chrome.storage.local.get('recommendations__default_languages', (settings) => {
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
  });
};

const saveLocalPreferences = () => {
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
