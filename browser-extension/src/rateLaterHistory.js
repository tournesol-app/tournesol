const RATE_LATER_BULK_MAX_SIZE = 20;

const onYoutubeReady = (callback) => {
  /**
   * Youtube doesnt completely load a video page, so content script doesn't
   * launch correctly without these events.
   *
   * This part is called on connection for the first time on youtube.com/*
   */
  document.addEventListener('yt-navigate-finish', () => {
    callback();
  });

  if (document.body) {
    callback();
  } else {
    document.addEventListener('DOMContentLoaded', () => {
      callback();
    });
  }
};

const addOverlay = () => {
  const overlay = document.createElement('div');
  overlay.id = 'tournesol-rate-later-history-overlay';
  document.body.append(overlay);

  const statusBox = document.createElement('div');
  statusBox.id = 'tournesol-rate-later-history-status-box';
  overlay.append(statusBox);

  const title = document.createElement('h3');
  title.textContent = chrome.i18n.getMessage('rateLaterHistoryStatusBoxTitle');
  statusBox.append(title);

  const loader = document.createElement('div');
  loader.classList.add('lds-dual-ring');
  statusBox.append(loader);

  const addCounter = ({ label, initialValue = 0 }) => {
    const container = document.createElement('div');

    const labelElement = document.createElement('span');
    labelElement.textContent = label;
    container.append(labelElement);

    container.append(document.createTextNode(' '));

    const countElement = document.createElement('span');
    countElement.classList.add('count');
    container.append(countElement);

    const displayCount = (count) => {
      countElement.textContent = count.toString();
    };

    displayCount(initialValue);

    statusBox.append(container);

    return { displayCount };
  };

  const { displayCount: displayHistoryVideoCount } = addCounter({
    label: chrome.i18n.getMessage('rateLaterHistoryVideoCount'),
  });

  const { displayCount: displaySentVideoCount } = addCounter({
    label: chrome.i18n.getMessage('rateLaterHistoryAddedCount'),
  });

  const { displayCount: displayFailedVideoCount } = addCounter({
    label: chrome.i18n.getMessage('rateLaterHistoryFailureCount'),
  });

  const message = document.createElement('p');
  message.textContent = chrome.i18n.getMessage(
    'rateLaterHistoryStatusBoxMessage'
  );
  statusBox.append(message);

  const stopButton = document.createElement('button');
  stopButton.id = 'tournesol-rate-later-history-stop-button';
  stopButton.classList.add('tournesol-rate-later-history-button');
  stopButton.textContent = chrome.i18n.getMessage(
    'rateLaterHistoryStopButtonLabel'
  );
  statusBox.append(stopButton);

  const removeOverlay = () => overlay.remove();

  return {
    removeOverlay,
    displayHistoryVideoCount,
    displaySentVideoCount,
    displayFailedVideoCount,
    stopButton,
  };
};

const addRateLaterBulk = async (videoIds) =>
  new Promise((resolve, reject) => {
    chrome.runtime.sendMessage(
      {
        message: 'addRateLaterBulk',
        videoIds,
      },
      (response) => {
        if (response === undefined)
          reject(new Error('addRateLaterBulk failed'));
        else if (response instanceof Error) reject(response);
        else resolve(response);
      }
    );
  });

const chunkArray = (array, chunkSize) => {
  if (chunkSize <= 0) {
    throw new Error('Chunk size must be greater than 0');
  }

  const chunks = [];

  for (let i = 0; i < array.length; i += chunkSize) {
    chunks.push(array.slice(i, i + chunkSize));
  }

  return chunks;
};

const addVideoIdsToRateLater = async (videoIds) => {
  let promise = Promise.resolve();

  const addedSet = new Set();
  const failedSet = new Set();

  const chunkedVideoIds = chunkArray(
    Array.from(videoIds),
    RATE_LATER_BULK_MAX_SIZE
  );

  chunkedVideoIds.forEach((chunk) => {
    promise = promise.then(async () => {
      try {
        await addRateLaterBulk(chunk);
        chunk.forEach((videoId) => addedSet.add(videoId));
      } catch (e) {
        console.error(e);
        chunk.forEach((videoId) => failedSet.add(videoId));
      }
    });
  });

  await promise;

  return { addedSet, failedSet };
};

const forEachVisibleVideoId = (callback) => {
  const previews = document.querySelectorAll('ytd-video-renderer');
  previews.forEach((preview) => {
    const title = preview.querySelector('#video-title');
    const href = title.getAttribute('href');
    const params = new URLSearchParams(href.replace(/.*\?/, ''));
    const videoId = params.get('v');
    if (videoId) callback(videoId);
  });
};

const loadMoreVideos = () => {
  // Scroll to the bottom of the page to trigger the infinite loader
  const previews = document.querySelectorAll('ytd-video-renderer');
  previews[previews.length - 1].scrollIntoView(true);
};

const startHistoryCapture = async () =>
  new Promise((resolve) => {
    const historyVideoIdSet = new Set();
    let sentVideoIdSet = new Set();
    let addedCount = 0;
    let failedCount = 0;

    let abort = false;

    document.body.classList.add('tournesol-capturing-history');

    const {
      removeOverlay,
      displayHistoryVideoCount,
      displaySentVideoCount,
      displayFailedVideoCount,
      stopButton,
    } = addOverlay();

    let timeout;

    const captureStep = async () => {
      forEachVisibleVideoId((videoId) => {
        historyVideoIdSet.add(videoId);
      });

      displayHistoryVideoCount(historyVideoIdSet.size);

      const videosToSend = historyVideoIdSet.difference(sentVideoIdSet);
      if (videosToSend.size > 0) {
        const { addedSet, failedSet } = await addVideoIdsToRateLater(
          videosToSend
        );

        sentVideoIdSet = sentVideoIdSet.union(videosToSend);

        addedCount += addedSet.size;
        displaySentVideoCount(addedCount);

        failedCount += failedSet.size;
        displayFailedVideoCount(failedCount);
      }

      if (abort) return;

      loadMoreVideos();

      if (abort) return;

      timeout = setTimeout(captureStep, 1000);
    };
    captureStep();

    stopButton.addEventListener('click', () => {
      abort = true;
      if (timeout) clearTimeout(timeout);
      removeOverlay();
      document.body.classList.remove('tournesol-capturing-history');
      resolve();
    });
  });

const isLoggedIn = async () =>
  new Promise((resolve) => {
    chrome.runtime.sendMessage({ message: 'isLoggedIn' }, (response) =>
      resolve(response)
    );
  });

const requestLogin = () => {
  chrome.runtime.sendMessage({ message: 'displayModal' });
};

const addRateLaterHistoryButton = () => {
  const buttonId = 'tournesol-rate-later-history-import-button';
  const previousButton = document.getElementById(buttonId);
  if (previousButton) previousButton.remove();

  const button = document.createElement('button');
  button.id = buttonId;
  button.classList.add('tournesol-rate-later-history-button');

  button.append(chrome.i18n.getMessage('rateLaterHistoryImportButton'));

  button.addEventListener('click', async () => {
    if (await isLoggedIn()) {
      try {
        button.disabled = true;
        await startHistoryCapture();
      } finally {
        button.disabled = false;
      }
    } else requestLogin();
  });

  const menuContents = document.querySelector(
    'ytd-browse-feed-actions-renderer #contents'
  );
  menuContents.prepend(button);
};

onYoutubeReady(() => {
  addRateLaterHistoryButton();
});
