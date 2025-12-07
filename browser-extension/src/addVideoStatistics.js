/**
 * Create the statistics container.
 *
 * This content script is meant to be run on each YouTube video page.
 */

import { frontendUrl } from './config.js';

const TS_ACTIONS_ROW_ID = 'ts-video-actions-row';
var browser = browser || chrome;

// Refresh stats at the end of YT page transition
document.addEventListener('yt-navigate-finish', addVideoStatistics);

/*
 * Create the statistics container with the tournesol score, comparisons and contributors.
 */
function addVideoStatistics() {
  const videoId = new URL(location.href).searchParams.get('v');
  if (!location.pathname.startsWith('/watch') || !videoId) return;

  let videoStatsResponse = null;
  browser.runtime.sendMessage(
    {
      message: 'getVideoStatistics',
      video_id: videoId,
    },
    function (resp) {
      videoStatsResponse = resp;
    }
  );

  const timer = window.setInterval(createStatisticsIsReady, 300);

  /**
   * Create the statistics container.
   */
  function createStatisticsIsReady() {
    const actionsRow = document.getElementById(TS_ACTIONS_ROW_ID);
    if (!actionsRow) return;

    const existingInfo = document.getElementById('tournesol-statistics-info');
    if (existingInfo) {
      existingInfo.remove();
    }

    if (videoStatsResponse == null) {
      return;
    }

    window.clearInterval(timer);

    const infoElem = document.createElement('span');
    infoElem.setAttribute('id', 'tournesol-statistics-info');
    infoElem.className = 'tournesol-statistics-info';

    if (videoStatsResponse && videoStatsResponse.body) {
      const details = videoStatsResponse.body.collective_rating;
      if (!details?.n_comparisons) {
        infoElem.textContent = chrome.i18n.getMessage('videoNotRatedMessage');
      } else {
        // Show sunflower icon, score, comparisons, contributors
        const tournesolScore = document.createElement('span');
        tournesolScore.className = 'tournesol-statistics-score';
        tournesolScore.textContent =
          details.tournesol_score == null
            ? '?'
            : details.tournesol_score.toFixed(0);

        const dotSpan = document.createElement('span');
        dotSpan.classList.add('dot');
        dotSpan.textContent = '\xA0•\xA0';
        tournesolScore.appendChild(dotSpan);

        const sunflowerImg = document.createElement('img');
        sunflowerImg.src = `${frontendUrl}/svg/tournesol.svg`;
        sunflowerImg.alt = 'Tournesol logo';
        sunflowerImg.classList.add('tournesol-statistics-icon');
        if (details.unsafe.status) {
          sunflowerImg.classList.add('unsafe');
        }
        const comparisonsSpan = document.createElement('span');
        comparisonsSpan.className = 'tournesol-statistics-comparisons';
        comparisonsSpan.textContent = chrome.i18n.getMessage('comparisonsBy', [
          details.n_comparisons,
        ]);

        const contributorsSpan = document.createElement('span');
        contributorsSpan.className = 'tournesol-statistics-contributors';
        contributorsSpan.textContent = chrome.i18n.getMessage(
          'comparisonsContributors',
          [details.n_contributors]
        );

        infoElem.appendChild(sunflowerImg);
        infoElem.appendChild(tournesolScore);

        infoElem.appendChild(comparisonsSpan);
        infoElem.appendChild(contributorsSpan);
      }
    } else {
      infoElem.textContent = chrome.i18n.getMessage('videoNotRatedMessage');
    }
    actionsRow.insertBefore(infoElem, actionsRow.firstChild);
  }
}
