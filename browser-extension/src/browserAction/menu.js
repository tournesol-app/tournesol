import { addRateLater } from '../utils.js';
import { frontendUrl } from '../config.js';

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
    url: `${frontendUrl}?utm_source=extension&utm_medium=menu`,
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
        url: `${frontendUrl}/comparison?uidA=yt:${videoId}&utm_source=extension&utm_medium=menu`,
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
        url: `${frontendUrl}/entities/yt:${videoId}?utm_source=extension&utm_medium=menu`,
      });
    },
    () => {
      button.disabled = true;
      button.setAttribute('data-error', 'Not a YouTube video page.');
    }
  );
}

function openOptionsPage() {
  chrome.runtime.openOptionsPage();
}

/**
 * Create the action menu.
 */
document.addEventListener('DOMContentLoaded', function () {
  const tournesolHomeLink = document.getElementById('tournesol_home');
  const rateNowButton = document.getElementById('rate_now');
  const rateLaterButton = document.getElementById('rate_later');
  const analysisButton = document.getElementById('analysis');
  const preferencesButton = document.getElementById('preferences');

  tournesolHomeLink.addEventListener('click', openTournesolHome);
  rateNowButton.addEventListener('click', rateNowAction);
  rateLaterButton.addEventListener('click', addToRateLaterAction);
  analysisButton.addEventListener('click', openAnalysisPageAction);
  preferencesButton.addEventListener('click', openOptionsPage);

  rateNowButton.textContent = i18n.getMessage('menuRateNow');
  rateLaterButton.textContent = i18n.getMessage('menuRateLater');
  analysisButton.textContent = i18n.getMessage('menuAnalysis');
  preferencesButton.textContent = i18n.getMessage('menuPreferences');
});
