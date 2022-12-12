/**
 * Create the Rate Later button.
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
   * Create the Rate Later button.
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

    const addRateButton = ({ id, label, onClick }) => {
      // Create Button
      const button = document.createElement('button');
      button.setAttribute('id', id);
      button.setAttribute('class', 'tournesol-rate-button');

      // Image td for better vertical alignment
      const img_td = document.createElement('td');
      img_td.setAttribute('valign', 'middle');
      const image = document.createElement('img');
      image.setAttribute('class', 'tournesol-button-image');
      image.setAttribute('src', chrome.runtime.getURL('Logo128.png'));
      image.setAttribute('width', '20');
      img_td.append(image);
      button.append(img_td);

      // Text td for better vertical alignment
      const text_td = document.createElement('td');
      text_td.setAttribute('valign', 'middle');
      let text_td_text = document.createTextNode(label);
      text_td.append(text_td_text);
      button.append(text_td);

      const setLabel = (label) => {
        const new_text = document.createTextNode(label);
        text_td_text.replaceWith(new_text);
        text_td_text = new_text;
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
      onClick: () => {
        chrome.runtime.sendMessage({
          message: 'displayModal',
          modalSrc: `https://tournesol.app/comparison?embed=1&uidA=yt%3A${videoId}`,
        });
      },
    });

    const { button: rateLaterButton, setLabel: setRateLaterButtonLabel } =
      addRateButton({
        id: 'tournesol-rate-later-button',
        label: 'Rate Later',
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
