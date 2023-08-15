import { addRateLater } from '../utils.js';

const i18n = chrome.i18n;

function get_current_tab_video_id() {
  function get_tab_video_id(tabs) {
    for (let tab of tabs) {
      // only one tab is returned
      var video_id = new URL(tab.url).searchParams.get('v');
      if (video_id == null || video_id === '') {
        return Promise.reject(new Error('not a video id'));
      }
      return video_id;
    }
  }

  return new Promise((resolve) => {
    chrome.tabs.query({ active: true, currentWindow: true }, resolve);
  }).then(get_tab_video_id);
}

/**
 * Open the Tournesol home page.
 */
function openTournesolHome() {
  chrome.tabs.create({
    url: `https://tournesol.app?utm_source=extension&utm_medium=menu`,
  });
}

/**
 * Open the Tournesol comparison page in a new tab.
 */
function rateNowAction(event) {
  const button = event.target;
  get_current_tab_video_id().then(
    (videoId) => {
      chrome.tabs.create({
        url: `https://tournesol.app/comparison?uidA=yt:${videoId}&utm_source=extension&utm_medium=menu`,
      });
    },
    () => {
      button.disabled = true;
      button.setAttribute('data-error', 'Not a YouTube video page.');
    }
  );
}

/**
 * Add the video to the user's rate-later list.
 *
 * If the user is not logged, display the login iframe.
 */
function addToRateLaterAction(event) {
  const button = event.target;
  get_current_tab_video_id().then(
    async (videoId) => {
      button.disabled = true;
      const { success, message } = await addRateLater(videoId);

      if (success) {
        button.setAttribute('data-success', message);
      } else {
        // ask the content script to display the modal containing the login iframe
        chrome.tabs.query(
          { active: true, currentWindow: true },
          function (tabs) {
            chrome.tabs.sendMessage(
              tabs[0].id,
              { message: 'displayModal' },
              function (response) {
                if (!response.success) {
                  button.setAttribute('data-error', 'Failed.');
                }
              }
            );
          }
        );
      }
    },
    () => {
      button.disabled = true;
      button.setAttribute('data-error', 'Not a YouTube video page.');
    }
  );
}

/**
 * Open the Tournesol entity analysis page in a new tab.
 */
function openAnalysisPageAction(event) {
  const button = event.target;
  get_current_tab_video_id().then(
    (videoId) => {
      chrome.tabs.create({
        url: `https://tournesol.app/entities/yt:${videoId}?utm_source=extension&utm_medium=menu`,
      });
    },
    () => {
      button.disabled = true;
      button.setAttribute('data-error', 'Not a YouTube video page.');
    }
  );
}

/**
 * Initialize the search state button style according to the current state of
 * the search defined in the local storage.
 */
function initSearchStateButtonStyle() {
  const searchButton = document.getElementById('search_state');

  // The search is disabled by default.
  chrome.storage.local.get('searchEnabled', ({ searchEnabled }) => {
    const enabled = searchEnabled;
    if (enabled === null || enabled === undefined) {
      chrome.storage.local.set({ searchEnabled: false });
    }

    if (enabled) {
      searchButton.classList.add('enabled');
      searchButton.textContent = i18n.getMessage('menuSearchEnabled');
    } else {
      searchButton.classList.remove('enabled');
      searchButton.textContent = i18n.getMessage('menuSearchDisabled');
    }
  });
}

/**
 * Enable or disable the search state and update the search state button style
 * accordingly.
 */
function toggleSearchStateAction(event) {
  const searchButton = event.target;

  chrome.storage.local.get('searchEnabled', ({ searchEnabled }) => {
    const newState = searchEnabled ? false : true;

    if (newState === true) {
      searchButton.classList.add('enabled');
    } else {
      searchButton.classList.remove('enabled');
    }

    searchButton.textContent = newState
      ? i18n.getMessage('menuSearchEnabled')
      : i18n.getMessage('menuSearchDisabled');
    chrome.storage.local.set({ searchEnabled: newState });
  });
}

function openOptionsPage() {
  browser.runtime.openOptionsPage();
}

/**
 * Create the action menu.
 */
document.addEventListener('DOMContentLoaded', function () {
  const tournesolHomeLink = document.getElementById('tournesol_home');
  const rateNowButton = document.getElementById('rate_now');
  const rateLaterButton = document.getElementById('rate_later');
  const analysisButton = document.getElementById('analysis');
  const enableSearchButton = document.getElementById('search_state');
  const preferencesButton = document.getElementById('preferences');

  initSearchStateButtonStyle();

  tournesolHomeLink.addEventListener('click', openTournesolHome);
  rateNowButton.addEventListener('click', rateNowAction);
  rateLaterButton.addEventListener('click', addToRateLaterAction);
  analysisButton.addEventListener('click', openAnalysisPageAction);
  enableSearchButton.addEventListener('click', toggleSearchStateAction);
  preferencesButton.addEventListener('click', openOptionsPage);

  rateNowButton.textContent = i18n.getMessage('menuRateNow');
  rateLaterButton.textContent = i18n.getMessage('menuRateLater');
  analysisButton.textContent = i18n.getMessage('menuAnalysis');
  preferencesButton.textContent = i18n.getMessage('menuPreferences');
});
