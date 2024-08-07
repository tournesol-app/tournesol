/**
 * Create the Rate Later, the Rate Now and the Wacth on Tournesol buttons.
 *
 * This content script is meant to be run on each YouTube video page.
 */

import { frontendUrl } from './config.js';

const TS_ACTIONS_ROW_ID = 'ts-video-actions-row';
const TS_ACTIONS_ROW_BEFORE_REF = 'bottom-row';

/**
 * Youtube doesnt completely load a video page, so content script doesn't
 * launch correctly without these events.
 *
 * This part is called on connection for the first time on youtube.com/*
 */
document.addEventListener('yt-navigate-finish', addVideoButtons);

if (document.body) {
  addVideoButtons();
} else {
  document.addEventListener('DOMContentLoaded', addVideoButtons);
}

/**
 * The Tournesol video actions row contains the video actions related to the
 * Tournesol project.
 *
 * This container is meant to be displayed after the YouTube actions and
 * before the video descrition container.
 */
const createVideoActionsRow = () => {
  const existing = document.getElementById(TS_ACTIONS_ROW_ID);
  if (existing) {
    existing.remove();
  }

  const videoActions = document.createElement('div');
  videoActions.id = TS_ACTIONS_ROW_ID;

  const beforeRef = document.getElementById(TS_ACTIONS_ROW_BEFORE_REF);
  const parent = document.getElementById(beforeRef.parentElement.id);

  parent.insertBefore(videoActions, beforeRef);
  return videoActions;
};

function createVideoActionsRowParent() {
  const beforeRef = document.getElementById(TS_ACTIONS_ROW_BEFORE_REF);
  if (!beforeRef) {
    return;
  }

  return document.getElementById(beforeRef.parentElement.id);
}

function addVideoButtons() {
  const videoId = new URL(location.href).searchParams.get('v');

  // Only enable on youtube.com/watch?v=* pages
  if (!location.pathname.startsWith('/watch') || !videoId) return;

  // Timers will run until needed elements are generated
  const timer = window.setInterval(createButtonIsReady, 300);

  /**
   * Create the Rate Later, the Rate Now and the Wacth on Tournesol buttons.
   */
  function createButtonIsReady() {
    const buttonsContainer = createVideoActionsRowParent();
    if (!buttonsContainer) {
      return;
    }

    window.clearInterval(timer);
    const videoActions = createVideoActionsRow();

    const addVideoButton = ({ id, label, iconSrc, iconClass, onClick }) => {
      // Create Button
      const button = document.createElement('button');
      button.setAttribute('id', id);
      button.setAttribute('class', 'tournesol-video-button');

      // Icon
      const image = document.createElement('img');
      image.classList.add('tournesol-button-image');
      if (iconClass) image.classList.add(iconClass);
      image.setAttribute('src', iconSrc);
      image.setAttribute('width', '24');
      button.append(image);

      // Label
      const text = document.createTextNode(label);
      button.append(text);

      const setLabel = (label) => {
        text.textContent = label;
      };

      const setIcon = (iconSrc) => {
        image.setAttribute('src', iconSrc);
      };

      button.onclick = onClick;
      videoActions.appendChild(button);

      return { button, setLabel, setIcon };
    };

    // This button doesn't work when: the user is not authenticated, and the
    // video is not in the database.
    //
    // For now, it is displayed only for authenticated users.
    //
    // See: https://github.com/tournesol-app/tournesol/issues/1904
    chrome.storage.local.get(['access_token'], (items) => {
      if (items.access_token) {
        addVideoButton({
          id: 'tournseol-watch-button',
          label: chrome.i18n.getMessage('watchOnTournesolButtonLabel'),
          iconSrc: chrome.runtime.getURL('images/watch.svg'),
          onClick: () => {
            window.open(
              `${frontendUrl}/entities/yt:${videoId}?utm_source=extension&utm_medium=video_button`,
              '_blank'
            );
          },
        });
      }

      addVideoButton({
        id: 'tournesol-rate-now-button',
        label: chrome.i18n.getMessage('rateNowButtonLabel'),
        iconSrc: chrome.runtime.getURL('images/compare.svg'),
        onClick: () => {
          chrome.runtime.sendMessage({
            message: 'displayModal',
            modalOptions: {
              src: `${frontendUrl}/comparison?embed=1&utm_source=extension&utm_medium=frame&uidA=yt%3A${videoId}`,
              height: '90vh',
            },
          });
        },
      });

      const {
        button: rateLaterButton,
        setLabel: setRateLaterButtonLabel,
        setIcon: setRateLaterButtonIcon,
      } = addVideoButton({
        id: 'tournesol-rate-later-button',
        label: chrome.i18n.getMessage('rateLaterButtonLabel'),
        iconSrc: chrome.runtime.getURL('images/add.svg'),
        iconClass: 'tournesol-rate-later',
        onClick: () => {
          rateLaterButton.disabled = true;

          new Promise((resolve, reject) => {
            chrome.runtime.sendMessage(
              {
                message: 'addRateLater',
                video_id: videoId,
              },
              (data) => {
                if (data.success) {
                  setRateLaterButtonLabel(
                    chrome.i18n.getMessage('rateLaterButtonSuccessLabel')
                  );
                  setRateLaterButtonIcon(
                    chrome.runtime.getURL('images/checkmark.svg')
                  );
                  resolve();
                } else {
                  rateLaterButton.disabled = false;
                  reject();
                }
              }
            );
          }).catch(() => {
            chrome.runtime.sendMessage({ message: 'displayModal' });
          });
        },
      });
    });
  }
}
