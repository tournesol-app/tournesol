/**
 * Create and add a hidden modal in the DOM, by default including a Tournesol
 * login iframe.
 *
 * This content script is meant to be run on each YouTube page.
 */

// unique HTML id of the extension modal
const EXT_MODAL_ID = 'x-tournesol-modal';
// the value of the CSS property display used to make the modal visible
const EXT_MODAL_VISIBLE_STATE = 'flex';
// the value of the CSS property display used to make the modal invisible
const EXT_MODAL_INVISIBLE_STATE = 'none';

// unique HTML id of the Tournesol iframe
const IFRAME_TOURNESOL_ID = 'x-tournesol-iframe';
// URL of the Tournesol login page
const IFRAME_TOURNESOL_LOGIN_URL = 'https://tournesol.app/login?embed=1&dnt=1';

/**
 * YouTube doesnt completely load a page, so content script doesn't
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
  if (request.message === 'hideModal') {
    const hidden = hideModal();
    sendResponse({ success: hidden });
    return;
  }

  if (request.message === 'displayModal') {
    const displayed = displayModal(request.modalOptions);

    if (displayed) {
      sendResponse({ success: true });
    } else {
      sendResponse({ success: false, message: 'modal not found in DOM' });
    }
  }
});

function initTournesolModal() {
  const iframeTimer = window.setInterval(createTournesolModal, 300);

  /**
   * Create the extension modal, including a default iframe to the Tournesol
   * application.
   *
   * Adding an hidden iframe in each YouTube page allows to silently trigger
   * a token refresh in the background. This makes the already logged users
   * able to use the extension features seamlessly, without requiring to visit
   * the Tournesol application site to trigger a token refresh.
   */
  function createTournesolModal() {
    // don't do anything if the modal is already in the DOM
    if (document.getElementById(EXT_MODAL_ID)) {
      window.clearInterval(iframeTimer);
      return;
    }
    window.clearInterval(iframeTimer);

    const modal = document.createElement('div');
    modal.setAttribute('id', EXT_MODAL_ID);

    const iframe = document.createElement('iframe');
    iframe.setAttribute('id', IFRAME_TOURNESOL_ID);
    iframe.setAttribute('src', IFRAME_TOURNESOL_LOGIN_URL);
    modal.append(iframe);
    document.body.prepend(modal);

    // hide the modal on click
    document.onclick = function (event) {
      const expectedModal = document.getElementById(EXT_MODAL_ID);
      if (event.target === expectedModal) {
        expectedModal.style.display = EXT_MODAL_INVISIBLE_STATE;
      }
    };

    // hide the modal when the escape key is pressed
    document.onkeydown = function (event) {
      const expectedModal = document.getElementById(EXT_MODAL_ID);
      const currentDisplay = expectedModal.style.display;

      if (
        (event.key === 'Escape' || event.code === 'Escape') &&
        currentDisplay !== EXT_MODAL_INVISIBLE_STATE
      ) {
        expectedModal.style.display = EXT_MODAL_INVISIBLE_STATE;
      }
    };
  }
}

/**
 * Single entry point to display the extension modal.
 */
function displayModal({ src, height } = {}) {
  const modal = document.getElementById(EXT_MODAL_ID);
  const iframe = document.getElementById(IFRAME_TOURNESOL_ID);

  if (!modal) {
    return false;
  }

  const display = function display() {
    modal.style.display = EXT_MODAL_VISIBLE_STATE;
    iframe.removeEventListener('load', display);
  };

  // prevent visual blink while refreshing the iframe
  iframe.addEventListener('load', display);

  if (src) {
    iframe.src = src;
  } else {
    // This manual iframe refresh allows to trigger an access token
    // refresh (see the content scripts configuration in manifest.json).
    // This operation is mandatory here as it allows to dismiss any
    // outdated token in the chrome.storage.local. Using the iframe
    // without discarding a local outdated token, will erroneously display
    // the Tournesol home page, instead of the login form.
    iframe.src = IFRAME_TOURNESOL_LOGIN_URL;
  }

  iframe.style.height = height || '';

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
