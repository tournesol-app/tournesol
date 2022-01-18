import {fetchTournesolApi, getRandomSubarray, addRateLater, alertUseOnLinkToYoutube} from  './utils.js'

const oversamplingRatioForRecentVideos = 3;
const oversamplingRatioForOldVideos = 50;
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

const request_recommendations = async (options) => {
  const api_url = 'video/';

  const resp = await fetchTournesolApi(`${api_url}${options ? '?' : ''}${options}`, 'GET');
  if (resp && resp.ok) {
    const json = await resp.json();
    return json.results
  }
  return []
};

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.message == "addRateLater") {
    addRateLater(request.video_id).then(sendResponse);
    return true;
  }
  if (request.message == "getVideoStatistics") {
    // getVideoStatistics(request.video_id).then(sendResponse);
    return true;
  }

  
  

  

  if (request.message == "getTournesolRecommendations") {
    const threeWeeksAgo = getDateThreeWeeksAgo();
    const URLparams = `date_gte=${threeWeeksAgo}`;
    const process = getRecommandations(URLparams, request,
      {oversamplingRatioForRecentVideos,
        oversamplingRatioForOldVideos,
        recentVideoProportion,
        recentVideoProportionForAdditionalVideos});
    process.then(sendResponse);
    return true;
  }
  if (request.message == "getTournesolSearchRecommendations") {
    const process = async () => {
      const videos = await request_recommendations(`search=${request.query}&language=${request.language}&limit=${request.videosNumber}`);
      
      return {
        data: videos,
        loadVideos:request.videosNumber > 0, 
        loadAdditionalVideos:false };
    }
    process().then(sendResponse);
    return true;
  }
});

async function getRecommandations(URLparams, request, 
  {oversamplingRatioForRecentVideos,
    oversamplingRatioForOldVideos,
    recentVideoProportion,
    recentVideoProportionForAdditionalVideos}){
  // Compute the number of videos to load in each category
  const recentVideoToLoad = Math.round(request.videosNumber*oversamplingRatioForRecentVideos*recentVideoProportion);
  const oldVideoToLoad = Math.round(request.videosNumber*oversamplingRatioForOldVideos*(1-recentVideoProportion));
  const recentAdditionalVideoToLoad = 
    Math.round(request.additionalVideosNumber*oversamplingRatioForRecentVideos*recentVideoProportionForAdditionalVideos);
  const oldAdditionalVideoToLoad = 
    Math.round(request.additionalVideosNumber*oversamplingRatioForOldVideos*(1-recentVideoProportionForAdditionalVideos));
  
  // Only one request for both videos and additional videos
  const recent = await request_recommendations(
    `${URLparams}&language=${request.language}&limit=${recentVideoToLoad+recentAdditionalVideoToLoad}`
  );
  const old = await request_recommendations(
    `${URLparams}&language=${request.language}&limit=${oldVideoToLoad+oldAdditionalVideoToLoad}`
  );
  
  // Cut the response into the part for the videos and the one for the additional videos
  const videoRecent = recent.slice(0,recentVideoToLoad);
  const videoOld = old.slice(0,oldVideoToLoad);
  const additionalVideoRecent = recent.slice(recentVideoToLoad);
  const additionalVideoOld = old.slice(oldVideoToLoad);
  
  // Compute the actual number of videos from each category that will appear in the feed
  // If there is not enough recent videos, use old ones of the same category instead
  let numberOfRecentVideoToRespond = Math.round(request.videosNumber*recentVideoProportion);
  if(numberOfRecentVideoToRespond > videoRecent.length){
    numberOfRecentVideoToRespond = videoRecent.length;
  }
  const numberOfOldVideoToRespond = request.videosNumber - numberOfRecentVideoToRespond;

  let numberOfRecentAdditionalVideoToRespond = Math.round(request.additionalVideosNumber*recentVideoProportionForAdditionalVideos);
  if(numberOfRecentAdditionalVideoToRespond > additionalVideoRecent.length){
    numberOfRecentAdditionalVideoToRespond = additionalVideoRecent.length;
  }
  const numberOfOldAdditionalVideoToRespond = request.additionalVideosNumber - numberOfRecentAdditionalVideoToRespond;

  // Select randomly which videos are selected, merge them, and shuffle them
  // (separely for videos and additional videos)
  const recentVideos = getRandomSubarray(videoRecent, numberOfRecentVideoToRespond);
  const oldVideos = getRandomSubarray(videoOld, numberOfOldVideoToRespond);
  const videos = getRandomSubarray([...oldVideos, ...recentVideos], request.videosNumber);

  const additionalRecentVideos = getRandomSubarray(additionalVideoRecent, numberOfRecentAdditionalVideoToRespond);
  const additionalOldVideos = getRandomSubarray(additionalVideoOld, numberOfOldAdditionalVideoToRespond);
  const additionalVideos = getRandomSubarray([...additionalRecentVideos, ...additionalOldVideos], request.additionalVideosNumber);
  
  return { 
    data: [...videos, ...additionalVideos], 
    loadVideos:request.videosNumber > 0, 
    loadAdditionalVideos:request.additionalVideosNumber > 0 
  };
}

// Send message to Tournesol tab on URL change, to sync access token
// during navigation (after login, logout, etc.)
chrome.webNavigation.onHistoryStateUpdated.addListener(event => {
  chrome.tabs.sendMessage(event.tabId, "historyStateUpdated")
}, {
  url: [{hostEquals: "tournesol.app"}]
});