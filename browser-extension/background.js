import {fetchTournesolApi, getRandomSubarray} from  './utils.js'

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
    alert('This must be used on a link to a youtube video', 'ok');
  } else {
    addRateLater(videoId)
  }
});

function getDateThreeWeeksAgo() {
  // format a string to properly display years months and day: 2011 -> 11, 5 -> 05, 12 -> 12
  const format = (str) => str.length == 1 ? `0${str}` : str.length == 4 ? str.slice(2) : str
  const threeWeeksAgo = new Date(Date.now() - 3 * 7 * 24 * 3600)
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

chrome.runtime.onMessage.addListener(function (request, sender, sendResponse) {
  console.log("onMessage")
  if (request.message == "addRateLater") {
    addRateLater(request.video_id)
  }
  else if (request.message == "getVideoStatistics") {
    getVideoStatistics(request.video_id).then(sendResponse);
    return true;
  } 
  else if (request.message == "getTournesolRecommendations") {
    console.log("received message getTournesolReco")
    const api_url = 'video/';

    const request_recommendations = async (options) => {
      const json = await fetchTournesolApi(`${api_url}${options ? '?' : ''}${options}`, 'GET', null);
      console.log(json)
      return json.results;
    };

    const process = async () => {
      const threeWeeksAgo = getDateThreeWeeksAgo()
      const recent = await request_recommendations(`date_gte=${threeWeeksAgo}&language=${request.language}&limit=10`);
      const old = await request_recommendations(`date_lte=${threeWeeksAgo}&language=${request.language}&limit=50`);
      const recent_sub = getRandomSubarray(recent, 3);
      const old_sub = getRandomSubarray(old, 4 - recent_sub.length);
      const videos = getRandomSubarray([...old_sub, ...recent_sub], 4);
      sendResponse({ data: videos });
    };

    process();
    return true;
  }
});
