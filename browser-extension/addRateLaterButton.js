/**
 * Create the Rate Later button and the Tournesol iframe.
 *
 * This content script is meant to be run on each YouTube video page.
 */

const TOURNESOL_IFRAME_ID = 'x-tournesol-iframe';
const TOURNESOL_IFRAME_PARENT_SELECTOR = 'div#info.ytd-watch-flexy';

// Youtube doesnt completely load a video page, so content script doesn't
// launch correctly without these events.

// This part is called on connection for the first time on youtube.com/*

/* ********************************************************************* */

document.addEventListener('yt-navigate-finish', process);

if (document.body) process();
else document.addEventListener('DOMContentLoaded', process);

/* ********************************************************************* */

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.message === "hideTournesolIframe") {
    const iframe = document.getElementById(TOURNESOL_IFRAME_ID);
    if (iframe) {
      iframe.style.display = 'none';
    }
  }
});

function process() {
  // Get video id via URL
  var videoId = new URL(location.href).searchParams.get('v');

  // Only enable on youtube.com/watch?v=* pages
  if (!location.pathname.startsWith('/watch') || !videoId) return;

  // Timers will run until needed elements are generated
  const timer = window.setInterval(createButtonIsReady, 300);
  const iframeTimer = window.setInterval(createTournesolIframe, 300);

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
    if (
      !document.getElementById('menu-container') ||
      !document.getElementById('menu-container').children['menu'] ||
      !document.getElementById('menu-container').children['menu'].children[0] ||
      !document.getElementById('menu-container').children['menu'].children[0].children['top-level-buttons-computed']
    ) return;


    // If the button already exists, don't create a new one
    if (document.getElementById('tournesol-rate-button')) {
      window.clearInterval(timer);
      return;
    }

    window.clearInterval(timer);

    // Create Button
    var rateLaterButton = document.createElement('button');
    rateLaterButton.setAttribute('id', 'tournesol-rate-button');

    // Image td for better vertical alignment
    var img_td = document.createElement('td');
    img_td.setAttribute('valign', 'middle');
    var image = document.createElement('img');
    image.setAttribute('id', 'tournesol-button-image');
    image.setAttribute('src', chrome.runtime.getURL('Logo128.png'));
    image.setAttribute('width', '20');
    img_td.append(image);
    rateLaterButton.append(img_td);

    // Text td for better vertical alignment
    var text_td = document.createElement('td');
    text_td.setAttribute('valign', 'middle');
    text_td_text = document.createTextNode('Rate Later')
    text_td.append(text_td_text);
    rateLaterButton.append(text_td);

    // On click
    rateLaterButton.onclick = () => {
      rateLaterButton.disabled = true;

      const resp = new Promise((resolve, reject) => {
        chrome.runtime.sendMessage(
          {
            message: 'addRateLater',
            video_id: videoId
          },
          (data) => {
            if (data.success) {
              text_td_text.replaceWith(document.createTextNode('Done!'))
              resolve();
            } else {
              rateLaterButton.disabled = false;
              reject();
            }
          }
        );

      }).catch((reason) => {
        const iframe = document.getElementById(TOURNESOL_IFRAME_ID);
        iframe.style.display = 'initial';
      });
    }

    // Insert after like and dislike buttons
    var div = document.getElementById('menu-container').children['menu'].children[0].children['top-level-buttons-computed'];
    div.insertBefore(rateLaterButton, div.children[2]);
  }

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

    const parent = document.querySelector(TOURNESOL_IFRAME_PARENT_SELECTOR);
    const iframe = document.createElement('iframe');

    iframe.setAttribute('id', TOURNESOL_IFRAME_ID);
    iframe.setAttribute('src', chrome.runtime.getURL(
      'html/tournesol-iframe.html'
    ));
    parent.appendChild(iframe);
  }
}
