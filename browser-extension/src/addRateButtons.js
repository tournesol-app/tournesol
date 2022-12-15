/**
 * Create the Rate Later and the Rate Now buttons.
 *
 * This content script is meant to be run on each YouTube video page.
 */

/**
 * Youtube doesnt completely load a video page, so content script doesn't
 * launch correctly without these events.
 *
 * This part is called on connection for the first time on youtube.com/*
 */
document.addEventListener('yt-navigate-finish', addRateButtons);

if (document.body) {
  addRateButtons();
} else {
  document.addEventListener('DOMContentLoaded', addRateButtons);
}

function getYtButtonsContainer() {
  return (
    // 2022-06-06: container used by Youtube redesign will be searched first.
    document.querySelector(
      '#menu.ytd-watch-metadata #top-level-buttons-computed'
    ) ||
    document.querySelector(
      '#menu.ytd-video-primary-info-renderer #top-level-buttons-computed'
    )
  );
}

function addRateButtons() {
  const videoId = new URL(location.href).searchParams.get('v');

  // Only enable on youtube.com/watch?v=* pages
  if (!location.pathname.startsWith('/watch') || !videoId) return;

  // Timers will run until needed elements are generated
  const timer = window.setInterval(createButtonIsReady, 300);

  /**
   * Create the Rate Later and the Rate Now buttons.
   */
  function createButtonIsReady() {
    /*
     ** Wait for needed elements to be generated
     ** It seems those elements are generated via javascript, so run-at document_idle in manifest is not enough to prevent errors
     **
     ** Some ids on video pages are duplicated, so I take the first non-duplicated id and search in its childs the correct div to add the button
     ** Note: using .children[index] when child has no id
     */
    const buttonsContainer = getYtButtonsContainer();
    if (!buttonsContainer) {
      return;
    }

    // If the button already exists, don't create a new one
    if (document.getElementById('tournesol-rate-later-button')) {
      window.clearInterval(timer);
      return;
    }

    window.clearInterval(timer);

    const addRateButton = ({ id, label, iconSrc, onClick }) => {
      // Create Button
      const button = document.createElement('button');
      button.setAttribute('id', id);
      button.setAttribute('class', 'tournesol-rate-button');

      // Icon
      const image = document.createElement('img');
      image.setAttribute('class', 'tournesol-button-image');
      image.setAttribute('src', iconSrc);
      image.setAttribute('width', '24');
      button.append(image);

      // Label
      const text = document.createTextNode(label);
      button.append(text);

      const setLabel = (label) => {
        text.textContent = label;
      };

      // On click
      button.onclick = onClick;

      // Insert after like and dislike buttons
      buttonsContainer.insertBefore(button, buttonsContainer.children[2]);

      return { button, setLabel };
    };

    addRateButton({
      id: 'tournesol-rate-now-button',
      label: 'Rate Now',
      iconSrc: chrome.runtime.getURL('images/compare.svg'),
      onClick: () => {
        chrome.runtime.sendMessage({
          message: 'displayModal',
          modalOptions: {
            src: `https://tournesol.app/comparison?embed=1&uidA=yt%3A${videoId}`,
            height: '90vh',
          },
        });
      },
    });

    const { button: rateLaterButton, setLabel: setRateLaterButtonLabel } =
      addRateButton({
        id: 'tournesol-rate-later-button',
        label: 'Rate Later',
        iconSrc: chrome.runtime.getURL('images/add.svg'),
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
                  setRateLaterButtonLabel('Done!');
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
  }
}
