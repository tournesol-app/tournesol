/**
 * Create the statistics container.
 *
 * This content script is meant to be run on each YouTube video page.
 */

import { frontendUrl } from './config.js';

const TS_ACTIONS_ROW_ID = 'ts-video-actions-row';
var browser = browser || chrome;

/**
 * Youtube doesnt completely load a video page, so content script doesn't
 * launch correctly without these events.
 *
 * This part is called on connection for the first time on youtube.com/*
 */
document.addEventListener('yt-navigate-finish', addVideoStatistics);

if (document.body) {
  addVideoStatistics();
} else {
  document.addEventListener('DOMContentLoaded', addVideoStatistics);
}

/*
 * Create the statistics container with the tournesol score, comparisons and contributors.
 */
function addVideoStatistics() {
  const videoId = new URL(location.href).searchParams.get('v');
  if (!location.pathname.startsWith('/watch') || !videoId) return;

  const timer = window.setInterval(createStatisticsIsReady, 300);

  /**
   * Create the statistics container.
   */
  function createStatisticsIsReady() {
    const actionsRow = document.getElementById(TS_ACTIONS_ROW_ID);
    if (!actionsRow) return;

    if (document.getElementById('tournesol-statistics-info')) {
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
        const prev = document.getElementById('tournesol-statistics-info');
        if (prev) prev.remove();

        const infoElem = document.createElement('span');
        infoElem.setAttribute('id', 'tournesol-statistics-info');
        infoElem.className = 'tournesol-statistics-info';

        if (
          resp &&
          resp.body &&
          resp.body.results &&
          resp.body.results.length === 1
        ) {
          const details = resp.body.results[0];
          if (details.collective_rating?.tournesol_score == null) {
            infoElem.textContent = chrome.i18n.getMessage(
              'tournesolNotRatedMessage'
            );
          } else {
            // Show sunflower icon, score, comparisons, contributors
            const scoreSpan = document.createElement('span');
            scoreSpan.className = 'tournesol-statistics-score';
            scoreSpan.textContent =
              details.collective_rating.tournesol_score.toFixed(0);

            const sunflowerImg = document.createElement('img');
            sunflowerImg.src = `${frontendUrl}/svg/tournesol.svg`;
            sunflowerImg.alt = 'Tournesol logo';
            sunflowerImg.className = 'tournesol-statistics-icon';
            scoreSpan.appendChild(sunflowerImg);

            const comparisonsSpan = document.createElement('span');
            comparisonsSpan.className = 'tournesol-statistics-comparisons';
            comparisonsSpan.textContent = chrome.i18n.getMessage(
              'comparisonsBy',
              details.collective_rating.n_contributors
            );

            const contributorsSpan = document.createElement('span');
            contributorsSpan.className = 'tournesol-statistics-contributors';
            contributorsSpan.textContent = chrome.i18n.getMessage(
              'comparisonsContributors',
              details.collective_rating.n_comparisons
            );

            infoElem.appendChild(scoreSpan);
            infoElem.appendChild(comparisonsSpan);
            infoElem.appendChild(contributorsSpan);
          }
        } else {
          infoElem.textContent = chrome.i18n.getMessage('videoNotRatedMessage');
        }
        actionsRow.insertBefore(infoElem, actionsRow.firstChild);
      }
    );
  }
}
