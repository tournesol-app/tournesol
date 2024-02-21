import {
  addRateLater,
  alertOnCurrentTab,
  alertUseOnLinkToYoutube,
  fetchTournesolApi,
  getAccessToken,
  getRandomSubarray,
  getUserProof,
  getRecommendationsLanguagesAuthenticated,
  getSingleSetting,
} from './utils.js';

import { frontendHost } from './config.js';

const RECENT_VIDEOS_RATIO = 0.75;
const RECENT_VIDEOS_EXTRA_RATIO = 0.5;
const BUNDLE_OVERFETCH_FACTOR = 3;

/**
 * Build the extension context menu.
 *
 * TODO: could be moved in its own `contextMenus` folder, imported and
 *       executed here. Investigate if it's possible.
 */
const createContextMenu = function createContextMenu() {
  chrome.contextMenus.removeAll(function () {
    chrome.contextMenus.create({
      id: 'tournesol_add_rate_later',
      title: 'Rate later on Tournesol',
      contexts: ['link'],
    });
  });

  chrome.contextMenus.onClicked.addListener(function (e, tab) {
    var videoId = new URL(e.linkUrl).searchParams.get('v');
    if (!videoId) {
      alertUseOnLinkToYoutube(tab);
    } else {
      addRateLater(videoId).then((response) => {
        if (!response.success) {
          chrome.tabs.query(
            { active: true, currentWindow: true },
            function (tabs) {
              chrome.tabs.sendMessage(
                tabs[0].id,
                { message: 'displayModal' },
                function (response) {
                  if (!response.success) {
                    alertOnCurrentTab(
                      'Sorry, an error occured while opening the Tournesol login form.',
                      tab
                    );
                  }
                }
              );
            }
          );
        }
      });
    }
  });
};
createContextMenu();

