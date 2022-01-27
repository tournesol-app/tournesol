/**
 * Create and add a hidden modal in the DOM, by default including a Tournesol
 * login iframe.
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
document.addEventListener('yt-navigate-finish', initTournesolModal);

if (document.body) {
  initTournesolModal();
} else {
  document.addEventListener('DOMContentLoaded', initTournesolModal);
}

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.message === "hideModal") {
    const hidden = hideModal();
    sendResponse({success: hidden});
    return;
  }

  if (request.message === "displayModal") {
    const displayed = displayModal();

    if (displayed) {
      sendResponse({success: true});
    } else {
      sendResponse({success: false, message: "modal not found in DOM"});
    }
  }
});

function initTournesolModal() {
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
        expectedModal.style.display = EXT_MODAL_INVISIBLE_STATE;
      }
    }

    // hide the modal when the escape key is pressed
    document.onkeydown = function(event) {
      const expectedModal = document.getElementById(EXT_MODAL_ID);
      const currentDisplay = expectedModal.style.display;

      if ((event.key === 'Escape' || event.code === 'Escape')
          && currentDisplay !== EXT_MODAL_INVISIBLE_STATE) {
        expectedModal.style.display = EXT_MODAL_INVISIBLE_STATE;
      }
    }
  }
};


/**
 * Single entry point to display the extension modal.
 */
function displayModal() {
  const modal = document.getElementById(EXT_MODAL_ID);
  const iframe = document.getElementById(IFRAME_TOURNESOL_LOGIN_ID);

  if (!modal) {
    return false;
  }

  const displayModal = function displayModal() {
    modal.style.display = EXT_MODAL_VISIBLE_STATE;
    iframe.removeEventListener('load', displayModal);
  }

  // prevent visual blink while refreshing the iframe
  iframe.addEventListener('load', displayModal);

  // This manual iframe refresh allows to trigger an access token
  // refresh (see the content scripts configuration in manifest.json).
  // This operation is mandatory here as it allows to dismiss any
  // outdated token in the chrome.storage.local. Using the iframe
  // without discarding a local outdated token, will erroneously display
  // the Tournesol home page, instead of the login form.
  iframe.src = iframe.src;
  return true;
}

function hideModal() {
  const modal = document.getElementById(EXT_MODAL_ID);
  if (!modal) {
    return false;
  }

  modal.style.display = EXT_MODAL_INVISIBLE_STATE;
  return true;
}
