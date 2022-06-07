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
document.addEventListener('yt-navigate-finish', addRateLaterButton);

if (document.body) {
  addRateLaterButton();
} else {
  document.addEventListener('DOMContentLoaded', addRateLaterButton);
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

function addRateLaterButton() {
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
    if (document.getElementById('tournesol-rate-button')) {
      window.clearInterval(timer);
      return;
    }

    window.clearInterval(timer);

    // Create Button
    const rateLaterButton = document.createElement('button');
    rateLaterButton.setAttribute('id', 'tournesol-rate-button');

    // Image td for better vertical alignment
    const img_td = document.createElement('td');
    img_td.setAttribute('valign', 'middle');
    const image = document.createElement('img');
    image.setAttribute('id', 'tournesol-button-image');
    image.setAttribute('src', chrome.runtime.getURL('Logo128.png'));
    image.setAttribute('width', '20');
    img_td.append(image);
    rateLaterButton.append(img_td);

    // Text td for better vertical alignment
    const text_td = document.createElement('td');
    text_td.setAttribute('valign', 'middle');
    const text_td_text = document.createTextNode('Rate Later');
    text_td.append(text_td_text);
    rateLaterButton.append(text_td);

    // On click
    rateLaterButton.onclick = () => {
      rateLaterButton.disabled = true;

      new Promise((resolve, reject) => {
        chrome.runtime.sendMessage(
          {
            message: 'addRateLater',
            video_id: videoId,
          },
          (data) => {
            if (data.success) {
              text_td_text.replaceWith(document.createTextNode('Done!'));
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
    };

    // Insert after like and dislike buttons
    buttonsContainer.insertBefore(
      rateLaterButton,
      buttonsContainer.children[2]
    );
  }
}
