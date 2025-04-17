const getYoutubeVideosPerRow = () => {
  const youtubeThumbnail = document.querySelector(
    '#primary #contents > ytd-rich-item-renderer.ytd-rich-grid-renderer'
  );
  if (!youtubeThumbnail) {
    return undefined;
  }

  const itemsPerRowCssValue = window
    .getComputedStyle(youtubeThumbnail)
    .getPropertyValue('--ytd-rich-grid-items-per-row');
  if (!itemsPerRowCssValue) {
    return undefined;
  }

  return Number(itemsPerRowCssValue);
};

const getHomeRecommendationsLayout = () =>
  new Promise((resolve) => {
    const startTime = new Date();
    const maximumSecondsWaitingForThumbnails = 5;
    const millisecondsBetweenRetries = 300;
    const defaultLayout = {
      videosPerRow: 4,
      rowsWhenCollapsed: 1,
      rowsWhenExpanded: 3,
    };
    const layoutByYoutubeVideosPerRow = {
      1: { rowsWhenCollapsed: 2, rowsWhenExpanded: 12 },
      2: { rowsWhenCollapsed: 2, rowsWhenExpanded: 6 },
      3: { rowsWhenCollapsed: 1, rowsWhenExpanded: 4 },
      4: { rowsWhenCollapsed: 1, rowsWhenExpanded: 3 },
      5: { rowsWhenCollapsed: 1, rowsWhenExpanded: 2 },
      6: { rowsWhenCollapsed: 1, rowsWhenExpanded: 2 },
    };

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

      const layout = layoutByYoutubeVideosPerRow[youtubeVideosPerRow];
      if (layout === undefined) {
        resolve(defaultLayout);
        return;
      }

      const videosPerRow = youtubeVideosPerRow;
      const { rowsWhenCollapsed, rowsWhenExpanded } = layout;
      resolve({ videosPerRow, rowsWhenCollapsed, rowsWhenExpanded });
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

    const { videosPerRow, rowsWhenCollapsed, rowsWhenExpanded } =
      await getHomeRecommendationsLayout();

    const options = new TournesolRecommendationsOptions({
      videosPerRow,
      rowsWhenCollapsed,
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
