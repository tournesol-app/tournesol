export const getAccessToken = async () => {
  return new Promise((resolve) => {
    chrome.storage.local.get(['access_token'], (items) => {
      resolve(items.access_token);
    });
  });
};

export const alertOnCurrentTab = async (msg) => {
  chrome.tabs.executeScript({
    code: `alert("${msg}", 'ok')`,
  });
};

export const alertUseOnLinkToYoutube = () => {
  alertOnCurrentTab('This must be used on a link to a youtube video');
};

export const alertInvalidAccessToken = () => {
  alertOnCurrentTab(
    'Your connection to Tournesol needs to be refreshed.\\n\\n' +
      'Please log in using the form below.'
  );
};

export const fetchTournesolApi = async (url, method, data) => {
  const headers = {
    Accept: 'application/json',
    'Content-Type': 'application/json',
  };
  const access_token = await getAccessToken();
  if (access_token) {
    headers['Authorization'] = `Bearer ${access_token}`;
  }

  const body = {
    credentials: 'include',
    method: method,
    mode: 'cors',
    headers: headers,
  };
  if (data) {
    body['body'] = JSON.stringify(data);
  }
  return fetch(`https://api.tournesol.app/${url}`, body)
    .then((r) => {
      if (r.status === 401 || r.status === 403) {
        // 401 Unauthorized with an access token means either
        // - the token has expired
        // - the token has been crafted
        if (r.status === 401 && access_token) {
          alertInvalidAccessToken();
        }
      }
      return r;
    })
    .catch(console.error);
};

export const addRateLater = async (video_id) => {
  const ratingStatusReponse = await fetchTournesolApi(
    'users/me/rate_later/videos/',
    'POST',
    { entity: { uid: 'yt:' + video_id } }
  );
  if (ratingStatusReponse && ratingStatusReponse.ok) {
    return {
      success: true,
      message: 'Done!',
    };
  }
  if (ratingStatusReponse && ratingStatusReponse.status === 409) {
    return {
      success: true,
      message: 'Already added.',
    };
  }
  return {
    success: false,
    message: 'Failed.',
  };
};

/*
 ** Useful method to extract a subset from an array
 ** Copied from https://stackoverflow.com/questions/11935175/sampling-a-random-subset-from-an-array
 ** Used for adding some randomness in recommendations
 */
export const getRandomSubarray = (arr, size) => {
  var shuffled = arr.slice(0),
    i = arr.length,
    temp,
    index;
  while (i--) {
    index = Math.floor((i + 1) * Math.random());
    temp = shuffled[index];
    shuffled[index] = shuffled[i];
    shuffled[i] = temp;
  }
  return shuffled.slice(0, size);
};

export const getVideoStatistics = (videoId) => {
  return fetchTournesolApi(`videos/?video_id=${videoId}`, 'GET', {});
};

export const millifyViews = (videoViews) => {
  videoViews = videoViews.toString().replace(/[^0-9.]/g, '');
  if (videoViews < 1000) {
    return videoViews;
  }
  let si = [
    { v: 1e3, s: 'K' },
    { v: 1e6, s: 'M' },
    { v: 1e9, s: 'B' },
  ];
  let index;
  for (index = si.length - 1; index > 0; index--) {
    if (videoViews >= si[index].v) {
      break;
    }
  }
  return (
    (videoViews / si[index].v)
      .toFixed(1)
      .replace(/\.0+$|(\.[0-9]*[1-9])0+$/, '$1') + si[index].s
  );
};

// Code for TimeAgo
const MONTH_NAMES = [
  'January',
  'February',
  'March',
  'April',
  'May',
  'June',
  'July',
  'August',
  'September',
  'October',
  'November',
  'December',
];

function getFormattedDate(date, prefomattedDate = false, hideYear = false) {
  const day = date.getDate();
  const month = MONTH_NAMES[date.getMonth()];
  const year = date.getFullYear();
  const hours = date.getHours();
  let minutes = date.getMinutes();

  if (minutes < 10) {
    // Adding leading zero to minutes
    minutes = `0${minutes}`;
  }

  if (prefomattedDate) {
    // Today at 10:20
    // Yesterday at 10:20
    return `${prefomattedDate} at ${hours}:${minutes}`;
  }

  if (hideYear) {
    // 10. January at 10:20
    return `${day}. ${month} at ${hours}:${minutes}`;
  }

  // 10. January 2017. at 10:20
  return `${day}. ${month} ${year}. at ${hours}:${minutes}`;
}

// --- Main function
function timeAgo(dateParam) {
  if (!dateParam) {
    return null;
  }

  const date = typeof dateParam === 'object' ? dateParam : new Date(dateParam);
  const DAY_IN_MS = 86400000; // 24 * 60 * 60 * 1000
  const today = new Date();
  const yesterday = new Date(today - DAY_IN_MS);
  const seconds = Math.round((today - date) / 1000);
  const minutes = Math.round(seconds / 60);
  const isToday = today.toDateString() === date.toDateString();
  const isYesterday = yesterday.toDateString() === date.toDateString();
  const isThisYear = today.getFullYear() === date.getFullYear();

  if (seconds < 5) {
    return 'now';
  } else if (seconds < 60) {
    return `${seconds} seconds ago`;
  } else if (seconds < 90) {
    return 'about a minute ago';
  } else if (minutes < 60) {
    return `${minutes} minutes ago`;
  } else if (isToday) {
    return getFormattedDate(date, 'Today'); // Today at 10:20
  } else if (isYesterday) {
    return getFormattedDate(date, 'Yesterday'); // Yesterday at 10:20
  } else if (isThisYear) {
    return getFormattedDate(date, false, true); // 10. January at 10:20
  }

  return getFormattedDate(date); // 10. January 2017. at 10:20
}
