const DEFAULT_RECO_LANG = 'en';

const loadPreferences = () => {
  chrome.storage.local.get(
    { recommendations__default_languages: DEFAULT_RECO_LANG },
    (settings) => {
      document.getElementById('recommendations__default_languages').value =
        settings.recommendations__default_languages;
    }
  );
};

const savePreferences = () => {
  const submit = document.getElementById('save-preferences');
  submit.setAttribute('disabled', '');

  const recoDefaultLanguages = document.getElementById(
    'recommendations__default_languages'
  ).value;

  browser.storage.local.set(
    { recommendations__default_languages: recoDefaultLanguages },
    () => {
      // todo: add a visual feedback here
    }
  );

  setTimeout(() => {
    submit.removeAttribute('disabled');
  }, 600);
};

document.addEventListener('DOMContentLoaded', loadPreferences);

document
  .getElementById('save-preferences')
  .addEventListener('click', savePreferences);

document
  .getElementById('preferences-form')
  .addEventListener('submit', (event) => {
    event.preventDefault();
  });
