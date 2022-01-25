/**
 * Create the Tournesol iframe.
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
document.addEventListener('yt-navigate-finish', addTournesolIframe);

if (document.body) {
  addTournesolIframe();
} else {
  document.addEventListener('DOMContentLoaded', addTournesolIframe);
}

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.message === "hideTournesolIframe") {
    const iframe = document.getElementById(TOURNESOL_IFRAME_ID);

    if (iframe) {
      const previousState = iframe.style.display;
      iframe.style.display = 'none';

      if (previousState === TOURNESOL_IFRAME_VISIBLE_STATE) {
        window.scroll({top: 0, left: 0, behavior: "smooth"});
      }
    }
  }
});

function addTournesolIframe() {
  const videoId = new URL(location.href).searchParams.get('v');

  // Only enable this script on youtube.com/watch?v=* pages
  if (!location.pathname.startsWith('/watch') || !videoId) return;

  // Timers will run until needed elements are generated
  const iframeTimer = window.setInterval(createTournesolIframe, 300);

  /**
   * Create the an iframe to the Tournesol application.
   *
   * Adding an hidden iframe in each YouTube video page allows to silently
   * trigger a token refresh in the background. This makes the already logged
   * users able to use the extension features seamlessly, without requiring to
   * visit the Tournesol application site to trigger a token refresh.
   */
  function createTournesolIframe() {
    // don't do anything if the required parent is not available
    if (!document.querySelector(TOURNESOL_IFRAME_PARENT_SELECTOR)) return;

    // don't do anything if the iframe is already in the DOM
    if (document.getElementById(TOURNESOL_IFRAME_ID)) {
      window.clearInterval(iframeTimer);
      return;
    }

    window.clearInterval(iframeTimer);

    const iframe = document.createElement('iframe');
    const parent = document.querySelector(TOURNESOL_IFRAME_PARENT_SELECTOR);

    iframe.setAttribute('id', TOURNESOL_IFRAME_ID);
    iframe.setAttribute('src', chrome.runtime.getURL(
      'html/tournesol-iframe.html'
    ));
    parent.appendChild(iframe);
  }
};
