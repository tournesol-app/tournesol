async function getAccessToken() {
  return new Promise((resolve) => {
    chrome.storage.local.get(['access_token'], items => {
      resolve(items.access_token)
    })
  })
}

async function getCurrentTab() {
  let queryOptions = { active: true, currentWindow: true };
  let [tab] = await chrome.tabs.query(queryOptions);
  return tab;
}

export const alertOnCurrentTab = async (msg) => {
  const tab = await getCurrentTab();
  function sendAlert(m) { alert(m, 'ok') }
  chrome.scripting.executeScript({
    target: {tabId: tab.id},
    func: sendAlert,
    args: [msg]
  })
}

export const alertUseOnLinkToYoutube = () => {
  alertOnCurrentTab('This must be used on a link to a youtube video')
}

export const alertNotLoggedInOrError = () => {
  alertOnCurrentTab('Make sure you are logged in on https://tournesol.app/. If you are logged in and this error persist, please let us know by creating an issue on https://github.com/tournesol-app/tournesol-chrome-extension/')
}

export const fetchTournesolApi = async (url, method, data) => {
  const headers = {
    Accept: 'application/json',
    'Content-Type': 'application/json',
  }
  const access_token = await getAccessToken();
  if (access_token){
    headers['Authorization']= `Bearer ${access_token}`
  }
  const body = {
    credentials: 'include',
    method: method,
    mode: 'cors',
    headers: headers,
  }
  if (data) {
    body["body"]= JSON.stringify(data)
  }
  return fetch(`https://api.tournesol.app/${url}`, body).then(r => {
    if (r.status == 403 || r.status == 401) alertNotLoggedInOrError()
    return r.json()
  }).catch(console.error)
}

export const addRateLater = (video_id) => {
  fetchTournesolApi('video/', 'POST', {video_id: video_id}, () => {}).then( () => {
    fetchTournesolApi('users/me/video_rate_later/', 'POST', {video: {video_id: video_id}}, () => {})
  })
};

/*
 ** Useful method to extract a subset from an array
 ** Copied from https://stackoverflow.com/questions/11935175/sampling-a-random-subset-from-an-array
 ** Used for adding some randomness in recommendations
 */
export const getRandomSubarray = (arr, size) => {
  var shuffled = arr.slice(0), i = arr.length, temp, index;
  while (i--) {
    index = Math.floor((i + 1) * Math.random());
    temp = shuffled[index];
    shuffled[index] = shuffled[i];
    shuffled[i] = temp;
  }
  return shuffled.slice(0, size);
}

export const getVideoStatistics = (videoId) => {
  return fetchTournesolApi(`videos/?video_id=${videoId}`, 'GET', {});
}
