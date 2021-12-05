// Youtube doesnt completely load a video page, so content script doesn't lauch correctly without these events

// This part is called on connection for the first time on youtube.com/*
/* ********************************************************************* */

document.addEventListener('yt-navigate-finish', process);

if (document.body) process();
else document.addEventListener('DOMContentLoaded', process);

/* ********************************************************************* */

function process() {
  // Get video id via URL
  var videoId = new URL(location.href).searchParams.get('v');

  // Only enable on youtube.com/watch?v=* pages
  if (!location.pathname.startsWith('/watch') || !videoId) return;

  // Timer will run until needed elements are generated
  var timer = window.setInterval(createButtonIsReady, 300);

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
      chrome.runtime.sendMessage(
        {
          message: 'addRateLater',
          video_id: videoId
        },
        (data) => {
          if (data.success) {
            text_td_text.replaceWith(document.createTextNode('Done!'))
          }
          else {
            rateLaterButton.disabled = false;
          }
        }
      );
    }

    // Insert after like and dislike buttons
    var div = document.getElementById('menu-container').children['menu'].children[0].children['top-level-buttons-computed'];
    div.insertBefore(rateLaterButton, div.children[2]);
  }
}
