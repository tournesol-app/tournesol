console.log('123')
let access_token;
chrome.storage.local.get(['access_token'], (storage) => {
  access_token = storage.access_token
  addRateLater('xaQJbozY_Is')
})

const alertNotLoggedInOrError = () => {
  console.log("Failed")
  // chrome.tabs.executeScript(null, { code: "window.alert('Make sure you are logged in on https://tournesol.app/. If you are logged in and this error persist, please let us know by creating an issue on https://github.com/tournesol-app/tournesol-chrome-extension/', 'ok')"})
}

const fetchTournesolApi = (url, method, data, callback) => {
  console.log(access_token)

  const headers = {
    Accept: 'application/json',
    'Content-Type': 'application/json',
  }
  if (access_token){
    headers['Authorization']= `Bearer ${access_token}`
  }
  return fetch(`https://api.staging.tournesol.app/${url}`, {
    credentials: 'include',
    method: method,
    mode: 'cors',
    headers: headers,
    body: JSON.stringify(data),
  }).then(r => {
    console.log(r)
    if (r.status == 403 || r.status == 401) alertNotLoggedInOrError()
    return r.json()
  }).then(callback).catch(console.log)
}

const addRateLater = (video_id) => {
  fetchTournesolApi('video/', 'POST', {video_id: video_id}, () => {})
  fetchTournesolApi('users/lpfaucon/video_rate_later/', 'POST', {video: {video_id: video_id}}, () => {})
};

/*
 ** Useful method to extract a subset from an array
 ** Copied from https://stackoverflow.com/questions/11935175/sampling-a-random-subset-from-an-array
 ** Used for adding some randomness in recommendations
 */
const getRandomSubarray = (arr, size) => {
  var shuffled = arr.slice(0), i = arr.length, temp, index;
  while (i--) {
    index = Math.floor((i + 1) * Math.random());
    temp = shuffled[index];
    shuffled[index] = shuffled[i];
    shuffled[i] = temp;
  }
  return shuffled.slice(0, size);
}

const getVideoStatistics = (videoId) => {
  return fetchTournesolApi(`videos/?video_id=${videoId}`, 'GET', {});
}
