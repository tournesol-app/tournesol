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

  const loader = document.createElement('div');
  loader.classList.add('lds-dual-ring');
  statusBox.append(loader);

  const showTooManyRequests = () => {
    loader.classList.remove('lds-dual-ring');
    title.textContent = chrome.i18n.getMessage(
      'rateLaterHistoryStatusBoxRateLimited'
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

  const { displayCount: displaySentVideoCount } = addCounter({
    label: chrome.i18n.getMessage('rateLaterHistoryAddedCount'),
  });

  const { displayCounts: displayNewVideosCount } = addCounterList({
    labels: [
      chrome.i18n.getMessage('rateLaterHistoryAddedNewCount'),
      chrome.i18n.getMessage('rateLaterHistoryAddedExistingCount'),
    ],
  });

  const { displayCount: displayFailedVideoCount } = addCounter({
    label: chrome.i18n.getMessage('rateLaterHistoryFailureCount'),
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
    displaySentVideoCount,
    displayNewVideosCount,
    displayFailedVideoCount,
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
      if (e?.cause?.status === 429) {
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
    const historyVideoIdSet = new Set();
    let sentVideoIdSet = new Set();
    let addedCount = 0;
    let failedCount = 0;

    let newlyImportedTotal = 0;
    let previouslyImportedTotal = 0;

    let abort = false;

    const {
      removeOverlay,
      displayHistoryVideoCount,
      displaySentVideoCount,
      displayNewVideosCount,
      displayFailedVideoCount,
      stopButton,
    } = addOverlay();

    let timeout;

    const abortCapture = ({ close = false }) => {
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

      const videosToSend = historyVideoIdSet.difference(sentVideoIdSet);
      if (videosToSend.size > 0) {
        const {
          processedSet,
          failedSet,
          addedNbr,
          alreadyExistingNbr,
          tooManyRequests,
        } = await addVideoIdsToRateLater(videosToSend);

        sentVideoIdSet = sentVideoIdSet.union(videosToSend);

        addedCount += processedSet.size;
        displaySentVideoCount(addedCount);

        newlyImportedTotal += addedNbr;
        previouslyImportedTotal += alreadyExistingNbr;
        displayNewVideosCount([newlyImportedTotal, previouslyImportedTotal]);

        failedCount += failedSet.size;
        displayFailedVideoCount(failedCount);

        if (tooManyRequests) {
          abortCapture();
          return;
        }
      }

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
  menuContents.prepend(button);
};

onYoutubeReady(() => {
  addRateLaterHistoryButton();
});