function getDateThreeWeeksAgo() {
  // format a string to properly display years months and day: 2011 -> 11, 5 -> 05, 12 -> 12
  const threeWeeksAgo = new Date(Date.now() - 3 * 7 * 24 * 3600000);
  // we truncate minutes, seconds and ms from the date in order to benefit
  // from caching at the API level.
  threeWeeksAgo.setMinutes(0, 0, 0);
  return threeWeeksAgo.toISOString();
}

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  // Return the current access token in the chrome.storage.local.
  if (request.message === 'extAccessTokenNeeded') {
    getAccessToken().then((token) => sendResponse({ access_token: token }));
    return true;
  }

  // Automatically hide the extension modal containing the login iframe after
  // the access token has been refreshed.
  if (request.message === 'accessTokenRefreshed') {
    chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
      chrome.tabs.sendMessage(tabs[0].id, { message: 'hideModal' });
    });

    return true;
  }

  // Forward the need to the proper content script.
  if (request.message === 'displayModal') {
    chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
      chrome.tabs.sendMessage(
        tabs[0].id,
        {
          message: 'displayModal',
          modalOptions: request.modalOptions,
        },
        function (response) {
          sendResponse(response);
        }
      );
    });
    return true;
  }

  if (request.message === 'openOptionsPage') {
    chrome.runtime.openOptionsPage();
    return true;
  }

  if (request.message == 'addRateLater') {
    addRateLater(request.video_id).then(sendResponse);
    return true;
  }

  if (request.message.startsWith('getProof:')) {
    const keyword = request.message.split(':')[1];

    if (keyword) {
      getUserProof(keyword).then((response) => {
        sendResponse(response);
      });
      return true;
    }
  }

  if (request.message == 'getVideoStatistics') {
    // getVideoStatistics(request.video_id).then(sendResponse);
    return true;
  }

  if (request.message && request.message.startsWith('get:setting:')) {
    let setting = request.message.split(':')[2];

    if (!setting) {
      sendResponse({ value: null });
      return true;
    }

    getSingleSetting(setting, false).then((value) => {
      sendResponse({ value: value });
    });
    return true;
  } else if (
    request.message == 'getTournesolRecommendations' ||
    request.message == 'getTournesolSearchRecommendations'
  ) {
    const poll_name = 'videos';

    const request_recommendations = async (api_path, options) => {
      const resp = await fetchTournesolApi(
        `${api_path}${options ? '?' : ''}${options}`
      );
      if (resp && resp.ok) {
        const json = await resp.json();
        return json.results;
      }
      return [];
    };

    if (request.message === 'getTournesolRecommendations') {
      const api_path = `polls/${poll_name}/recommendations/random/`;

      const nbrPerRow = request.videosNumber;
      const extraNbr = request.additionalVideosNumber;

      const recentToLoadRow1 = Math.round(nbrPerRow * RECENT_VIDEOS_RATIO);
      const oldToLoadRow1 = Math.round(nbrPerRow * (1 - RECENT_VIDEOS_RATIO));

      const recentToLoadExtra = Math.round(
        extraNbr * RECENT_VIDEOS_EXTRA_RATIO
      );
      const oldToLoadExtra = Math.round(
        extraNbr * (1 - RECENT_VIDEOS_EXTRA_RATIO)
      );

      const process = async () => {
        const threeWeeksAgo = getDateThreeWeeksAgo();
        const recommendationsLangs =
          await getRecommendationsLanguagesAuthenticated();

        const recentParams = new URLSearchParams([
          ['date_gte', threeWeeksAgo],
          [
            'limit',
            (recentToLoadRow1 + recentToLoadExtra) * BUNDLE_OVERFETCH_FACTOR,
          ],
          ['bundle', request.queryParamBundle],
        ]);

        const oldParams = new URLSearchParams([
          ['date_lte', threeWeeksAgo],
          ['limit', (oldToLoadRow1 + oldToLoadExtra) * BUNDLE_OVERFETCH_FACTOR],
          ['bundle', request.queryParamBundle],
        ]);

        recommendationsLangs.forEach((lang) => {
          if (lang !== '') {
            oldParams.append('metadata[language]', lang);
            recentParams.append('metadata[language]', lang);
          }
        });

        const [poolRecent, poolOld] = await Promise.all([
          request_recommendations(api_path, recentParams),
          request_recommendations(api_path, oldParams),
        ]);

        const videosRecent = poolRecent.slice(0, recentToLoadRow1);
        const videosRecentExtra = poolRecent.slice(recentToLoadRow1);
        const videosOld = poolOld.slice(0, oldToLoadRow1);
        const videosOldExtra = poolOld.slice(oldToLoadRow1);

        // Compute the actual number of videos from each category that will appear in the feed.
        // If there is not enough recent videos, use old ones of the same category instead.
        let recentRow1Nbr = Math.round(nbrPerRow * RECENT_VIDEOS_RATIO);
        if (recentRow1Nbr > videosRecent.length) {
          recentRow1Nbr = videosRecent.length;
        }

        const oldRow1Nbr = nbrPerRow - recentRow1Nbr;

        let recentExtraNbr = Math.round(extraNbr * RECENT_VIDEOS_EXTRA_RATIO);
        if (recentExtraNbr > videosRecentExtra.length) {
          recentExtraNbr = videosRecentExtra.length;
        }

        const oldExtraNbr = extraNbr - recentExtraNbr;

        // Select randomly which videos are displayed, merge them, and shuffle them
        // (separely for videos and extra videos).
        const selectedRecentRow1 = getRandomSubarray(
          videosRecent,
          recentRow1Nbr
        );
        const selectedOldRow1 = getRandomSubarray(videosOld, oldRow1Nbr);

        const row1 = getRandomSubarray(
          [...selectedRecentRow1, ...selectedOldRow1],
          nbrPerRow
        );

        const selectedRecentExtra = getRandomSubarray(
          videosRecentExtra,
          recentExtraNbr
        );
        const selectedOldExtra = getRandomSubarray(videosOldExtra, oldExtraNbr);

        const extraRows = getRandomSubarray(
          [...selectedRecentExtra, ...selectedOldExtra],
          extraNbr
        );

        return {
          data: [...row1, ...extraRows],
          recommandationsLanguages: recommendationsLangs.join(','),
          loadVideos: nbrPerRow > 0,
          loadAdditionalVideos: extraNbr > 0,
        };
      };
      process().then(sendResponse);
      return true;
    } else if (request.message === 'getTournesolSearchRecommendations') {
      const process = async () => {
        const api_path = `polls/${poll_name}/recommendations/`;

        const videosNumber = request.videosNumber;
        const recommendationsLangs =
          await getRecommendationsLanguagesAuthenticated();

        // Only one request for both videos and additional videos
        const params = new URLSearchParams([
          ['limit', Math.max(20, videosNumber)],
          ['search', request.search],
          ['unsafe', false],
          ['score_mode', 'default'],
        ]);

        recommendationsLangs.forEach((lang) => {
          if (lang !== '') {
            params.append('metadata[language]', lang);
          }
        });

        const [videosList] = await Promise.all([
          request_recommendations(api_path, params),
        ]);

        return {
          data: videosList.splice(0, videosNumber),
          recommandationsLanguages: recommendationsLangs.join(','),
          loadVideos: request.videosNumber > 0,
          loadAdditionalVideos: request.additionalVideosNumber > 0,
        };
      };
      process().then(sendResponse);
      return true;
    }
  } else if (request.message === 'getBanners') {
    const process = async () => {
      const path = 'backoffice/banners/';

      const response = await fetchTournesolApi(path, { authenticate: false });
      const banners =
        response && response.ok ? await response.json() : undefined;

      sendResponse({ banners });
    };
    process();
    return true;
  }
});

// Send message to Tournesol tab on URL change, to sync access token
// during navigation (after login, logout, etc.)
chrome.webNavigation.onHistoryStateUpdated.addListener(
  (event) => {
    chrome.tabs.sendMessage(event.tabId, 'historyStateUpdated');
  },
  {
    url: [{ hostEquals: frontendHost }],
  }
);
