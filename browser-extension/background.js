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

chrome.runtime.onMessage.addListener(function (request, sender, sendResponse) {
  console.log("onMessage")
  if (request.message == "addRateLater") {
    addRateLater(request.video_id)
  }
  else if (request.message == "getVideoStatistics") {
    getVideoStatistics(request.video_id).then(sendResponse);
    return true;
  }

  if (request.message == "getTournesolRecommendations") {
    console.log("received message getTournesolReco")
    const api_url = 'video/?search=tournesol';

    const request_recommendations = async (options) => {
      const json = await fetchTournesolApi(`${api_url}&${options}`, 'GET', null);
      console.log(json)
      return json.results;
    };

    const process = async () => {
      const videos = await request_recommendations('')
      // const recent = await request_recommendations(`days_ago_lte=21&language=${request.language}&limit=10`);
      // const old = await request_recommendations(`days_ago_gte=21&language=${request.language}&limit=30`);
      // const recent_sub = getRandomSubarray(recent.results, Math.ceil(request.video_amount / 2));
      // const old_sub = getRandomSubarray(old.results, Math.floor(request.video_amount / 2));
      // const videos = getRandomSubarray([...old_sub, ...recent_sub], request.video_amount);
      chrome.tabs.sendMessage(sender.tab.id, { data: getRandomSubarray(videos, 8) });
    };

    process();
    return;
  }
});
