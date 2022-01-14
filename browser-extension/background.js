import {fetchTournesolApi, getRandomSubarray, addRateLater, alertUseOnLinkToYoutube} from  './utils.js'

const oversamplingRatioForRecentVideos = 2.5;
const oversamplingRatioForOldVideos = 5;
// Higher means videos recommended can come from further down the recommandation list
// and returns videos that are more diverse on reload

const recentVideoProportion = 0.75;
const recentVideoProportionForAdditionalVideos = 0.5;


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

    const videoNumber = request.videosNumber + request.additionalVideosNumber;
    const recentVideoToLoad = Math.round(request.videosNumber*oversamplingRatioForRecentVideos*recentVideoProportion);
    const oldVideoToLoad = Math.round(request.videosNumber*oversamplingRatioForOldVideos*(1-recentVideoProportion));
    const recentAdditionalVideoToLoad = 
      Math.round(request.additionalVideosNumber*oversamplingRatioForRecentVideos*recentVideoProportionForAdditionalVideos);
    const oldAdditionalVideoToLoad = 
      Math.round(request.additionalVideosNumber*oversamplingRatioForOldVideos*(1-recentVideoProportionForAdditionalVideos));

    const process = async () => {
      const threeWeeksAgo = getDateThreeWeeksAgo()

      // Only one request for both videos and additional videos
      // That is why the responses are cut after that
      const recent = await request_recommendations(
        `date_gte=${threeWeeksAgo}&language=${request.language}&limit=${recentVideoToLoad+recentAdditionalVideoToLoad}`
      );
      const old = await request_recommendations(
        `date_lte=${threeWeeksAgo}&language=${request.language}&limit=${oldVideoToLoad+oldAdditionalVideoToLoad}`
      );

      const videoRecent = recent.slice(0,recentVideoToLoad);
      const videoOld = old.slice(0,oldVideoToLoad);
      const additionalVideoRecent = recent.slice(recentVideoToLoad);
      const additionalVideoOld = old.slice(oldVideoToLoad);

      const numberOfRecentVideoToRespond = Math.round(request.videosNumber*recentVideoProportion);
      const numberOfOldVideoToRespond = request.videosNumber - numberOfRecentVideoToRespond;
      const numberOfRecentAdditionalVideoToRespond = Math.round(request.additionalVideosNumber*recentVideoProportionForAdditionalVideos);
      const numberOfOldAdditionalVideoToRespond = request.additionalVideosNumber - numberOfRecentAdditionalVideoToRespond;

      const recentVideos = getRandomSubarray(videoRecent, numberOfRecentVideoToRespond);
      const oldVideos = getRandomSubarray(videoOld, numberOfOldVideoToRespond);
      const videos = getRandomSubarray([...oldVideos, ...recentVideos], request.videosNumber);

      const additionalRecentVideos = getRandomSubarray(additionalVideoRecent, numberOfRecentAdditionalVideoToRespond);
      const additionalOldVideos = getRandomSubarray(additionalVideoOld, numberOfOldAdditionalVideoToRespond);
      const additionalVideos = getRandomSubarray([...additionalRecentVideos, ...additionalOldVideos], request.additionalVideosNumber);
      alert(additionalVideoRecent.length + " " + recent.length+ " "+recentVideoToLoad + " nbreq "+ (recentVideoToLoad+recentAdditionalVideoToLoad)+" resp "+ recent.length);
      return { 
        data: [...videos, ...additionalVideos], 
        loadVideos:request.videosNumber > 0, 
        loadAdditionalVideos:request.additionalVideosNumber > 0 
      };
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
