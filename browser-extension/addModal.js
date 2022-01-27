/**
 * Create a modal including a Tournesol login iframe.
 *
 * This content script is meant to be run on each YouTube video page.
 *
 * @require config/const.js
 */

/**
 * Youtube doesnt completely load a video page, so content script doesn't
 * launch correctly without these events.
 *
 * This part is called on connection for the first time on youtube.com/*
 */
document.addEventListener('yt-navigate-finish', addTournesolModal);

if (document.body) {
  addTournesolModal();
} else {
  document.addEventListener('DOMContentLoaded', addTournesolModal);
}

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.message === "hideExtensionModal") {
    const modal = document.getElementById(EXT_MODAL_ID);

    if (modal) {
      modal.style.display = 'none';
    }
    return;
  }

  if (request.message === "displayModal") {
    const modal = document.getElementById(EXT_MODAL_ID);
    modal.style.display = EXT_MODAL_VISIBLE_STATE;
    if (modal) {
      sendResponse({success: true});
    } else {
      sendResponse({success: false, message: "modal not found in DOM"});
    }
  }
});

function addTournesolModal() {
  const videoId = new URL(location.href).searchParams.get('v');

  // Only enable this script on youtube.com/watch?v=* pages
  if (!location.pathname.startsWith('/watch') || !videoId) return;

  // Timers will run until needed elements are generated
  const iframeTimer = window.setInterval(createTournesolModal, 300);

  /**
   * Create the extension modal, including a default iframe to the Tournesol
   * application.
   *
   * Adding an hidden iframe in each YouTube video page allows to silently
   * trigger a token refresh in the background. This makes the already logged
   * users able to use the extension features seamlessly, without requiring to
   * visit the Tournesol application site to trigger a token refresh.
   */
  function createTournesolModal() {
    // don't do anything if the required parent is not available
    if (!document.querySelector(EXT_MODAL_WAIT_FOR)) return;

    // don't do anything if the modal is already in the DOM
    if (document.getElementById(EXT_MODAL_ID)) {
      window.clearInterval(iframeTimer);
      return;
    }

    window.clearInterval(iframeTimer);

    const modal = document.createElement('div');
    modal.setAttribute('id', EXT_MODAL_ID);

    const iframe = document.createElement('iframe');
    iframe.setAttribute('id', IFRAME_TOURNESOL_LOGIN_ID);
    iframe.setAttribute('src', chrome.runtime.getURL(
      'html/tournesol-iframe.html'
    ));
    modal.append(iframe);
    document.body.prepend(modal);

    // hide the modal on click
    document.onclick = function(event) {
      const expectedModal = document.getElementById(EXT_MODAL_ID);
      if (event.target === expectedModal) {
        expectedModal.style.display = 'none';
      }
    }

    // hide the modal when the escape key is pressed
    document.onkeydown = function(event) {
      const expectedModal = document.getElementById(EXT_MODAL_ID);
      const currentDisplay = expectedModal.style.display;

      if ((event.key === 'Escape' || event.code === 'Escape')
          && currentDisplay !== 'none') {
        expectedModal.style.display = 'none';
      }
    }
  }
};
