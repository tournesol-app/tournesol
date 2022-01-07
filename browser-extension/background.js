import {fetchTournesolApi, getRandomSubarray, addRateLater, alertUseOnLinkToYoutube} from  './utils.js'

chrome.contextMenus.removeAll(function (e, tab) {
  chrome.contextMenus.create({
    id: 'tournesol_add_rate_later',
    title: 'Rate later on Tournesol',
    contexts: ['link'],
  });
});

chrome.contextMenus.onClicked.addListener(function (e, tab) {
  var videoId = new URL(e.linkUrl).searchParams.get('v');
  if (!videoId) {
    alertUseOnLinkToYoutube()
  } else {
    addRateLater(videoId)
  }
});

function getDateThreeWeeksAgo() {
  // format a string to properly display years months and day: 2011 -> 11, 5 -> 05, 12 -> 12
  const format = (str) => str.length == 1 ? `0${str}` : str.length == 4 ? str.slice(2) : str
  const threeWeeksAgo = new Date(Date.now() - 3 * 7 * 24 * 3600000)
  const [d, m, y, H, M, S] = [
    threeWeeksAgo.getDate(),
    (threeWeeksAgo.getMonth() + 1), // adds 1 because January has index 0 in Javascript but Django expect "01"
    threeWeeksAgo.getFullYear(),
    threeWeeksAgo.getHours(),
    threeWeeksAgo.getMinutes(),
    threeWeeksAgo.getSeconds(),
  ].map((t) => format(t.toString()));
  return `${d}-${m}-${y}-${H}-${M}-${S}`;
}

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.message == "addRateLater") {
    addRateLater(request.video_id).then(sendResponse);
    return true;
  }
  else if (request.message == "getVideoStatistics") {
    // getVideoStatistics(request.video_id).then(sendResponse);
    return true;
  } 
  else if (request.message == "getTournesolRecommendations") {
    const api_url = 'video/';

    const request_recommendations = async (options) => {
      const resp = await fetchTournesolApi(`${api_url}${options ? '?' : ''}${options}`, 'GET');
      if (resp && resp.ok) {
        const json = await resp.json();
        return json.results
      }
      return []
    };

    const process = async () => {
      const threeWeeksAgo = getDateThreeWeeksAgo()
      const recent = await request_recommendations(`date_gte=${threeWeeksAgo}&language=${request.language}&limit=10`);
      const old = await request_recommendations(`date_lte=${threeWeeksAgo}&language=${request.language}&limit=50`);
      const recent_sub = getRandomSubarray(recent, request.number - 1);
      const old_sub = getRandomSubarray(old, request.number - recent_sub.length);
      const videos = getRandomSubarray([...old_sub, ...recent_sub], request.number);
      return { data: videos };
    }
    process().then(sendResponse);
    return true;
  }
});

// Send message to Tournesol tab on URL change, to sync access token
// during navigation (after login, logout, etc.)
chrome.webNavigation.onHistoryStateUpdated.addListener(event => {
  chrome.tabs.sendMessage(event.tabId, "historyStateUpdated")
}, {
  url: [{hostEquals: "tournesol.app"}]
});
