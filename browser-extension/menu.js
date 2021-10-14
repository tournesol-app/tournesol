
function get_current_tab_video_id() {
  function get_tab_video_id(tabs) {
    for (let tab of tabs) { // only one tab is returned
      var video_id = new URL(tab.url).searchParams.get('v');
      if (video_id == null || video_id === "") {
        return Promise.reject(new Error("not a video id"));
      }
      return video_id;
    }
  }

  return new Promise((resolve, reject) => {
    chrome.tabs.query({active:true, currentWindow:true}, resolve);
  }).then(get_tab_video_id);
}


function rate_now() {
  get_current_tab_video_id().then(videoId => {
     chrome.tabs.create({url: `https://tournesol.app/comparison/?videoA=${videoId}`})
  },
    err => {
      alert('This must be used on the page of a youtube video', 'ok');
    }
  );
}


function rate_later() {
  get_current_tab_video_id().then(videoId => {
    const button = document.getElementById('rate_later')
    button.innerText = 'Done!'
    button.disabled = true
    addRateLater(videoId)
  },
    err => {
      alert('This must be used on the page of a youtube video', 'ok');
    }
  );
}


function details() {
  get_current_tab_video_id().then(videoId => {
     chrome.tabs.create({url: `https://tournesol.app/video/${videoId}`})
  },
    err => {
      alert('This must be used on the page of a youtube video', 'ok');
    }
  );
}

document.addEventListener('DOMContentLoaded', function () {
  document.getElementById('rate_now').addEventListener('click', rate_now);
  document.getElementById('rate_later').addEventListener('click', rate_later);
  document.getElementById('details').addEventListener('click', details);
});
