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
  const recoDefaultLanguages = document.getElementById(
    'recommendations__default_languages'
  ).value;

  browser.storage.local.set(
    { recommendations__default_languages: recoDefaultLanguages },
    () => {
      // todo: add a visual feedback here
    }
  );
};

document.addEventListener('DOMContentLoaded', loadPreferences);
document
  .getElementById('save-preferences')
  .addEventListener('click', savePreferences);
