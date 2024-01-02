// Youtube doesnt completely load a video page, so content script doesn't lauch correctly without these events

// This part is called on connection for the first time on youtube.com/*
/* ********************************************************************* */

import { frontendUrl } from './config.js';

var browser = browser || chrome;

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
      !document.getElementById('menu-container').children.item('menu') ||
      !document.getElementById('menu-container').children.item('menu')
        .children[0] ||
      !document.getElementById('menu-container').children['menu'].children[0]
        .children['top-level-buttons-computed']
    )
      return;

    // If the button already exists, don't create a new one
    if (document.getElementById('tournesol-statistics')) {
      window.clearInterval(timer);
      return;
    }

    window.clearInterval(timer);

    browser.runtime.sendMessage(
      {
        message: 'getVideoStatistics',
        video_id: videoId,
      },
      function (resp) {
        if (document.getElementById('tournesol-details-button')) {
          return;
        }

        if (resp && resp.results && resp.results.length == 1) {
          const details = resp.results[0];
          if (details.tournesol_score == 0) return;
          if (details.tournesol_score > 0 && details.tournesol_score < 400)
            alert(
              "This video was rated below average by Tournesol's contributors",
              'Ok'
            );
          if (details.tournesol_score < 0)
            alert(
              "Be careful! This video was rated very negatively by Tournesol's contributors",
              'Ok'
            );

          // Create Button
          var statisticsButton = document.createElement('button');
          statisticsButton.setAttribute('id', 'tournesol-details-button');

          // Text td for better vertical alignment
          var statisticsTextTd = document.createElement('td');
          statisticsTextTd.setAttribute('valign', 'middle');
          const statisticsTextTdText = document.createTextNode(
            `Score: ${details.tournesol_score.toFixed(0)}`
          );
          statisticsTextTd.append(statisticsTextTdText);
          statisticsButton.append(statisticsTextTd);

          // On click
          statisticsButton.onclick = () => {
            open(`${frontendUrl}/entities/yt:${videoId}?utm_source=extension`);
          };

          var div =
            document.getElementById('menu-container').children['menu']
              .children[0].children['top-level-buttons-computed'];
          div.insertBefore(statisticsButton, div.children[2]);
        }
      }
    );
  }
}
