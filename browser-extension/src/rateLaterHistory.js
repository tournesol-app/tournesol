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
  document.body.classList.add('tournesol-capturing-history');

  const overlay = document.createElement('div');
  overlay.id = 'tournesol-rate-later-history-overlay';
  document.body.append(overlay);

  const statusBox = document.createElement('div');
  statusBox.id = 'tournesol-rate-later-history-status-box';
  overlay.append(statusBox);

  const title = document.createElement('h3');
  title.textContent = chrome.i18n.getMessage('rateLaterHistoryStatusBoxTitle');
  statusBox.append(title);

  const alertBox = document.createElement('div');
  alertBox.classList.add('alert-box', 'display-none');
  const alertBoxText1 = document.createElement('p');
  alertBoxText1.textContent = chrome.i18n.getMessage(
    'rateLaterHistoryStatusBox429AlertP1'
  );
  const alertBoxText2 = document.createElement('p');
  alertBoxText2.textContent = chrome.i18n.getMessage(
    'rateLaterHistoryStatusBox429AlertP2'
  );
  alertBox.append(alertBoxText1);
  alertBox.append(alertBoxText2);
  statusBox.append(alertBox);

  const loader = document.createElement('div');
  loader.classList.add('lds-dual-ring');
  statusBox.append(loader);

  const showTooManyRequests = () => {
    loader.classList.add('display-none');
    loader.classList.remove('lds-dual-ring');
    alertBox.classList.remove('display-none');
    message.classList.add('visibility-hidden');

    stopButton.textContent = chrome.i18n.getMessage(
      'rateLaterHistoryCloseButtonLabel'
    );
  };

  const addCounter = ({ label, initialValue = 0 }) => {
    const container = document.createElement('div');
    container.classList.add('counter-section');

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

  const addCounterList = ({ labels, initialValue = 0 }) => {
    const container = document.createElement('div');
    const uList = document.createElement('ul');

    const counters = [];

    labels.forEach((label) => {
      const lineElement = document.createElement('li');
      const labelElement = document.createElement('span');
      labelElement.textContent = label;
      lineElement.append(labelElement);

      lineElement.append(document.createTextNode(' '));

      const countElement = document.createElement('span');
      countElement.classList.add('count');
      lineElement.append(countElement);
      counters.push(countElement);
      uList.append(lineElement);
    });

    container.append(uList);

    const displayCounts = (counts) => {
      for (let i = 0; i < counts.length; i++) {
        counters[i].textContent = counts[i].toString();
      }
    };

    displayCounts(new Array(labels.length).fill(initialValue));
    statusBox.append(container);

    return { displayCounts };
  };

  const { displayCount: displayHistoryVideoCount } = addCounter({
    label: chrome.i18n.getMessage('rateLaterHistoryVideoCount'),
  });

  const { displayCount: displayProcessedVideoCount } = addCounter({
    label: chrome.i18n.getMessage('rateLaterHistoryProcessedCount'),
  });

  const { displayCounts: displayDetailedVideoCounts } = addCounterList({
    labels: [
      chrome.i18n.getMessage('rateLaterHistorySentCount'),
      chrome.i18n.getMessage('rateLaterHistorySkippedCount'),
      chrome.i18n.getMessage('rateLaterHistoryFailureCount'),
    ],
  });

  const message = document.createElement('p');
  message.id = 'when-to-stop';
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

  const removeOverlay = () => {
    overlay.remove();
    document.body.classList.remove('tournesol-capturing-history');
  };

  return {
    removeOverlay,
    displayHistoryVideoCount,
    displayProcessedVideoCount,
    displayDetailedVideoCounts,
    showTooManyRequests,
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
        if (response.success) {
          resolve(response.body)
        }
        else {
          reject(response)
        }
      }
    );
  });

const skipPreviouslyImported = async (videoSet) => {
  const newVideos = new Set();
  const localStorage = await chrome.storage.local.get('youtubeHistoryImported');
  const historyInStorage = localStorage?.youtubeHistoryImported;

  for (const video of videoSet) {
    if (!historyInStorage?.includes(video)) {
      newVideos.add(video);
    }
  }

  return newVideos;
};

