const getYoutubeVideosPerRow = () => {
  const youtubeThumbnails = Array.from(
    document.querySelectorAll(
      '#primary #contents > ytd-rich-item-renderer.ytd-rich-grid-renderer'
    )
  );
  const youtubeThumbnailsY = youtubeThumbnails
    .map((e) => e.getBoundingClientRect().y)
    .filter((y) => y !== 0);

  if (youtubeThumbnailsY.length === 0) {
    return undefined;
  }

  // We get the maximum number of thumbnails on a row because
  // sometimes YouTube renders some rows with fewer thumbnails.
  const counts = {};
  let maxCount = 0;
  for (const y of youtubeThumbnailsY) {
    const key = y.toString();
    const count = (counts[key] || 0) + 1;
    counts[key] = count;
    if (count > maxCount) maxCount = count;
  }
  return maxCount;
};

const getHomeRecommendationsLayout = () =>
  new Promise((resolve) => {
    const startTime = new Date();
    const maximumSecondsWaitingForThumbnails = 5;
    const millisecondsBetweenRetries = 300;
    const defaultLayout = { videosPerRow: 4, rowsWhenExpanded: 3 };

    const getLayout = () => {
      const elapsedSeconds = (new Date() - startTime) / 1000;
      if (elapsedSeconds > maximumSecondsWaitingForThumbnails) {
        resolve(defaultLayout);
        return;
      }

      const youtubeVideosPerRow = getYoutubeVideosPerRow();

      if (youtubeVideosPerRow === undefined) {
        setTimeout(getLayout, millisecondsBetweenRetries);
        return;
      }

      const videosPerRow = youtubeVideosPerRow;
      const rowsWhenExpanded = 3;
      resolve({ videosPerRow, rowsWhenExpanded });
    };

    getLayout();
  });

(async () => {
  let homeRecommendations;

  const initializeHomeRecommendations = async () => {
    const [
      { TournesolRecommendations },
      { TournesolRecommendationsOptions },
      { fetchBanner },
    ] = await Promise.all(
      [
        './models/tournesolRecommendations/TournesolRecommendations.js',
        './models/tournesolRecommendations/TournesolRecommendationsOptions.js',
        './models/banner/fetchBanner.js',
      ].map((path) => import(chrome.runtime.getURL(path)))
    );

    const banner = await fetchBanner();

    const { videosPerRow, rowsWhenExpanded } =
      await getHomeRecommendationsLayout();

    const options = new TournesolRecommendationsOptions({
      videosPerRow,
      rowsWhenExpanded,
      banner,
      parentComponentQuery: '#primary > ytd-rich-grid-renderer',
      displayCriteria: false,
    });
    return new TournesolRecommendations(options);
  };

  const processHomeRecommendations = async () => {
    if (homeRecommendations === undefined) {
      homeRecommendations = initializeHomeRecommendations();
    }
    (await homeRecommendations).process();
  };

  const clearHomeRecommendations = async () => {
    if (homeRecommendations === undefined) {
      return;
    }
    (await homeRecommendations).clear();
  };

  const process = () => {
    // Display the home page recommendations.
    if (location.pathname === '/') {
      processHomeRecommendations();
    } else {
      clearHomeRecommendations();
    }
  };

  /**
   * YouTube doesn't completely load a video page. The content script needs
   * these events to run correctly.
   */
  document.addEventListener('yt-navigate-finish', process);

  if (document.body) {
    process();
  } else {
    document.addEventListener('DOMContentLoaded', process);
  }
})();
