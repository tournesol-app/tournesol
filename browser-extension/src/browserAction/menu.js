import { addRateLater } from '../utils.js';

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

  return new Promise((resolve, reject) => {
    chrome.tabs.query({ active: true, currentWindow: true }, resolve);
  }).then(get_tab_video_id);
}

function rate_now(e) {
  const button = e.target;
  get_current_tab_video_id().then(
    (videoId) => {
      chrome.tabs.create({
        url: `https://tournesol.app/comparison/?videoA=${videoId}`,
      });
    },
    (err) => {
      button.disabled = true;
      button.setAttribute('data-error', 'Not a Youtube video page.');
    }
  );
}

function rate_later(e) {
  const button = e.target;
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
    (err) => {
      button.disabled = true;
      button.setAttribute('data-error', 'Not a Youtube video page.');
    }
  );
}

function details(e) {
  const button = e.target;
  get_current_tab_video_id().then(
    (videoId) => {
      chrome.tabs.create({ url: `https://tournesol.app/video/${videoId}` });
    },
    (err) => {
      button.disabled = true;
      button.setAttribute('data-error', 'Not a Youtube video page.');
    }
  );
}

document.addEventListener('DOMContentLoaded', function () {
  document.getElementById('rate_now').addEventListener('click', rate_now);
  document.getElementById('rate_later').addEventListener('click', rate_later);
  document.getElementById('details').addEventListener('click', details);
});