const saveImportedToLocalStorage = async (importedVideosSet) => {
  const localStorage = await chrome.storage.local.get('youtubeHistoryImported');
  const historyInStorage = localStorage?.youtubeHistoryImported;

  let videosStr = '';
  for (const video of importedVideosSet) {
    if (!historyInStorage?.includes(video)) {
      videosStr += `,${video}`;
    }
  }

  if (!historyInStorage) {
    videosStr = videosStr.substring(1);
  }

  await chrome.storage.local.set({
    youtubeHistoryImported: historyInStorage
      ? historyInStorage + videosStr
      : videosStr,
  });
};

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
  const processedSet = new Set();
  const failedSet = new Set();

  let addedNbr = 0;
  let alreadyExistingNbr = 0;
  let tooManyRequests = false;

  const chunkedVideoIds = chunkArray(
    Array.from(videoIds),
    RATE_LATER_BULK_MAX_SIZE
  );

  for (const chunk of chunkedVideoIds) {
    try {
      const videosAddedByChunk = await addRateLaterBulk(chunk);
      addedNbr += videosAddedByChunk.length;
      alreadyExistingNbr += chunk.length - videosAddedByChunk.length;
      chunk.forEach((videoId) => processedSet.add(videoId));
    } catch (e) {
      console.error(e);
      chunk.forEach((videoId) => failedSet.add(videoId));
      if (e?.status === 429) {
        tooManyRequests = true;
        break;
      }
    }
  }

  return {
    processedSet,
    failedSet,
    addedNbr,
    alreadyExistingNbr,
    tooManyRequests,
  };
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
    // Videos currently visible in the YT history.
    const historyVideoIdSet = new Set();
    // Visible videos that have been sent to the Tournesol API.
    let sentVideoIdSet = new Set();
    // Visible videos that have been skipped, and not sent to the Tournesol API.
    let skippedVideoIdSet = new Set();

    let addedCount = 0;
    let failedCount = 0;
    let skippedCount = 0;
    let abort = false;

    const {
      removeOverlay,
      displayHistoryVideoCount,
      displayProcessedVideoCount,
      displayDetailedVideoCounts,
      showTooManyRequests,
      stopButton,
    } = addOverlay();

    let timeout;

    const abortCapture = ({ close = false } = {}) => {
      abort = true;
      if (timeout) clearTimeout(timeout);
      if (close) {
        removeOverlay();
        resolve();
      }
    };

    const captureStep = async () => {
      forEachVisibleVideoId((videoId) => {
        historyVideoIdSet.add(videoId);
      });

      displayHistoryVideoCount(historyVideoIdSet.size);

      const videosToSend = historyVideoIdSet
        .difference(sentVideoIdSet)
        .difference(skippedVideoIdSet);

      let newVideosToSend = new Set();

      try {
        newVideosToSend = await skipPreviouslyImported(videosToSend);
      } catch (error) {
        console.error(error);
        newVideosToSend = videosToSend;
      }

      if (newVideosToSend.size > 0) {
        const { processedSet, failedSet, tooManyRequests } =
          await addVideoIdsToRateLater(newVideosToSend);

        try {
          await saveImportedToLocalStorage(processedSet);
        } catch (error) {
          console.error(error);
        }

        addedCount += processedSet.size;
        failedCount += failedSet.size;

        sentVideoIdSet = sentVideoIdSet.union(newVideosToSend);

        if (tooManyRequests) {
          abortCapture();
          showTooManyRequests();
          return;
        }
      }

      const skipped = videosToSend.difference(newVideosToSend);
      if (skipped.size > 0) {
        skippedCount += skipped.size;
        skippedVideoIdSet = skippedVideoIdSet.union(skipped);
      }

      displayProcessedVideoCount(addedCount + skippedCount + failedCount);
      displayDetailedVideoCounts([addedCount, skippedCount, failedCount]);

      if (abort) return;

      loadMoreVideos();

      if (abort) return;

      timeout = setTimeout(captureStep, 1000);
    };
    captureStep();

    stopButton.addEventListener('click', () => {
      abortCapture({ close: true });
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
  if (menuContents) {
    // The menu may not be found yet when the History page is the entry page.
    menuContents.prepend(button);
  }
};

onYoutubeReady(() => {
  addRateLaterHistoryButton();
});
